#!/usr/bin/env python3
"""
System health monitor for WSL2 Linux with NVIDIA GPU.

Usage:
    Standalone:  python3 sys_monitor.py
    Importable:  from sys_monitor import get_health_report
"""

import os
import subprocess
import datetime


def _read_file(path):
    """Read a file and return its content, or None on failure."""
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def get_ram_usage():
    """Return RAM usage dict from /proc/meminfo."""
    content = _read_file("/proc/meminfo")
    if not content:
        return {"error": "Could not read /proc/meminfo"}

    info = {}
    for line in content.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            info[parts[0].rstrip(":")] = int(parts[1])  # values in kB

    total_kb = info.get("MemTotal", 0)
    free_kb = info.get("MemFree", 0)
    buffers_kb = info.get("Buffers", 0)
    cached_kb = info.get("Cached", 0)
    available_kb = info.get("MemAvailable", free_kb + buffers_kb + cached_kb)
    used_kb = total_kb - available_kb

    def to_gb(kb):
        return round(kb / 1048576, 2)

    percent = round((used_kb / total_kb) * 100, 1) if total_kb else 0

    return {
        "total_gb": to_gb(total_kb),
        "used_gb": to_gb(used_kb),
        "free_gb": to_gb(available_kb),
        "percent": percent,
    }


def get_gpu_usage():
    """Return GPU VRAM usage via nvidia-smi."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"error": f"nvidia-smi failed: {result.stderr.strip()}"}

        gpus = []
        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                total = float(parts[1])
                used = float(parts[2])
                free = float(parts[3])
                gpus.append({
                    "name": parts[0],
                    "total_mb": total,
                    "used_mb": used,
                    "free_mb": free,
                    "percent": round((used / total) * 100, 1) if total else 0,
                    "gpu_util_percent": parts[4],
                })
        return gpus if gpus else {"error": "No GPUs found"}
    except FileNotFoundError:
        return {"error": "nvidia-smi not found"}
    except subprocess.TimeoutExpired:
        return {"error": "nvidia-smi timed out"}


def get_disk_usage(path="/"):
    """Return disk usage for the given mount point."""
    try:
        st = os.statvfs(path)
        total = st.f_frsize * st.f_blocks
        free = st.f_frsize * st.f_bavail
        used = total - free

        def to_gb(b):
            return round(b / (1024 ** 3), 2)

        percent = round((used / total) * 100, 1) if total else 0
        return {
            "path": path,
            "total_gb": to_gb(total),
            "used_gb": to_gb(used),
            "free_gb": to_gb(free),
            "percent": percent,
        }
    except OSError as e:
        return {"error": str(e)}


def get_top_processes(n=5):
    """Return top N processes by memory (RSS) from /proc."""
    procs = []
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                status = _read_file(f"/proc/{pid}/status")
                if not status:
                    continue
                name = pid
                rss_kb = 0
                for line in status.splitlines():
                    if line.startswith("Name:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.startswith("VmRSS:"):
                        rss_kb = int(line.split()[1])
                procs.append({"pid": int(pid), "name": name, "rss_mb": round(rss_kb / 1024, 1)})
            except (OSError, ValueError, IndexError):
                continue
    except OSError:
        return [{"error": "Could not read /proc"}]

    procs.sort(key=lambda p: p["rss_mb"], reverse=True)
    return procs[:n]


def get_zombie_processes():
    """Return list of zombie processes."""
    zombies = []
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                stat = _read_file(f"/proc/{pid}/stat")
                if not stat:
                    continue
                # State is the field after the comm (in parens)
                parts = stat.split(") ")
                if len(parts) >= 2 and parts[1].startswith("Z"):
                    name = stat.split("(")[1].split(")")[0] if "(" in stat else pid
                    zombies.append({"pid": int(pid), "name": name})
            except (OSError, ValueError, IndexError):
                continue
    except OSError:
        pass
    return zombies


def get_uptime_and_load():
    """Return uptime and load average."""
    result = {}

    uptime_str = _read_file("/proc/uptime")
    if uptime_str:
        secs = float(uptime_str.split()[0])
        result["uptime"] = str(datetime.timedelta(seconds=int(secs)))
    else:
        result["uptime"] = "unknown"

    loadavg = _read_file("/proc/loadavg")
    if loadavg:
        parts = loadavg.split()
        result["load_1m"] = float(parts[0])
        result["load_5m"] = float(parts[1])
        result["load_15m"] = float(parts[2])
    else:
        result["load_1m"] = result["load_5m"] = result["load_15m"] = 0

    return result


def get_health_report():
    """Return a complete system health report as a dict."""
    return {
        "ram": get_ram_usage(),
        "gpu": get_gpu_usage(),
        "disk": get_disk_usage("/"),
        "top_processes": get_top_processes(5),
        "zombies": get_zombie_processes(),
        "uptime": get_uptime_and_load(),
    }


def _format_report(report):
    """Format the health report as a readable string."""
    lines = []
    sep = "-" * 50

    lines.append(sep)
    lines.append("  SYSTEM HEALTH REPORT")
    lines.append(sep)

    # Uptime
    up = report["uptime"]
    lines.append(f"\n  Uptime:       {up['uptime']}")
    lines.append(f"  Load avg:     {up['load_1m']}  {up['load_5m']}  {up['load_15m']}  (1m / 5m / 15m)")

    # RAM
    ram = report["ram"]
    if "error" in ram:
        lines.append(f"\n  RAM:          {ram['error']}")
    else:
        lines.append(f"\n  RAM:          {ram['used_gb']} / {ram['total_gb']} GB  ({ram['percent']}% used)")
        lines.append(f"                {ram['free_gb']} GB available")

    # GPU
    gpu = report["gpu"]
    if isinstance(gpu, dict) and "error" in gpu:
        lines.append(f"\n  GPU:          {gpu['error']}")
    elif isinstance(gpu, list):
        for i, g in enumerate(gpu):
            label = f"  GPU {i}:" if len(gpu) > 1 else "  GPU:"
            lines.append(f"\n{label}         {g['name']}")
            lines.append(f"  VRAM:         {g['used_mb']:.0f} / {g['total_mb']:.0f} MB  ({g['percent']}% used)")
            lines.append(f"  GPU Util:     {g['gpu_util_percent']}%")

    # Disk
    disk = report["disk"]
    if "error" in disk:
        lines.append(f"\n  Disk /:       {disk['error']}")
    else:
        lines.append(f"\n  Disk /:       {disk['used_gb']} / {disk['total_gb']} GB  ({disk['percent']}% used)")
        lines.append(f"                {disk['free_gb']} GB free")

    # Top processes
    lines.append(f"\n  Top 5 by memory:")
    for p in report["top_processes"]:
        if "error" in p:
            lines.append(f"    {p['error']}")
        else:
            lines.append(f"    PID {p['pid']:>7}  {p['rss_mb']:>8.1f} MB  {p['name']}")

    # Zombies
    zombies = report["zombies"]
    if zombies:
        lines.append(f"\n  Zombie processes ({len(zombies)}):")
        for z in zombies:
            lines.append(f"    PID {z['pid']:>7}  {z['name']}")
    else:
        lines.append(f"\n  Zombies:      none")

    lines.append(sep)
    return "\n".join(lines)


if __name__ == "__main__":
    report = get_health_report()
    print(_format_report(report))
