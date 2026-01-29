#!/usr/bin/env python3
"""
Display and manage configuration values.

Usage:
    python config_viewer.py [--path PATH] [--key KEY] [--format FORMAT]
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
import os


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        return {"error": "PyYAML not installed"}


def load_toml(path: Path) -> dict:
    """Load TOML file."""
    try:
        import tomllib
    except ImportError:
        try:
            import toml as tomllib
        except ImportError:
            return {"error": "tomllib not available"}
    
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config(path: Path) -> dict:
    """Load config file based on extension."""
    suffix = path.suffix.lower()
    
    if suffix == ".json":
        with open(path) as f:
            return json.load(f)
    elif suffix in [".yaml", ".yml"]:
        return load_yaml(path)
    elif suffix == ".toml":
        return load_toml(path)
    elif suffix == ".env":
        config = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip('"\'')
        return config
    else:
        raise ValueError(f"Unknown format: {suffix}")


def find_config_files(base_path: str = ".") -> list:
    """Find common config files."""
    patterns = [
        "*.yaml", "*.yml", "*.json", "*.toml", ".env",
        "config/*.yaml", "config/*.json", ".codomyrmex/*.yaml"
    ]
    found = []
    root = Path(base_path)
    
    for pattern in patterns:
        found.extend(root.glob(pattern))
    
    # Filter out package-lock and node_modules
    return [f for f in found if "node_modules" not in str(f) and "package-lock" not in f.name]


def get_nested_value(data: dict, key: str):
    """Get nested value using dot notation."""
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def main():
    parser = argparse.ArgumentParser(description="View configuration files")
    parser.add_argument("--path", "-p", default=None, help="Config file path")
    parser.add_argument("--key", "-k", default=None, help="Specific key to display (dot notation)")
    parser.add_argument("--list", "-l", action="store_true", help="List config files")
    parser.add_argument("--format", "-f", choices=["json", "yaml", "table"], default="json")
    parser.add_argument("--env", "-e", action="store_true", help="Show environment variables")
    args = parser.parse_args()
    
    if args.env:
        print("🔧 Environment Variables:\n")
        for key in sorted(os.environ.keys()):
            if any(x in key.upper() for x in ["CONFIG", "PATH", "DATABASE", "API", "SECRET", "KEY"]):
                value = os.environ[key]
                if "SECRET" in key.upper() or "KEY" in key.upper() or "PASSWORD" in key.upper():
                    value = value[:4] + "..." if len(value) > 4 else "***"
                print(f"   {key}={value[:60]}")
        return 0
    
    if args.list:
        files = find_config_files()
        print(f"📋 Config files found ({len(files)}):\n")
        for f in files[:20]:
            print(f"   📄 {f}")
        return 0
    
    if not args.path:
        print("🔧 Configuration Viewer\n")
        print("Usage:")
        print("  python config_viewer.py --path config.yaml")
        print("  python config_viewer.py --path config.yaml --key database.host")
        print("  python config_viewer.py --list")
        print("  python config_viewer.py --env")
        return 0
    
    config_path = Path(args.path)
    if not config_path.exists():
        print(f"❌ File not found: {args.path}")
        return 1
    
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return 1
    
    if "error" in config:
        print(f"❌ {config['error']}")
        return 1
    
    print(f"📄 Config: {config_path.name}\n")
    
    if args.key:
        value = get_nested_value(config, args.key)
        if value is not None:
            print(f"   {args.key} = {json.dumps(value, indent=2)}")
        else:
            print(f"   Key not found: {args.key}")
        return 0
    
    if args.format == "table":
        def print_flat(d, prefix=""):
            for k, v in d.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    print_flat(v, key)
                else:
                    print(f"   {key} = {v}")
        print_flat(config)
    else:
        print(json.dumps(config, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
