# CodeScene MCP Server Analysis
**Date:** 2026-04-02 | **Session:** 4

## Overview
17 tools, Rust-based, single-purpose design. Focused entirely on Code Health (static quality 1-10 score). Embeds CodeScene CLI binary.

## What They Have (We Don't)
- Business case / ROI projection for refactoring: `code_health_refactoring_business_case`
- Auto-refactoring: `code_health_auto_refactor` (ACE-powered)
- Hotspot detection: revision frequency × health score
- Static docs as tools: `explain_code_health` lets agents self-serve documentation

## What We Have (They Don't)
- Co-change / evolutionary coupling
- Blast radius across services
- Composite risk scoring (0-100)
- Granger causality (directional co-change)
- Configurable policy rules (YAML)
- JSONL history for risk trending
- Predict missing changes

## Adoptable Patterns
1. **Rich tool descriptions** — structured with "When to use / Limitations / Returns / Example"
2. **Business case framing** — quantify value, not just detect problems
3. **Explain tools** — static docs as MCP tools for agent self-service

## Verdict
Complementary, not competing. They answer "is this code healthy?" We answer "what breaks if you change this?" Different buyers, different use cases. Could potentially integrate (use their Code Health score as another component in our risk scoring).
