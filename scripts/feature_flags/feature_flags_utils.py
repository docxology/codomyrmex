#!/usr/bin/env python3
"""
Feature flags management utilities.

Usage:
    python feature_flags.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import os


DEFAULT_FLAGS = {
    "new_dashboard": {"enabled": False, "description": "New dashboard UI"},
    "dark_mode": {"enabled": True, "description": "Dark mode support"},
    "experimental_api": {"enabled": False, "description": "Experimental API endpoints"},
    "cache_v2": {"enabled": True, "description": "New caching system"},
}


def load_flags(path: Path = None) -> dict:
    """Load feature flags from file or defaults."""
    if path and path.exists():
        return json.loads(path.read_text())
    
    # Check environment
    env_flags = {}
    for key, val in os.environ.items():
        if key.startswith("FF_") or key.startswith("FEATURE_"):
            flag_name = key.replace("FF_", "").replace("FEATURE_", "").lower()
            env_flags[flag_name] = {"enabled": val.lower() in ["true", "1", "yes"]}
    
    if env_flags:
        return {**DEFAULT_FLAGS, **env_flags}
    
    return DEFAULT_FLAGS


def save_flags(flags: dict, path: Path):
    """Save feature flags to file."""
    path.write_text(json.dumps(flags, indent=2))


def is_enabled(flags: dict, name: str) -> bool:
    """Check if a flag is enabled."""
    flag = flags.get(name, {})
    return flag.get("enabled", False)


def main():
    parser = argparse.ArgumentParser(description="Feature flags utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    list_cmd = subparsers.add_parser("list", help="List all flags")
    list_cmd.add_argument("--file", "-f", help="Flags file")
    
    # Get command
    get_cmd = subparsers.add_parser("get", help="Get flag status")
    get_cmd.add_argument("name", help="Flag name")
    
    # Set command
    set_cmd = subparsers.add_parser("set", help="Set flag")
    set_cmd.add_argument("name", help="Flag name")
    set_cmd.add_argument("value", choices=["on", "off"])
    set_cmd.add_argument("--file", "-f", default="feature_flags.json")
    
    # Create command
    create = subparsers.add_parser("create", help="Create flags file")
    create.add_argument("--output", "-o", default="feature_flags.json")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🚩 Feature Flags Utilities\n")
        print("Commands:")
        print("  list   - List all flags")
        print("  get    - Get flag status")
        print("  set    - Set flag on/off")
        print("  create - Create flags file")
        return 0
    
    if args.command == "list":
        path = Path(args.file) if args.file else None
        flags = load_flags(path)
        
        print("🚩 Feature Flags:\n")
        for name, config in flags.items():
            status = "✅ ON " if config.get("enabled") else "⚪ OFF"
            desc = config.get("description", "")
            print(f"   {status} {name}")
            if desc:
                print(f"         {desc}")
    
    elif args.command == "get":
        flags = load_flags()
        if args.name not in flags:
            print(f"❌ Unknown flag: {args.name}")
            return 1
        
        enabled = is_enabled(flags, args.name)
        status = "enabled" if enabled else "disabled"
        print(f"🚩 {args.name}: {status}")
    
    elif args.command == "set":
        path = Path(args.file)
        flags = load_flags(path if path.exists() else None)
        
        if args.name not in flags:
            flags[args.name] = {"description": ""}
        
        flags[args.name]["enabled"] = args.value == "on"
        save_flags(flags, path)
        
        print(f"✅ Set {args.name} = {args.value}")
    
    elif args.command == "create":
        save_flags(DEFAULT_FLAGS, Path(args.output))
        print(f"✅ Created: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
