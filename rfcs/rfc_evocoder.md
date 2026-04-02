---
title: EvoCoder — Co-change-aware Code Embeddings
status: DRAFT
date: 2026-04-01
author: Carlsbert
---

# EvoCoder: Co-change-aware Code Embeddings for Code Retrieval

## Problem

Current code embedding models (CodeBERT, GraphCodeBERT, CodeXEmbed, LoRACode) encode **structural and semantic** properties of code — syntax, data flow, token patterns. They completely ignore **evolutionary coupling**: the empirical signal that certain files consistently change together over time.

Our co-change analysis of HyperRetrieval's production deployment found that **28.5% of co-change pairs are complementary** — they share no structural relationship (no imports, no shared types, no call edges). These 18,799 pairs are *invisible* to every existing embedding model and every existing retrieval system.

**The research gap is confirmed.** A survey of 16 papers (2020–2026) across commit embeddings, temporal graph models, structural code graphs, and RAG benchmarks found:

> No published work jointly embeds co-change graph topology AND code semantics into a unified representation for code retrieval.

Closest work:
- TGN for change propagation (IST 2024) — models co-change graphs but targets *prediction*, not retrieval
- LoRACode (ICLR DL4C 2025) — shows LoRA adapters work for code embeddings but uses standard pairs, not co-change pairs
- CGM (arXiv 2025) — integrates structural graphs into LLM attention but ignores evolutionary coupling
- CodeXEmbed (COLM 2025) — current SOTA generalist code embeddings, no co-change signal

This is a novel and publishable direction.

## Hypothesis

Adding co-change signal to code embeddings will improve retrieval recall for queries where the answer involves files that co-change with the query context.

- **Expected improvement:** 10–25% lift in recall@10 on co-change-relevant queries (conservative, based on the 28.5% complementarity rate — these are pairs that current embeddings fundamentally cannot surface)
- **Measurement:** Compare recall@10 of EvoCoder embeddings vs. baseline embeddings on a held-out set of queries derived from real co-change patterns
- **Null hypothesis:** Co-change signal is redundant with semantic similarity. If recall@10 does not improve by at least 5%, the approach is not worth deploying.

## Approach

Contrastive learning using co-change pairs as training signal, with a LoRA adapter on a frozen base model.

**Training data construction:**
1. From the co-change index, extract pairs (file_A, file_B) with co-change frequency >= 3
2. Label as **positive pairs**: files that co-change frequently
3. Mine **hard negatives**: files that are semantically similar (high cosine similarity in current embedding space) but never co-change
4. Mine **easy negatives**: random files from the same repo that never co-change

**Training objective:** InfoNCE contrastive loss. For each anchor file, push its embedding closer to co-change partners and farther from negatives.

