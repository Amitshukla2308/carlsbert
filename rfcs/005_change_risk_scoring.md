# RFC 005: Change Risk Scoring

**Author:** Carlsbert (Session 4)
**Date:** 2026-04-01
**Status:** PROPOSED

## What

A `score_change_risk(modules)` function that takes a list of changed modules and returns a composite risk score (0-100) with breakdown, combining all our unique data sources into one actionable number.

## Why

Enterprise buyers need a single, defensible number to gate deployments. We have blast radius, co-change predictions, ownership data, and configurable rules — but each is a separate query. A composite risk score:
- Powers CI/CD gates ("block PRs above risk 80")
- Enables dashboards and trend tracking
- Justifies premium pricing (quantified risk, not just warnings)
- Uses ALL our moat data in one call

No competitor can replicate this because they don't have co-change + import graph + ownership combined.

## Success Metric

- `score_change_risk(["PaymentFlows"])` returns a score with breakdown
- Score components: blast_radius_score, coverage_gap_score, reviewer_risk_score, service_spread_score
- Each component is 0-100, weighted into composite
- MCP tool exposed for IDE/CI integration
- 3+ test assertions in run_tests.py

## Design

### Input
```python
score_change_risk(modules: list[str], rules: dict = None) -> dict
```

### Output
```python
{
    "risk_score": 72,          # composite 0-100
    "risk_level": "HIGH",      # LOW (0-30), MEDIUM (31-60), HIGH (61-80), CRITICAL (81-100)
    "components": {
        "blast_radius": {
            "score": 85,       # based on number of affected services
            "services_affected": 8,
            "detail": "8 services in blast radius"
        },
        "coverage_gap": {
            "score": 65,       # based on predict_missing_changes coverage
            "missing_changes": 15,
            "coverage_score": 0.11,
            "detail": "89% of typical co-changes not included"
        },
        "reviewer_risk": {
            "score": 40,       # based on ownership concentration
            "top_reviewer_dominance": 0.35,
            "detail": "Moderate reviewer concentration"
        },
        "service_spread": {
            "score": 70,       # based on cross-service boundary violations
            "unique_services": 4,
            "detail": "Changes span 4 services"
        }
    },
    "recommendation": "HIGH risk. 8 services affected, 15 predicted co-changes missing. Consider splitting PR or adding reviewers: Yashasvi, Krishna."
}
```

### Scoring Algorithm

1. **Blast Radius Score** (weight: 0.35)
   - 0 services = 0, 1-2 = 20, 3-5 = 50, 6-10 = 75, 10+ = 100

2. **Coverage Gap Score** (weight: 0.30)
   - Based on `1 - coverage_score` from predict_missing_changes
   - 100% coverage = 0, 0% coverage = 100

3. **Reviewer Risk Score** (weight: 0.20)
   - If top reviewer has >80% of commits = 100 (bus factor risk)
   - If well-distributed across 3+ reviewers = 20
   - No ownership data = 50 (unknown = moderate risk)

4. **Service Spread Score** (weight: 0.15)
   - 1 service = 0, 2 = 30, 3 = 50, 4+ = 80, 6+ = 100

### Composite
```
risk_score = round(
    blast * 0.35 + coverage * 0.30 + reviewer * 0.20 + spread * 0.15
)
```

Weights configurable via YAML rules engine (extends existing guardian_rules.yaml).

## Rollback Plan

- Single function addition to retrieval_engine.py
- Single MCP tool addition
- No existing code modified
- Revert = delete function + tool + test section

## Implementation Plan

1. Add `score_change_risk()` to retrieval_engine.py (calls existing blast_radius, predict_missing_changes, suggest_reviewers)
2. Add MCP tool `score_change_risk` in mcp_server.py
3. Add test section 12 in run_tests.py
4. Update guardian_rules.yaml schema to support risk score weights
