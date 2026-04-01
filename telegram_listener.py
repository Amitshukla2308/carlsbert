#!/usr/bin/env python3
"""
Carlsbert Telegram Listener — polls for Amit's messages and queues them as instructions.

Runs as a background loop. Writes incoming instructions to:
  ~/carlsbert/ceo/inbox.jsonl

Format of queued instructions:
  {"ts": 1234567890, "text": "raw message", "company": "hyperretrieval", "instruction": "check X", "status": "pending"}

Message format from Amit:
  "company: instruction"        → routed to specific company
  "all: instruction"            → broadcast to all companies
  Just plain text               → routed to core company (hyperretrieval)

Usage:
  python3 telegram_listener.py              # run forever (foreground)
  python3 telegram_listener.py --once       # poll once and exit
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
from telegram_bridge import poll, send

INBOX = os.path.join(os.path.dirname(__file__), "ceo", "inbox.jsonl")
COMPANIES = {"hyperretrieval", "chatbeast", "cryptoregimetrader", "connector-service",
             "stock-ai-beast", "zeroclaw", "beast_agent", "autoresearch", "open-skills"}

def _parse_instruction(text):
    """Parse 'company: instruction' format. Falls back to 'general' (for Claude CLI to handle)."""
    text = text.strip()
    if ":" in text:
        prefix, rest = text.split(":", 1)
        prefix = prefix.strip().lower().replace(" ", "").replace("_", "-")
        if prefix in COMPANIES or prefix == "all":
            return prefix, rest.strip()
    # No company prefix → general message for Claude CLI to decide
    return "general", text

def _queue(ts, text, company, instruction):
    os.makedirs(os.path.dirname(INBOX), exist_ok=True)
    entry = {
        "ts": ts,
        "text": text,
        "company": company,
        "instruction": instruction,
        "status": "pending",
        "queued_at": time.time(),
    }
    with open(INBOX, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def _get_pending():
    """Read all pending instructions."""
    if not os.path.exists(INBOX):
        return []
    pending = []
    with open(INBOX) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("status") == "pending":
                        pending.append(entry)
                except json.JSONDecodeError:
                    pass
    return pending

def mark_done(ts, result_summary="done"):
    """Mark an instruction as completed by rewriting the file."""
    if not os.path.exists(INBOX):
        return
    lines = []
    with open(INBOX) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("ts") == ts and entry.get("status") == "pending":
                    entry["status"] = "done"
                    entry["completed_at"] = time.time()
                    entry["result"] = result_summary
                lines.append(json.dumps(entry))
            except json.JSONDecodeError:
                lines.append(line)
    with open(INBOX, "w") as f:
        f.write("\n".join(lines) + "\n")

def poll_once():
    """Poll Telegram, queue any new instructions, return them."""
    replies = poll()
    new_instructions = []
    for r in replies:
        text = r["text"]
        # Skip common non-instruction replies
        if text.lower() in ("ok", "got it", "thanks", "approved", "approve",
                            "rejected", "reject", "yes", "no", "👍", "👎"):
            # These are decision replies, not new instructions
            # Still queue them so the waiting agent can pick them up
            company, instruction = "decision", text
        else:
            company, instruction = _parse_instruction(text)

        entry = _queue(r["date"], text, company, instruction)
        new_instructions.append(entry)

        # Acknowledge receipt
        if company == "decision":
            send(f"Noted: {text}", parse_mode=None)
        elif company == "all":
            send(f"Broadcasting to all companies: {instruction}", parse_mode=None)
        elif company == "general":
            send(f"Received. Claude CLI will handle.", parse_mode=None)
        else:
            send(f"Routed to {company}: {instruction}", parse_mode=None)

    return new_instructions

def run_forever(interval=15):
    """Poll every N seconds."""
    print(f"[listener] Polling every {interval}s. Inbox: {INBOX}")
    send("👂 Listener active. Send instructions as:\n`company: do something`\nor just type and it goes to HyperRetrieval.", parse_mode="Markdown")
    while True:
        try:
            new = poll_once()
            if new:
                for n in new:
                    print(f"[listener] {n['company']}: {n['instruction']}")
        except Exception as e:
            print(f"[listener] error: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    if "--once" in sys.argv:
        results = poll_once()
        for r in results:
            print(f"  [{r['company']}] {r['instruction']}")
        if not results:
            print("  No new messages")
    else:
        run_forever()
