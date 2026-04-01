# Co-Change Analysis Meets Code Embeddings: A Literature Survey

**Date:** 2026-04-01  
**Purpose:** Survey the intersection of co-change analysis and code embeddings for HyperRetrieval  
**Scope:** Papers from 2020-2026, with emphasis on 2023-2026

---

## Executive Summary

This survey covers five research threads: (1) learning embeddings from co-change/commit graphs, (2) software evolution embeddings, (3) combining structural + evolutionary coupling for retrieval, (4) extending Code2Vec/CodeBERT with change history, and (5) GNNs on software evolution networks.

**Key finding: There is a significant research gap at the intersection of co-change graph structure and semantic code embeddings for retrieval. No paper we found jointly learns from co-change topology AND code semantics to produce embeddings optimized for code search/retrieval. This is a novel and publishable direction.**

---

## 1. Embeddings from Code Changes (Commit-Level Representations)

### 1.1 CC2Vec: Distributed Representations of Code Changes
- **Authors:** Hoang et al.
- **Venue:** ICSE 2020
- **URL:** https://dl.acm.org/doi/10.1145/3377811.3380361
- **Key idea:** Learns distributed representations of code changes guided by commit log messages. Uses hierarchical attention to model the structure of a code change (removed vs. added code). Evaluated on log message generation, bug-fixing patch identification, and just-in-time defect prediction.
- **HyperRetrieval relevance:** CC2Vec's change embeddings could augment HyperRetrieval's vector store — indexing not just current code state but the *trajectory* of how code evolved. This enables queries like "find code that was recently refactored" or "find changes similar to this diff."

### 1.2 Commit2Vec: Learning Distributed Representations of Code Changes
- **Authors:** Lozoya et al.
- **Venue:** SN Computer Science, 2021
- **URL:** https://link.springer.com/article/10.1007/s42979-021-00566-z
- **Key idea:** Adapts code2vec's path-based approach to represent commits instead of functions. Uses AST paths from changed code to build commit representations. Applied to classifying security-relevant commits.
- **HyperRetrieval relevance:** Could power a "security impact" signal in HyperRetrieval — embedding commits to identify security-relevant changes and flagging affected code regions.

### 1.3 Patcherizer: Learning to Represent Patches
- **Authors:** Tang et al.
- **Venue:** Empirical Software Engineering, 2025 (earlier version at ICSE 2024 Poster)
- **URL:** https://link.springer.com/article/10.1007/s10664-025-10763-6
- **ArXiv:** https://arxiv.org/abs/2308.16586
- **Key idea:** Combines context-aware sequence features (via transformers) with structural AST graph features (via GCNs) to represent code changes. Captures both the "intention sequence" and "intention graph" of a patch. Evaluated on change description generation, patch correctness prediction, and change intent detection.
- **HyperRetrieval relevance:** Patcherizer's dual-representation approach (sequence + graph) for changes is directly applicable. HyperRetrieval could embed patches using both textual and structural channels, enabling richer change-aware retrieval.

### 1.4 Beyond Syntax Trees: Learning Embeddings of Code Edits
- **Authors:** (OpenReview submission)
- **Venue:** OpenReview (workshop/conference submission)
- **URL:** https://openreview.net/forum?id=H8qETo_W1-9
- **Key idea:** Extends commit2vec by combining paths from AST, Control Flow Graph (CFG), and Data Flow Graph (DFG) to represent code edits. Preliminary evaluation on security-relevant commit classification shows improvements over AST-only approaches.
- **HyperRetrieval relevance:** Multi-graph edit embeddings could enrich HyperRetrieval's understanding of code changes — not just what tokens changed, but how control flow and data flow were affected.

---

## 2. Software Evolution & Temporal Graph Models

### 2.1 To Change or Not to Change? Temporal Graphs and GNNs for Change Propagation
- **Authors:** (ScienceDirect publication)
- **Venue:** Information and Software Technology, 2024
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0950584923002239
- **Key idea:** Models a software system as a temporal graph where nodes = files, edges = co-changeability. Uses Temporal Graph Networks (TGN) + LSTM to predict which files will be impacted by a modification. Outperforms prior change propagation methods.
- **HyperRetrieval relevance:** **This is the closest paper to our target intersection.** HyperRetrieval could use temporal co-change graphs to predict "if file X changes, what else likely needs to change?" — a powerful feature for LLM-assisted code review and refactoring. The TGN embeddings could be fused with semantic code embeddings.

