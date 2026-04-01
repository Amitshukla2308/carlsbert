# Analysis 1: Co-change vs Import Graph Complementarity

## Summary

| Metric | Value |
|--------|-------|
| Total unique co-change pairs (weight >= 3) | 65,968 |
| Import-connected (1-hop) | 25,989 (39.4%) |
| Import-connected (within 2-hop) | 47,169 (71.5%) |
| NOT import-connected (within 2-hop) | 18,799 (28.5%) |
| **Complementarity ratio** | **28.5%** |

## Interpretation

The complementarity ratio of **28.5%** means that 28.5% of evolutionary
coupling relationships (modules that frequently change together) cannot be discovered
through structural analysis of imports and call graphs alone.

This represents the unique value that co-change analysis adds on top of static code analysis.

## Complementarity by Weight Bucket

| Weight | Total Pairs | Not Connected | Complementarity |
|--------|-------------|---------------|-----------------|
| 3 | 19,006 | 7,293 | 38.4% |
| 4 | 12,293 | 4,045 | 32.9% |
| 5 | 8,092 | 2,299 | 28.4% |
| 6-10 | 16,960 | 3,986 | 23.5% |
| 11-20 | 6,920 | 925 | 13.4% |
| 21+ | 2,697 | 251 | 9.3% |

## Methodology

- Co-change pairs: all module pairs with co-change weight >= 3 from 138,117 commits
- Import graph: built from import edges (module-to-module) and call edges (function-to-function, mapped to modules)
- 2-hop check: module A and B are "import-connected" if there exists a path of length <= 2 in the undirected import graph
- Services indexed: basilisk-v3, euler-api-customer, euler-api-gateway, euler-api-order, euler-api-pre-txn, euler-api-txns, euler-db, euler-drainer, graphh, haskell-sequelize, token_issuer_portal_backend
