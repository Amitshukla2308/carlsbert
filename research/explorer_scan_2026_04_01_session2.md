# Explorer Scan — Code Intelligence Landscape
**Date:** 2026-04-01 | **Session:** 2 | **Focus:** Code graph, embeddings, co-change, retrieval

---

## Finding 1: CodeScout — RL-trained Code Search Agents (March 2026)
**Source:** [arxiv 2603.17829](https://arxiv.org/abs/2603.17829) | [GitHub](https://github.com/OpenHands/codescout) | [Models on HF](https://huggingface.co/OpenHands/CodeScout-14B)

OpenHands released CodeScout, an RL-trained agent for code localization using only a Unix terminal (no specialized tools, no repo graphs). Key insight: **RL on a simple terminal agent beats complex graph-based retrieval** for file/function localization. 1.7B model rivals 14B+ base models. New open-source SoTA on code localization benchmarks.

**Relevance to HyperRetrieval:** Direct competitor approach. They show terminal-only RL agents can match graph-based retrieval. But their approach requires RL training per-task — HyperRetrieval's pre-computed graph + embeddings is zero-shot and faster at inference. Worth understanding their reward function design (F1 on file/module/function match).

**Rating: TRIAL** — Experiment with CodeScout-1.7B as a baseline comparator for HyperRetrieval's retrieval quality.

---

## Finding 2: RepoGraph — Line-level Code Graph for SWE-bench (Oct 2024, gaining traction 2026)
**Source:** [arxiv 2410.14684](https://arxiv.org/abs/2410.14684) | [GitHub](https://github.com/ozyyshr/RepoGraph)

RepoGraph builds a **line-level** code graph (not file-level) where nodes = code lines, edges = def-ref dependencies. Sub-graph retrieval via ego-graphs around keywords. Plugged into 4 different SWE-bench systems, it boosted success rate by **32.8% on average**.

**Relevance to HyperRetrieval:** Very aligned architecture. HyperRetrieval already does symbol-level graph — RepoGraph validates the approach but goes finer (line-level). Their ego-graph retrieval pattern is worth studying. Consider whether line-level granularity adds value over symbol-level for co-change analysis.

**Rating: ASSESS** — Study their ego-graph retrieval algorithm. Line-level may be overkill for co-change but useful for precise context windows.

---

## Finding 3: Greptile v4 — Claude Agent SDK + Full Code Graph (Early 2026)
**Source:** [Greptile docs](https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context) | [SiliconANGLE](https://siliconangle.com/2025/09/23/greptile-bags-25m-funding-take-coderabbit-graphite-ai-code-validation/)

Greptile v4 shipped with significant accuracy improvements (74% more addressed comments, 68% positive dev replies). Uses Anthropic Claude Agent SDK for autonomous multi-hop investigation. Built on full-repo code graph + git history analysis. $25M raised (Sep 2025).

**Relevance to HyperRetrieval:** Closest competitor in philosophy (code graph + git history). They're productizing code review; HyperRetrieval targets retrieval. Their multi-hop investigation pattern is interesting — trace dependency chains across files using the graph. Their 82% bug catch rate (vs Cursor 58%) validates graph-based approaches.

**Rating: ASSESS** — Watch their architecture evolution. Their success validates HyperRetrieval's graph-first approach.

---

## Finding 4: Sourcegraph Cody — Deeper Multi-Repo Intelligence (2026)
**Source:** [SitePoint comparison](https://www.sitepoint.com/ai-ides-compared-cursor-claude-code-cody-2026/)

Sourcegraph overhauled Cody's enterprise codebase intelligence with deeper multi-repository understanding and compliance tooling. Cody's code graph understands cross-service dependencies across repos.

**Relevance to HyperRetrieval:** Multi-repo is a gap in HyperRetrieval currently. Sourcegraph's cross-repo dependency tracking is relevant for enterprise use cases.

**Rating: ASSESS** — Multi-repo support should be on HyperRetrieval roadmap but not urgent.

---

## Finding 5: GitHub AI-Powered Security Scanning (April 2026)
**Source:** [PRSOL:CC](https://www.prsol.cc/2026/04/01/github-adds-ai-powered-bug-detection-to-expand-security-coverage/)

GitHub expanding Code Security beyond CodeQL with AI-based scanning. Public preview expected Q2 2026. Covers Shell, Dockerfiles, Terraform, PHP.

**Relevance to HyperRetrieval:** Tangential. Shows trend of AI augmenting static analysis. Not directly competitive.

**Rating: IGNORE** — Different problem space.

---

## Summary Matrix

| Finding | Rating | Action |
|---------|--------|--------|
| CodeScout (RL code search) | TRIAL | Benchmark against HyperRetrieval retrieval |
| RepoGraph (line-level graph) | ASSESS | Study ego-graph retrieval algorithm |
| Greptile v4 (graph + agent) | ASSESS | Validates our approach, watch evolution |
| Sourcegraph Cody (multi-repo) | ASSESS | Roadmap consideration |
| GitHub AI Security | IGNORE | Different domain |

---

## Telegram Alert (High-Signal)

**CodeScout is the one to watch.** OpenHands showing that RL-trained terminal agents can rival graph-based retrieval is both a validation (code localization matters) and a challenge (simpler approaches catching up). HyperRetrieval's advantage: zero-shot, pre-computed, no RL training needed. But we should benchmark CodeScout-1.7B against our retrieval to quantify the gap.

---

*Generated by Carlsbert Explorer — Session 2, 2026-04-01*
