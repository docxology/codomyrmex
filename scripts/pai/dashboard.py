#!/usr/bin/env python3
"""
PAI Dashboard Orchestrator
==========================
Single entry point for setting up, restarting, and launching the
Codomyrmex PAI dashboard (port 8787).

Usage:
    python scripts/pai/dashboard.py              # setup + start + open browser
    python scripts/pai/dashboard.py --restart    # kill existing + setup + start + open
    python scripts/pai/dashboard.py --no-open    # setup + start, skip browser
    python scripts/pai/dashboard.py --setup-only # generate files only, no server
    python scripts/pai/dashboard.py --port 8080  # use alternate port
"""

import argparse
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
    """Kill all processes listening on *port*. Returns True if any were killed."""
    pids = _pids_on_port(port)
    if not pids:
        return False
    for pid in pids:
        try:
            import os
            os.kill(pid, signal.SIGTERM)
            print_info(f"Sent SIGTERM to PID {pid} (was on :{port})")
        except ProcessLookupError:
            pass
    # Brief wait, then SIGKILL anything still alive
    time.sleep(0.8)
    for pid in _pids_on_port(port):
        try:
            import os
            os.kill(pid, signal.SIGKILL)
            print_info(f"Sent SIGKILL to PID {pid} (did not exit cleanly)")
        except ProcessLookupError:
            pass
    return True


# ── phases ────────────────────────────────────────────────────────────────────

def phase_setup(project_root: Path) -> bool:
    """Generate dashboard static files. Returns True on success."""
    print_info("=== SETUP: Generating dashboard static files ===")
    try:
        output_dir = project_root / "output" / "website"
        generator = WebsiteGenerator(output_dir=output_dir, root_dir=project_root)
        generator.generate()
        print_success(f"Dashboard generated → {output_dir}")
    except Exception as exc:
        print_error(f"Generation failed: {exc}")
        print_info("Attempting to proceed with existing files (if any)...")

    # Ensure root index.html redirects to dashboard
    index_file = project_root / "index.html"
    try:
        index_file.write_text(
            "<!DOCTYPE html>\n"
            "<html><head>\n"
            '  <meta http-equiv="refresh" content="0; url=/output/website/index.html">\n'
            "  <title>Redirecting…</title>\n"
            "</head><body>\n"
            '  <p>Redirecting to <a href="/output/website/index.html">Codomyrmex Dashboard</a>…</p>\n'
            "</body></html>\n"
        )
        print_success(f"Root redirect written → {index_file}")
    except Exception as exc:
        print_error(f"Could not write root redirect: {exc}")
        return False
    return True


def phase_restart(port: int) -> None:
    """Kill any existing process on *port*."""
    print_info(f"=== RESTART: Stopping any process on :{port} ===")
    killed = kill_port(port)
    if killed:
        print_success(f"Cleared :{port}")
        time.sleep(0.3)  # Let OS reclaim the port
    else:
        print_info(f"No existing process found on :{port}")


def phase_run(project_root: Path, port: int, host: str, open_browser: bool) -> int:
    """Initialise DataProvider and serve forever. Returns exit code."""
    print_info("=== RUN: Starting PAI dashboard server ===")

    # Initialise data provider
    try:
        data_provider = DataProvider(root_dir=project_root)
        summary = data_provider.get_system_summary()
        print_success(f"DataProvider ready — environment: {summary.get('environment', 'unknown')}")
        print_info(f"Modules loaded: {len(data_provider.get_modules())}")
    except Exception as exc:
        print_error(f"DataProvider init failed: {exc}")
        return 1

    WebsiteServer.root_dir = project_root
    WebsiteServer.data_provider = data_provider

    # Bind server — try up to 3 ports if first is still busy
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer((host, port), WebsiteServer) as httpd:
                url = f"http://localhost:{port}/output/website/index.html"
                print_success(f"Dashboard live → {url}")
                print_info("Press Ctrl+C to stop.\n")

                if open_browser:
                    def _open():
                        time.sleep(1.2)
                        webbrowser.open(url)
                    threading.Thread(target=_open, daemon=True).start()

                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print_info("\nStopped by user.")
                return 0
        except OSError as exc:
            if exc.errno == 48 and attempt < max_attempts - 1:  # Address already in use
                print_error(f"Port {port} still in use, trying {port + 1}…")
                port += 1
            else:
                print_error(f"Cannot bind to :{port}: {exc}")
                return 1

    print_error("Could not find a free port. Use --restart to clear the existing process.")
    return 1


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PAI Dashboard Orchestrator — setup, restart, and launch Codomyrmex dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--port",       type=int, default=8787,   help="Port to serve on (default: 8787)")
    parser.add_argument("--host",       default="0.0.0.0",        help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--restart",    action="store_true",       help="Kill existing server before starting")
    parser.add_argument("--no-open",    action="store_true",       help="Do not open browser automatically")
    parser.add_argument("--setup-only", action="store_true",       help="Generate files only, do not start server")
    parser.add_argument("--no-setup",   action="store_true",       help="Skip generation, just (re)start the server")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(level="INFO")

    print_info(f"PAI Dashboard Orchestrator — project root: {_PROJECT_ROOT}")

    # Phase 1: restart (optional)
    if args.restart:
        phase_restart(args.port)

    # Phase 2: setup (optional skip)
    if not args.no_setup:
        ok = phase_setup(_PROJECT_ROOT)
        if not ok and args.setup_only:
            return 1

    if args.setup_only:
        print_success("Setup complete. Run without --setup-only to start the server.")
        return 0

    # Phase 3: run
    return phase_run(
        project_root=_PROJECT_ROOT,
        port=args.port,
        host=args.host,
        open_browser=not args.no_open,
    )


if __name__ == "__main__":
    sys.exit(main())
