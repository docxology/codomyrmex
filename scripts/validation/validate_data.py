#!/usr/bin/env python3
"""
Validate data against schemas (JSON Schema, Pydantic models).

Usage:
    python validate_data.py <data_file> [--schema SCHEMA]
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


def validate_json_structure(data: dict) -> list:
    """Basic structural validation."""
    issues = []
    
    def check_node(node, path=""):
        if isinstance(node, dict):
            if not node:
                issues.append(f"{path or 'root'}: Empty object")
            for k, v in node.items():
                check_node(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            if not node:
                issues.append(f"{path}: Empty array")
            for i, item in enumerate(node):
                check_node(item, f"{path}[{i}]")
        elif node is None:
            issues.append(f"{path}: Null value")
    
    check_node(data)
    return issues


def validate_against_schema(data: dict, schema: dict) -> list:
    """Validate against JSON Schema."""
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        return [f"{'.'.join(str(p) for p in e.path)}: {e.message}" for e in errors]
    except ImportError:
        return ["jsonschema not installed - run: pip install jsonschema"]


def infer_types(data: dict, path: str = "") -> dict:
    """Infer type structure from data."""
    if isinstance(data, dict):
        return {k: infer_types(v, f"{path}.{k}") for k, v in data.items()}
    elif isinstance(data, list):
        if data:
            return [infer_types(data[0], f"{path}[]")]
        return ["unknown"]
    elif isinstance(data, str):
        return "string"
    elif isinstance(data, bool):
        return "boolean"
    elif isinstance(data, int):
        return "integer"
    elif isinstance(data, float):
        return "number"
    elif data is None:
        return "null"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Validate data files")
    parser.add_argument("data_file", nargs="?", help="JSON data file to validate")
    parser.add_argument("--schema", "-s", default=None, help="JSON Schema file")
    parser.add_argument("--infer", "-i", action="store_true", help="Infer and show type structure")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings")
    args = parser.parse_args()
    
    if not args.data_file:
        print("🔍 Data Validator\n")
        print("Usage:")
        print("  python validate_data.py data.json")
        print("  python validate_data.py data.json --schema schema.json")
        print("  python validate_data.py data.json --infer")
        return 0
    
    data_path = Path(args.data_file)
    if not data_path.exists():
        print(f"❌ File not found: {args.data_file}")
        return 1
    
    try:
        with open(data_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    
    print(f"📄 Validating: {data_path.name}\n")
    
    if args.infer:
        types = infer_types(data)
        print("📊 Inferred type structure:")
        print(json.dumps(types, indent=2))
        return 0
    
    issues = []
    warnings = []
    
    # Basic structure check
    struct_issues = validate_json_structure(data)
    warnings.extend(struct_issues)
    
    # Schema validation
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"❌ Schema not found: {args.schema}")
            return 1
        
        with open(schema_path) as f:
            schema = json.load(f)
        
        schema_issues = validate_against_schema(data, schema)
        issues.extend(schema_issues)
    
    # Results
    if issues:
        print(f"❌ Validation errors ({len(issues)}):")
        for issue in issues[:20]:
            print(f"   • {issue}")
        return 1
    
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"   • {w}")
        if args.strict:
            return 1
    
    print("✅ Validation passed")
    
    # Stats
    if isinstance(data, dict):
        print(f"   Keys: {len(data)}")
    elif isinstance(data, list):
        print(f"   Items: {len(data)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
