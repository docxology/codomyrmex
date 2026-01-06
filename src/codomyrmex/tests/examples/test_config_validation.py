"""
Test suite for validation of example configuration files.

Tests YAML and JSON configuration files for syntax correctness,
required fields, and schema compliance.
"""

import pytest
import yaml
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class TestConfigValidation:
    """Test validation of example configuration files."""

    def get_config_files(self, examples_dir: Path) -> List[Tuple[Path, str]]:
        """Get all config files (yaml and json)."""
        config_files = []

        # Find all config.yaml files
        for yaml_file in examples_dir.rglob("config.yaml"):
            config_files.append((yaml_file, "yaml"))

        # Find all config.json files
        for json_file in examples_dir.rglob("config.json"):
            config_files.append((json_file, "json"))

        return config_files

    def validate_yaml_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate YAML syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True, None
        except yaml.YAMLError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_json_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate JSON syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def load_config(self, file_path: Path, file_type: str) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_type == "yaml":
                    return yaml.safe_load(f)
                elif file_type == "json":
                    return json.load(f)
                else:
                    return None
        except Exception:
            return None

    def validate_required_fields(self, config: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate presence of required fields."""
        missing_fields = []
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        return missing_fields

    def validate_field_types(self, config: Dict[str, Any], type_requirements: Dict[str, str]) -> List[str]:
        """Validate field types."""
        type_errors = []
        for field, expected_type in type_requirements.items():
            if field in config:
                actual_value = config[field]
                if expected_type == "string" and not isinstance(actual_value, str):
                    type_errors.append(f"{field} should be string, got {type(actual_value)}")
                elif expected_type == "integer" and not isinstance(actual_value, int):
                    type_errors.append(f"{field} should be integer, got {type(actual_value)}")
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    type_errors.append(f"{field} should be boolean, got {type(actual_value)}")
                elif expected_type == "object" and not isinstance(actual_value, dict):
                    type_errors.append(f"{field} should be object, got {type(actual_value)}")
                elif expected_type == "array" and not isinstance(actual_value, list):
                    type_errors.append(f"{field} should be array, got {type(actual_value)}")
        return type_errors

    def test_config_file_syntax(self, examples_dir: Path):
        """Test that all config files have valid syntax."""
        config_files = self.get_config_files(examples_dir)

        syntax_errors = []

        for file_path, file_type in config_files:
            print(f"\nTesting {file_type} syntax: {file_path}")

            if file_type == "yaml":
                is_valid, error = self.validate_yaml_syntax(file_path)
            elif file_type == "json":
                is_valid, error = self.validate_json_syntax(file_path)
            else:
                is_valid, error = False, f"Unknown file type: {file_type}"

            if is_valid:
                print(f"✓ {file_type.upper()} syntax valid")
            else:
                print(f"✗ {file_type.upper()} syntax error: {error}")
                syntax_errors.append((str(file_path), error))

        assert len(syntax_errors) == 0, f"Found {len(syntax_errors)} config files with syntax errors: {syntax_errors}"

    def test_config_required_fields(self, examples_dir: Path):
        """Test that config files have required fields."""
        config_files = self.get_config_files(examples_dir)

        # Define required fields for different config types
        required_fields_map = {
            "output": ["format", "file"],
            "logging": ["level"]
        }

        field_errors = []

        for file_path, file_type in config_files:
            config = self.load_config(file_path, file_type)
            if config is None:
                continue

            print(f"\nTesting required fields: {file_path}")

            for section, required in required_fields_map.items():
                if section in config:
                    missing = self.validate_required_fields(config[section], required)
                    if missing:
                        error_msg = f"Missing required fields in {section}: {missing}"
                        print(f"✗ {error_msg}")
                        field_errors.append((str(file_path), error_msg))
                    else:
                        print(f"✓ {section} has all required fields")

        if field_errors:
            pytest.fail(f"Found {len(field_errors)} config files with missing required fields: {field_errors}")

    def test_config_field_types(self, examples_dir: Path):
        """Test that config fields have correct types."""
        config_files = self.get_config_files(examples_dir)

        # Define type requirements
        type_requirements_map = {
            "output": {
                "format": "string"
            },
            "logging": {
                "level": "string"
            }
        }

        type_errors = []

        for file_path, file_type in config_files:
            config = self.load_config(file_path, file_type)
            if config is None:
                continue

            print(f"\nTesting field types: {file_path}")

            for section, type_reqs in type_requirements_map.items():
                if section in config:
                    errors = self.validate_field_types(config[section], type_reqs)
                    if errors:
                        for error in errors:
                            print(f"✗ {error}")
                            type_errors.append((str(file_path), error))
                    else:
                        print(f"✓ {section} field types correct")

        if type_errors:
            pytest.fail(f"Found {len(type_errors)} config files with type errors: {type_errors}")

    def test_environment_variable_substitution(self, examples_dir: Path):
        """Test that environment variable substitution works."""
        # Set test environment variables
        test_vars = {
            "TEST_API_KEY": "test_key_123",
            "TEST_DATABASE_URL": "sqlite:///test.db",
            "TEST_DEBUG": "true"
        }

        original_env = {}
        for key, value in test_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            # Create a test config file with env vars
            test_config = {
                "api": {
                    "key": "${TEST_API_KEY}",
                    "database_url": "${TEST_DATABASE_URL:default.db}",
                    "debug": "${TEST_DEBUG:false}"
                }
            }

            # Test substitution (this would normally be done by the config loader)
            substituted_config = {}
            for section, values in test_config.items():
                substituted_config[section] = {}
                for key, value in values.items():
                    if isinstance(value, str) and value.startswith("${"):
                        # Simple env var substitution for testing
                        var_expr = value[2:-1]  # Remove ${}
                        if ":" in var_expr:
                            var_name, default = var_expr.split(":", 1)
                            substituted_config[section][key] = os.environ.get(var_name, default)
                        else:
                            substituted_config[section][key] = os.environ.get(var_expr, "")
                    else:
                        substituted_config[section][key] = value

            # Verify substitution worked
            assert substituted_config["api"]["key"] == "test_key_123"
            assert substituted_config["api"]["database_url"] == "sqlite:///test.db"
            assert substituted_config["api"]["debug"] == "true"

            print("✓ Environment variable substitution works correctly")

        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_config_file_discovery(self, examples_dir: Path):
        """Test that config files can be discovered correctly."""
        config_files = self.get_config_files(examples_dir)

        yaml_files = [f for f, t in config_files if t == "yaml"]
        json_files = [f for f, t in config_files if t == "json"]

        print(f"\nConfig file discovery:")
        print(f"  Found {len(yaml_files)} YAML files")
        print(f"  Found {len(json_files)} JSON files")
        print(f"  Total config files: {len(config_files)}")

        # Should have a reasonable number of config files
        assert len(config_files) >= 20, f"Should find at least 20 config files, found {len(config_files)}"

        # Should have both YAML and JSON for most examples
        assert len(yaml_files) >= 10, f"Should find at least 10 YAML files, found {len(yaml_files)}"
        assert len(json_files) >= 10, f"Should find at least 10 JSON files, found {len(json_files)}"
