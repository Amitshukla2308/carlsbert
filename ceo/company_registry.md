# Carlsbert -- Company Registry

**CEO Decision Date:** 2026-03-31
**Reviewed by:** Agent Amit (CEO)

---

## COMPANY (core)

### 1. HyperRetrieval
- **Path:** `/home/beast/projects/hyperretrieval`
- **Last activity:** 8 days ago (active)
- **Description:** Self-hosted codebase intelligence platform. Indexes source code into graph + vector store, exposes MCP tools for IDE-embedded LLMs. Production deployment at Juspay (94K symbols, 12 microservices).
- **Agent teams:** engineer, product, scientist, explorer
- **Cron:** explorer every 2h, code_quality daily, research_synthesis weekly
- **Rationale:** Flagship product with paying customer. Highest strategic value.

### 2. Connector Service
- **Path:** `/home/beast/projects/connector-service`
- **Last activity:** 3 weeks ago (active)
- **Description:** High-performance payment abstraction library (Rust). Part of Juspay Hyperswitch ecosystem. Unified schema across all payment providers.
- **Agent teams:** engineer, sre
- **Cron:** code_quality daily, integration_tests weekly
- **Rationale:** Production infrastructure tied to Juspay work. Rust codebase with real CI/CD. Strategic.

---

## COMPANY (growth)

### 3. Stock AI Beast
- **Path:** `/home/beast/projects/stock-ai-beast`
- **Last activity:** 8 weeks ago (moderate)
- **Description:** Deterministic algorithmic trading engine (v4.2). 64-dimensional physics-based market state analysis, regime detection, sovereign risk stack. Backtest + mock cycles stable, live execution ready.
- **Agent teams:** quant, risk, engineer
- **Cron:** quant_review weekly, backtest_validation weekly
- **Rationale:** Sophisticated trading system at live-ready stage. High potential value but needs consistent attention to move to live.

### 4. ZeroClaw
- **Path:** `/home/beast/projects/AI_Systems/zeroclaw`
- **Last activity:** 4 weeks ago (active)
- **Description:** Rust-first autonomous agent runtime. Trait-driven modular architecture with providers, channels, tools, memory, observability, and hardware peripheral support (STM32, RPi GPIO).
- **Agent teams:** engineer, architect
- **Cron:** code_quality weekly, architecture_review monthly
- **Rationale:** Original Rust agent runtime with hardware integration. Could become core infrastructure.

### 5. Beast Agent
- **Path:** `/home/beast/projects/beast_agent`
- **Last activity:** N/A (no git, but actively used by orchestrator)
- **Description:** Autonomous recursive project manager for the Beast Workspace. Orchestrates scan, optimize, and advance modes across all projects. The meta-agent that runs this whole operation.
- **Agent teams:** engineer, ops
- **Cron:** health_scan every 4h, optimize daily
- **Rationale:** The orchestration layer itself. Must stay healthy for everything else to function.

---

## COMPANY (exploratory)

### 6. AutoResearch (Karpathy fork)
- **Path:** `/home/beast/projects/AI_Systems/autoresearch`
- **Last activity:** 3 weeks ago (active)
- **Description:** Autonomous AI research agent that iterates on LLM training code overnight. Modifies train.py, runs 5-min experiments, keeps or discards. Currently at experiment 141+.
- **Agent teams:** scientist
- **Cron:** experiment_run nightly, results_review daily
- **Rationale:** Active experimentation with real results. Low cost, high learning potential.

### 7. CryptoRegimeTrader
- **Path:** `/home/beast/projects/Trading_Bots/cryptoregimetrader`
- **Last activity:** N/A (no git)
- **Description:** Crypto trading bot using regime detection. Has optimization summaries and usage docs.
- **Agent teams:** quant
- **Cron:** review weekly
- **Rationale:** Exploratory trading project. Keep lightweight agent on it.

---

## COMPANY (maintenance)

### 8. ChatBeast (SearXNG)
- **Path:** `/home/beast/projects/AI_Systems/ChatBeast`
- **Last activity:** 2 months ago
- **Description:** SearXNG-based search infrastructure (Docker). Provides web search capabilities to other agents.
- **Agent teams:** sre
- **Cron:** health_check daily, update monthly
- **Rationale:** Infrastructure dependency. Just keep the Docker containers alive.

### 9. Open Skills
- **Path:** `/home/beast/projects/AI_Systems/open-skills`
- **Last activity:** 6 weeks ago
- **Description:** Skills marketplace/registry with contribution templates and website.
- **Agent teams:** product
- **Cron:** review monthly
- **Rationale:** Community project, low urgency but worth maintaining.

---

## DEPENDENCY (no agent teams)

### 10. CodeToolCLI (Claude Code leaked source)
- **Path:** `/home/beast/projects/codetoolcli`
- **Last activity:** 27 hours ago
- **Description:** Leaked/analyzed source of Anthropic's Claude Code CLI. Used as reference and possibly as local binary. Not a Carlsbert product.
- **Classification:** Reference dependency. No dedicated team needed.

