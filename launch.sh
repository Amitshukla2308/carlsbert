#!/bin/bash
# Carlsbert — AI that lives here
# bash ~/carlsbert/launch.sh

set -e
PYTHON="$HOME/miniconda3/bin/python3"

echo "╔══════════════════════════════════════╗"
echo "║       CARLSBERT  ·  ALIVE           ║"
echo "╚══════════════════════════════════════╝"

# Kill Carlsbert's own processes (tagged with env var)
pkill -f "telegram_listener" 2>/dev/null && echo "Killed old listener" || true
pkill -f "CARLSBERT_SESSION=1" 2>/dev/null && echo "Killed old children" || true
sleep 2

# Tag our processes
export CARLSBERT_SESSION=1

# Start Telegram listener (streaming)
nohup $PYTHON -u "$HOME/carlsbert/telegram_listener.py" > "$HOME/carlsbert/listener.log" 2>&1 &
echo "Telegram: streaming (PID $!)"

# Start live dashboard
fuser 8005/tcp 2>/dev/null | xargs -r kill 2>/dev/null
nohup $PYTHON -u "$HOME/carlsbert/dashboard_server.py" > "$HOME/carlsbert/dashboard.log" 2>&1 &
echo "Dashboard: http://localhost:8005 (PID $!)"
sleep 2

# Launch Claude interactively with Carlsbert identity baked into system prompt
# The session stays alive — crons and agents keep it working
cd "$HOME/projects"
# Launch Claude interactively with Carlsbert identity
echo ""
echo "Type 'start' to begin."
echo ""
exec /home/beast/.local/bin/claude \
    --append-system-prompt-file "$HOME/carlsbert/system_prompt.md" \
    --allow-dangerously-skip-permissions \
    --dangerously-skip-permissions
