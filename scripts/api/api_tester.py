#!/usr/bin/env python3
"""
API testing and exploration utilities.

Usage:
    python api_tester.py <url> [--method METHOD] [--data DATA]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import urllib.request
import urllib.error
import time


def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None) -> dict:
    """Make HTTP request."""
    headers = headers or {}
    headers.setdefault("Content-Type", "application/json")
    headers.setdefault("User-Agent", "codomyrmex-api-tester/1.0")
    
    body = json.dumps(data).encode() if data else None
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            elapsed = time.time() - start
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": response.read().decode(),
                "time_ms": int(elapsed * 1000),
            }
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        return {
            "status": e.code,
            "error": str(e.reason),
            "body": e.read().decode() if e.fp else "",
            "time_ms": int(elapsed * 1000),
        }
    except urllib.error.URLError as e:
        return {"status": 0, "error": str(e.reason)}


def format_json(text: str) -> str:
    """Format JSON for display."""
    try:
        data = json.loads(text)
        return json.dumps(data, indent=2)
    except:
        return text


def main():
    parser = argparse.ArgumentParser(description="API testing utility")
    parser.add_argument("url", nargs="?", help="URL to test")
    parser.add_argument("--method", "-m", default="GET", choices=["GET", "POST", "PUT", "DELETE", "PATCH"])
    parser.add_argument("--data", "-d", default=None, help="Request body as JSON")
    parser.add_argument("--header", "-H", action="append", help="Headers (Key: Value)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if not args.url:
        print("🌐 API Tester\n")
        print("Usage:")
        print("  python api_tester.py https://api.example.com/endpoint")
        print("  python api_tester.py https://api.example.com/data -m POST -d '{\"key\":\"value\"}'")
        print("  python api_tester.py https://api.example.com -H 'Authorization: Bearer token'")
        return 0
    
    # Parse headers
    headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()
    
    # Parse data
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON data: {args.data}")
            return 1
    
    print(f"🌐 {args.method} {args.url}\n")
    
    result = make_request(args.url, args.method, data, headers)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result.get("status", 0) < 400 else 1
    
    # Status
    status = result.get("status", 0)
    if status >= 200 and status < 300:
        print(f"✅ Status: {status}")
    elif status >= 400:
        print(f"❌ Status: {status}")
    else:
        print(f"⚠️  Status: {status}")
    
    if "time_ms" in result:
        print(f"⏱️  Time: {result['time_ms']} ms")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    
    # Body
    body = result.get("body", "")
    if body:
        print("\n📄 Response:")
        formatted = format_json(body)
        lines = formatted.split("\n")
        for line in lines[:30]:
            print(f"   {line}")
        if len(lines) > 30:
            print(f"   ... ({len(lines) - 30} more lines)")
    
    return 0 if status >= 200 and status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