### 2.2 RAG-Enhanced Commit Message Generation (REACT)
- **Authors:** Zhang et al.
- **Venue:** arXiv 2024 (2406.05514)
- **URL:** https://arxiv.org/abs/2406.05514
- **Key idea:** Uses a hybrid retriever to find similar code diffs and their commit messages as exemplars for RAG-based commit message generation. Improves BLEU by 55% (CodeT5) and 102% (Llama 3).
- **HyperRetrieval relevance:** Demonstrates that commit-level retrieval (finding similar past changes) is valuable. HyperRetrieval could index all historical diffs as embeddings and retrieve relevant past changes to inform current development tasks.

---

## 3. Structural Code Graphs + Embeddings for Retrieval

### 3.1 Code Graph Model (CGM): Graph-Integrated LLM for Repository-Level Tasks
- **Authors:** (arXiv 2025)
- **Venue:** arXiv 2505.16901 (June 2025)
- **URL:** https://arxiv.org/abs/2505.16901
- **Key idea:** Integrates repository code graph structures (call graphs, class hierarchies, import dependencies) directly into an LLM's attention mechanism via a graph adapter. Includes a Graph RAG framework with Rewriter, Retriever, Reranker, and Reader modules. Unlike prior work that flattens graph-retrieved code into text, CGM preserves graph structure during generation.
- **HyperRetrieval relevance:** **Highly relevant architecture.** CGM's Graph RAG pipeline (Rewriter → Retriever → Reranker → Reader) is essentially what HyperRetrieval should implement. The key insight is preserving graph structure through the entire pipeline rather than flattening to text.

### 3.2 Integrated GNN for Defect Prediction + Code Quality Assessment
- **Authors:** (Scientific Reports, 2025)
- **Venue:** Nature Scientific Reports, 2025
- **URL:** https://www.nature.com/articles/s41598-025-31209-5
- **Key idea:** Multi-level graph representations (AST + CFG + DFG) with dual-branch attention-based GNN for joint defect prediction and code quality assessment. The shared encoder learns structural patterns relevant to both tasks.
- **HyperRetrieval relevance:** The multi-level graph encoding approach (AST+CFG+DFG) could be adopted by HyperRetrieval to create richer code node embeddings that capture syntax, control flow, and data flow simultaneously.

### 3.3 GraphCodeBERT: Pre-training Code Representations with Data Flow
- **Authors:** Guo et al. (Microsoft Research)
- **Venue:** ICLR 2021
- **URL:** https://arxiv.org/abs/2009.08366
- **Key idea:** First pre-trained model to leverage code structure (data flow graphs) for code representation. Uses graph-guided masked attention and structure-aware pre-training tasks (edge prediction, code-structure alignment). SOTA on code search, clone detection, translation, refinement.
- **HyperRetrieval relevance:** GraphCodeBERT is a strong baseline embedding model for HyperRetrieval. Its data-flow-aware embeddings capture semantic relationships that pure token models miss. Could serve as the base encoder that gets augmented with co-change signals.

### 3.4 UniXcoder: Unified Cross-Modal Pre-training for Code Representation
- **Authors:** Guo et al. (Microsoft Research)
- **Venue:** ACL 2022
- **URL:** https://github.com/microsoft/CodeBERT/tree/master/UniXcoder
- **Key idea:** Unified model supporting both understanding and generation tasks. Incorporates semantic info from comments and structural info from ASTs via a cross-modal architecture.
- **HyperRetrieval relevance:** UniXcoder's multi-modal approach (text + structure) provides a template for how HyperRetrieval could add a third modality: evolutionary coupling / co-change signals.

---

## 4. Code Embedding Models for Retrieval (State of the Art)

### 4.1 CodeXEmbed: A Generalist Embedding Model Family
- **Authors:** Liu et al. (Salesforce AI Research)
- **Venue:** COLM 2025
- **URL:** https://arxiv.org/abs/2411.12644
- **Key idea:** Family of code embedding models (400M to 7B params) with a training pipeline that unifies multiple programming languages and code-related tasks into a common retrieval framework. The 7B model outperforms Voyage-Code by 20%+ on CoIR benchmark.
- **HyperRetrieval relevance:** **Direct competitor/complement.** CodeXEmbed represents the current SOTA in pure semantic code embeddings. HyperRetrieval's differentiator would be augmenting these embeddings with co-change graph structure — something CodeXEmbed does NOT do.

