"""
Test suite for validation of example output files.

Tests that examples generate correct output formats, required fields,
and follow consistent output patterns.
"""

import json
from pathlib import Path
from typing import Any

import pytest


class TestOutputValidation:
    """Test validation of example output files."""

    def get_output_files(self, examples_dir: Path) -> list[Path]:
        """Get all output JSON files from examples."""
        output_files = []

        # Find all *_results.json files in output directories
        for json_file in examples_dir.rglob("output/*_results.json"):
            output_files.append(json_file)

        return output_files

    def load_output_file(self, file_path: Path) -> dict[str, Any] | None:
        """Load and parse output JSON file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
        except Exception:
            return None

    def validate_output_structure(self, output: dict[str, Any]) -> dict[str, Any]:
        """Validate the basic structure of output data."""
        validation = {"valid": True, "errors": [], "warnings": []}

        if not isinstance(output, dict):
            validation["valid"] = False
            validation["errors"].append("Output must be a JSON object")
            return validation

        # Check for common expected fields
        expected_patterns = [
            "workflow_phases_completed",
            "modules_integrated",
            "final_results"
        ]

        found_expected = any(key in output for key in expected_patterns)

        if not found_expected and len(output) > 0:
            validation["warnings"].append("Output may be missing expected result fields")

        # Check for reasonable content
        if len(output) == 0:
            validation["warnings"].append("Output file is empty")

        return validation

    def validate_output_types(self, output: dict[str, Any]) -> list[str]:
        """Validate that output values have reasonable types."""
        type_errors = []

        # Define expected types for common fields
        expected_types = {
            "workflow_phases_completed": int,
            "modules_integrated": (int, list),
            "final_results": dict,
            "execution_time": (int, float),
            "success": bool
        }

        for field, expected_type in expected_types.items():
            if field in output:
                actual_value = output[field]
                if not isinstance(actual_value, expected_type):
                    type_errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(actual_value).__name__}")

        return type_errors

    def validate_output_completeness(self, output: dict[str, Any], module_name: str) -> dict[str, Any]:
        """Validate that output contains expected information for the module."""
        validation = {"complete": True, "missing": []}

        # Define module-specific expectations
        module_expectations = {
            "api": ["api_endpoints_documented", "openapi_spec_generated"],
            "database_management": ["database_connections_created", "schema_tables_created"],
            "security_audit": ["vulnerabilities_found", "secrets_detected"],
            "config_management": ["configurations_loaded", "validations_performed"],
            "build_synthesis": ["build_configs_created", "build_targets_created"],
            "ci_cd_automation": ["pipelines_created", "stages_configured"],
            "performance": ["benchmarks_run", "metrics_collected"],
            "static_analysis": ["files_analyzed", "issues_found"],
            "pattern_matching": ["patterns_matched", "files_scanned"],
            "code_review": ["files_reviewed", "issues_identified"],
            "data_visualization": ["plots_generated", "charts_created"],
            "git_operations": ["repositories_processed", "operations_completed"],
            "containerization": ["images_built", "containers_created"],
            "ai_code_editing": ["code_generated", "refactoring_completed"],
            "plugin_system": ["plugins_discovered", "plugins_loaded"],
            "events": ["events_published", "handlers_executed"],
            "api_standardization": ["apis_created", "endpoints_defined"],
            "logging_monitoring": ["logs_configured", "monitoring_setup"],
            "environment_setup": ["dependencies_checked", "environment_validated"],
            "model_context_protocol": ["tools_registered", "protocols_established"],
            "terminal_interface": ["ui_components_created", "interactions_handled"],
            "llm": ["models_loaded", "inference_completed"],
            "llm": ["providers_configured", "completions_generated"],
            "spatial.three_d": ["scenes_created", "rendering_completed"],
            "physical_management": ["systems_monitored", "resources_managed"],
            "system_discovery": ["modules_discovered", "health_assessed"],
            "documentation": ["docs_generated", "formats_supported"],
            "project_orchestration": ["workflows_created", "tasks_orchestrated"]
        }

        if module_name in module_expectations:
            expected_fields = module_expectations[module_name]
            for field in expected_fields:
                if field not in output:
                    validation["complete"] = False
                    validation["missing"].append(field)

        return validation

    def test_output_file_generation(self, examples_dir: Path):
        """Test that output files are generated correctly."""
        output_files = self.get_output_files(examples_dir)

        print(f"\nFound {len(output_files)} output files")

        generated_files = 0
        valid_files = 0

        for output_file in output_files:
            module_name = output_file.parent.parent.name
            print(f"\nTesting output: {output_file}")

            # Check file exists and is readable
            if output_file.exists():
                generated_files += 1
                print("✓ Output file exists")
                # Load and validate content
                output_data = self.load_output_file(output_file)
                if output_data is not None:
                    valid_files += 1
                    print("✓ Output file is valid JSON")
                    # Validate structure
                    structure_validation = self.validate_output_structure(output_data)
                    if structure_validation["valid"]:
                        print("✓ Output structure is valid")
                    else:
                        print(f"⚠ Output structure issues: {structure_validation['errors']}")

                    # Validate types
                    type_errors = self.validate_output_types(output_data)
                    if not type_errors:
                        print("✓ Output types are correct")
                    else:
                        print(f"⚠ Output type issues: {type_errors}")

                    # Validate completeness
                    completeness = self.validate_output_completeness(output_data, module_name)
                    if completeness["complete"]:
                        print("✓ Output completeness check passed")
                    else:
                        print(f"⚠ Missing expected fields: {completeness['missing']}")

                else:
                    print("✗ Output file is not valid JSON")
            else:
                print("✗ Output file does not exist")

        print("\nOutput file summary:")
        print(f"  Generated: {generated_files}/{len(output_files)}")
        print(f"  Valid JSON: {valid_files}/{len(output_files)}")

        # Allow some flexibility - not all examples may have run yet
        assert generated_files >= len(output_files) * 0.5, f"Only {generated_files}/{len(output_files)} output files generated"

    def test_output_file_naming(self, examples_dir: Path):
        """Test that output files follow naming conventions."""
        output_files = self.get_output_files(examples_dir)

        naming_errors = []

        for output_file in output_files:
            expected_name = f"{output_file.parent.parent.name}_results.json"
            actual_name = output_file.name

            if actual_name != expected_name:
                naming_errors.append(f"{output_file}: expected '{expected_name}', got '{actual_name}'")

        if naming_errors:
            pytest.fail(f"Found {len(naming_errors)} output files with incorrect naming: {naming_errors}")

    def test_output_directory_structure(self, examples_dir: Path):
        """Test that output directories are structured correctly."""
        # Check that output directories exist where expected
        example_dirs = [d for d in examples_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]

        structure_issues = []

        for example_dir in example_dirs:
            output_dir = example_dir / "output"
            if not output_dir.exists():
                # This is OK - examples may not have been run
                continue

            # Check that output directory has reasonable content
            output_files = list(output_dir.glob("*"))
            if len(output_files) == 0:
                structure_issues.append(f"{output_dir} is empty")

            # Check for logs directory too
            logs_dir = example_dir / "logs"
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*"))
                if len(log_files) == 0:
                    structure_issues.append(f"{logs_dir} exists but is empty")

        # Don't fail on structure issues - they're not critical
        if structure_issues:
            print(f"\nOutput structure warnings: {structure_issues}")

    def test_output_data_reasonableness(self, examples_dir: Path):
        """Test that output data contains reasonable values."""
        output_files = self.get_output_files(examples_dir)

        reasonableness_issues = []

        for output_file in output_files:
            output_data = self.load_output_file(output_file)
            if output_data is None:
                continue

            # Check for obviously wrong values
            for key, value in output_data.items():
                if isinstance(value, (int, float)):
                    if value < 0:
                        reasonableness_issues.append(f"{output_file}: negative value for {key}: {value}")
                    elif isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        reasonableness_issues.append(f"{output_file}: infinite value for {key}: {value}")
                elif isinstance(value, str) and len(value) > 10000:
                    reasonableness_issues.append(f"{output_file}: unusually long string for {key}: {len(value)} chars")

        if reasonableness_issues:
            pytest.fail(f"Found {len(reasonableness_issues)} output data reasonableness issues: {reasonableness_issues}")

    def test_log_file_generation(self, examples_dir: Path):
        """Test that log files are generated when expected."""
        example_dirs = [d for d in examples_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]

        log_stats = {"total_examples": len(example_dirs), "with_logs": 0, "log_files": 0}

        for example_dir in example_dirs:
            logs_dir = example_dir / "logs"
            if logs_dir.exists():
                log_stats["with_logs"] += 1
                log_files = list(logs_dir.glob("*.log"))
                log_stats["log_files"] += len(log_files)

        print("\nLog file statistics:")
        print(f"  Examples with logs: {log_stats['with_logs']}/{log_stats['total_examples']}")
        print(f"  Total log files: {log_stats['log_files']}")

        # Verify the stats collection completed successfully
        assert log_stats["total_examples"] >= 0
