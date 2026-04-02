# RFC 006: Granger Causality for Directional Co-Change Prediction

**Author:** Carlsbert (Session 4)
**Date:** 2026-04-02
**Status:** PROPOSED

## What

Add a build step (`09_build_granger.py`) that computes Granger causality between co-changing modules, producing a directional co-change index. Upgrade `predict_missing_changes()` to use causal direction and temporal lag for more accurate predictions.

## Why

Current co-change analysis is symmetric: "A and B changed together 15 times." This misses critical information:

1. **Directionality**: Changes to A may CAUSE changes to B (not vice versa). Knowing direction improves prediction precision — we can say "you changed A, B usually follows" rather than "A and B are related."

2. **Temporal lag**: B may change 1-3 commits AFTER A. This distinguishes "forgotten file" (lag 0-1) from "downstream effect" (lag 2-5).

3. **Research backing**: Papers show +13% recall improvement with only 2% precision drop when combining association rules with Granger causality for co-change prediction.

No competitor uses Granger causality for code intelligence. This is a genuine Layer 4 moat differentiator.

## Success Metric

- `predict_missing_changes` recall improves by >= 5% on held-out test set
- New predictions include causal direction and confidence: "AuthModule → SessionManager (p=0.003, lag=1)"
- No regression in existing test suite

## Baseline

- Current `predict_missing_changes("PaymentFlows")`: 20 predictions, coverage 0.11
- Predictions are based on co-change frequency (weight) only — no direction or lag

## Design

### Build Step: `09_build_granger.py`

**Input:** `git_history.json` (1.1GB, already exists in workspace)

**Algorithm:**
1. Parse git history into per-module time series: for each module, create binary vector (1 = changed in commit, 0 = not changed)
2. Filter to existing co-change pairs only (~111K pairs, not 54M)
3. For each pair (A, B), run bivariate Granger causality test with lags 1-5
4. Store results for pairs with p < 0.05 (statistically significant causal relationship)

**Output:** `granger_index.json`
```json
{
  "PaymentFlows→TransactionTransforms": {
    "source": "PaymentFlows",
    "target": "TransactionTransforms",
    "direction": "A→B",
    "best_lag": 2,
    "p_value": 0.003,
    "f_statistic": 8.42,
    "cochange_weight": 15
  }
}
```

**Computational cost estimate:**
- 111K pairs × Granger test (statsmodels, ~1ms each) = ~2 minutes
- Memory: ~500MB for time series (manageable)
- No GPU needed

### Retrieval Engine Changes

Upgrade `predict_missing_changes()`:
```python
# Current: predictions sorted by co-change weight
# New: predictions enriched with causal info
{
    "module": "TransactionTransforms",
    "reason": "co-change (15 commits)",
    "weight": 15,
    "confidence": 0.85,
    "causal": {                          # NEW
        "direction": "PaymentFlows→TransactionTransforms",
        "lag": 2,
        "p_value": 0.003,
        "strength": "strong"             # strong (p<0.01), moderate (p<0.05)
    }
}
```

Scoring adjustment:
```python
# Boost predictions that have causal support
if granger_data and granger_data["p_value"] < 0.01:
    confidence *= 1.3   # 30% boost for strong causal relationship
elif granger_data and granger_data["p_value"] < 0.05:
    confidence *= 1.15  # 15% boost for moderate causal relationship
```

### Evaluation

Create a held-out evaluation:
1. Take the last 100 PRs from git history
2. For each PR, hide one file and predict it
3. Measure recall@5 and recall@10 with and without Granger boost
4. Target: +5% recall improvement

## Rollback Plan

- Granger index is a new file — doesn't affect existing indexes
- Confidence boost is additive — remove it to revert to original behavior
- No schema changes to existing data

## Dependencies

- `statsmodels` (Python package, has `grangercausalitytests()`)
- Existing `git_history.json` in workspace
- Existing `cochange_index.json` for pair filtering

## Implementation Plan

1. Write `build/09_build_granger.py` — parse git history, compute Granger tests, output index
2. Load granger_index in `retrieval_engine.py` initialize()
3. Integrate causal boost into `predict_missing_changes()` scoring
4. Add test section 13 with assertions for causal predictions
5. Run held-out evaluation and report recall improvement
