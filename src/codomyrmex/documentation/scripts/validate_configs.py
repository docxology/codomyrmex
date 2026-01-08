from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import argparse
import json
import logging
import os
import re
import sys

import yaml

from codomyrmex.logging_monitoring import get_logger




























































#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides validate_configs functionality including:
- 18 functions: main, __init__, validate_all_configs...
- 1 classes: ConfigValidator

Usage:
    # Example usage here
"""
Configuration Validator for Codomyrmex Examples

This script validates all YAML and JSON configuration files in the examples directory.
It checks syntax, required fields, and schema compliance.

Usage:
    python scripts/examples/validate_configs.py

Options:
    --fix: Attempt to fix common issues automatically
    --verbose: Show detailed validation results

Output:
    - Validation results for each config file
    - Summary of errors and warnings
    - Suggestions for fixes
"""


try:
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration files for Codomyrmex examples."""

    def __init__(self, project_root: Path):
        """Initialize the config validator."""
        self.project_root = project_root
        self.examples_dir = project_root / "examples"
        self.validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "warnings": [],
            "file_results": {}
        }

    def validate_all_configs(self, fix: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Validate all configuration files."""
        logger.info("Starting configuration validation...")

        if not YAML_AVAILABLE:
            logger.warning("PyYAML not available. YAML validation will be skipped.")

        # Find all config files
        config_files = self._find_config_files()

        self.validation_results["total_files"] = len(config_files)

        for file_path, file_type in config_files:
            result = self._validate_config_file(file_path, file_type, fix, verbose)
            self.validation_results["file_results"][str(file_path)] = result

            if result["valid"]:
                self.validation_results["valid_files"] += 1
            else:
                self.validation_results["invalid_files"] += 1
                self.validation_results["errors"].extend(result["errors"])
                self.validation_results["warnings"].extend(result["warnings"])

        # Calculate summary
        self.validation_results["success_rate"] = (
            self.validation_results["valid_files"] / self.validation_results["total_files"] * 100
            if self.validation_results["total_files"] > 0 else 0
        )

        logger.info(f"Validation complete. {self.validation_results['valid_files']}/{self.validation_results['total_files']} files valid.")
        return self.validation_results

    def _find_config_files(self) -> List[Tuple[Path, str]]:
        """Find all configuration files in examples directory."""
        config_files = []

        if not self.examples_dir.exists():
            logger.error(f"Examples directory not found: {self.examples_dir}")
            return config_files

        # Find YAML files
        for yaml_file in self.examples_dir.rglob("config.yaml"):
            config_files.append((yaml_file, "yaml"))

        # Find JSON files
        for json_file in self.examples_dir.rglob("config.json"):
            config_files.append((json_file, "json"))

        logger.info(f"Found {len(config_files)} configuration files")
        return config_files

    def _validate_config_file(self, file_path: Path, file_type: str, fix: bool, verbose: bool) -> Dict[str, Any]:
        """Validate a single configuration file."""
        result = {
            "file": str(file_path),
            "type": file_type,
            "valid": True,
            "errors": [],
            "warnings": [],
            "fixed": False
        }

        if verbose:
            logger.info(f"Validating {file_type.upper()}: {file_path}")

        # Load the configuration
        config = self._load_config_file(file_path, file_type, result)
        if config is None:
            return result

        # Validate syntax
        self._validate_syntax(config, result)

        # Validate structure
        self._validate_structure(config, result)

        # Validate content
        self._validate_content(config, result)

        # Attempt fixes if requested
        if fix and not result["valid"]:
            self._attempt_fixes(file_path, file_type, result)

        if verbose:
            status = "✓ VALID" if result["valid"] else "✗ INVALID"
            logger.info(f"  {status}: {file_path}")

        return result

    def _load_config_file(self, file_path: Path, file_type: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_type == "yaml":
                    if not YAML_AVAILABLE:
                        result["valid"] = False
                        result["errors"].append("PyYAML not available for YAML validation")
                        return None
                    config = yaml.safe_load(f)
                elif file_type == "json":
                    config = json.load(f)
                else:
                    result["valid"] = False
                    result["errors"].append(f"Unsupported file type: {file_type}")
                    return None

            return config

        except yaml.YAMLError as e:
            result["valid"] = False
            result["errors"].append(f"YAML syntax error: {e}")
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"JSON syntax error: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"File read error: {e}")

        return None

    def _validate_syntax(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate basic syntax and structure."""
        if not isinstance(config, dict):
            result["valid"] = False
            result["errors"].append("Configuration must be a dictionary/object")
            return

        # Check for empty config
        if len(config) == 0:
            result["warnings"].append("Configuration file is empty")

    def _validate_structure(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate configuration structure."""
        # Required top-level sections for examples
        expected_sections = ["output", "logging"]
        optional_sections = ["module", "api", "database", "performance", "integration"]

        missing_required = []
        for section in expected_sections:
            if section not in config:
                missing_required.append(section)

        if missing_required:
            result["valid"] = False
            result["errors"].append(f"Missing required sections: {', '.join(missing_required)}")

        # Validate output section
        if "output" in config:
            output_config = config["output"]
            if not isinstance(output_config, dict):
                result["errors"].append("output section must be a dictionary")
            elif "format" not in output_config:
                result["warnings"].append("output section missing 'format' field")
            elif "file" not in output_config:
                result["warnings"].append("output section missing 'file' field")

        # Validate logging section
        if "logging" in config:
            logging_config = config["logging"]
            if not isinstance(logging_config, dict):
                result["errors"].append("logging section must be a dictionary")
            elif "level" not in logging_config:
                result["warnings"].append("logging section missing 'level' field")

    def _validate_content(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate configuration content and values."""
        # Validate output format
        if "output" in config and "format" in config["output"]:
            valid_formats = ["json", "text", "yaml"]
            output_format = config["output"]["format"]
            if output_format not in valid_formats:
                result["warnings"].append(f"output.format '{output_format}' not in valid formats: {valid_formats}")

        # Validate logging level
        if "logging" in config and "level" in config["logging"]:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            log_level = config["logging"]["level"]
            if log_level not in valid_levels:
                result["warnings"].append(f"logging.level '{log_level}' not in valid levels: {valid_levels}")

        # Validate environment variable references
        self._validate_env_vars(config, result)

        # Validate file paths
        self._validate_file_paths(config, result)

        # Validate numeric ranges
        self._validate_numeric_ranges(config, result)

    def _validate_env_vars(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate environment variable references."""
        def check_env_vars(obj, path=""):
    """Brief description of check_env_vars.

Args:
    obj : Description of obj
    path : Description of path

    Returns: Description of return value
"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and value.startswith("${"):
                        # Extract variable name
                        var_expr = value[2:-1]  # Remove ${}
                        if ":" in var_expr:
                            var_name, default = var_expr.split(":", 1)
                        else:
                            var_name, default = var_expr, None

                        # Check if environment variable is actually available
                        if var_name not in os.environ and default is None:
                            result["warnings"].append(f"Environment variable '{var_name}' not set and no default provided at {current_path}")
                    else:
                        check_env_vars(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_env_vars(item, f"{path}[{i}]")

        check_env_vars(config)

    def _validate_file_paths(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate file paths in configuration."""
        def check_file_paths(obj, path=""):
    """Brief description of check_file_paths.

Args:
    obj : Description of obj
    path : Description of path

    Returns: Description of return value
"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and key in ["file", "log_file", "database", "path"]:
                        # Check for obviously invalid paths
                        if ".." in value:
                            result["warnings"].append(f"Potentially unsafe path with '..' at {current_path}: {value}")
                        if value.startswith("/") and not Path(value).exists():
                            # Absolute path that doesn't exist - might be OK if created at runtime
                            pass
                    else:
                        check_file_paths(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_file_paths(item, f"{path}[{i}]")

        check_file_paths(config)

    def _validate_numeric_ranges(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate numeric values are in reasonable ranges."""
        def check_numeric_ranges(obj, path=""):
    """Brief description of check_numeric_ranges.

Args:
    obj : Description of obj
    path : Description of path

    Returns: Description of return value
"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (int, float)):
                        # Check for obviously wrong values
                        if key in ["port"] and not (1 <= value <= 65535):
                            result["warnings"].append(f"Port {value} at {current_path} not in valid range 1-65535")
                        elif key in ["timeout"] and value < 0:
                            result["warnings"].append(f"Negative timeout {value} at {current_path}")
                        elif key in ["max_workers", "max_concurrent"] and value < 1:
                            result["warnings"].append(f"Invalid worker count {value} at {current_path}, should be >= 1")
                    else:
                        check_numeric_ranges(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_numeric_ranges(item, f"{path}[{i}]")

        check_numeric_ranges(config)

    def _attempt_fixes(self, file_path: Path, file_type: str, result: Dict[str, Any]):
        """Attempt to automatically fix common issues."""
        if not result["errors"]:
            return

        logger.info(f"Attempting to fix issues in {file_path}")

        # Load current config
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_type == "yaml" and YAML_AVAILABLE:
                    config = yaml.safe_load(f)
                elif file_type == "json":
                    config = json.load(f)
                else:
                    return
        except Exception:
            return

        # Apply fixes
        fixed = False

        # Fix missing required sections
        if "output" not in config:
            config["output"] = {"format": "json", "file": "output/results.json"}
            fixed = True

        if "logging" not in config:
            config["logging"] = {"level": "INFO", "file": "logs/example.log"}
            fixed = True

        # Fix missing output fields
        if "output" in config:
            if "format" not in config["output"]:
                config["output"]["format"] = "json"
                fixed = True
            if "file" not in config["output"]:
                config["output"]["file"] = f"output/{file_path.parent.name}_results.json"
                fixed = True

        # Fix missing logging fields
        if "logging" in config:
            if "level" not in config["logging"]:
                config["logging"]["level"] = "INFO"
                fixed = True

        # Save fixed config
        if fixed:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_type == "yaml" and YAML_AVAILABLE:
                        yaml.dump(config, f, default_flow_style=False, indent=2)
                    elif file_type == "json":
                        json.dump(config, f, indent=2, ensure_ascii=False)

                result["fixed"] = True
                result["errors"] = [e for e in result["errors"] if "Missing required" not in e]
                if not result["errors"]:
                    result["valid"] = True

                logger.info(f"Applied automatic fixes to {file_path}")

            except Exception as e:
                logger.error(f"Failed to save fixes to {file_path}: {e}")

    def print_report(self, results: Dict[str, Any], verbose: bool = False):
        """Print validation results."""
        print("\n" + "="*80)
        print("🔧 CONFIGURATION VALIDATION REPORT")
        print("="*80)

        print(f"\n📊 SUMMARY:")
        print(f"   Total Files: {results['total_files']}")
        print(f"   Valid Files: {results['valid_files']}")
        print(f"   Invalid Files: {results['invalid_files']}")
        print(f"   Success Rate: {results['success_rate']:.1f}%")
        print(f"   Total Errors: {len(results['errors'])}")
        print(f"   Total Warnings: {len(results['warnings'])}")

        if results['invalid_files'] > 0:
            print(f"\n❌ INVALID FILES:")
            for file_path, result in results['file_results'].items():
                if not result['valid']:
                    print(f"   ✗ {file_path}")
                    if verbose:
                        for error in result['errors']:
                            print(f"     • {error}")
                        for warning in result['warnings']:
                            print(f"     ⚠ {warning}")

        if results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
            for warning in results['warnings'][:10]:  # Show first 10
                print(f"   • {warning}")
            if len(results['warnings']) > 10:
                print(f"   ... and {len(results['warnings']) - 10} more")

        if results['errors']:
            print(f"\n🔴 ERRORS ({len(results['errors'])}):")
            for error in results['errors'][:10]:  # Show first 10
                print(f"   • {error}")
            if len(results['errors']) > 10:
                print(f"   ... and {len(results['errors']) - 10} more")

        print(f"\n✅ REPORT GENERATED")
        print("="*80)

    def save_report(self, results: Dict[str, Any], output_file: str = None):
        """Save validation results to file."""
        if output_file is None:
            output_file = self.project_root / "examples" / "config_validation_report.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {output_file}")


def main():
    """Main function to run config validation."""
    parser = argparse.ArgumentParser(description="Validate Codomyrmex example configurations")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix common issues automatically")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed validation results")
    parser.add_argument("--output", "-o", help="Output file for validation report")

    args = parser.parse_args()

    validator = ConfigValidator(project_root)

    # Run validation
    results = validator.validate_all_configs(fix=args.fix, verbose=args.verbose)

    # Print report
    validator.print_report(results, verbose=args.verbose)

    # Save report
    validator.save_report(results, args.output)

    # Exit with appropriate code
    if results["invalid_files"] > 0:
        logger.error(f"Found {results['invalid_files']} invalid configuration files")
        sys.exit(1)
    else:
        logger.info("All configuration files are valid! 🎉")
        sys.exit(0)


if __name__ == "__main__":
    main()
