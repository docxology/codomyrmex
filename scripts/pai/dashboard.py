#!/usr/bin/env python3
"""
PAI Dashboard Orchestrator
==========================
Launches BOTH PAI interfaces in one command:

  🚀 PAI Project Manager  → http://localhost:8888  (primary)
     Missions, projects, tasks, Kanban, Gantt, GitHub sync, AI agent dispatch
     Powered by: bun ~/.claude/skills/PAI/Tools/PMServer.ts

  ◆  Codomyrmex Admin     → http://localhost:8787  (secondary)
     Module health, MCP tools, trust gateway, system audit
     Powered by: Python WebsiteServer

Usage:
    python scripts/pai/dashboard.py              # start both + open PAI PM in browser
    python scripts/pai/dashboard.py --restart    # kill both ports, regenerate, restart
    python scripts/pai/dashboard.py --no-open    # start both, skip browser
    python scripts/pai/dashboard.py --setup-only # generate Codomyrmex files only
    python scripts/pai/dashboard.py --no-pai-pm  # skip PAI PM, only run Codomyrmex
    python scripts/pai/dashboard.py --no-setup   # skip file generation, just restart servers
"""

import argparse
import os
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure codomyrmex package is importable when run from any cwd
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

_PAI_PM_SERVER = Path.home() / ".claude" / "skills" / "PAI" / "Tools" / "PMServer.ts"
_PAI_PM_PORT   = 8888
_CODO_PORT     = 8787

try:
    from codomyrmex.utils.cli_helpers import print_error, print_info, print_success, setup_logging
    from codomyrmex.website import DataProvider, WebsiteGenerator, WebsiteServer
except ImportError as exc:
    print(f"[ERROR] Cannot import codomyrmex: {exc}", file=sys.stderr)
    print("[INFO]  Run: uv sync  (from project root)", file=sys.stderr)
    sys.exit(1)


# ── helpers ──────────────────────────────────────────────────────────────────

