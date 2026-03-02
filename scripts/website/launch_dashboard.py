#!/usr/bin/env python3
"""
Dashboard Launcher Script

Starts the Codomyrmex Website Server for local development and review.
Usage: python scripts/launch_dashboard.py [--port 8787] [--open]
"""

import argparse
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    # Add src to sys.path if running from source without install
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.website import DataProvider, WebsiteServer, WebsiteGenerator

def parse_args():
    parser = argparse.ArgumentParser(description="Launch Codomyrmex Dashboard")
    parser.add_argument("--port", type=int, default=8787, help="Port to serve on")
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(level="INFO")
    
    # Determine project root
    project_root = Path(__file__).resolve().parent.parent
    print_info(f"Project Root: {project_root}")

    # 1. Auto-Generate Dashboard
    print_info("Generating dashboard static files...")
    try:
        output_dir = project_root / "output/website"
        generator = WebsiteGenerator(output_dir=output_dir, root_dir=project_root)
        generator.generate()
        print_success(f"Dashboard generated in {output_dir}")
    except Exception as e:
        print_error(f"Failed to generate dashboard: {e}")
        print_info("Attempting to proceed with existing files (if any)...")

    # 2. Create Root Redirect
    # This ensures http://localhost:8787/ redirects to the actual dashboard
    index_file = project_root / "index.html"
    try:
        # Simple HTML redirect
        redirect_content = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=/output/website/index.html">
    <title>Redirecting to Dashboard...</title>
</head>
<body>
    <p>Redirecting to <a href="/output/website/index.html">Codomyrmex Dashboard</a>...</p>
</body>
</html>
"""
        index_file.write_text(redirect_content.strip())
        print_success(f"Created root redirect at {index_file}")
    except Exception as e:
        print_error(f"Failed to create root redirect: {e}")

    # Initialize Data Provider
    print_info("Initializing Data Provider...")
    try:
        data_provider = DataProvider(root_dir=project_root)
        summary = data_provider.get_system_summary()
        print_success(f"System loaded. Environment: {summary.get('environment', 'unknown')}")
        print_info(f"Loaded {len(data_provider.get_modules())} modules.")
    except Exception as e:
        print_error(f"Failed to initialize DataProvider: {e}")
        return 1

    # Configure WebsiteServer
    WebsiteServer.root_dir = project_root
    WebsiteServer.data_provider = data_provider

    # Start Server
    print_info(f"Starting server at http://localhost:{args.port}...")
    
    try:
        max_retries = 10
        for attempt in range(max_retries):
            try:
                # Create server with allow_reuse_address to avoid "Address already in use" on restarts
                socketserver.TCPServer.allow_reuse_address = True
                with socketserver.TCPServer((args.host, args.port), WebsiteServer) as httpd:
                    if args.open:
                        threading.Thread(target=lambda p=args.port: (time.sleep(1), webbrowser.open(f"http://localhost:{p}"))).start()
                    
                    print_success(f"Dashboard active at http://localhost:{args.port}")
                    print_info("Press Ctrl+C to stop.")
                    httpd.serve_forever()
                break # successful exit
            except OSError as e:
                if e.errno == 48: # Address already in use
                    if attempt < max_retries - 1:
                        print_error(f"Could not bind to port {args.port}: [Errno 48] Address already in use")
                        args.port += 1
                        print_info(f"Trying port {args.port}...")
                    else:
                        print_error(f"Could not bind to port {args.port}: [Errno 48] Address already in use (max retries reached)")
                        return 1
                else:
                    print_error(f"Could not bind to port {args.port}: {e}")
                    return 1
    except KeyboardInterrupt:
        print_info("\nServer stopped by user.")
    except Exception as e:
        print_error(f"Server error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
