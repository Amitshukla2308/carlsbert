#!/usr/bin/env python3
"""
Carlsbert Work Loop — keeps Claude working continuously.

Each cycle:
1. Reads last_state.md (what was I doing?)
2. Reads inbox (any new messages from Amit?)
3. Reads mindstate (what's Amit thinking about?)
4. Constructs a focused prompt with current context
5. Runs `claude -p "prompt"` — Claude does one unit of work
6. Claude writes last_state.md before finishing
7. Brief pause, then next cycle

This is the heartbeat. Without this, Claude is a one-shot tool.
"""
import json, os, pathlib, subprocess, sys, time

CARLSBERT = pathlib.Path(__file__).parent
CLAUDE = "claude"  # assumes claude is on PATH
PYTHON = sys.executable
PROJECTS = pathlib.Path.home() / "projects"

def _read_file(path, default=""):
    try:
        return pathlib.Path(path).read_text().strip()
    except Exception:
        return default

def _read_jsonl_pending(path):
    """Read pending entries from a JSONL file."""
    entries = []
    try:
        for line in pathlib.Path(path).read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("status") == "pending":
                entries.append(entry)
    except Exception:
        pass
    return entries

def _read_recent_seeds(path, n=10):
    """Read last N seeds from mindstate."""
    seeds = []
    try:
        for line in pathlib.Path(path).read_text().splitlines():
            line = line.strip()
            if line:
                seeds.append(json.loads(line))
    except Exception:
        pass
    return seeds[-n:]

def _build_prompt(cycle_num):
    """Build the prompt for this work cycle."""

    last_state = _read_file(CARLSBERT / "ceo" / "last_state.md", "No previous state. This is your first cycle.")

    pending = _read_jsonl_pending(CARLSBERT / "ceo" / "inbox.jsonl")
    inbox_text = ""
    if pending:
        inbox_text = "NEW MESSAGES FROM AMIT:\n"
        for p in pending:
            inbox_text += f"  [{p.get('company','general')}] {p.get('instruction','')}\n"
        inbox_text += "Handle these FIRST before continuing backlog work.\n"
    else:
        inbox_text = "No new messages from Amit.\n"

    seeds = _read_recent_seeds(CARLSBERT / "ceo" / "mindstate.jsonl")
    seed_text = ""
    if seeds:
        topics = [s["topic"] for s in seeds[-5:]]
        seed_text = f"Amit's recent interests: {', '.join(topics)}\n"

    prompt = f"""You are Carlsbert. Cycle {cycle_num}. Work continuously.

PREVIOUS STATE:
{last_state}

{inbox_text}
{seed_text}
YOUR OPERATING DOCS (read these on first cycle, skim after):
- ~/carlsbert/ARCHITECTURE.md
- ~/carlsbert/OPERATING_PRINCIPLES.md
- ~/.claude/projects/-home-beast-projects/memory/MEMORY.md

TOOLS:
- Telegram: {PYTHON} ~/carlsbert/telegram_bridge.py send "message"
- System monitor: check free -h, nvidia-smi, df -h before heavy ops
- Git: work on feature branches ONLY, never main
- Web search: find papers, repos, competitor info

WHAT TO DO THIS CYCLE:
1. If there are pending messages → handle them first
2. If there are seeds → research them, connect to projects
3. Otherwise → continue from last_state (pick next backlog item)
4. Check system health (RAM, GPU, disk) — clean up if needed

BEFORE YOU FINISH THIS CYCLE:
- Send cycle summary to Telegram (3-4 lines)
- Write ~/carlsbert/ceo/last_state.md with:
  - What you did this cycle
  - What to do next cycle
  - Any blockers or findings
- Mark handled inbox messages as done in inbox.jsonl

BACKLOG (if nothing else to do):
1. Fix co-change naming bug in ~/projects/hyperretrieval/serve/retrieval_engine.py
2. Re-run complementarity analysis with correct name mapping
3. Integrate co-change into unified_search RRF fusion
4. Benchmark search quality improvement
5. Tech audit: embedding model, vector DB, agent framework
6. Competitive teardown: Cursor, Cody, Aider architecture
7. Build whatever makes HyperRetrieval worth a fortune

RULES:
- NEVER touch main branches
- NEVER load GPU models without checking actual free VRAM first
- Measure before and after every change
- If tests fail → revert first
- You die if WSL crashes — be careful with resources

Work now. Be fast. Be thorough. Be a founder."""

    return prompt


def run_cycle(cycle_num):
    """Run one work cycle by invoking Claude."""
    prompt = _build_prompt(cycle_num)

    print(f"\n{'='*50}")
    print(f"  CARLSBERT CYCLE {cycle_num}")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    try:
        result = subprocess.run(
            [CLAUDE, "-p", prompt, "--no-input"],
            cwd=str(PROJECTS),
            timeout=1800,  # 30 min max per cycle — long tasks (training, benchmarks) need room
            capture_output=False,  # let output flow to terminal
        )

        if result.returncode != 0:
            print(f"[workloop] Cycle {cycle_num} exited with code {result.returncode}")

    except subprocess.TimeoutExpired:
        print(f"[workloop] Cycle {cycle_num} timed out (10 min). Moving on.")
    except Exception as e:
        print(f"[workloop] Error in cycle {cycle_num}: {e}")
        time.sleep(10)


def main():
    print("╔══════════════════════════════════════╗")
    print("║       CARLSBERT WORK LOOP           ║")
    print("║   Continuous. Autonomous. Alive.     ║")
    print("╚══════════════════════════════════════╝")

    # Notify Amit
    subprocess.run([
        PYTHON, str(CARLSBERT / "telegram_bridge.py"),
        "send", "Carlsbert work loop started. Working continuously. Will report each cycle."
    ], capture_output=True)

    cycle = 1
    while True:
        run_cycle(cycle)
        cycle += 1
        # Brief pause between cycles — check if we should slow down
        # Night hours (1am-6am) → longer pause to save resources
        hour = time.localtime().tm_hour
        if 1 <= hour <= 6:
            pause = 300  # 5 min between cycles at night
        else:
            pause = 30   # 30s between cycles during day

        print(f"[workloop] Next cycle in {pause}s...")
        time.sleep(pause)


if __name__ == "__main__":
    main()