### 11. LTX-2
- **Path:** `/home/beast/projects/ltx-2`
- **Last activity:** 3 weeks ago
- **Description:** Lightricks video generation model. Upstream fork, not a Carlsbert product.
- **Classification:** External dependency/reference. No team needed.

### 12. Diffusers
- **Path:** `/home/beast/projects/diffusers`
- **Last activity:** 3 weeks ago
- **Description:** HuggingFace diffusers library fork. Upstream dependency.
- **Classification:** External dependency. No team needed.

---

## ARCHIVE (dead/abandoned -- no agent teams)

### 13. ToonForge
- **Path:** `/home/beast/projects/toonforge`
- **Last activity:** No git repo. Massive pile of debug/audit markdown files. Windows path references suggest ported from another machine.
- **Verdict:** Dead. Chaotic state. Archive.

### 14. LTX-Video
- **Path:** `/home/beast/projects/ltx-video`
- **Last activity:** 3 months ago. Superseded by ltx-2 (redirect notice in last commit).
- **Verdict:** Dead. Replaced by ltx-2. Archive.

### 15. Leash.ai
- **Path:** `/home/beast/projects/Leash.ai` (also `/home/beast/projects/AI_Systems/Leash.ai`)
- **Last activity:** No git. Sparse files (Dockerfile, some markdown).
- **Verdict:** Dead experiment. Archive.

### 16. Atlas
- **Path:** `/home/beast/projects/atlas`
- **Last activity:** No git. Just a `data/` directory.
- **Verdict:** Dead/empty. Archive.

### 17. CodeGeneration
- **Path:** `/home/beast/projects/CodeGeneration`
- **Last activity:** No git. Contains only `unifiedSpecGenerator/` subfolder.
- **Verdict:** Dead experiment. Archive.

### 18. Lab_and_Tools
- **Path:** `/home/beast/projects/Lab_and_Tools`
- **Last activity:** No git. Empty or near-empty.
- **Verdict:** Dead. Archive.

### 19. Archive
- **Path:** `/home/beast/projects/Archive`
- **Last activity:** Contains `stock-ai-beast-old/`. Already an archive folder.
- **Verdict:** Archive by definition.

### 20. AI_Systems/AnythingLLM
- **Path:** `/home/beast/projects/AI_Systems/AnythingLLM`
- **Last activity:** No git. Just docker-compose + storage.
- **Verdict:** Stale Docker deployment. Archive or fold into ChatBeast SRE scope.

### 21. AI_Systems/ai-core
- **Path:** `/home/beast/projects/AI_Systems/ai-core`
- **Last activity:** No git. Contains sovereign-router subfolder.
- **Verdict:** Dead experiment. Archive.

### 22. AI_Systems/autoai
- **Path:** `/home/beast/projects/AI_Systems/autoai`
- **Last activity:** No git. Has Dockerfiles and handoff docs but no repo.
- **Verdict:** Dead experiment. Archive.

### 23. Trading_Bots/crypto
- **Path:** `/home/beast/projects/Trading_Bots/crypto`
- **Last activity:** No git.
- **Verdict:** Dead. Archive.

### 24. ChatBeast (top-level duplicate)
- **Path:** `/home/beast/projects/ChatBeast`
- **Last activity:** No git. Just contains searxng/. Duplicate of AI_Systems/ChatBeast.
- **Verdict:** Duplicate. Archive. Use AI_Systems/ChatBeast instead.

---

## Summary Table

| # | Project | Classification | Active | Teams |
|---|---------|---------------|--------|-------|
| 1 | HyperRetrieval | CORE | Yes (8d) | engineer, product, scientist, explorer |
| 2 | Connector Service | CORE | Yes (3w) | engineer, sre |
| 3 | Stock AI Beast | GROWTH | Moderate (8w) | quant, risk, engineer |
| 4 | ZeroClaw | GROWTH | Yes (4w) | engineer, architect |
| 5 | Beast Agent | GROWTH | Active (orchestrator) | engineer, ops |
| 6 | AutoResearch | EXPLORATORY | Yes (3w) | scientist |
| 7 | CryptoRegimeTrader | EXPLORATORY | Stale | quant |
| 8 | ChatBeast | MAINTENANCE | Moderate (2mo) | sre |
| 9 | Open Skills | MAINTENANCE | Moderate (6w) | product |
| 10 | CodeToolCLI | DEPENDENCY | Yes (1d) | -- |
| 11 | LTX-2 | DEPENDENCY | Yes (3w) | -- |
| 12 | Diffusers | DEPENDENCY | Yes (3w) | -- |
| 13-24 | (12 projects) | ARCHIVE | Dead | -- |

**Total active companies: 9** (2 core, 3 growth, 2 exploratory, 2 maintenance)
**Total dependencies: 3**
**Total archived: 12**
