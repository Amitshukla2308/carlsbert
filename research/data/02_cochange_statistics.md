# Analysis 2: Co-change Distribution Statistics

## Weight Distribution

| Weight | Pairs | % of Total |
|--------|-------|------------|
| 3 | 19,006 | 28.8% |
| 4 | 12,293 | 18.6% |
| 5 | 8,092 | 12.3% |
| 6-10 | 16,960 | 25.7% |
| 11-20 | 6,920 | 10.5% |
| 21+ | 2,697 | 4.1% |
| **Total** | **65,968** | **100%** |

## Partners Per Module Distribution

| Metric | Value |
|--------|-------|
| Total modules with co-change data | 7,363 |
| Mean partners per module | 14.5 |
| Median partners per module | 10 |
| P90 partners per module | 40 |
| P99 partners per module | 40 |
| Max partners per module | 40 |
| Module with most partners | `Euler.App.Routes` |

## Cold-Start Modules

| Metric | Value |
|--------|-------|
| Total modules in co-change index | 7,363 |
| Modules WITH co-change partners | 7,363 |
| Modules with ZERO co-change partners (cold-start) | 0 (0.0%) |

Note: "Cold-start" modules have no co-change signal. For these modules, retrieval must
rely entirely on structural (import/call) analysis or semantic similarity.

## Cross-Service vs Intra-Service

| Type | Pairs | % |
|------|-------|---|
| Intra-service (same repo) | 65,968 | 100.0% |
| Cross-service (different repo) | 0 | 0.0% |
| **Total** | **65,968** | **100%** |

## Top 10 Strongest Co-change Pairs

| Rank | Module A | Module B | Weight |
|------|----------|----------|--------|
| 1 | `Gateway.App.Routes` | `Gateway.Gateway.Common` | 479 |
| 2 | `Gateway.App.Routes` | `Gateway.App.Server` | 419 |
| 3 | `Gateway.Remote.CommonService` | `Gateway.Remote.Types` | 403 |
| 4 | `Common.Types.Gateway` | `Euler.Types.Gateway` | 400 |
| 5 | `Euler.API.Order` | `OLTP.Order.OrderStatus` | 385 |
| 6 | `Gateway.App.Server` | `Gateway.Gateway.Common` | 331 |
| 7 | `Gateway.CommonGateway` | `Gateway.Remote.CommonService` | 326 |
| 8 | `Config.Constants` | `Product.OLTP.Transaction` | 311 |
| 9 | `Gateway.Remote.CommonService` | `Product.OLTP.Transaction` | 287 |
| 10 | `Gateway.Gateway.Common` | `Utils.Domain.Transformer` | 254 |

## Source Data

- Total commits analyzed: 138,117
- Repos: basilisk-v3, euler-api-customer, euler-api-gateway, euler-api-order, euler-api-pre-txn, euler-api-txns, euler-db, euler-drainer, graphh, haskell-sequelize, token_issuer_portal_backend
- Minimum co-change weight threshold: 3
- Top-K partners per module: 40
