#!/usr/bin/env python3
"""
Carlsbert Live Dashboard — serves all Carlsbert outputs as a dynamic website.
Reads files on every request — always shows latest content.

Run: python3 ~/carlsbert/dashboard_server.py
Visit: http://localhost:8005
"""
import http.server
import json
import os
import pathlib
import time
import urllib.parse

PORT = int(os.environ.get("CARLSBERT_DASH_PORT", 8005))
ROOT = pathlib.Path(__file__).parent

# Sections to display — each maps to a directory or file pattern
SECTIONS = {
    "board_reviews": {
        "title": "Board Reviews",
        "icon": "🏛",
        "path": ROOT / "ceo" / "daily_reports",
        "type": "dir",
    },
    "rfcs": {
        "title": "RFCs",
        "icon": "📋",
        "path": ROOT / "rfcs",
        "type": "dir",
        "exclude": ["TEMPLATE.md"],
    },
    "explorer": {
        "title": "Explorer Findings",
        "icon": "🌐",
        "path": ROOT / "research",
        "type": "dir",
        "include_pattern": "explorer",
    },
    "brainstorms": {
        "title": "Brainstorms & Debates",
        "icon": "🧠",
        "path": ROOT / "research" / "brainstorms",
        "type": "dir",
    },
    "competitive": {
        "title": "Competitive Intel",
        "icon": "🕵",
        "path": ROOT / "research" / "competitive",
        "type": "dir",
    },
    "tech_radar": {
        "title": "Tech Radar",
        "icon": "📡",
        "path": ROOT / "tech_radar" / "radar.md",
        "type": "file",
    },
    "research_data": {
        "title": "Research Data",
        "icon": "📊",
        "path": ROOT / "research" / "data",
        "type": "dir",
    },
    "failure_reports": {
        "title": "Failure Reports",
        "icon": "⚠",
        "path": ROOT / "failure_reports",
        "type": "dir",
        "exclude": ["TEMPLATE.md"],
    },
    "journal": {
        "title": "Journal",
        "icon": "📝",
        "path": ROOT / "journal.md",
        "type": "file",
    },
    "last_state": {
        "title": "Current State",
        "icon": "⚡",
        "path": ROOT / "ceo" / "last_state.md",
        "type": "file",
    },
    "system": {
        "title": "System Health",
        "icon": "💻",
        "path": None,
        "type": "dynamic",
    },
}


def _read_file(path):
    try:
        return pathlib.Path(path).read_text(errors="replace")
    except Exception:
        return ""


