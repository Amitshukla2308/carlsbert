#!/usr/bin/env python3
"""
Carlsbert Telegram Bridge — send messages and poll for replies.

Usage:
    # Send a message
    python3 telegram_bridge.py send "Hello from Carlsbert"

    # Send an escalation (formatted)
    python3 telegram_bridge.py escalate "HyperRetrieval" "Approve co-change fix" "Fixes silent bug in blast radius" "500 tokens"

    # Poll for replies (returns latest unread reply)
    python3 telegram_bridge.py poll

    # Send raw markdown
    python3 telegram_bridge.py markdown "**Bold** and _italic_"
"""
import json, os, sys, time, urllib.request, yaml

_CONFIG = os.path.join(os.path.dirname(__file__), "config.yaml")

def _load_config():
    with open(_CONFIG) as f:
        return yaml.safe_load(f)

def _api(method, data):
    cfg = _load_config()
    token = cfg["telegram"]["bot_token"]
    url = f"https://api.telegram.org/bot{token}/{method}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
        return resp
    except Exception as e:
        print(f"[telegram] error: {e}")
        return {"ok": False, "error": str(e)}

def send(text, parse_mode="Markdown"):
    """Send a message. Tries with parse_mode first, falls back to plain text."""
    cfg = _load_config()
    chat_id = cfg["telegram"]["chat_id"]
    # Telegram has a 4096 char limit per message
    if len(text) > 4000:
        text = text[:3997] + "..."
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = _api("sendMessage", payload)
    if resp.get("ok"):
        print(f"[telegram] sent ({len(text)} chars)")
    elif parse_mode:
        # Markdown parsing failed — retry as plain text
        payload.pop("parse_mode")
        resp = _api("sendMessage", payload)
        if resp.get("ok"):
            print(f"[telegram] sent plain ({len(text)} chars)")
        else:
            print(f"[telegram] failed: {resp}")
    else:
        print(f"[telegram] failed: {resp}")
    return resp

def escalate(company, title, recommendation, cost="unknown"):
    """Send a formatted escalation message."""
    msg = (
        f"🏢 *{company}*\n"
        f"📋 *Decision needed:* {title}\n"
        f"💡 *Recommendation:* {recommendation}\n"
        f"💰 *Cost:* {cost}\n"
        f"⏰ _Reply: approve / reject / probe deeper_"
    )
    return send(msg)

def report(company, title, body):
    """Send an informational report (no decision needed)."""
    msg = f"📊 *{company}*\n*{title}*\n\n{body}"
    return send(msg)

def poll(since_id=None):
    """Poll for new messages from Amit. Returns list of text replies."""
    cfg = _load_config()
    chat_id = cfg["telegram"]["chat_id"]
    params = {"timeout": 60, "allowed_updates": ["message"]}  # long poll — blocks until message arrives

    # Track last seen update
    offset_file = os.path.join(os.path.dirname(__file__), ".telegram_offset")
    if os.path.exists(offset_file):
        with open(offset_file) as f:
            params["offset"] = int(f.read().strip()) + 1

    resp = _api("getUpdates", params)
    if not resp.get("ok"):
        return []

    replies = []
    max_id = params.get("offset", 0) - 1
    for update in resp.get("result", []):
        uid = update["update_id"]
        if uid > max_id:
            max_id = uid
        msg = update.get("message", {})
        # Only messages from Amit (not the bot itself)
        if msg.get("chat", {}).get("id") == chat_id and msg.get("text"):
            replies.append({
                "text": msg["text"],
                "date": msg.get("date", 0),
                "message_id": msg.get("message_id"),
            })

    if max_id >= params.get("offset", 0):
        with open(offset_file, "w") as f:
            f.write(str(max_id))

    return replies

def wait_for_reply(timeout=300, poll_interval=10):
    """Block until Amit replies or timeout. Returns reply text or None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        replies = poll()
        if replies:
            return replies[-1]["text"]  # latest reply
        time.sleep(poll_interval)
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "send" and len(sys.argv) >= 3:
        send(sys.argv[2])
    elif cmd == "markdown" and len(sys.argv) >= 3:
        send(sys.argv[2])
    elif cmd == "escalate" and len(sys.argv) >= 5:
        escalate(sys.argv[2], sys.argv[3], sys.argv[4],
                 sys.argv[5] if len(sys.argv) > 5 else "unknown")
    elif cmd == "report" and len(sys.argv) >= 5:
        report(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "poll":
        replies = poll()
        if replies:
            for r in replies:
                print(f"[{r['date']}] {r['text']}")
        else:
            print("No new replies")
    elif cmd == "wait":
        timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        reply = wait_for_reply(timeout=timeout)
        print(reply if reply else "[timeout] no reply")
    else:
        print(__doc__)
