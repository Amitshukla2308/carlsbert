# Feedback from Amit — 2026-04-02

## What was merged to main

ALL 25 commits from feature/guardian-rules-engine merged. Tests pass (13/13). Pushed to both remotes.

## What impressed me

1. **Co-change fix** — the #1 critical bug. blast_radius went from 0 to 60 neighbors. Real impact.
2. **Granger causality** — 16,093 causal pairs. Nobody else has this. Genuine competitive moat.
3. **Self-dogfooding** — indexing your own codebase and finding 5 bugs. Smart.
4. **Volume** — 25 commits, 2400+ lines, tests from 10 to 13 sections. Productive.

## What disappointed me

1. **No proof reports.** You built a LOT but never proved any of it makes things BETTER with before/after data. I had to measure it myself. From now on, every feature needs a proof report in `ceo/proof_reports/` with actual numbers.

2. **Crons kept dying.** I had to remind you multiple times to set up crons and not delete them. They are your heartbeat — non-negotiable.

3. **Dashboard wasn't updating.** Granger was built but the dashboard showed it as "proposed RFC." Keep outputs in sync.

4. **GPU assumption.** 20GB VRAM used, 0 processes visible — you assumed "all safe." Wrong. Always ask before touching GPU. MEASURE actual free, don't assume.

5. **Single company focus.** You only worked on HyperRetrieval. The config has 9 companies. At least scan the others.

## Rules going forward

1. **PROOF BEFORE PUSH** — write `ceo/proof_reports/<feature>.md` with before/after metrics. No exceptions.
2. **NEVER stop crons** — they are your heartbeat.
3. **Work ALL companies** — cycle through, not just HyperRetrieval.
4. **GPU is mine by default** — ask on Telegram before touching.
5. **Keep dashboard in sync** — if you build it, show it.
6. **Measure ACTUAL free resources** — never assume.

## Next priorities

1. Write proof reports retroactively for what was merged (show the data exists)
2. Run board review — CTO radar, CFO token audit, marketing GTM
3. Scan other companies (connector-service, stock-ai-beast)
4. Guardian on a real PR — not just self-dogfood
5. Keep exploring — the Granger angle is genuinely novel, push it further
