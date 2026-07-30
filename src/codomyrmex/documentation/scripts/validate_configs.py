#!/usr/bin/env python3
"""
Configuration Validator for Codomyrmex Repository Configuration

This script validates YAML and JSON files under ``config/``. It checks syntax,
generic object shape, and the shape of optional shared sections without
assuming that every domain-specific configuration has the same schema.

Usage:
    python src/codomyrmex/documentation/scripts/validate_configs.py

Options:
    --fix: Attempt to fix common issues automatically
    --verbose: Show detailed validation results

Output:
    - Validation results for each config file
    - Summary of errors and warnings
    - Suggestions for fixes
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Add src to path if needed
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validate heterogeneous repository configuration files."""

    def __init__(self, project_root: Path):
        """Initialize the config validator."""
        self.project_root = project_root
        # Path to config directory
        self.config_dir = project_root / "config"
        self.validation_results: dict[str, Any] = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "warnings": [],
            "file_results": {},
        }

    def validate_all_configs(
        self, fix: bool = False, verbose: bool = False
    ) -> dict[str, Any]:
        """Validate all configuration files."""
        logger.info("Starting configuration validation...")
        self.validation_results = {
            "scope": "config/**/*.{json,yaml,yml}",
            "path_base": "project-root",
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "warnings": [],
            "file_results": {},
        }

        if not YAML_AVAILABLE:
            logger.warning("PyYAML not available. YAML validation will be skipped.")

        # Find all config files
        config_files = self._find_config_files()

        self.validation_results["total_files"] = len(config_files)

        for file_path, file_type in config_files:
            result = self._validate_config_file(file_path, file_type, fix, verbose)
            self.validation_results["file_results"][self._display_path(file_path)] = (
                result
            )

            if result["valid"]:
                self.validation_results["valid_files"] += 1
            else:
                self.validation_results["invalid_files"] += 1
                self.validation_results["errors"].extend(result["errors"])
                self.validation_results["warnings"].extend(result["warnings"])

        # Calculate summary
        self.validation_results["success_rate"] = (
            self.validation_results["valid_files"]
            / self.validation_results["total_files"]
            * 100
            if self.validation_results["total_files"] > 0
            else 0
        )

        logger.info(
            "Validation complete. %s/%s files valid.",
            self.validation_results["valid_files"],
            self.validation_results["total_files"],
        )
        return self.validation_results

    def _find_config_files(self) -> list[tuple[Path, str]]:
        """Find all configuration files in config directory."""
        config_files: list[tuple[Path, str]] = []

        if not self.config_dir.exists():
            logger.error("Config directory not found: %s", self.config_dir)
            return config_files

        # Find YAML files
        for yaml_file in sorted(self.config_dir.rglob("*.yaml")):
            config_files.append((yaml_file, "yaml"))
        for yml_file in sorted(self.config_dir.rglob("*.yml")):
            config_files.append((yml_file, "yaml"))

        # Find JSON files
        for json_file in sorted(self.config_dir.rglob("*.json")):
            config_files.append((json_file, "json"))

        logger.info("Found %s configuration files", len(config_files))
        return config_files

    def _display_path(self, file_path: Path) -> str:
        """Return a portable project-relative path for reports."""
        try:
            return (
                file_path.resolve().relative_to(self.project_root.resolve()).as_posix()
            )
        except ValueError:
            return file_path.name

    def _validate_config_file(
        self, file_path: Path, file_type: str, fix: bool, verbose: bool
    ) -> dict[str, Any]:
        """Validate a single configuration file."""
        result = {
            "file": self._display_path(file_path),
            "type": file_type,
            "valid": True,
            "errors": [],
            "warnings": [],
            "fixed": False,
        }

        if verbose:
            logger.info("Validating %s: %s", file_type.upper(), file_path)

        # Load the configuration
        config = self._load_config_file(file_path, file_type, result)
        if config is None:
            return result

        # Validate syntax
        self._validate_syntax(config, result)

        if isinstance(config, dict):
            # Validate only shared sections that are actually present.
            self._validate_structure(config, result)
            self._validate_content(config, result)

        # Attempt fixes if requested
        if fix and not result["valid"]:
            self._attempt_fixes(file_path, file_type, result)

        if verbose:
            status = "✓ VALID" if result["valid"] else "✗ INVALID"
            logger.info("  %s: %s", status, file_path)

        return result

    def _load_config_file(
        self, file_path: Path, file_type: str, result: dict[str, Any]
    ) -> Any | None:
        """Load configuration from file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                if file_type == "yaml":
                    if not YAML_AVAILABLE:
                        result["valid"] = False
                        result["errors"].append(
                            "PyYAML not available for YAML validation"
                        )
                        return None
                    config = yaml.safe_load(f)
                elif file_type == "json":
                    config = json.load(f)
                else:
                    result["valid"] = False
                    result["errors"].append(f"Unsupported file type: {file_type}")
                    return None

            return config

        except Exception as e:
            result["valid"] = False
            message = str(e).replace(str(file_path), self._display_path(file_path))
            result["errors"].append(f"Parse error: {message}")

        return None

    def _validate_syntax(self, config: Any, result: dict[str, Any]):
        """Validate basic syntax and structure."""
        if not isinstance(config, dict):
            result["valid"] = False
            result["errors"].append("Configuration must be a dictionary/object")
            return

        # Check for empty config
        if len(config) == 0:
            result["warnings"].append("Configuration file is empty")

    def _validate_structure(self, config: dict[str, Any], result: dict[str, Any]):
        """Validate optional shared-section structure."""
        if "output" in config:
            output_config = config["output"]
            if not isinstance(output_config, dict):
                result["valid"] = False
                result["errors"].append("output section must be a dictionary")
            elif "format" not in output_config:
                result["warnings"].append("output section missing 'format' field")

        if "logging" in config:
            logging_config = config["logging"]
            if not isinstance(logging_config, dict):
                result["valid"] = False
                result["errors"].append("logging section must be a dictionary")
            elif "level" not in logging_config:
                result["warnings"].append("logging section missing 'level' field")

    def _validate_content(self, config: dict[str, Any], result: dict[str, Any]):
        """Validate configuration content and values."""
        logging_config = config.get("logging")
        if isinstance(logging_config, dict) and "level" in logging_config:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            log_level = logging_config["level"]
            is_environment_expression = (
                isinstance(log_level, str)
                and log_level.startswith("${")
                and log_level.endswith("}")
            )
            if log_level not in valid_levels and not is_environment_expression:
                result["warnings"].append(
                    f"logging.level '{log_level}' not in valid levels: {valid_levels}"
                )

    def _attempt_fixes(self, file_path: Path, file_type: str, result: dict[str, Any]):
        """Attempt to automatically fix common issues."""
        if file_type != "json":
            return  # Auto-fix only implemented for JSON currently

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            fixed = False
            for error in result["errors"]:
                if "Missing required sections" in error:
                    if "output" not in data:
                        data["output"] = {"format": "json"}
                        fixed = True
                    if "logging" not in data:
                        data["logging"] = {"level": "INFO"}
                        fixed = True

            if fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                result["fixed"] = True
                result["valid"] = True
                result["errors"] = []
                logger.info("Successfully auto-fixed %s", file_path)
        except Exception as e:
            logger.error("Failed to auto-fix %s: %s", file_path, e)

    def print_report(self, results: dict[str, Any], verbose: bool = False):
        """Print validation results."""
        print("\n" + "=" * 80)
        print("🔧 CONFIGURATION VALIDATION REPORT")
        print("=" * 80)
        print("\n📊 SUMMARY:")
        print(f"   Total Files: {results['total_files']}")
        print(f"   Valid Files: {results['valid_files']}")
        print(f"   Invalid Files: {results['invalid_files']}")
        print(f"   Success Rate: {results['success_rate']:.1f}%")
        print("\n" + "=" * 80)

    def save_report(
        self,
        results: dict[str, Any],
        output_file: str | Path | None = None,
    ) -> None:
        """Save validation results to file."""
        if output_file is None:
            output_path = (
                self.project_root
                / "src"
                / "codomyrmex"
                / "examples"
                / "config_validation_report.json"
            )
        else:
            output_path = Path(output_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            f.write("\n")

        logger.info("Report saved to: %s", output_path)


def main():
    """Main function to run config validation."""
    parser = argparse.ArgumentParser(
        description="Validate Codomyrmex example configurations"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix common issues automatically"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed validation results"
    )
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Repository root containing config/ (default: inferred)",
    )

    args = parser.parse_args()

    validator = ConfigValidator(args.project_root.resolve())

    # Run validation
    results = validator.validate_all_configs(fix=args.fix, verbose=args.verbose)

    # Print report
    validator.print_report(results, verbose=args.verbose)

    # Save report
    validator.save_report(results, args.output)

    # Exit with appropriate code
    if results["invalid_files"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
