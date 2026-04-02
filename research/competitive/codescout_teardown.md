# CodeScout Competitive Teardown
**Paper:** [arxiv 2603.17829](https://arxiv.org/abs/2603.17829) | **Team:** OpenHands (Lintang Sutawika et al.) | **Date:** March 2026

## How It Works

**Architecture:** RL-trained terminal agent using OpenHands-Bash scaffold. Only 2 tools: a Terminal (rg, find, grep, ls) and LocalizationFinish (structured output). No static analysis, no code graphs, no language-specific tooling.

**Base Models:** Qwen3 family — CodeScout-14B (from Qwen3-14B), CodeScout-4B, CodeScout-1.7B (distilled from 14B via 4K perfect-score trajectories).

**RL Method:** GSPO (Group Sequence Policy Optimization) with multi-level F1 reward at file, module, and function granularity. 6 turns per episode (4B), 40-50K token context window. Reward combines F1 scores across all three granularities.

**Training Data:** SWE-Bench instances repurposed for localization. Python-only repositories.

## Where CodeScout Wins

- **Simplicity:** 1 tool vs 3-5 tools in prior methods. Zero engineering overhead for new languages (in theory).
- **Small model, big results:** 1.7B model beats 8x larger Qwen3-14B by 11-18% file F1 and 10-15% function F1. Competitive with Claude Sonnet on SWE-Bench Verified (500 instances), Lite (300), and Pro-Python (266).
- **Portable:** Bash is universal — works anywhere OpenHands/SWE-Agent/Claude Code runs.
- **Fully open-source:** Models, code, training rollouts all released.

## Where CodeScout Can't Compete (HyperRetrieval Advantages)

| Dimension | CodeScout | HyperRetrieval |
|---|---|---|
| **Latency** | Multi-turn LLM inference (6+ steps) | Pre-indexed, sub-second |
| **Per-query cost** | GPU inference per query | Zero inference cost |
| **Structural awareness** | Discovers structure at query time via grep | Pre-computed graph (114K nodes, 43K import edges) |
| **Change coupling** | No historical signal | Co-change index (111K pairs from git history) |
| **Completeness analysis** | Finds what you ask for | Guardian Mode finds what you missed |
| **Language coverage** | Trained/evaluated on Python only | Language-agnostic graph construction |
| **Ranking fusion** | Single-signal (LLM judgment) | 3-signal RRF (vector + BM25 + co-change) |
| **Determinism** | Non-deterministic (LLM sampling) | Deterministic, reproducible |

## Key Insight: Fundamental Philosophy Difference

**CodeScout = search-time compute.** Spend inference budget per query. The agent reasons about the repo live, exploring with terminal commands. Strength: adapts to novel queries. Weakness: slow, expensive, non-deterministic.

**HyperRetrieval = index-time compute.** Spend compute once building the graph, then queries are free. Strength: instant, deterministic, captures structural relationships CodeScout can never discover (co-change patterns, import graphs). Weakness: requires pre-indexing.

## What to Steal

1. **RL for search policy:** Their GSPO recipe could train a model to pick better *entry points* for graph traversal in HyperRetrieval — hybrid approach.
2. **Multi-level F1 reward:** Their file/module/function granularity reward is a clean evaluation metric we should adopt for benchmarking Guardian Mode.
3. **SWE-Bench as localization benchmark:** They repurposed SWE-Bench for code search eval. We should benchmark HyperRetrieval's retrieval on the same 500 instances for direct comparison.
4. **Distillation recipe:** Their 14B→1.7B distillation via perfect trajectories is elegant. If we ever add an LLM re-ranker, this approach keeps it tiny.

## Threat Assessment

**Low-medium.** CodeScout solves a different problem (ad-hoc localization for coding agents) than HyperRetrieval (production code intelligence with structural understanding). However, if they add graph signals or caching, the gap narrows. Our moat is the pre-computed graph + co-change index — signals that no amount of terminal grep can replicate.

---
*Sources: [arxiv](https://arxiv.org/abs/2603.17829) | [GitHub](https://github.com/OpenHands/codescout) | [HuggingFace 14B](https://huggingface.co/OpenHands/CodeScout-14B) | [HuggingFace 1.7B](https://huggingface.co/OpenHands/CodeScout-1.7B) | [EmergentMind](https://www.emergentmind.com/papers/2603.17829)*
