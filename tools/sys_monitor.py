#!/usr/bin/env python3
"""
Carlsbert System Monitor
Provides VRAM, RAM, disk, GPU process, and port status monitoring.

CLI usage:
    python3 sys_monitor.py                  → prints report()
    python3 sys_monitor.py check 4000 2000  → can_i_use(vram=4000, ram=2000)
    python3 sys_monitor.py status           → full JSON status
    python3 sys_monitor.py kill 8000        → kill process on port
"""

import json
import os
import re
import signal
import shutil
import subprocess
import sys


# Port → service name mapping
PORT_SERVICES = {
    8000: "chainlit",
    8001: "embed",
    8002: "mcp",
    8003: "viz",
    8004: "dashboard",
}

# Safety margins
VRAM_HEADROOM_MB = 2048   # 2 GB
RAM_HEADROOM_MB = 3072    # 3 GB
DISK_HEADROOM_GB = 20     # 20 GB


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], timeout: int = 10) -> str:
    """Run a subprocess and return stdout. Returns empty string on failure."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def _nvidia_available() -> bool:
    return shutil.which("nvidia-smi") is not None


def _parse_nvidia_memory() -> dict:
    """Parse VRAM from nvidia-smi."""
    if not _nvidia_available():
        return {"vram_total_mb": 0, "vram_used_mb": 0, "vram_free_mb": 0}
    out = _run([
        "nvidia-smi",
        "--query-gpu=memory.total,memory.used,memory.free",
        "--format=csv,noheader,nounits",
    ])
    if not out:
        return {"vram_total_mb": 0, "vram_used_mb": 0, "vram_free_mb": 0}
    parts = out.splitlines()[0].split(",")
    try:
        total, used, free = (int(p.strip()) for p in parts[:3])
    except (ValueError, IndexError):
        return {"vram_total_mb": 0, "vram_used_mb": 0, "vram_free_mb": 0}
    return {"vram_total_mb": total, "vram_used_mb": used, "vram_free_mb": free}


def _parse_gpu_processes() -> list[dict]:
    """List GPU processes from nvidia-smi full output.
    Uses full nvidia-smi (not --query-compute-apps which misses some processes)."""
    if not _nvidia_available():
        return []
    # Full nvidia-smi output reliably shows all GPU processes
    out = _run(["nvidia-smi"])
    if not out:
        return []
    processes = []
    # Parse the "Processes:" table at the bottom of nvidia-smi output
    in_processes = False
    for line in out.splitlines():
        if "Processes:" in line:
            in_processes = True
            continue
        if not in_processes:
            continue
        # Process lines look like: |    0   N/A  N/A    12345    C   python3    15000MiB |
        m = re.search(r'\|\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\S+\s+(\S+)\s+(\d+)\s*MiB\s*\|', line)
        if m:
            processes.append({
                "pid": int(m.group(1)),
                "name": m.group(2),
                "vram_mb": int(m.group(3)),
            })
    # Fallback: also try the query API in case full parse missed something
    if not processes:
        out2 = _run([
            "nvidia-smi",
            "--query-compute-apps=pid,process_name,used_memory",
            "--format=csv,noheader,nounits",
        ])
        if out2:
            for line in out2.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    try:
                        processes.append({
                            "pid": int(parts[0]),
                            "name": parts[1],
                            "vram_mb": int(parts[2]),
                        })
                    except ValueError:
                        continue
    return processes


def _parse_ram() -> dict:
    """Parse RAM from free -m."""
    out = _run(["free", "-m"])
    if not out:
        return {"ram_total_mb": 0, "ram_used_mb": 0, "ram_free_mb": 0}
    for line in out.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            total = int(parts[1])
            # Prefer 'available' column (index 6) over raw 'free'
            if len(parts) >= 7:
                available = int(parts[6])
            else:
                available = int(parts[3])
            used = total - available
            return {"ram_total_mb": total, "ram_used_mb": used, "ram_free_mb": available}
    return {"ram_total_mb": 0, "ram_used_mb": 0, "ram_free_mb": 0}


def _parse_disk() -> dict:
    """Parse disk usage from df -BG /home."""
    out = _run(["df", "-BG", "/home"])
    if not out:
        return {"disk_total_gb": 0, "disk_used_gb": 0, "disk_free_gb": 0}
    lines = out.splitlines()
    if len(lines) < 2:
        return {"disk_total_gb": 0, "disk_used_gb": 0, "disk_free_gb": 0}
    parts = lines[1].split()
    try:
        total = int(parts[1].rstrip("G"))
        used = int(parts[2].rstrip("G"))
        free = int(parts[3].rstrip("G"))
        return {"disk_total_gb": total, "disk_used_gb": used, "disk_free_gb": free}
    except (IndexError, ValueError):
        return {"disk_total_gb": 0, "disk_used_gb": 0, "disk_free_gb": 0}


def _check_ports() -> dict:
    """Check which known ports are active. Returns {port: service_name} for active ones."""
    active = {}
    for port, service in PORT_SERVICES.items():
        # Try ss first, fall back to lsof
        out = _run(["ss", "-tlnp", f"sport = :{port}"])
        if out and str(port) in out:
            active[port] = service
            continue
        out = _run(["lsof", "-i", f":{port}", "-sTCP:LISTEN"])
        if out and str(port) in out:
            active[port] = service
    return active


def _get_load_avg() -> str:
    """Return system load average string."""
    try:
        load1, load5, load15 = os.getloadavg()
        return f"{load1:.2f} {load5:.2f} {load15:.2f}"
    except OSError:
        return "N/A"


def _get_process_count() -> int:
    """Return total number of running processes."""
    out = _run(["ps", "aux", "--no-headers"])
    if not out:
        return 0
    return len(out.splitlines())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_status() -> dict:
    """Full system status snapshot."""
    mem = _parse_nvidia_memory()
    ram = _parse_ram()
    disk = _parse_disk()
    gpu_procs = _parse_gpu_processes()
    ports = _check_ports()
    load = _get_load_avg()
    proc_count = _get_process_count()

    return {
        **mem,
        **ram,
        **disk,
        "gpu_processes": gpu_procs,
        "ports": ports,
        "process_count": proc_count,
        "load_avg": load,
    }


def can_i_use(
    vram_needed_mb: int = 0,
    ram_needed_mb: int = 0,
    disk_needed_gb: int = 0,
) -> tuple[bool, str]:
    """
    Check whether requested resources are available after safety margins.
    Safety margins: 2 GB VRAM, 3 GB RAM, 20 GB disk.
    Returns (ok, reason_string).
    """
    status = get_status()
    issues = []

    if vram_needed_mb > 0:
        free = status["vram_free_mb"]
        needed_total = vram_needed_mb + VRAM_HEADROOM_MB
        if free < needed_total:
            issues.append(
                f"Only {free / 1024:.1f}GB VRAM free, "
                f"need {vram_needed_mb / 1024:.1f}GB + {VRAM_HEADROOM_MB / 1024:.0f}GB safety"
            )

    if ram_needed_mb > 0:
        free = status["ram_free_mb"]
        needed_total = ram_needed_mb + RAM_HEADROOM_MB
        if free < needed_total:
            issues.append(
                f"Only {free / 1024:.1f}GB RAM free, "
                f"need {ram_needed_mb / 1024:.1f}GB + {RAM_HEADROOM_MB / 1024:.0f}GB safety"
            )

    if disk_needed_gb > 0:
        free = status["disk_free_gb"]
        needed_total = disk_needed_gb + DISK_HEADROOM_GB
        if free < needed_total:
            issues.append(
                f"Only {free}GB disk free, "
                f"need {disk_needed_gb}GB + {DISK_HEADROOM_GB}GB safety"
            )

    if issues:
        return False, "; ".join(issues)
    return True, "Resources available"


def safe_to_load_model(model_size_gb: float) -> bool:
    """Shorthand: check if VRAM is sufficient to load a model of given size in GB."""
    ok, _ = can_i_use(vram_needed_mb=int(model_size_gb * 1024))
    return ok


def kill_port(port: int) -> str:
    """Kill whatever process is listening on the given port."""
    # Try lsof first for clean PID extraction
    out = _run(["lsof", "-t", f"-i:{port}"])
    if out:
        pids = [p.strip() for p in out.splitlines() if p.strip()]
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except (ProcessLookupError, ValueError, PermissionError):
                pass
        return f"Killed PID(s) {', '.join(pids)} on port {port}"

    # Fallback: try ss + regex PID extraction
    out = _run(["ss", "-tlnp", f"sport = :{port}"])
    if not out or str(port) not in out:
        return f"Nothing running on port {port}"
    pids = re.findall(r"pid=(\d+)", out)
    if not pids:
        return f"Port {port} is active but could not extract PID"
    for pid in set(pids):
        try:
            os.kill(int(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
    return f"Killed PID(s) {', '.join(sorted(set(pids)))} on port {port}"


def report() -> str:
    """Short formatted summary suitable for Telegram (5-6 lines)."""
    s = get_status()
    gpu_tag = "NO GPU" if s["vram_total_mb"] == 0 else (
        f"{s['vram_used_mb']}/{s['vram_total_mb']}MB"
    )
    active_ports = ", ".join(
        f"{p}:{n}" for p, n in sorted(s["ports"].items())
    ) or "none"
    gpu_procs = len(s["gpu_processes"])

    lines = [
        f"GPU: {gpu_tag} | RAM: {s['ram_used_mb']}/{s['ram_total_mb']}MB",
        f"Disk: {s['disk_used_gb']}/{s['disk_total_gb']}GB",
        f"Load: {s['load_avg']} | Procs: {s['process_count']}",
        f"GPU procs: {gpu_procs}",
        f"Ports: {active_ports}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    if not args:
        print(report())
        return

    cmd = args[0]

    if cmd == "check":
        vram = int(args[1]) if len(args) > 1 else 0
        ram = int(args[2]) if len(args) > 2 else 0
        disk = int(args[3]) if len(args) > 3 else 0
        ok, reason = can_i_use(vram, ram, disk)
        status_label = "OK" if ok else "FAIL"
        print(f"[{status_label}] {reason}")
        sys.exit(0 if ok else 1)

    if cmd == "status":
        print(json.dumps(get_status(), indent=2))
        return

    if cmd == "kill" and len(args) > 1:
        print(kill_port(int(args[1])))
        return

    print(f"Usage: {sys.argv[0]} [check VRAM_MB RAM_MB [DISK_GB] | status | kill PORT]")
    sys.exit(1)


if __name__ == "__main__":
    main()
