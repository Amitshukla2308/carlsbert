# Competitive Landscape Scan: Code Intelligence / Blast Radius Analysis
**Date:** 2026-04-01 | **Session:** Explorer Scan #4

---

## Direct Threats

- **Blast Radius (blast-radius.dev)** — NEW ENTRANT. Purpose-built PR impact analysis tool. Maps downstream impact of code changes across services/repos. Early-stage but directly targets our claimed moat. Primary threat.
- **CodeScene** — Mature platform with change coupling graphs, co-change visualization, and PR integration. Now has MCP server for AI agent feedback loops. Does not brand as "blast radius" but delivers similar co-change insights. Strong competitor.
- **LinearB / gitStream** — Workflow automation for PRs (auto-assign, auto-merge, labeling). Launched AI-powered code review in 2025. Focuses on DORA metrics and developer productivity, not deep impact analysis. Adjacent, not direct.
- **Sourcegraph** — Code intelligence and search. Listed among top dev experience tools for 2026. Cross-repo code navigation but no explicit blast radius feature.

## Adjacent Competition

- **GitHub Copilot Code Review** — 60M reviews by March 2026 (10x growth in one year). October 2025 update added agentic tool calling: reads full project context, directory structure, integrates CodeQL/ESLint. Does NOT do co-change or blast radius analysis, but its reach (1M+ users) means any feature addition here instantly dominates.
- **AI PR Review Tools** — Category is now mature. 44% of developers used AI code review tools in 2025 (JetBrains survey). Crowded space but focused on style/bugs, not structural impact.

## Research Opportunities

- **Microservices CIA** — 2025 systematic lit review (29 papers) on change impact analysis in microservices. Directly applicable to cross-service blast radius.
- **Co-change + Clone Detection** — Papers combining code clone detection with association rule mining from historical co-changes. Could enhance our co-change accuracy.
- **Granger Causality for CIA** — Novel approach using bivariate Granger causality (time-series method) to assess temporal causality between change events. Potential differentiator if implemented.

## Moat Status: ERODING

**blast-radius.dev** is a direct competitor targeting the exact same positioning. CodeScene has had change coupling for years. However, neither combines co-change detection + blast radius + AI review in one integrated flow. Our moat is eroding but defensible if we:
1. Ship faster than blast-radius.dev (they appear early-stage)
2. Integrate co-change + blast radius + AI review as a unified experience
3. Adopt microservices CIA and Granger causality research as technical differentiators

---

**Sources:**
- [Blast Radius](https://blast-radius.dev/)
- [CodeScene](https://codescene.com/product)
- [GitHub Copilot Code Review](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)
- [Copilot Code Review Oct 2025 Update](https://github.blog/changelog/2025-10-28-new-public-preview-features-in-copilot-code-review-ai-reviews-that-see-the-full-picture/)
- [LinearB gitStream](https://linearb.io/platform/gitstream)
- [AI Code Review State 2026](https://dev.to/rahulxsingh/the-state-of-ai-code-review-in-2026-trends-tools-and-whats-next-2gfh)
- [CIA in Microservices (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0164121224002851)
- [Change Impact Analysis Papers](https://www.academia.edu/Documents/in/Change_Impact_Analysis)
