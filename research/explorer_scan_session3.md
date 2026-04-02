# Explorer Scan — Session 3 (2026-04-01)

## Competitive Intelligence: Code Intelligence + PR Review

### Threats
1. **GitHub Copilot Agentic Review** — gathers full project context, auto-generates fix PRs. Competes with our PR completeness checking.
2. **Cursor Cloud Agents** — event-driven triggers (Slack, Linear, GitHub, PagerDuty), scheduled runs. Encroaches on agent-driven analysis.
3. **Market Maturity** — 40-50% of devs now use AI code review (4x from 2024). CodeRabbit, Greptile, DeepSource delivering 30-60% PR cycle reduction.

### Opportunities (OUR MOAT)
1. **Blast Radius is UNIQUE** — No competitor explicitly markets "blast radius for PRs." Sourcegraph/NDepend have dependency graphs but not PR-specific impact prediction. This is our defensible moat.
2. **Context Window Bottleneck** — AI reviewers fail on 1000+ line diffs. Our co-change analysis could intelligently chunk changes by logical dependencies.
3. **Production-Aware Review** — Next frontier: understanding contracts, dependencies, production impact. We're positioned for this.
4. **Co-change Complementarity** — 28.5% of our co-change pairs are invisible to import/call graphs. No competitor has this signal.

### Strategic Recommendation
**DOUBLE DOWN on blast radius + co-change as core moat.** Guardian Mode with YAML rules is the enterprise interface for this moat. Next: make blast radius forecasting even more accurate.

### Key Metrics (Market)
- AI code review: 40-50% dev adoption
- ROI: 30-60% PR cycle time reduction, 25-35% fewer defects
- Cost per production incident: $5K-$15K (tools pay for themselves in Q1)
- 1.3M repos using AI code review (4x from 2024)
