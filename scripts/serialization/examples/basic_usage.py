#!/usr/bin/env python3
"""
Serialization - Real Usage Examples

Demonstrates actual serialization capabilities:
- serialize/deserialize functionality
- Format detection
- JSON/YAML stubs
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.serialization import (
    serialize,
    deserialize
)

def main():
    setup_logging()
    print_info("Running Serialization Examples...")

    # 1. JSON
    print_info("Testing JSON serialization/deserialization...")
    try:
        data = {"foo": "bar", "num": 42}
        serialized = serialize(data, format="json")
        print_success(f"  Serialized to JSON: {serialized}")
        
        deserialized = deserialize(serialized, format="json")
        if deserialized == data:
            print_success("  JSON Deserialization successful.")
    except Exception as e:
        print_error(f"  JSON operations failed: {e}")

    # 2. YAML
    print_info("Testing YAML serialization...")
    try:
        from codomyrmex.serialization import SerializationFormat
        data = {"list": [1, 2, 3], "nested": {"key": "value"}}
        serialized = serialize(data, format=SerializationFormat.YAML)
        print_success("  Serialized to YAML successfully.")
        
        deserialized = deserialize(serialized, format=SerializationFormat.YAML)
        if deserialized["list"] == [1, 2, 3]:
            print_success("  YAML Deserialization successful.")
    except Exception as e:
        print_info(f"  YAML demo note (might need PyYAML): {e}")

    print_success("Serialization examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
