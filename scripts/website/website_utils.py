#!/usr/bin/env python3
"""
Website development and management utilities.

Usage:
    python website_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
import http.server
import socketserver
import os


def find_html_files(path: str = ".") -> list:
    """Find HTML files."""
    p = Path(path)
    return list(p.rglob("*.html"))


def analyze_html(path: Path) -> dict:
    """Analyze HTML file."""
    with open(path) as f:
        content = f.read()
    
    info = {
        "path": str(path),
        "size": len(content),
        "has_doctype": content.lower().startswith("<!doctype"),
        "title": "",
        "links": 0,
        "images": 0,
        "scripts": 0,
        "styles": 0,
    }
    
    # Extract title
    match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
    if match:
        info["title"] = match.group(1)
    
    info["links"] = len(re.findall(r'<a\s', content, re.IGNORECASE))
    info["images"] = len(re.findall(r'<img\s', content, re.IGNORECASE))
    info["scripts"] = len(re.findall(r'<script', content, re.IGNORECASE))
    info["styles"] = len(re.findall(r'<link.*stylesheet|<style', content, re.IGNORECASE))
    
    return info


def check_broken_links(path: Path) -> list:
    """Check for potentially broken internal links."""
    with open(path) as f:
        content = f.read()
    
    broken = []
    base = path.parent
    
    # Find href and src attributes
    links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', content)
    
    for link in links:
        if link.startswith(("http://", "https://", "#", "mailto:", "tel:", "javascript:")):
            continue
        
        link_path = base / link.split("?")[0].split("#")[0]
        if not link_path.exists():
            broken.append(link)
    
    return broken


def main():
    parser = argparse.ArgumentParser(description="Website utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze HTML files")
    analyze.add_argument("path", nargs="?", default=".", help="Path to analyze")
    
    # Check links command
    check = subparsers.add_parser("check-links", help="Check for broken links")
    check.add_argument("path", nargs="?", default=".", help="Path to check")
    
    # Serve command
    serve = subparsers.add_parser("serve", help="Start development server")
    serve.add_argument("--port", "-p", type=int, default=8000)
    serve.add_argument("--dir", "-d", default=".")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🌐 Website Utilities\n")
        print("Commands:")
        print("  analyze     - Analyze HTML files")
        print("  check-links - Check for broken links")
        print("  serve       - Start development server")
        return 0
    
    if args.command == "analyze":
        files = find_html_files(args.path)
        print(f"📄 HTML Files ({len(files)}):\n")
        
        for f in files[:20]:
            info = analyze_html(f)
            title = info["title"] or "(no title)"
            print(f"   📄 {f.name}: {title}")
            print(f"      Links: {info['links']}, Images: {info['images']}, Scripts: {info['scripts']}")
    
    elif args.command == "check-links":
        files = find_html_files(args.path)
        total_broken = 0
        
        print(f"🔍 Checking links in {len(files)} files...\n")
        
        for f in files[:30]:
            broken = check_broken_links(f)
            if broken:
                total_broken += len(broken)
                print(f"   ⚠️  {f.name}: {len(broken)} broken")
                for link in broken[:3]:
                    print(f"      - {link}")
        
        if total_broken == 0:
            print("   ✅ No broken links found")
        else:
            print(f"\n   Found {total_broken} potentially broken links")
    
    elif args.command == "serve":
        os.chdir(args.dir)
        handler = http.server.SimpleHTTPRequestHandler
        
        print(f"🌐 Starting server at http://localhost:{args.port}")
        print(f"   Serving: {Path(args.dir).absolute()}")
        print("   Press Ctrl+C to stop\n")
        
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n   Server stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
