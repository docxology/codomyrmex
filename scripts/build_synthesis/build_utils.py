#!/usr/bin/env python3
"""
Build synthesis utilities.

Usage:
    python build_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
from datetime import datetime


def find_build_files() -> list:
    """Find build configuration files."""
    patterns = [
        "Makefile",
        "pyproject.toml",
        "setup.py",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "build.gradle",
        "pom.xml",
        "CMakeLists.txt",
    ]
    
    found = []
    for p in patterns:
        if Path(p).exists():
            found.append(p)
    
    return found


def get_build_info() -> dict:
    """Get build environment info."""
    info = {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Check for common build tools
    tools = ["make", "pip", "npm", "cargo", "go", "gradle", "maven"]
    info["tools"] = {}
    
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                info["tools"][tool] = result.stdout.split("\n")[0][:40]
        except:
            pass
    
    return info


def main():
    parser = argparse.ArgumentParser(description="Build utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Info command
    subparsers.add_parser("info", help="Show build info")
    
    # Find command
    subparsers.add_parser("find", help="Find build files")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔨 Build Utilities\n")
        print("Commands:")
        print("  info - Show build environment info")
        print("  find - Find build configuration files")
        return 0
    
    if args.command == "info":
        info = get_build_info()
        print("🔨 Build Environment:\n")
        print(f"   Python: {info['python']}")
        print(f"   Platform: {info['platform']}")
        
        if info["tools"]:
            print("\n   Available tools:")
            for tool, version in info["tools"].items():
                print(f"      ✅ {tool}: {version}")
    
    elif args.command == "find":
        files = find_build_files()
        print(f"📋 Build Files ({len(files)}):\n")
        for f in files:
            print(f"   📄 {f}")
        
        if not files:
            print("   No build files found")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
