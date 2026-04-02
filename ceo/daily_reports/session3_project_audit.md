# Project Audit — Session 3
**Date:** 2026-04-01

## Disk Usage Summary: 145GB across 19 projects

### KEEP (Core Mission)
| Project | Size | Last Commit | Why |
|---------|------|-------------|-----|
| hyperretrieval | 1.3GB | 2026-04-01 | Core product. Active development. |
| codetoolcli | 53MB | 2026-03-31 | Related CLI tool. Tiny footprint. |

### REVIEW (May still be useful)
| Project | Size | Last Commit | Why |
|---------|------|-------------|-----|
| connector-service | 3.3GB | 2026-03-14 | Integration layer. Recent work. |
| diffusers | 147MB | 2026-03-12 | ML library fork. Small. |

### ARCHIVE CANDIDATES (Stale, reclaimable)
| Project | Size | Last Commit | Savings |
|---------|------|-------------|---------|
| toonforge | 85GB | no-git | 85GB — biggest win |
| AI_Systems | 17GB | no-git | 17GB |
| models | 15GB | no-git | 15GB (downloaded models) |
| ltx-2 | 8.1GB | 2026-03-11 | 8.1GB — video gen experiment |
| ltx-video | 7.4GB | 2026-01-06 | 7.4GB — stale |
| workspaces | 5.2GB | no-git | 5.2GB |
| stock-ai-beast | 1.5GB | 2026-02-03 | 1.5GB |
| Trading_Bots | 1.3GB | no-git | 1.3GB |

**Total reclaimable: ~141GB**

### TINY (not worth worrying about)
beast_agent, atlas, Leash.ai, Lab_and_Tools, CodeGeneration, ChatBeast, Archive — all under 300MB total.

## Recommendation
Trim to 4 projects (as discussed):
1. **HyperRetrieval** — the product
2. **codetoolcli** — supporting tool
3. **connector-service** — review first, may archive
4. **carlsbert** — operating system

Everything else → archive to external storage or delete. Saves ~141GB.

## Decision Needed
- Which projects to delete vs archive?
- Is anything in toonforge/AI_Systems/models worth keeping?