def _list_md_files(dirpath, exclude=None, include_pattern=None):
    """List markdown files in a directory, sorted by modification time (newest first)."""
    exclude = exclude or []
    files = []
    try:
        for f in pathlib.Path(dirpath).iterdir():
            if f.suffix == ".md" and f.name not in exclude:
                if include_pattern and include_pattern not in f.name.lower():
                    continue
                files.append(f)
    except Exception:
        pass
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def _get_system_health():
    """Run sys_monitor and return output."""
    import subprocess
    try:
        r = subprocess.run(
            ["/home/beast/miniconda3/bin/python3", str(ROOT / "tools" / "sys_monitor.py")],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout or "sys_monitor not available"
    except Exception as e:
        return f"Error: {e}"


def _get_inbox_summary():
    """Read recent inbox entries."""
    inbox = ROOT / "ceo" / "inbox.jsonl"
    if not inbox.exists():
        return "No messages yet."
    lines = inbox.read_text().strip().splitlines()[-20:]  # last 20
    entries = []
    for line in reversed(lines):
        try:
            e = json.loads(line)
            status = e.get("status", "?")
            icon = "✅" if status == "done" else "⏳"
            entries.append(f"{icon} [{e.get('company','?')}] {e.get('instruction','')[:80]}")
        except Exception:
            pass
    return "\n".join(entries) if entries else "No messages."


def _get_mindstate():
    """Read Amit's mindstate seeds."""
    ms = ROOT / "ceo" / "mindstate.jsonl"
    if not ms.exists():
        return "No seeds yet."
    lines = ms.read_text().strip().splitlines()[-10:]
    seeds = []
    for line in reversed(lines):
        try:
            e = json.loads(line)
            seeds.append(f"🌱 {e.get('topic', '?')}")
        except Exception:
            pass
    return "\n".join(seeds) if seeds else "No seeds."


def _md_to_html(md_text):
    """Basic markdown to HTML — headers, bold, italic, code, lists, links, tables."""
    import re
    html = md_text

    # Escape HTML
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Code blocks (``` ... ```)
    html = re.sub(r'```(\w*)\n(.*?)```', lambda m: f'<pre><code class="{m.group(1)}">{m.group(2)}</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Headers
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

    # Simple table support
    def _table_replace(m):
        rows = m.group(0).strip().split('\n')
        out = '<table>'
        for i, row in enumerate(rows):
            if '---' in row and '|' in row:
                continue
            cells = [c.strip() for c in row.split('|')[1:-1]]
            tag = 'th' if i == 0 else 'td'
            out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'
        out += '</table>'
        return out
    html = re.sub(r'(\|.+\|[\n\r]+)+', _table_replace, html)

    # List items
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)

    # Paragraphs (double newlines)
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = f'<p>{html}</p>'

    # Clean up empty paragraphs around block elements
    for tag in ['h1','h2','h3','h4','pre','table','hr','li']:
        html = html.replace(f'<p><{tag}>', f'<{tag}>')
        html = html.replace(f'</{tag}></p>', f'</{tag}>')

    return html


def _render_page(title, content_html, active_section=""):
    """Render full HTML page with sidebar navigation."""
    nav_items = []
    for key, sec in SECTIONS.items():
        active = ' class="active"' if key == active_section else ""
        nav_items.append(f'<a href="/{key}"{active}>{sec["icon"]} {sec["title"]}</a>')
    nav_html = "\n".join(nav_items)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Carlsbert — {title}</title>
<meta http-equiv="refresh" content="60">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: #080808; color: #e3e3e3; display: flex; min-height: 100vh; }}

/* Sidebar */
.sidebar {{ width: 260px; background: #0f0f0f; border-right: 1px solid rgba(255,255,255,0.08); padding: 20px 0; position: fixed; height: 100vh; overflow-y: auto; }}
.sidebar .logo {{ padding: 0 20px 20px; font-family: 'JetBrains Mono', monospace; font-size: 16px; color: #00D1FF; letter-spacing: 0.2em; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px; }}
.sidebar .logo span {{ font-size: 10px; color: #666; display: block; letter-spacing: 0.1em; margin-top: 4px; }}
.sidebar a {{ display: block; padding: 10px 20px; color: #8e8e8e; text-decoration: none; font-size: 13px; transition: all 0.15s; }}
.sidebar a:hover {{ color: #e3e3e3; background: rgba(255,255,255,0.04); }}
.sidebar a.active {{ color: #00D1FF; background: rgba(0,209,255,0.06); border-right: 2px solid #00D1FF; }}

/* Main */
.main {{ margin-left: 260px; flex: 1; padding: 32px 48px; max-width: 960px; }}
.main h1 {{ font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #f0f0f0; }}
.main .meta {{ font-size: 12px; color: #666; margin-bottom: 24px; }}
.main .file-list {{ list-style: none; margin-bottom: 24px; }}
.main .file-list li {{ margin-bottom: 6px; }}
.main .file-list a {{ color: #00D1FF; text-decoration: none; font-size: 14px; }}
.main .file-list a:hover {{ text-decoration: underline; }}
.main .file-list .date {{ color: #555; font-size: 11px; margin-left: 8px; }}

/* Content */
.content {{ line-height: 1.7; font-size: 15px; }}
.content h1 {{ font-size: 18px; font-weight: 600; margin-top: 28px; margin-bottom: 8px; color: #f0f0f0; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px; }}
.content h2 {{ font-size: 16px; font-weight: 600; margin-top: 24px; margin-bottom: 6px; color: #e8e8e8; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 4px; }}
.content h3 {{ font-size: 14px; font-weight: 600; margin-top: 18px; color: #ddd; }}
.content h4 {{ font-size: 13px; font-weight: 600; margin-top: 14px; color: #b0b0b0; }}
.content p {{ margin-bottom: 12px; }}
.content strong {{ color: #f0f0f0; }}
.content a {{ color: #00D1FF; text-decoration: none; }}
.content a:hover {{ text-decoration: underline; }}
.content pre {{ background: #0f0f0f; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 14px 18px; overflow-x: auto; margin: 14px 0; }}
.content code {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
.content :not(pre) > code {{ background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
.content table {{ border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 13px; }}
.content th {{ background: rgba(255,255,255,0.04); color: #aaa; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; padding: 8px 12px; border: 1px solid rgba(255,255,255,0.08); text-align: left; }}
.content td {{ padding: 6px 12px; border: 1px solid rgba(255,255,255,0.08); }}
.content tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
.content li {{ margin-left: 20px; margin-bottom: 4px; }}
.content hr {{ border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0; }}
.content blockquote {{ border-left: 3px solid #00D1FF; background: rgba(0,209,255,0.04); padding: 10px 14px; margin: 12px 0; color: #a0a0a0; border-radius: 0 6px 6px 0; }}

/* Status cards */
.status-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
.status-card {{ background: #0f0f0f; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; }}
.status-card h3 {{ font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }}
.status-card pre {{ margin: 0; border: none; padding: 0; background: transparent; font-size: 12px; }}

/* Auto-refresh indicator */
.refresh-badge {{ position: fixed; bottom: 16px; right: 16px; background: rgba(0,209,255,0.1); color: #00D1FF; font-size: 10px; padding: 4px 10px; border-radius: 12px; font-family: 'JetBrains Mono', monospace; }}
</style>
</head>
<body>
<div class="sidebar">
    <div class="logo">CARLSBERT<span>autonomous AI org</span></div>
    <a href="/" {"class='active'" if not active_section else ""}>⚡ Overview</a>
    {nav_html}
</div>
<div class="main">
    <h1>{title}</h1>
    <div class="meta">Auto-refreshes every 60s · Last loaded: {time.strftime("%Y-%m-%d %H:%M:%S")}</div>
    {content_html}
</div>
<div class="refresh-badge">⟳ live</div>
</body>
</html>"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/" or path == "":
            self._serve_overview()
        elif path.startswith("/file/"):
            filepath = path[6:]
            self._serve_file(filepath)
        else:
            section = path.strip("/").split("/")[0]
            if section in SECTIONS:
                self._serve_section(section)
            else:
                self.send_error(404)

    def _serve_overview(self):
        """Overview page with system health, inbox, mindstate, and section summaries."""
        health = _get_system_health()
        inbox = _get_inbox_summary()
        mindstate = _get_mindstate()
        last_state = _read_file(ROOT / "ceo" / "last_state.md") or "No state saved yet."

        content = f"""
        <div class="status-grid">
            <div class="status-card">
                <h3>💻 System Health</h3>
                <pre>{health}</pre>
            </div>
            <div class="status-card">
                <h3>📨 Recent Inbox</h3>
                <pre>{inbox}</pre>
            </div>
            <div class="status-card">
                <h3>🌱 Amit's Mindstate</h3>
                <pre>{mindstate}</pre>
            </div>
            <div class="status-card">
                <h3>⚡ Current State</h3>
                <pre>{last_state[:500]}</pre>
            </div>
        </div>
        <h2>Sections</h2>
        <ul class="file-list">
        """
        for key, sec in SECTIONS.items():
            count = ""
            if sec["type"] == "dir" and sec["path"] and sec["path"].exists():
                n = len(_list_md_files(sec["path"], sec.get("exclude"), sec.get("include_pattern")))
                count = f' <span class="date">({n} files)</span>'
            content += f'<li><a href="/{key}">{sec["icon"]} {sec["title"]}</a>{count}</li>'
        content += "</ul>"

        html = _render_page("Overview", content)
        self._respond(html)

    def _serve_section(self, section):
        sec = SECTIONS[section]

        if sec["type"] == "file":
            text = _read_file(sec["path"]) if sec["path"] and sec["path"].exists() else "File not found."
            content = f'<div class="content">{_md_to_html(text)}</div>'
            html = _render_page(sec["title"], content, section)

        elif sec["type"] == "dynamic":
            health = _get_system_health()
            content = f'<div class="content"><pre>{health}</pre></div>'
            html = _render_page(sec["title"], content, section)

        elif sec["type"] == "dir":
            files = _list_md_files(sec["path"], sec.get("exclude"), sec.get("include_pattern"))
            if not files:
                content = '<p style="color:#666">No files yet.</p>'
            else:
                content = '<ul class="file-list">'
                for f in files:
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(f.stat().st_mtime))
                    rel = str(f.relative_to(ROOT))
                    content += f'<li><a href="/file/{rel}">{f.name}</a> <span class="date">{mtime}</span></li>'
                content += '</ul>'
            html = _render_page(sec["title"], content, section)
        else:
            html = _render_page(sec["title"], "<p>Unknown section type</p>", section)

        self._respond(html)

    def _serve_file(self, filepath):
        full = ROOT / filepath
        if not full.exists() or not str(full).startswith(str(ROOT)):
            self.send_error(404)
            return
        text = _read_file(full)
        content = f'<div class="content">{_md_to_html(text)}</div>'
        title = full.stem.replace("_", " ").replace("-", " ").title()
        html = _render_page(title, content)
        self._respond(html)

    def _respond(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, fmt, *args):
        pass  # suppress request logs


if __name__ == "__main__":
    httpd = http.server.HTTPServer(("", PORT), DashboardHandler)
    print(f"Carlsbert Dashboard: http://localhost:{PORT}")
    httpd.serve_forever()
