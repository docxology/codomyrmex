#!/usr/bin/env python3
"""
Example: Validation - Data Validation Framework

Demonstrates:
- JSON Schema validation
- Custom validation rules
- Validation result handling
- Validation manager usage

Tested Methods:
- validate() - Verified in test_validation.py::TestValidator::test_validate
- is_valid() - Verified in test_validation.py::TestValidator::test_is_valid
- ValidationManager.validate() - Verified in test_validation.py::TestValidationManager::test_validate
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import common utilities
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.validation import validate, is_valid, ValidationManager, ValidationError

def main():
    """Run the validation example."""
    print_section("Validation Module Example")
    print("Demonstrating data validation functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize validation manager
        manager = ValidationManager()
        print_success("✓ Validation manager initialized")

        # Example 1: JSON Schema validation
        print("\n1. JSON Schema Validation")
        user_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["id", "name", "email"]
        }

        valid_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }

        invalid_data = {
            "id": "not_an_integer",
            "name": "Jane Doe"
            # Missing required email field
        }

        # Validate valid data
        result_valid = validate(valid_data, user_schema)
        if result_valid.is_valid:
            print_success("✓ Valid data passed validation")
        else:
            print_error(f"✗ Valid data failed validation: {result_valid.errors}")

        # Validate invalid data
        result_invalid = validate(invalid_data, user_schema)
        if not result_invalid.is_valid:
            print_success(f"✓ Invalid data correctly rejected ({len(result_invalid.errors)} errors)")
        else:
            print_error("✗ Invalid data incorrectly passed validation")

        # Example 2: Using is_valid helper
        print("\n2. Quick Validation Check")
        is_data_valid = is_valid(valid_data, user_schema)
        if is_data_valid:
            print_success("✓ is_valid() helper works correctly")

        # Example 3: Validation manager
        print("\n3. Validation Manager")
        manager_result = manager.validate(valid_data, user_schema, validator_type="json_schema")
        if manager_result.is_valid:
            print_success("✓ Validation manager works correctly")

        # Example 4: Custom validation (if supported)
        print("\n4. Custom Validation")
        try:
            # Try to register a custom validator
            def custom_validator(data, schema):
                # Simple custom validation: check if data is a dict
                if not isinstance(data, dict):
                    from codomyrmex.validation import ValidationResult, ValidationError
                    return ValidationResult(
                        is_valid=False,
                        errors=[ValidationError("Data must be a dictionary", code="type_error")]
                    )
                return ValidationResult(is_valid=True)

            manager.register_validator("custom_dict", custom_validator)
            print_success("✓ Custom validator registered")

            # Test custom validator
            custom_result = manager.validate({"key": "value"}, None, validator_type="custom_dict")
            if custom_result.is_valid:
                print_success("✓ Custom validator works correctly")
        except Exception as e:
            print_error(f"Custom validation test failed: {e}")

        operations_summary = {
            "manager_initialized": True,
            "json_schema_validation_tested": True,
            "valid_data_passed": result_valid.is_valid,
            "invalid_data_rejected": not result_invalid.is_valid,
            "is_valid_helper_tested": is_data_valid,
            "manager_validation_tested": manager_result.is_valid,
            "errors_detected": len(result_invalid.errors),
            "warnings_detected": len(result_invalid.warnings) if hasattr(result_invalid, 'warnings') else 0
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Validation example completed successfully!")
    except Exception as e:
        runner.error("Validation example failed", e)
        print_error(f"Validation example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

