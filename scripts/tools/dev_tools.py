#!/usr/bin/env python3
"""
Development tools utilities.

Usage:
    python dev_tools.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
import shutil


def check_tool(name: str) -> dict:
    """Check if a development tool is installed."""
    path = shutil.which(name)
    if not path:
        return {"installed": False}
    
    info = {"installed": True, "path": path}
    
    # Try to get version
    version_flags = ["--version", "-V", "version"]
    for flag in version_flags:
        try:
            result = subprocess.run([name, flag], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                info["version"] = result.stdout.strip().split("\n")[0][:50]
                break
        except:
            continue
    
    return info


DEV_TOOLS = {
    "python": "Python interpreter",
    "pip": "Python package manager",
    "uv": "Fast Python package manager",
    "node": "Node.js runtime",
    "npm": "Node package manager",
    "docker": "Container runtime",
    "git": "Version control",
    "make": "Build automation",
    "curl": "HTTP client",
    "jq": "JSON processor",
    "ruff": "Python linter",
    "black": "Python formatter",
    "pytest": "Python testing",
    "cargo": "Rust package manager",
    "go": "Go compiler",
}


def main():
    parser = argparse.ArgumentParser(description="Development tools utilities")
    parser.add_argument("--check", "-c", action="store_true", help="Check all tools")
    parser.add_argument("--tool", "-t", help="Check specific tool")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if not args.check and not args.tool:
        print("🛠️  Development Tools\n")
        print("Usage:")
        print("  python dev_tools.py --check")
        print("  python dev_tools.py --tool python")
        print("\nChecked tools:")
        for name, desc in DEV_TOOLS.items():
            print(f"   {name:<10} - {desc}")
        return 0
    
    tools_to_check = {args.tool: ""} if args.tool else DEV_TOOLS
    results = {}
    
    print("🛠️  Tool Check\n")
    
    for name, desc in tools_to_check.items():
        info = check_tool(name)
        results[name] = info
        
        if not args.json:
            icon = "✅" if info["installed"] else "❌"
            version = info.get("version", "")
            print(f"   {icon} {name:<10} {version}")
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        installed = sum(1 for r in results.values() if r["installed"])
        print(f"\n   {installed}/{len(results)} tools installed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
