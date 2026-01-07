#!/usr/bin/env python3
"""
Simple HTTP server to serve the generated website.
"""
import http.server
import socketserver
import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Serve the Codomyrmex website.")
    parser.add_argument(
        "--directory", "-d",
        type=str,
        default="./output/website",
        help="Directory containing the website to serve."
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to serve on."
    )
    
    args = parser.parse_args()
    
    # Project root is 2 levels up from scripts/website
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    
    from codomyrmex.website.server import WebsiteServer
    from codomyrmex.website.data_provider import DataProvider
    
    web_dir = Path(args.directory).resolve()
    
    if not web_dir.exists():
        print(f"Error: Directory {web_dir} does not exist. Run generate.py first.", file=sys.stderr)
        sys.exit(1)
        
    os.chdir(web_dir)
    
    # Configure Server
    WebsiteServer.root_dir = PROJECT_ROOT
    WebsiteServer.data_provider = DataProvider(PROJECT_ROOT)
    
    with socketserver.TCPServer(("", args.port), WebsiteServer) as httpd:
        print(f"Serving at http://localhost:{args.port}")
        print(f"Serving content from: {web_dir}")
        print("API endpoints active (/api/execute, /api/chat, /api/refresh)")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