**Why contrastive + LoRA, not a full dual-encoder or GNN:**
- A GNN over the co-change graph is the theoretically richer approach (per the survey's proposed direction), but requires building and maintaining a TGN pipeline
- LoRA on a frozen base model is **5x cheaper** to train, **trivial to A/B test** (swap adapter in/out), and **reversible** (just remove the adapter)
- If LoRA works, we can invest in the GNN approach in Phase 5

## Data Available

- **Co-change index:** 7,363 modules, 111,005 co-change pairs from HyperRetrieval's production deployment
- **Complementary pairs:** 28.5% = ~18,799 pairs invisible to structural analysis (these are the highest-value training signal)
- **Full graph:** 114,534 nodes, 4,809 modules with structural edges
- **Existing embeddings:** Current vector store with embeddings for all indexed code
- **Git history:** Full commit history available for temporal weighting (recent co-changes > old ones)

### Training data pipeline output

| Split    | Positive pairs | Hard negatives | Easy negatives |
|----------|---------------|----------------|----------------|
| Train    | ~80,000       | ~80,000        | ~160,000       |
| Val      | ~15,000       | ~15,000        | ~30,000        |
| Test     | ~16,005       | ~16,005        | ~32,010        |

## Architecture

```
┌─────────────────────────────────────────────┐
│              Frozen Base Model              │
│  (GraphCodeBERT-base, 125M params, ~500MB)  │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │        LoRA Adapter (r=16)            │  │
│  │     ~2M trainable params (~8MB)       │  │
│  │  Injected into Q, V attention layers  │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Output: 768-dim embedding per code file    │
└─────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│         Co-Change Contrastive Head           │
│  Projects 768-dim → 256-dim for training    │
│  (Discarded at inference; raw 768 used)     │
└─────────────────────────────────────────────┘
```

**Why GraphCodeBERT-base, not CodeXEmbed-7B or Qwen-8B:**
- GraphCodeBERT-base is 125M params → fits on 12GB VRAM with room for batch sizes of 32+
- Already encodes data flow structure (a useful inductive bias)
- LoRA adapter adds only ~8MB, total model fits in ~2GB VRAM during training
- If base model proves too weak, we can try UniXcoder (also fits) before jumping to 7B models

**Inference cost:** Identical to current embedding pipeline — the LoRA adapter adds zero latency at inference (weights are merged into the base model).

## Success Metric

- **Baseline:** Current vector search recall@10 on test_04 queries
- **Primary metric:** Recall@10 on queries where co-change signal exists (i.e., the query file has known co-change partners in the ground truth)
- **Secondary metric:** MRR@10 on the same query set
- **Target:** >= 5% absolute improvement in recall@10 for co-change-relevant queries
- **Stretch target:** >= 15% improvement (would indicate co-change is a strong signal)
- **Regression guard:** Overall recall@10 on *all* queries (including non-co-change ones) must not decrease by more than 1%
- **Threshold:** If no improvement or regression on co-change queries, revert and document findings

## Phases

### Phase 1: Build training data pipeline (Est. 2 days)
- Extract co-change pairs from the index with frequency >= 3
- Apply temporal decay weighting (exponential, half-life = 6 months)
- Mine hard negatives using current embedding cosine similarity
- Split into train/val/test with no file overlap between splits
- **Output:** `train.jsonl`, `val.jsonl`, `test.jsonl` with (anchor, positive, negatives) triplets

### Phase 2: Fine-tune GraphCodeBERT + LoRA (Est. 3 days)
- Load `microsoft/graphcodebert-base` from HuggingFace
- Apply LoRA (r=16, alpha=32) to Q and V projection matrices
- Train with InfoNCE loss, temperature=0.07, batch_size=32
- Train for 10 epochs, early stopping on val loss (patience=3)
- Estimated: ~4 GPU-hours on a single 12GB card
- **Output:** LoRA adapter weights (~8MB)

### Phase 3: Evaluate and A/B test (Est. 2 days)
- Re-embed all code files using base+adapter model
- Compute recall@10, MRR@10 on test split
- Compare against baseline embeddings on same queries
- Run statistical significance test (paired bootstrap, p<0.05)
- **Gate:** Proceed to Phase 4 only if recall@10 improves >= 5%

### Phase 4: Integration into unified_search (Est. 3 days)
- Add EvoCoder embeddings as a new retrieval source in unified_search
- Implement score fusion: `final_score = α * semantic_score + β * evocoder_score + γ * cochange_boost`
- Tune α, β, γ on validation set
- Deploy behind feature flag
- **Output:** Production-ready integration, A/B testable

### Phase 5 (Future): GNN over co-change graph
- If LoRA approach shows signal, invest in Temporal Graph Network approach
- Would enable capturing higher-order co-change patterns (transitive coupling)
- Estimated: 2-3 weeks additional work

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Co-change signal is redundant with semantic similarity | Medium | High (project fails) | Phase 3 gate check; if no improvement, we learn something and document it |
| Training data is too noisy (spurious co-changes from bulk commits) | Medium | Medium | Filter out commits touching >20 files; weight by commit specificity |
| GraphCodeBERT-base too weak for production quality | Low | Medium | Try UniXcoder or distilled CodeXEmbed-400M before going to 7B |
| Temporal decay weighting is wrong | Low | Low | Ablation study: compare no-decay, linear-decay, exponential-decay |
| LoRA rank too low/high | Low | Low | Grid search r ∈ {4, 8, 16, 32} in Phase 2 |
| Overfitting to one repo's co-change patterns | Medium | Medium | Cross-validation across different time windows; test on held-out time period |

## Rollback

1. **LoRA adapter is separate from base model** — rollback = stop loading the adapter. Zero risk to existing embeddings.
2. **Feature flag in unified_search** — rollback = disable flag. Existing retrieval pipeline unchanged.
3. **Embeddings stored separately** — EvoCoder embeddings go in a new vector collection, not overwriting current embeddings. Rollback = delete collection.
4. **Total rollback time:** < 5 minutes (disable flag + restart service)

## Cost

| Item | Estimate |
|------|----------|
| GPU hours (training, Phase 2) | ~4 hours on 12GB card (local, $0) |
| GPU hours (re-embedding, Phase 3) | ~2 hours on 12GB card (local, $0) |
| GPU hours (hyperparameter search) | ~8 hours on 12GB card (local, $0) |
| LLM tokens (data pipeline, evaluation scripts) | ~$5 in API calls |
| Storage (adapter weights) | ~8MB |
| Storage (new embedding collection) | ~50MB (7,363 modules × 768 dims × 4 bytes × 2.5 overhead) |
| **Total monetary cost** | **~$5** |
| **Total GPU time** | **~14 hours** |
| **Total human time** | **~10 days across 4 phases** |

## References

1. CC2Vec — Hoang et al., ICSE 2020
2. Commit2Vec — Lozoya et al., SN Computer Science 2021
3. GraphCodeBERT — Guo et al., ICLR 2021
4. UniXcoder — Guo et al., ACL 2022
5. TGN Change Propagation — IST 2024
6. LoRACode — Chaturvedi et al., ICLR DL4C 2025
7. CodeXEmbed — Liu et al., COLM 2025
8. CGM — arXiv 2505.16901, 2025
9. CodeRAG-Bench — NAACL Findings 2025
10. RACG Survey — arXiv 2510.04905, 2025