### 4.2 LoRACode: LoRA Adapters for Code Embeddings
- **Authors:** Chaturvedi, Chadha, Bindschaedler
- **Venue:** DL4C Workshop at ICLR 2025
- **URL:** https://arxiv.org/abs/2503.05315
- **Key idea:** Parameter-efficient fine-tuning (LoRA) to create task-specific code retrieval adapters. Reduces trainable params to <2% of base model. Up to 9.1% MRR improvement for Code2Code search. Fine-tunes 2M samples in 25 minutes on 2 H100s.
- **HyperRetrieval relevance:** LoRACode's approach could be used to create co-change-aware adapters for HyperRetrieval — fine-tune a base code embedding model with LoRA using co-change pairs as training signal (files that co-change should have closer embeddings).

### 4.3 xCoFormer: Effective, Efficient, Scalable Code Retrieval
- **Authors:** (Neurocomputing, 2024)
- **Venue:** Neurocomputing, 2024
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0925231224009433
- **Key idea:** Bi-encoder architecture with a novel TaG-Training (Turn-taking Alternating Game) strategy. Logarithmic complexity scaling for index growth. First representation learning model meeting all three requirements: effectiveness, efficiency, scalability.
- **HyperRetrieval relevance:** xCoFormer's bi-encoder architecture and scalability approach are relevant for HyperRetrieval's retrieval layer. The TaG-Training strategy could be adapted to train encoders that jointly consider code semantics and co-change signals.

---

## 5. RAG for Code (Benchmarks & Surveys)

### 5.1 CodeRAG-Bench: Can Retrieval Augment Code Generation?
- **Authors:** (Multi-institution)
- **Venue:** Findings of NAACL 2025
- **URL:** https://arxiv.org/abs/2406.14497
- **Key idea:** Comprehensive benchmark for code RAG with ~9,000 coding problems and 25M+ documents. Evaluates 10 retrievers and 10 LMs. Finds that diverse datastores give significant gains even on top of GPT-4. Identifies that retrievers often struggle to fetch useful contexts.
- **HyperRetrieval relevance:** CodeRAG-Bench provides the evaluation framework HyperRetrieval should target. The finding that retrievers struggle suggests co-change-aware retrieval could be a differentiating improvement.

### 5.2 Retrieval-Augmented Code Generation: A Survey (Repository-Level)
- **Authors:** Tao, Qin et al.
- **Venue:** arXiv 2510.04905 (2025)
- **URL:** https://arxiv.org/abs/2510.04905
- **Key idea:** Comprehensive survey of 110 papers on RACG. Categorizes work along retrieval modalities (sparse, dense, graph-based), generation strategies, training paradigms. Highlights that repository-level generation requires reasoning across entire repositories.
- **HyperRetrieval relevance:** This survey maps the landscape HyperRetrieval operates in. Notably, co-change-based retrieval is NOT covered as a retrieval modality — confirming the research gap.

### 5.3 Task-Agnostic Graph Convolutional Networks for Code Embeddings
- **Authors:** (ACM TOSEM, 2023)
- **Venue:** ACM Transactions on Software Engineering and Methodology
- **URL:** https://dl.acm.org/doi/10.1145/3542944
- **Key idea:** Generalizable code embeddings using GCNs that work across multiple downstream tasks without task-specific fine-tuning. Addresses the challenge that code embeddings often lack generalizability.
- **HyperRetrieval relevance:** Task-agnostic embeddings are exactly what HyperRetrieval needs — embeddings that work for search, similarity, clustering, and other tasks without retraining.

---

## 6. THE RESEARCH GAP: Co-Change Graph × Semantic Code Embeddings for Retrieval

### What exists:
- **Semantic code embeddings** (CodeBERT, GraphCodeBERT, CodeXEmbed, LoRACode) — encode code structure and semantics
- **Co-change/temporal graph models** (TGN for change propagation) — model file co-changeability over time
- **Commit-level embeddings** (CC2Vec, Commit2Vec, Patcherizer) — represent individual code changes
- **Graph RAG for code** (CGM) — use structural graphs for retrieval

### What does NOT exist (the gap):

> **No published work jointly embeds co-change graph topology AND code semantics into a unified representation for code retrieval.**

Specifically, nobody has:

1. **Built a co-change graph from git history and used GNN-based node embeddings (where nodes are files/functions) as retrieval vectors.** The TGN change propagation paper (Section 2.1) comes closest but targets prediction, not retrieval.

