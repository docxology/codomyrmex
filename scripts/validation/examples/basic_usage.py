#!/usr/bin/env python3
"""
Validation Module - Real Usage Examples

Demonstrates actual validation capabilities:
- JSON Schema validation
- Custom validators
- Error handling and reporting
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


def main():
    setup_logging()
    print_info("Running Validation Module Examples...")

    try:
        from codomyrmex.validation import validate, is_valid, get_errors, Validator
        print_info("Successfully imported validation module")
    except ImportError as e:
        print_error(f"Could not import validation: {e}")
        return 1

    # Example 1: Define a JSON Schema
    print_info("Defining JSON Schema for user data...")
    user_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }
    print("  Schema defined with required fields: name, email")

    # Example 2: Validate correct data
    print_info("Validating correct user data...")
    valid_user = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
    }
    
    try:
        is_user_valid = is_valid(valid_user, user_schema)
        print(f"  Valid user data: {is_user_valid}")
    except Exception as e:
        print_info(f"  Validation demo: {e}")

    # Example 3: Validate incorrect data and get errors
    print_info("Validating incorrect user data...")
    invalid_user = {
        "name": "",  # Empty name (violates minLength)
        "age": 200,  # Age too high
        # Missing required email
    }
    
    try:
        errors = get_errors(invalid_user, user_schema)
        print(f"  Found {len(errors)} validation errors:")
        for error in errors[:3]:
            print(f"    - {error}")
    except Exception as e:
        print_info(f"  Error detection demo: {e}")

    # Example 4: Validator types available
    print_info("Available validator types:")
    print("  - json_schema: JSON Schema Draft 7 validation")
    print("  - pydantic: Pydantic model validation")
    print("  - custom: Custom validator functions")

    print_success("Validation module examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
