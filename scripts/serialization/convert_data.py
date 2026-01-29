#!/usr/bin/env python3
"""
Data serialization and format conversion utilities.

Usage:
    python convert_data.py <input> <output> [--format FORMAT]
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
import csv


def load_json(path: Path) -> any:
    with open(path) as f:
        return json.load(f)


def save_json(data: any, path: Path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_csv(path: Path) -> list:
    with open(path) as f:
        return list(csv.DictReader(f))


def save_csv(data: list, path: Path):
    if not data:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def load_yaml(path: Path) -> any:
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        raise ImportError("PyYAML not installed")


def save_yaml(data: any, path: Path):
    try:
        import yaml
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    except ImportError:
        raise ImportError("PyYAML not installed")


LOADERS = {".json": load_json, ".csv": load_csv, ".yaml": load_yaml, ".yml": load_yaml}
SAVERS = {".json": save_json, ".csv": save_csv, ".yaml": save_yaml, ".yml": save_yaml}


def main():
    parser = argparse.ArgumentParser(description="Convert data between formats")
    parser.add_argument("input", nargs="?", help="Input file")
    parser.add_argument("output", nargs="?", help="Output file")
    parser.add_argument("--format", "-f", choices=["json", "csv", "yaml"], help="Output format")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print output")
    args = parser.parse_args()
    
    if not args.input:
        print("🔄 Data Converter\n")
        print("Converts between JSON, CSV, and YAML formats.\n")
        print("Usage:")
        print("  python convert_data.py data.json data.csv")
        print("  python convert_data.py data.yaml data.json")
        print("  python convert_data.py data.csv data.yaml")
        return 0
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input not found: {args.input}")
        return 1
    
    # Determine formats
    input_ext = input_path.suffix.lower()
    if input_ext not in LOADERS:
        print(f"❌ Unsupported input format: {input_ext}")
        return 1
    
    if args.output:
        output_path = Path(args.output)
        output_ext = output_path.suffix.lower() if not args.format else f".{args.format}"
    else:
        output_path = None
        output_ext = None
    
    # Load
    print(f"📥 Loading: {input_path.name}")
    try:
        data = LOADERS[input_ext](input_path)
    except Exception as e:
        print(f"❌ Load error: {e}")
        return 1
    
    # Stats
    if isinstance(data, list):
        print(f"   Records: {len(data)}")
    elif isinstance(data, dict):
        print(f"   Keys: {len(data)}")
    
    # Save or print
    if output_path:
        if output_ext not in SAVERS:
            print(f"❌ Unsupported output format: {output_ext}")
            return 1
        
        print(f"📤 Saving: {output_path.name}")
        try:
            SAVERS[output_ext](data, output_path)
            print(f"✅ Converted to {output_ext}")
        except Exception as e:
            print(f"❌ Save error: {e}")
            return 1
    else:
        print("\n📄 Data preview:")
        print(json.dumps(data, indent=2)[:500])
        if len(json.dumps(data)) > 500:
            print("\n   ... (truncated)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
