---
title: Agent Guardrails — HyperRetrieval as the SDLC Safety Net
status: DRAFT
date: 2026-04-01
author: Carlsbert
trigger: Amit asked "We need agent guardrails, who saves our SDLC?"
---

# Agent Guardrails: HyperRetrieval as the SDLC Safety Net

## The Problem

AI coding agents (Copilot, Cursor, Claude Code, Windsurf) are writing production code.
They're fast, capable, and have no SDLC discipline. They don't:
- Check if their changes break downstream services
- Know which files typically change together (and they forgot one)
- Understand architectural boundaries they shouldn't cross
- Verify their PR is complete before submitting

Human code review can't keep up. The review queue is already the bottleneck.
Adding 10x more agent-generated PRs makes it worse, not better.

**Who guards the guards?** HyperRetrieval.

## Why HyperRetrieval Is Uniquely Positioned

We already have the signals. No one else does:

| Signal | What it catches | Status |
|--------|----------------|--------|
| **Co-change index** (111K pairs) | "You changed X but historically Y always changes with X" | BUILT |
| **Blast radius** (import + co-change) | "Your 1-file change actually impacts 82 modules across 10 services" | BUILT |
| **predict_missing_changes** | "Your PR is missing 3 files that co-change with your changeset" | BUILT |
| **Module graph** (43K import edges) | "You're creating a circular dependency" / "You're breaking the dependency direction" | BUILT |
| **Cross-service tracking** (8,927 edges) | "Your change in service A will break service B" | BUILT |

These are already MCP tools. Any agent can call them. The missing piece is the
**orchestration layer** that makes agents call them automatically.

## The Product: Guardian Mode

### Layer 1: Pre-commit Self-Check (Agent-side)
The agent calls HyperRetrieval tools on its own changes before committing:

```
Agent writes code
  → calls get_blast_radius(changed_files)
  → calls predict_missing_changes(changed_files)
  → IF blast_radius > threshold OR missing_coverage < 80%:
       Agent self-corrects OR escalates to human
```

**Implementation:** A system prompt addition / MCP tool wrapper that agents
include in their workflow. Zero code change for us — it's a prompt pattern.

### Layer 2: CI/CD Gate (Pipeline-side)
A GitHub Action / CI step that runs on every PR:

```yaml
- name: HyperRetrieval Guardian
  run: python pr_analyzer.py --pr $PR_NUMBER --mode guardian
  # Fails the PR if:
  # - blast_radius > configured threshold
  # - predict_missing_changes finds likely-missing files
  # - circular dependency introduced
  # - cross-service boundary violated without explicit override
```

**Implementation:** We already have `pr_analyzer.py`. Extend it with:
- `--mode guardian` flag
- Configurable thresholds in workspace config.yaml
- GitHub PR comment with findings (not just pass/fail)

### Layer 3: Architectural Rules Engine (Org-side)
Organizations define rules:

```yaml
# workspace config.yaml
guardian:
  rules:
    - name: auth-review-required
      pattern: "*/Auth/*"
      requires: security-team-approval
      
    - name: db-migration-needs-rollback
      pattern: "*/migrations/*"
      check: file_contains("def rollback")
      
    - name: no-cross-service-without-approval
      check: blast_radius.cross_service_count <= 2
      escalate: architecture-team
      
    - name: pr-completeness
      check: predict_missing.coverage >= 0.8
      message: "Your PR might be missing: {missing_files}"
```

**Implementation:** New module `serve/guardian.py` that evaluates rules against
HyperRetrieval's analysis output. Returns pass/fail/warn per rule.

## The Buyer

**VP of Engineering** who is:
- Nervous about giving AI agents write access to production repos
- Drowning in code review requests (human + AI generated)
- Looking for automated quality gates that don't slow down velocity
- Required by compliance to demonstrate code review happened

**Pitch:** "Your agents write code. HyperRetrieval makes sure they write it right."

## Success Metric

- **Primary:** Number of "agent-generated PRs caught by Guardian" that would have
  caused production issues
- **Secondary:** Time saved in code review (Guardian auto-approves safe changes,
  flags risky ones)
- **Threshold:** Guardian must catch >80% of incomplete PRs (measured against
  historical git data where we know the "real" changeset)

## Implementation Phases

### Phase 1: PR Completeness Report (1-2 days)
- Extend `pr_analyzer.py` with `--mode guardian`
- Run `predict_missing_changes` + `get_blast_radius` on PR diff
- Output: markdown report as GitHub PR comment
- **This alone is valuable.** Ship it.

### Phase 2: CI/CD Integration (2-3 days)
- GitHub Action wrapper
- Configurable thresholds
- Pass/fail gate on PRs

### Phase 3: Agent Self-Check Protocol (1 day)
- System prompt pattern for agents
- MCP tool wrapper: `check_my_changes(files)` that runs all checks in one call
- Documentation for agent framework integration

### Phase 4: Rules Engine (3-5 days)
- YAML-based rule definitions
- Custom checks beyond co-change
- Per-team/per-service configuration

## Risks

1. **False positives:** Guardian flags changes as risky when they're fine → developers
   disable it. **Mitigation:** Start with high-confidence checks only (missing files,
   blast radius > 50). Tune thresholds over time.

2. **Performance:** Running full analysis on every PR commit. **Mitigation:**
   pr_analyzer already works in seconds. Cache graph between runs.

3. **Adoption:** Teams won't add another CI step unless forced. **Mitigation:**
   Make the first experience a helpful PR comment, not a blocking gate.

## Competitive Advantage

- **Greptile v4** has graph + agent but no co-change, no missing file prediction
- **Sourcegraph Cody** does multi-repo search but no SDLC integration
- **CodeScout** does RL retrieval but no quality gates
- **Nobody** combines evolutionary coupling (co-change) with real-time PR validation

HyperRetrieval becomes the **immune system** for codebases — it learns what
changes together, detects when something's missing, and prevents incomplete
changes from reaching production.

## Cost

- Phase 1-3: pure engineering time, zero infrastructure cost
- Phase 4: adds ~100ms per rule evaluation, negligible
- No GPU needed — all graph/co-change operations are CPU-only

## Rollback

Each phase is independent. Any phase can be disabled without affecting others.
Guardian mode is opt-in via config flag.

## The Vision

Today: "Search your code intelligently."
Tomorrow: "Your code protects itself."

The SDLC doesn't need more humans reviewing agent code.
It needs an automated system that understands the codebase deeply enough
to know when something's wrong — before it ships.

That's HyperRetrieval Guardian.
