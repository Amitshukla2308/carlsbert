# Analysis 3: Service Boundary Coupling

## Per-Service Cross-Boundary Exposure

| Service | Total Modules | Modules with Cross-Service Partners | Exposure % |
|---------|---------------|-------------------------------------|------------|
| basilisk-v3 | 29 | 0 | 0.0% |
| euler-api-customer | 209 | 0 | 0.0% |
| euler-api-gateway | 4,294 | 0 | 0.0% |
| euler-api-order | 336 | 0 | 0.0% |
| euler-api-pre-txn | 292 | 0 | 0.0% |
| euler-api-txns | 1,561 | 0 | 0.0% |
| euler-db | 595 | 0 | 0.0% |
| euler-drainer | 30 | 0 | 0.0% |
| haskell-sequelize | 2 | 0 | 0.0% |
| token_issuer_portal_backend | 15 | 0 | 0.0% |

## Top 10 Service Pairs by Total Co-change Weight

| Rank | Service A | Service B | Total Weight | Pair Count | Avg Weight |
|------|-----------|-----------|-------------|------------|------------|

## Cross-Service Coupling Matrix (Total Weight)

Shows total co-change weight between each service pair. Only pairs with weight > 0 shown.

| Service A | Service B | Weight | Pairs |
|-----------|-----------|--------|-------|

## Interpretation

- **Exposure %**: The fraction of a service's modules that have evolutionary coupling
  to modules in other services. High exposure means the service is tightly coupled at
  the implementation level, regardless of what the API boundaries suggest.
- **Top service pairs**: These represent the strongest cross-service evolutionary coupling.
  Changes in one service frequently require changes in the paired service.
- This data is valuable for: team coordination, deploy ordering, blast radius estimation,
  and identifying candidates for service merging or better API boundaries.
