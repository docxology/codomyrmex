#!/usr/bin/env python3
"""
Validation Framework - Real Usage Examples

Demonstrates actual validation capabilities:
- Validator initialization
- Data validation against schemas
- ValidationResult and Error handling
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.validation import (
    Validator,
    is_valid
)

def main():
    setup_logging()
    print_info("Running Validation Examples...")

    # 1. Simple Validation
    print_info("Testing unified validate function...")
    try:
        data = {"name": "Test", "age": 30}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        if is_valid(data, schema):
            print_success("  Data validated successfully via is_valid.")
    except Exception as e:
        print_info(f"  Validation note: {e}")

    # 2. Validator Instance
    print_info("Testing Validator instance...")
    try:
        validator = Validator(validator_type="json_schema")
        print_success("  Validator instance initialized.")
    except Exception as e:
        print_error(f"  Validator failed: {e}")

    print_success("Validation examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