def _pids_on_port(port: int) -> list[int]:
    """Return PIDs listening on *port* (macOS/Linux, best-effort)."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
        return [int(p) for p in result.stdout.split() if p.strip().isdigit()]
    except Exception:
        return []


def kill_port(port: int) -> bool:
    """Kill all processes on *port*. Returns True if any were killed."""
    pids = _pids_on_port(port)
    if not pids:
        return False
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            print_info(f"  SIGTERM → PID {pid} (:{port})")
        except ProcessLookupError:
            pass
    time.sleep(0.8)
    for pid in _pids_on_port(port):
        try:
            os.kill(pid, signal.SIGKILL)
            print_info(f"  SIGKILL → PID {pid} (did not exit cleanly)")
        except ProcessLookupError:
            pass
    return True


def _port_is_live(port: int, timeout: float = 3.0) -> bool:
    """Return True if something responds on *port* within *timeout* seconds."""
    import socket
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return True
        except OSError:
            time.sleep(0.2)
    return False


# ── phases ────────────────────────────────────────────────────────────────────

def phase_restart(ports: list[int]) -> None:
    """Kill any existing process on each port."""
    print_info(f"=== RESTART: Clearing ports {', '.join(f':{p}' for p in ports)} ===")
    for port in ports:
        killed = kill_port(port)
        if killed:
            print_success(f"  Cleared :{port}")
        else:
            print_info(f"  Nothing found on :{port}")
    time.sleep(0.3)


def phase_setup(project_root: Path) -> bool:
    """Generate Codomyrmex dashboard static files. Returns True on success."""
    print_info("=== SETUP: Generating Codomyrmex dashboard static files ===")
    try:
        output_dir = project_root / "output" / "website"
        generator = WebsiteGenerator(output_dir=output_dir, root_dir=project_root)
        generator.generate()
        print_success(f"  Dashboard generated → {output_dir}")
    except Exception as exc:
        print_error(f"  Generation failed: {exc}")
        print_info("  Attempting to proceed with existing files (if any)...")

    index_file = project_root / "index.html"
    try:
        index_file.write_text(
            "<!DOCTYPE html>\n"
            "<html><head>\n"
            '  <meta http-equiv="refresh" content="0; url=/output/website/index.html">\n'
            "  <title>Redirecting…</title>\n"
            "</head><body>\n"
            '  <p><a href="/output/website/index.html">Codomyrmex Dashboard</a></p>\n'
            "</body></html>\n"
        )
        print_success(f"  Root redirect → {index_file}")
    except Exception as exc:
        print_error(f"  Could not write root redirect: {exc}")
        return False
    return True


def phase_pai_pm(restart: bool, port: int = _PAI_PM_PORT) -> subprocess.Popen | None:
    """
    Start the PAI Project Manager (PMServer.ts) in the background.
    Returns the Popen handle, or None if unavailable.
    """
    print_info(f"=== PAI PM: Starting PAI Project Manager on :{port} ===")

    bun = shutil.which("bun")
    if not bun:
        print_error("  'bun' not found — cannot start PAI PM.")
        print_info("  Install from https://bun.sh  then re-run.")
        return None

    if not _PAI_PM_SERVER.exists():
        print_error(f"  PMServer.ts not found at {_PAI_PM_SERVER}")
        return None

    if restart:
        killed = kill_port(port)
        if killed:
            print_success(f"  Cleared :{port}")
            time.sleep(0.3)

    proc = subprocess.Popen(
        [bun, str(_PAI_PM_SERVER), f"--port={port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print_info(f"  PAI PM process started (PID {proc.pid}) — waiting for :{port}…")

    if _port_is_live(port, timeout=8.0):
        print_success(f"  PAI Project Manager live → http://localhost:{port}")
    else:
        print_error(f"  PAI PM did not respond on :{port} within 8s — it may still be starting.")

    return proc


def phase_run_codo(project_root: Path, port: int, host: str, open_browser: bool,
                   pai_pm_port: int | None = None) -> int:
    """Initialise DataProvider and serve Codomyrmex dashboard. Returns exit code."""
    print_info(f"=== RUN: Starting Codomyrmex Admin on :{port} ===")

    try:
        data_provider = DataProvider(root_dir=project_root)
        summary = data_provider.get_system_summary()
        print_success(f"  DataProvider ready — {summary.get('environment', 'unknown')}")
        print_info(f"  Modules loaded: {len(data_provider.get_modules())}")
    except Exception as exc:
        print_error(f"  DataProvider init failed: {exc}")
        return 1

    WebsiteServer.root_dir = project_root
    WebsiteServer.data_provider = data_provider

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer((host, port), WebsiteServer) as httpd:
                codo_url = f"http://localhost:{port}/output/website/index.html"
                pm_url   = f"http://localhost:{pai_pm_port}" if pai_pm_port else None

                print_success(f"  Codomyrmex Admin  → {codo_url}")
                if pm_url:
                    print_success(f"  PAI Project Manager → {pm_url}  (primary)")
                print_info("  Press Ctrl+C to stop both servers.\n")

                if open_browser:
                    def _open_both():
                        time.sleep(1.2)
                        if pm_url:
                            webbrowser.open(pm_url)       # primary — opens first
                            time.sleep(0.4)
                        webbrowser.open(codo_url)         # secondary — opens in new tab
                    threading.Thread(target=_open_both, daemon=True).start()

                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print_info("\nStopped by user.")
                return 0
        except OSError as exc:
            if exc.errno == 48 and attempt < max_attempts - 1:
                print_error(f"  Port {port} busy, trying {port + 1}…")
                port += 1
            else:
                print_error(f"  Cannot bind to :{port}: {exc}")
                return 1

    print_error("Could not find a free port. Use --restart to clear existing processes.")
    return 1


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Dashboard Orchestrator — launch PAI PM (8888) + Codomyrmex Admin (8787)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--port",       type=int, default=_CODO_PORT,   help=f"Codomyrmex port (default: {_CODO_PORT})")
    parser.add_argument("--pm-port",    type=int, default=_PAI_PM_PORT, help=f"PAI PM port (default: {_PAI_PM_PORT})")
    parser.add_argument("--host",       default="0.0.0.0",              help="Codomyrmex bind host (default: 0.0.0.0)")
    parser.add_argument("--restart",    action="store_true",             help="Kill existing servers on both ports before starting")
    parser.add_argument("--no-open",    action="store_true",             help="Do not open browser automatically")
    parser.add_argument("--setup-only", action="store_true",             help="Generate Codomyrmex files only, do not start servers")
    parser.add_argument("--no-setup",   action="store_true",             help="Skip file generation, just (re)start servers")
    parser.add_argument("--no-pai-pm",  action="store_true",             help="Skip PAI PM (port 8888), only run Codomyrmex")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(level="INFO")

    print_info("PAI Dashboard Orchestrator")
    print_info(f"  Project root : {_PROJECT_ROOT}")
    print_info(f"  PAI PM       : http://localhost:{args.pm_port}  (primary)")
    print_info(f"  Codomyrmex   : http://localhost:{args.port}  (admin)")
    print_info("")

    # Phase 1: restart
    if args.restart:
        ports_to_clear = [args.port]
        if not args.no_pai_pm:
            ports_to_clear.append(args.pm_port)
        phase_restart(ports_to_clear)

    # Phase 2: setup Codomyrmex files
    if not args.no_setup:
        ok = phase_setup(_PROJECT_ROOT)
        if not ok and args.setup_only:
            return 1

    if args.setup_only:
        print_success("Setup complete. Run without --setup-only to start both servers.")
        return 0

    # Phase 3: start PAI PM in background
    pai_pm_proc: subprocess.Popen | None = None
    if not args.no_pai_pm:
        pai_pm_proc = phase_pai_pm(restart=args.restart, port=args.pm_port)

    # Phase 4: start Codomyrmex in foreground (blocks until Ctrl+C)
    exit_code = phase_run_codo(
        project_root=_PROJECT_ROOT,
        port=args.port,
        host=args.host,
        open_browser=not args.no_open,
        pai_pm_port=args.pm_port if (not args.no_pai_pm and pai_pm_proc) else None,
    )

    # Cleanup: terminate PAI PM when Codomyrmex exits
    if pai_pm_proc and pai_pm_proc.poll() is None:
        print_info("Stopping PAI Project Manager…")
        pai_pm_proc.terminate()
        try:
            pai_pm_proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            pai_pm_proc.kill()
        print_success("PAI PM stopped.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
