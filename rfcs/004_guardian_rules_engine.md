# RFC-004: Guardian YAML Rules Engine

## What
Replace hardcoded verdict logic in `_guardian_verdict()` with a configurable YAML rules engine. Teams define their own policies for PASS/WARN/FAIL verdicts.

## Why
Current verdict thresholds are hardcoded (coverage < 0.5 = FAIL, < 0.8 = WARN, >3 services = WARN). Every team has different policies:
- A payments team needs stricter security checks
- A frontend team doesn't care about co-change coverage
- Some teams want FAIL on any security-sensitive file; others just want WARN

Configurability = enterprise readiness = moat.

## Success Metric
- Guardian loads rules from `.hyperretrieval/guardian_rules.yaml`
- Custom thresholds override defaults
- Custom security keywords extend/replace defaults
- Custom module patterns trigger specific verdicts
- Falls back to current behavior when no config exists
- All existing tests still pass + new rule engine tests

## Design

### Config file: `guardian_rules.yaml`

```yaml
# Guardian Rules Configuration
version: 1

# Override default thresholds
thresholds:
  coverage_fail: 0.5       # below this = FAIL (default: 0.5)
  coverage_warn: 0.8       # below this = WARN (default: 0.8)
  min_predictions_for_fail: 3  # need this many missing predictions to FAIL (default: 3)
  max_services_warn: 3     # above this = WARN (default: 3)

# Security keywords (extends defaults unless mode: replace)
security:
  mode: extend             # extend | replace
  keywords:
    - payment
    - pci
    - compliance

# Custom rules — evaluated in order, first match wins for each severity
rules:
  - name: "Block auth changes without tests"
    match:
      modules: ["**/Auth*", "**/Session*", "**/OAuth*"]
    require:
      files_present: ["**/test*", "**/spec*"]  # at least one test file in PR
    verdict: FAIL
    message: "Auth module changes require test coverage"

  - name: "Warn on database schema changes"
    match:
      modules: ["**/Migration*", "**/Schema*", "**/DB*"]
    verdict: WARN
    message: "Database schema change detected — review migration plan"

  - name: "Warn on cross-service blast"
    match:
      min_services: 2
    verdict: WARN
    message: "Changes affect multiple services"
```

### Implementation
1. Add `_load_rules(config_path)` — loads YAML, validates schema, returns rules dict
2. Modify `_guardian_verdict()` to accept rules and evaluate them
3. Add `--rules` CLI arg to `pr_analyzer.py`
4. Update GitHub Action to pass rules file path
5. Ship default `guardian_rules.example.yaml`

### Rollback
`git revert` the commit. No config = current hardcoded behavior (backward compatible).

## Lenses
- **Engineer:** Clean separation — rules loading vs evaluation. Testable.
- **Architect:** YAML config is the right level — not a DSL, not hardcoded. Extensible later.
- **Product:** Every enterprise team will customize this. It's what makes Guardian sellable.
- **Economist:** Zero runtime cost (YAML parsed once). Development cost: ~2 hours.
- **Scientist:** Hypothesis: configurable rules increase adoption. Measurable by config file presence.
