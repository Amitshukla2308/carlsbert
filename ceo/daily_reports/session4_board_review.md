# Session 4 Board Review
**Date:** 2026-04-02 ~00:00 IST

---

## CTO Lens: Technology

**What we shipped:** Change Risk Scoring — composite 0-100 from 4 signals, flowing through MCP tool → Guardian report → CLI → JSONL history. Clean, tested, configurable.

**Tech decisions validated:**
- YAML rules engine extensibility paid off immediately — risk_weights slot right into existing config
- Module-level functions (no classes) in retrieval_engine.py continues to work well for composability
- JSONL append for history is the right simple choice — no database needed yet

**Tech debt status:**
- Naming canonicalization: analyzed, ~40 lines, deferred correctly (bridge works)
- Loading messages go to stdout (should be stderr) — pre-existing, minor
- pr_analyzer JSON output mixed with loading messages — should fix initialization output routing

**Tech radar changes:**
- ADOPT: Change Risk Scoring, Suggested Reviewers (promoted from TRIAL/new)
- ASSESS: blast-radius.dev (new competitor), CodeScene MCP, Granger causality for CIA
- ERODING moat flag added

---

## CFO Lens: Token Economy

**This session:** Highly efficient. Three commits, all building on existing code. No redundant computation. Risk scoring reuses blast_radius + predict_missing_changes + suggest_reviewers calls.

**Cost analysis:**
- Explorer scan: ~1 agent call (web search + analysis)
- CodeScene research: ~1 agent call (still running)
- All other work: direct coding, no external API calls needed
- Zero token waste on LLM-as-judge or multi-agent meetings

**ROI:** High. Three features shipped in ~30 minutes of wall clock. Each adds enterprise value (risk scoring, CI/CD gating, historical trending).

---

## Intelligence Lens: Competitive Threats

**CRITICAL:** Moat status changed from UNIQUE (Session 3) to ERODING (Session 4).

**Threats by severity:**
1. **blast-radius.dev** (HIGH) — Direct competitor, same positioning. Early-stage. We must ship faster.
2. **CodeScene** (MEDIUM) — Has change coupling + new MCP server. Different focus (Code Health vs Change Impact) but could converge.
3. **GitHub Copilot** (EXISTENTIAL if they add blast radius) — 60M code reviews. If they add impact analysis, we can't compete on distribution.

**Opportunities:**
- Granger causality for temporal change prediction — nobody has this
- Historical risk trending — data moat that grows over time
- Configurable policies via YAML — enterprise customization nobody else offers

**Defense strategy:** 
1. Ship faster than blast-radius.dev
2. Build data moats (history accumulates, becomes irreplaceable)
3. Enterprise features (configurable policies, risk scoring, reviewer assignment)
4. Research differentiators (Granger causality, co-change + clone detection)

---

## Architect Lens: System Design

**Current architecture is solid:**
- retrieval_engine.py as the single source of truth for all data operations
- MCP server as the thin presentation layer
- pr_analyzer as the CLI entry point for CI/CD
- YAML rules engine for policy configuration
- JSONL history for longitudinal data

**2-year consequences of current decisions:**
- GOOD: JSONL history is append-only and schema-flexible — can add fields without migration
- GOOD: Configurable weights mean we can tune without code changes
- WATCH: If history grows large (>100K entries), JSONL scanning will slow. May need SQLite at scale.
- WATCH: The retrieval engine is getting large (~1200 lines). May need to split into modules eventually.

**No architectural changes needed this session.**

---

## Product Lens: User Value

**What we built matters because:**
1. **Risk score** answers "should I block this PR?" — directly actionable, not just informational
2. **JSONL history** enables "show me risk trends" — a board-level insight
3. **CLI integration** means it works in CI/CD TODAY, not just in IDE

**What users actually need next (in priority order):**
1. **GitHub Action for Guardian** — the deployment mechanism. Features mean nothing without distribution.
2. **Risk trending dashboard** — visualize guardian_history.jsonl data
3. **PR comment bot** — auto-comment Guardian report on every PR

**The buyer:**
- VP of Engineering who approved Copilot for 500 engineers
- Cares about: risk reduction, audit trail, policy enforcement
- Doesn't care about: blast radius visualization, co-change details
- Buys because: "Risk score 72/100 for this PR. Policy requires senior review."

---

## Summary & Next Priority

**Session 4 was highly productive.** Three features shipped, all tested, all integrated across the full stack (engine → MCP → CLI). Competitive intelligence revealed moat is eroding.

**#1 priority:** Ship faster. The unified Guardian experience (risk score + missing changes + blast radius + reviewers + history = one call) is our edge, but competitors are closing in.

**Next session should focus on:** Distribution (GitHub Action, PR bot) over features. The features exist. They need to reach users.