2. **Fine-tuned a code embedding model (like CodeBERT/CodeXEmbed) using co-change pairs as contrastive training signal.** LoRACode (Section 4.2) shows this is feasible with LoRA adapters, but uses standard code pairs, not co-change pairs.

3. **Combined structural code graphs (AST/CFG/DFG) with evolutionary coupling graphs (co-change) in a multi-relational GNN for code search.** CGM (Section 3.1) does structural graphs; the TGN paper does temporal co-change graphs; nobody combines them.

4. **Used temporal co-change embeddings to re-rank or boost code retrieval results.** CodeRAG-Bench (Section 5.1) evaluates many retrieval strategies but not co-change-aware retrieval.

---

## 7. Proposed Research Direction for HyperRetrieval

### Title (working): "EvoCoder: Co-Change-Aware Code Embeddings for Repository-Level Retrieval"

### Core Idea:
Augment semantic code embeddings with evolutionary coupling signals from git history to produce **evolution-aware code representations** that improve retrieval for LLM-powered code intelligence.

### Approach:
1. **Co-Change Graph Construction:** Mine git history to build a weighted, temporal co-change graph (nodes = files/functions, edges = co-change frequency, edge features = recency, commit type, author overlap)
2. **Dual-Encoder Architecture:**
   - **Semantic Encoder:** Base code embedding model (CodeXEmbed or GraphCodeBERT)
   - **Evolution Encoder:** Temporal GNN (TGN-style) over the co-change graph
   - **Fusion:** Learned weighted combination of semantic + evolutionary embeddings
3. **Training Signal:** Contrastive learning where:
   - Positive pairs: files that frequently co-change AND are semantically related
   - Hard negatives: files that are semantically similar but never co-change (or vice versa)
4. **Evaluation:** Code search, change impact prediction, related file retrieval on CodeRAG-Bench + custom repository-level benchmarks

### Why this is novel:
- First to use co-change as a training signal for code embeddings
- First to fuse temporal evolution graphs with semantic code graphs
- First to apply evolution-aware embeddings specifically for retrieval/RAG

### Why this matters for HyperRetrieval:
- Enables queries like "what files should I also look at when modifying X?"
- Improves retrieval relevance by capturing implicit dependencies not visible in import graphs
- Provides temporal awareness — recent co-changes weighted higher than old ones
- Can power change impact analysis, code review assistance, and refactoring guidance

---

## 8. Complete Reference List

| # | Paper | Year | Venue | Key Contribution |
|---|-------|------|-------|-----------------|
| 1 | CC2Vec | 2020 | ICSE | Hierarchical attention for code change embeddings |
| 2 | Commit2Vec | 2021 | SN Comp. Sci. | AST-path based commit representations |
| 3 | GraphCodeBERT | 2021 | ICLR | Data-flow-aware pre-trained code model |
| 4 | UniXcoder | 2022 | ACL | Unified cross-modal code pre-training |
| 5 | Task-Agnostic GCN Embeddings | 2023 | ACM TOSEM | Generalizable code embeddings via GCN |
| 6 | TGN Change Propagation | 2024 | Inf. Softw. Tech. | Temporal graph GNN for file change prediction |
| 7 | xCoFormer | 2024 | Neurocomputing | Scalable bi-encoder code retrieval |
| 8 | REACT (RAG Commit Msg) | 2024 | arXiv | RAG for commit message generation |
| 9 | Patcherizer | 2025 | Emp. Softw. Eng. | Dual sequence+graph patch representations |
| 10 | CodeXEmbed | 2025 | COLM | SOTA generalist code embedding family (400M-7B) |
| 11 | LoRACode | 2025 | ICLR DL4C | LoRA adapters for efficient code embedding fine-tuning |
| 12 | CodeRAG-Bench | 2025 | NAACL Findings | Benchmark for retrieval-augmented code generation |
| 13 | RACG Survey | 2025 | arXiv | 110-paper survey of retrieval-augmented code generation |
| 14 | Code Graph Model (CGM) | 2025 | arXiv | Graph-integrated LLM with Graph RAG pipeline |
| 15 | Multi-Level GNN Defect | 2025 | Sci. Reports | AST+CFG+DFG dual-branch GNN |
| 16 | Beyond Syntax Trees | 2024 | OpenReview | Multi-graph (AST+CFG+DFG) code edit embeddings |

---

*Survey compiled for HyperRetrieval R&D. The identified research gap — co-change-aware code embeddings for retrieval — represents a novel contribution opportunity at the intersection of software evolution mining and code representation learning.*
