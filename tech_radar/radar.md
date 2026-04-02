# Carlsbert Tech Radar
Last updated: 2026-04-01 (Session 4)

## ADOPT (proven, use everywhere)
- Python 3.13 (primary language)
- LanceDB (vector store)
- Qwen3-Embed-8B (embedding model)
- Chainlit 2.10 (chat UI)
- NetworkX (graph operations)
- kimi-latest (LLM via API)
- IDF-weighted keyword scoring (replaces hardcoded stopwords, self-tuning)
- Co-change RRF fusion (3-signal: vector + BM25 + co-change)
- Guardian Mode (PR completeness + blast radius + security scan + risk scoring)
- Change Risk Scoring (composite 0-100, configurable weights via YAML)
- Suggested Reviewers (module ownership from git history)
- Granger Causality for co-change prediction (directional, temporal lag, 89% hit rate)

## TRIAL (promising, evaluate on one project)
- TurboQuant (vector compression — Q3 2026 for llama.cpp)
- Co-change contrastive embeddings / EvoCoder (RFC written, 241K training triples ready)
- SWE-Bench Verified (benchmark for head-to-head vs CodeScout)
- GitHub Action for Guardian Mode (workflow written, needs live deployment test)
- Historical risk trending (JSONL time-series of risk scores per module — dream from journal)

## ASSESS (interesting, needs investigation)
- **blast-radius.dev** — DIRECT COMPETITOR. Purpose-built PR impact analysis. Early-stage. Monitor closely.
- **CodeScene MCP server** — mature change coupling platform, now with AI agent integration. Strongest existing competitor.
- ~~Granger causality~~ → promoted to ADOPT (shipped Session 4)
- Microservices CIA research (2025 systematic lit review, 29 papers — directly applicable)
- CodeScout 1.7B (RL terminal agent — different philosophy, benchmark candidate)
- Greptile v4 (graph+agent hybrid, closest competitor, 82% bug catch rate)
- RepoGraph (line-level code graph, 32.8% SWE-bench improvement)
- MiroFish (swarm intelligence prediction, 33K stars — study agent architecture for future code evolution simulation)
- Rust for retrieval engine (performance)
- nomic-embed-v2 (smaller, possibly better)
- ColBERT reranker (stage-2 reranking)

## HOLD (don't use yet)
- Full model fine-tuning (LoRA adapter first, if that works then revisit)
- Multi-GPU training (single RTX 5090 is sufficient)
- LangGraph (no clear advantage over direct MCP tools for our use case)

## COMPETITIVE MOAT STATUS: ERODING (as of Session 4)
- blast-radius.dev targets our exact positioning
- CodeScene has had change coupling for years, now adding AI
- GitHub Copilot: 60M reviews, no blast radius YET — if they add it, game over on reach
- **Our edge:** unified experience (risk score + missing changes + blast radius + reviewers = 1 call)
- **Defense strategy:** ship faster, deeper integration, configurable policies, historical trending
