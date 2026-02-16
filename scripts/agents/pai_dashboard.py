#!/usr/bin/env python3
"""
PAI Dashboard Launcher — Open the PAI Control Center in your browser.

This is the primary entry point for visually interacting with the
Personal AI Infrastructure through the Codomyrmex dashboard.

Usage:
    python scripts/agents/pai_dashboard.py             # Launch PAI Awareness page
    python scripts/agents/pai_dashboard.py --all       # Launch main dashboard instead
    python scripts/agents/pai_dashboard.py --no-open   # Start server without browser
    python scripts/agents/pai_dashboard.py --port 9000 # Custom port

What it does:
    1. Auto-generates the dashboard HTML/CSS/JS
    2. Starts the Codomyrmex website server
    3. Opens your browser directly to the PAI Awareness page
    4. Serves the REST API (including /api/awareness)
"""

import argparse
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.website import DataProvider, WebsiteServer, WebsiteGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the PAI Control Center (Codomyrmex Dashboard → Awareness)",
    )
    parser.add_argument(
        "--port", type=int, default=8787,
        help="Port to serve on (default: 8787)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--no-open", action="store_true",
        help="Start server without opening the browser",
    )
    parser.add_argument(
        "--all", action="store_true", dest="open_main",
        help="Open the main dashboard instead of the PAI Awareness page",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(level="INFO")

    project_root = Path(__file__).resolve().parent.parent.parent
    print_info(f"Project Root: {project_root}")

    # ── 1. Auto-generate dashboard ────────────────────────────────────
    print_info("Generating dashboard...")
    output_dir = project_root / "output" / "website"
    try:
        generator = WebsiteGenerator(output_dir=output_dir, root_dir=project_root)
        generator.generate()
        print_success(f"Dashboard generated → {output_dir}")
    except Exception as e:
        print_error(f"Generation failed: {e}")
        print_info("Continuing with existing files...")

    # ── 2. Root redirect ──────────────────────────────────────────────
    index_file = project_root / "index.html"
    try:
        target = "awareness.html" if not args.open_main else "index.html"
        redirect_html = (
            '<!DOCTYPE html>\n<html>\n<head>\n'
            f'  <meta http-equiv="refresh" content="0; url=/output/website/{target}">\n'
            f'  <title>Redirecting to PAI Control Center...</title>\n'
            '</head>\n<body>\n'
            f'  <p>Redirecting to <a href="/output/website/{target}">PAI Control Center</a>...</p>\n'
            '</body>\n</html>'
        )
        index_file.write_text(redirect_html)
    except Exception as e:
        print_error(f"Failed to create redirect: {e}")

    # ── 3. Initialize data provider ───────────────────────────────────
    print_info("Initializing Data Provider...")
    try:
        data_provider = DataProvider(root_dir=project_root)
        summary = data_provider.get_system_summary()
        print_success(f"System loaded — {len(data_provider.get_modules())} modules")

        # Quick PAI status
        awareness = data_provider.get_pai_awareness_data()
        metrics = awareness.get("metrics", {})
        print_info(
            f"PAI: {metrics.get('mission_count', 0)} missions, "
            f"{metrics.get('project_count', 0)} projects, "
            f"{metrics.get('overall_completion', 0)}% complete"
        )
    except Exception as e:
        print_error(f"DataProvider init failed: {e}")
        return 1

    # ── 4. Configure & start server ───────────────────────────────────
    WebsiteServer.root_dir = project_root
    WebsiteServer.data_provider = data_provider

    # Determine which page to open
    if args.open_main:
        url = f"http://localhost:{args.port}/output/website/index.html"
    else:
        url = f"http://localhost:{args.port}/output/website/awareness.html"

    print_info(f"Starting server at http://localhost:{args.port} ...")

    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer((args.host, args.port), WebsiteServer) as httpd:
            if not args.no_open:
                def _open_browser():
                    time.sleep(1.0)
                    webbrowser.open(url)
                threading.Thread(target=_open_browser, daemon=True).start()

            print_success(f"PAI Control Center active → {url}")
            print_info("Press Ctrl+C to stop.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print_info("\nServer stopped.")
    except OSError as e:
        print_error(f"Could not bind to port {args.port}: {e}")
        return 1
    except Exception as e:
        print_error(f"Server error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
