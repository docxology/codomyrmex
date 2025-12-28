#!/usr/bin/env python3
"""
Comprehensive Examples Validation Script

This script validates all Codomyrmex examples for correctness, completeness, and quality.
It performs validation across multiple dimensions:

- Example execution validation
- Configuration file validation
- Documentation validation
- Test method reference validation
- Output file validation
- Cross-validation between components

Features:
- Parallel execution for faster validation
- Progress indicators and detailed reporting
- Comprehensive error analysis with fix suggestions
- Multiple output formats (console, JSON, HTML)
- Summary statistics and quality metrics

Usage:
    python validate_examples.py [options]

Options:
    --parallel N    Number of parallel processes (default: 4)
    --output-dir    Output directory for reports (default: validation_reports)
    --verbose       Enable verbose output
    --fix           Attempt to fix common issues automatically
    --modules       Comma-separated list of modules to validate (default: all)
    --types         Comma-separated validation types (execution,config,docs,test_refs,output)

Tested Methods:
- Example execution validation covers all example_basic.py files
- Configuration validation covers all config.yaml and config.json files
- Documentation validation covers all README.md files
- Test reference validation covers all "Tested Methods" references
- Output validation covers all generated result files
"""

import sys
import os
import json
import yaml
import time
import argparse
import subprocess
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import hashlib
import tempfile
import shutil


class ValidationType(Enum):
    """Types of validation that can be performed."""
    EXECUTION = "execution"
    CONFIGURATION = "config"
    DOCUMENTATION = "docs"
    TEST_REFERENCES = "test_refs"
    OUTPUT = "output"


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    module: str
    validation_type: ValidationType
    severity: ValidationSeverity
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module": self.module,
            "validation_type": self.validation_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "fix_suggestion": self.fix_suggestion,
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number
        }


@dataclass
class ValidationResult:
    """Result of validating a single module."""
    module: str
    success: bool
    duration: float
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_issue(self, issue: ValidationIssue):
        """Add an issue to this result."""
        self.issues.append(issue)
        if not issue.severity == ValidationSeverity.INFO:
            self.success = False

    def get_issue_count(self, severity: Optional[ValidationSeverity] = None) -> int:
        """Get count of issues by severity."""
        if severity:
            return len([i for i in self.issues if i.severity == severity])
        return len(self.issues)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module": self.module,
            "success": self.success,
            "duration": self.duration,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics,
            "issue_count": len(self.issues),
            "issue_counts": {
                "critical": self.get_issue_count(ValidationSeverity.CRITICAL),
                "error": self.get_issue_count(ValidationSeverity.ERROR),
                "warning": self.get_issue_count(ValidationSeverity.WARNING),
                "info": self.get_issue_count(ValidationSeverity.INFO)
            }
        }


class ExamplesValidator:
    """Comprehensive validator for Codomyrmex examples."""

    def __init__(self, examples_root: Path, output_dir: Path, parallel_processes: int = 4):
        self.examples_root = examples_root
        self.output_dir = output_dir
        self.parallel_processes = parallel_processes
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Discover all modules
        self.modules = self._discover_modules()
        self.start_time = time.time()

        # Progress tracking
        self.processed_modules = 0
        self.total_modules = len(self.modules)

    def _discover_modules(self) -> List[str]:
        """Discover all module directories with examples."""
        modules = []
        exclude_dirs = {'__pycache__', '_common', '_templates', 'multi_module'}

        for item in self.examples_root.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                if (item / "example_basic.py").exists():
                    modules.append(item.name)

        # Add multi_module examples
        multi_module_dir = self.examples_root / "multi_module"
        if multi_module_dir.exists():
            for item in multi_module_dir.iterdir():
                if item.is_file() and item.name.startswith("example_workflow_") and item.name.endswith(".py"):
                    modules.append(f"multi_module/{item.stem}")

        return sorted(modules)

    def validate_all(self, validation_types: List[ValidationType],
                    verbose: bool = False, fix: bool = False) -> Dict[str, Any]:
        """Run all validations."""

        print(f"🔍 Validating {len(self.modules)} modules across {len(validation_types)} validation types")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"⚡ Parallel processes: {self.parallel_processes}")
        print()

        # Run validations
        results = {}

        with concurrent.futures.ProcessPoolExecutor(max_workers=self.parallel_processes) as executor:
            # Submit validation tasks
            future_to_module = {}
            for module in self.modules:
                future = executor.submit(self._validate_module, module, validation_types, verbose, fix)
                future_to_module[future] = module

            # Collect results
            for future in concurrent.futures.as_completed(future_to_module):
                module = future_to_module[future]
                try:
                    result = future.result()
                    results[module] = result
                    self.processed_modules += 1

                    # Progress indicator
                    success_icon = "✅" if result.success else "❌"
                    issue_count = len([i for i in result.issues if i.severity != ValidationSeverity.INFO])
                    print(f"{success_icon} {module:<30} ({result.duration:.2f}s, {issue_count} issues)")

                except Exception as exc:
                    print(f"❌ {module:<30} (ERROR: {exc})")
                    results[module] = ValidationResult(module, False, 0.0, [
                        ValidationIssue(
                            module=module,
                            validation_type=ValidationType.EXECUTION,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Validation failed: {exc}",
                            details=str(exc)
                        )
                    ])

        # Generate report
        report = self._generate_report(results, validation_types)
        self._save_report(report)

        return report

    def _validate_module(self, module: str, validation_types: List[ValidationType],
                        verbose: bool, fix: bool) -> ValidationResult:
        """Validate a single module."""
        start_time = time.time()
        result = ValidationResult(module, True, 0.0)

        try:
            # Run each validation type
            for validation_type in validation_types:
                if validation_type == ValidationType.EXECUTION:
                    self._validate_execution(module, result, verbose, fix)
                elif validation_type == ValidationType.CONFIGURATION:
                    self._validate_configuration(module, result, verbose, fix)
                elif validation_type == ValidationType.DOCUMENTATION:
                    self._validate_documentation(module, result, verbose, fix)
                elif validation_type == ValidationType.TEST_REFERENCES:
                    self._validate_test_references(module, result, verbose, fix)
                elif validation_type == ValidationType.OUTPUT:
                    self._validate_output(module, result, verbose, fix)

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.EXECUTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Module validation failed: {e}",
                details=str(e)
            ))

        result.duration = time.time() - start_time
        return result

    def _validate_execution(self, module: str, result: ValidationResult,
                           verbose: bool, fix: bool) -> None:
        """Validate example execution."""
        try:
            if module.startswith("multi_module/"):
                # Multi-module workflow
                script_path = self.examples_root / "multi_module" / f"{module.split('/', 1)[1]}.py"
            else:
                # Regular module example
                script_path = self.examples_root / module / "example_basic.py"

            if not script_path.exists():
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.EXECUTION,
                    severity=ValidationSeverity.ERROR,
                    message="Example script not found",
                    file_path=script_path,
                    fix_suggestion="Create example_basic.py file for this module"
                ))
                return

            # Execute the script
            exec_start = time.time()
            try:
                # Create temporary directory for output if needed
                with tempfile.TemporaryDirectory() as temp_dir:
                    env = os.environ.copy()
                    env['PYTHONPATH'] = str(self.examples_root.parent / "src")

                    # Run the script
                    process = subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=script_path.parent,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )

                    exec_time = time.time() - exec_start

                    # Check exit code
                    if process.returncode != 0:
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.EXECUTION,
                            severity=ValidationSeverity.ERROR,
                            message=f"Example execution failed with exit code {process.returncode}",
                            details=process.stderr[:500] if process.stderr else None,
                            file_path=script_path
                        ))
                    else:
                        result.metrics["execution_time"] = exec_time
                        result.metrics["exit_code"] = process.returncode

                        # Check for expected output files
                        expected_output = script_path.parent / "output"
                        if expected_output.exists():
                            result.metrics["output_files"] = len(list(expected_output.glob("*")))

                        # Check for log files
                        log_files = list(script_path.parent.glob("logs/*.log"))
                        result.metrics["log_files"] = len(log_files)

            except subprocess.TimeoutExpired:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.EXECUTION,
                    severity=ValidationSeverity.ERROR,
                    message="Example execution timed out",
                    details="Execution took longer than 5 minutes",
                    file_path=script_path
                ))
            except Exception as e:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.EXECUTION,
                    severity=ValidationSeverity.ERROR,
                    message=f"Example execution error: {e}",
                    details=str(e),
                    file_path=script_path
                ))

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.EXECUTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Execution validation failed: {e}",
                details=str(e)
            ))

    def _validate_configuration(self, module: str, result: ValidationResult,
                               verbose: bool, fix: bool) -> None:
        """Validate configuration files."""
        try:
            if module.startswith("multi_module/"):
                # Multi-module workflow configs
                config_dir = self.examples_root / "multi_module"
                yaml_file = config_dir / f"config_{module.split('/', 1)[1]}.yaml"
                json_file = config_dir / f"config_{module.split('/', 1)[1]}.json"
            else:
                # Regular module configs
                config_dir = self.examples_root / module
                yaml_file = config_dir / "config.yaml"
                json_file = config_dir / "config.json"

            # Validate YAML
            if yaml_file.exists():
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml_content = yaml.safe_load(f)

                    # Basic validation
                    if not isinstance(yaml_content, dict):
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.CONFIGURATION,
                            severity=ValidationSeverity.ERROR,
                            message="YAML config must be a dictionary at root level",
                            file_path=yaml_file
                        ))

                    result.metrics["yaml_valid"] = True

                except yaml.YAMLError as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.CONFIGURATION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid YAML syntax: {e}",
                        file_path=yaml_file
                    ))
                except Exception as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.CONFIGURATION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Failed to read YAML file: {e}",
                        file_path=yaml_file
                    ))
            else:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.CONFIGURATION,
                    severity=ValidationSeverity.WARNING,
                    message="YAML configuration file not found",
                    file_path=yaml_file,
                    fix_suggestion="Create config.yaml file for this module"
                ))

            # Validate JSON
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)

                    # Basic validation
                    if not isinstance(json_content, dict):
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.CONFIGURATION,
                            severity=ValidationSeverity.ERROR,
                            message="JSON config must be an object at root level",
                            file_path=json_file
                        ))

                    result.metrics["json_valid"] = True

                except json.JSONDecodeError as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.CONFIGURATION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid JSON syntax: {e}",
                        file_path=json_file
                    ))
                except Exception as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.CONFIGURATION,
                        severity=ValidationSeverity.ERROR,
                        message=f"Failed to read JSON file: {e}",
                        file_path=json_file
                    ))
            else:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.CONFIGURATION,
                    severity=ValidationSeverity.WARNING,
                    message="JSON configuration file not found",
                    file_path=json_file,
                    fix_suggestion="Create config.json file for this module"
                ))

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.CONFIGURATION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Configuration validation failed: {e}",
                details=str(e)
            ))

    def _validate_documentation(self, module: str, result: ValidationResult,
                               verbose: bool, fix: bool) -> None:
        """Validate documentation files."""
        try:
            if module.startswith("multi_module/"):
                # Multi-module workflow - might not have individual README
                return

            readme_file = self.examples_root / module / "README.md"

            if not readme_file.exists():
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.DOCUMENTATION,
                    severity=ValidationSeverity.ERROR,
                    message="README.md file not found",
                    file_path=readme_file,
                    fix_suggestion="Create README.md file for this module"
                ))
                return

            # Read README content
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required sections
            required_sections = ["# ", "## Overview", "## Features", "## Usage"]
            missing_sections = []

            for section in required_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)

            if missing_sections:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.DOCUMENTATION,
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing documentation sections: {', '.join(missing_sections)}",
                    file_path=readme_file,
                    fix_suggestion="Add the missing sections to README.md"
                ))

            # Check for code examples
            if "```" not in content:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.DOCUMENTATION,
                    severity=ValidationSeverity.INFO,
                    message="No code examples found in README",
                    file_path=readme_file,
                    fix_suggestion="Add code examples to demonstrate usage"
                ))

            result.metrics["readme_exists"] = True
            result.metrics["readme_length"] = len(content)
            result.metrics["has_code_examples"] = "```" in content

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.DOCUMENTATION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Documentation validation failed: {e}",
                details=str(e)
            ))

    def _validate_test_references(self, module: str, result: ValidationResult,
                                 verbose: bool, fix: bool) -> None:
        """Validate test method references."""
        try:
            if module.startswith("multi_module/"):
                # Multi-module workflows might not reference specific tests
                return

            example_file = self.examples_root / module / "example_basic.py"

            if not example_file.exists():
                return

            # Read example file
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for "Tested Methods:" section
            tested_methods_match = re.search(
                r'Tested Methods:\s*\n(.*?)(?=\n\n|\n##|\n```|\n[A-Z]|$)',
                content,
                re.DOTALL
            )

            if not tested_methods_match:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.TEST_REFERENCES,
                    severity=ValidationSeverity.WARNING,
                    message="No 'Tested Methods' section found",
                    file_path=example_file,
                    fix_suggestion="Add 'Tested Methods:' section documenting which test methods are verified"
                ))
                return

            tested_methods_text = tested_methods_match.group(1)
            result.metrics["has_tested_methods"] = True

            # Extract test method references
            test_refs = re.findall(r'(\w+)::(\w+)::(\w+)\(\)', tested_methods_text)

            if not test_refs:
                result.add_issue(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.TEST_REFERENCES,
                    severity=ValidationSeverity.WARNING,
                    message="No properly formatted test method references found",
                    details="Expected format: file::Class::method()",
                    file_path=example_file
                ))
            else:
                result.metrics["test_method_count"] = len(test_refs)

                # Basic validation of test file paths
                for file_name, class_name, method_name in test_refs:
                    # Check if test file exists (basic check)
                    test_file = self.examples_root.parent / "testing" / "unit" / f"test_{file_name}.py"
                    if not test_file.exists():
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.TEST_REFERENCES,
                            severity=ValidationSeverity.INFO,
                            message=f"Test file not found: test_{file_name}.py",
                            details=f"Referenced in: {file_name}::{class_name}::{method_name}()",
                            file_path=example_file
                        ))

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.TEST_REFERENCES,
                severity=ValidationSeverity.CRITICAL,
                message=f"Test reference validation failed: {e}",
                details=str(e)
            ))

    def _validate_output(self, module: str, result: ValidationResult,
                        verbose: bool, fix: bool) -> None:
        """Validate output files and results."""
        try:
            if module.startswith("multi_module/"):
                # Multi-module workflow outputs
                output_dir = self.examples_root / "multi_module" / "output"
            else:
                # Regular module outputs
                output_dir = self.examples_root / module / "output"

            if not output_dir.exists():
                result.metrics["output_dir_exists"] = False
                return

            result.metrics["output_dir_exists"] = True

            # Check for results files
            results_files = list(output_dir.glob("*_results.json"))
            result.metrics["results_files"] = len(results_files)

            # Validate results JSON files
            for results_file in results_files:
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results_data = json.load(f)

                    # Basic validation
                    if not isinstance(results_data, dict):
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.OUTPUT,
                            severity=ValidationSeverity.ERROR,
                            message=f"Results file must contain a JSON object: {results_file.name}",
                            file_path=results_file
                        ))
                        continue

                    # Check for required fields
                    required_fields = ["status"]
                    missing_fields = [field for field in required_fields if field not in results_data]

                    if missing_fields:
                        result.add_issue(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.OUTPUT,
                            severity=ValidationSeverity.WARNING,
                            message=f"Results file missing required fields: {', '.join(missing_fields)}",
                            file_path=results_file
                        ))

                    result.metrics["results_valid"] = True

                except json.JSONDecodeError as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.OUTPUT,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid JSON in results file: {e}",
                        file_path=results_file
                    ))
                except Exception as e:
                    result.add_issue(ValidationIssue(
                        module=module,
                        validation_type=ValidationType.OUTPUT,
                        severity=ValidationSeverity.ERROR,
                        message=f"Failed to read results file: {e}",
                        file_path=results_file
                    ))

        except Exception as e:
            result.add_issue(ValidationIssue(
                module=module,
                validation_type=ValidationType.OUTPUT,
                severity=ValidationSeverity.CRITICAL,
                message=f"Output validation failed: {e}",
                details=str(e)
            ))

    def _generate_report(self, results: Dict[str, ValidationResult],
                        validation_types: List[ValidationType]) -> Dict[str, Any]:
        """Generate validation report."""
        end_time = time.time()
        total_duration = end_time - self.start_time

        # Aggregate statistics
        total_modules = len(results)
        successful_modules = sum(1 for r in results.values() if r.success)
        total_issues = sum(len(r.issues) for r in results.values())

        # Issues by severity
        severity_counts = {
            "critical": sum(r.get_issue_count(ValidationSeverity.CRITICAL) for r in results.values()),
            "error": sum(r.get_issue_count(ValidationSeverity.ERROR) for r in results.values()),
            "warning": sum(r.get_issue_count(ValidationSeverity.WARNING) for r in results.values()),
            "info": sum(r.get_issue_count(ValidationSeverity.INFO) for r in results.values())
        }

        # Issues by validation type
        type_counts = {}
        for validation_type in validation_types:
            type_counts[validation_type.value] = sum(
                len([i for i in r.issues if i.validation_type == validation_type])
                for r in results.values()
            )

        # Issues by module
        module_issues = {}
        for module, result in results.items():
            module_issues[module] = {
                "total": len(result.issues),
                "critical": result.get_issue_count(ValidationSeverity.CRITICAL),
                "error": result.get_issue_count(ValidationSeverity.ERROR),
                "warning": result.get_issue_count(ValidationSeverity.WARNING),
                "info": result.get_issue_count(ValidationSeverity.INFO),
                "success": result.success,
                "duration": result.duration
            }

        # Overall health score (0-100)
        if total_modules == 0:
            health_score = 0
        else:
            # Weight issues by severity
            weighted_issues = (
                severity_counts["critical"] * 10 +
                severity_counts["error"] * 5 +
                severity_counts["warning"] * 2 +
                severity_counts["info"] * 1
            )
            health_score = max(0, 100 - (weighted_issues / total_modules * 10))

        return {
            "metadata": {
                "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_duration": total_duration,
                "examples_root": str(self.examples_root),
                "validation_types": [vt.value for vt in validation_types],
                "parallel_processes": self.parallel_processes
            },
            "summary": {
                "total_modules": total_modules,
                "successful_modules": successful_modules,
                "failed_modules": total_modules - successful_modules,
                "success_rate": successful_modules / total_modules if total_modules > 0 else 0,
                "total_issues": total_issues,
                "health_score": health_score,
                "severity_breakdown": severity_counts,
                "type_breakdown": type_counts
            },
            "modules": module_issues,
            "issues": [
                {
                    **issue.to_dict(),
                    "module": module
                }
                for module, result in results.items()
                for issue in result.issues
            ],
            "recommendations": self._generate_recommendations(results, severity_counts)
        }

    def _generate_recommendations(self, results: Dict[str, ValidationResult],
                                severity_counts: Dict[str, int]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Critical issues
        if severity_counts["critical"] > 0:
            recommendations.append("🔴 CRITICAL: Address critical issues immediately - these prevent basic functionality")

        # Error issues
        if severity_counts["error"] > 0:
            recommendations.append("🟠 ERRORS: Fix error-level issues - these indicate broken functionality")

        # Warning issues
        if severity_counts["warning"] > 0:
            recommendations.append("🟡 WARNINGS: Review warning issues - these indicate potential problems")

        # Execution issues
        execution_failures = sum(1 for r in results.values()
                               if any(i.validation_type == ValidationType.EXECUTION and i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
                                     for i in r.issues))
        if execution_failures > 0:
            recommendations.append(f"⚠️ EXECUTION: {execution_failures} modules have execution failures - fix to ensure examples work")

        # Missing documentation
        docs_missing = sum(1 for r in results.values()
                          if any(i.validation_type == ValidationType.DOCUMENTATION and i.severity == ValidationSeverity.ERROR
                                for i in r.issues))
        if docs_missing > 0:
            recommendations.append(f"📚 DOCUMENTATION: {docs_missing} modules missing README files - add documentation")

        # Configuration issues
        config_issues = sum(1 for r in results.values()
                           if any(i.validation_type == ValidationType.CONFIGURATION for i in r.issues))
        if config_issues > 0:
            recommendations.append(f"⚙️ CONFIGURATION: {config_issues} modules have configuration issues - validate config files")

        # Test reference issues
        test_ref_issues = sum(1 for r in results.values()
                             if any(i.validation_type == ValidationType.TEST_REFERENCES and i.severity == ValidationSeverity.WARNING
                                   for i in r.issues))
        if test_ref_issues > 0:
            recommendations.append(f"🧪 TESTING: {test_ref_issues} modules have test reference issues - verify test method links")

        # General recommendations
        if severity_counts["critical"] == 0 and severity_counts["error"] == 0:
            recommendations.append("✅ QUALITY: All critical and error issues resolved - good job!")
        else:
            recommendations.append("🔄 NEXT STEPS: Run validation again after fixes to track progress")

        return recommendations

    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save validation report in multiple formats."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # JSON report
        json_file = self.output_dir / f"validation_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # HTML report
        html_file = self.output_dir / f"validation_report_{timestamp}.html"
        html_content = self._generate_html_report(report)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Summary text report
        summary_file = self.output_dir / f"validation_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_text_summary(report))

        print(f"\n📊 Reports saved to: {self.output_dir}")
        print(f"   JSON: {json_file.name}")
        print(f"   HTML: {html_file.name}")
        print(f"   Text: {summary_file.name}")

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report."""
        summary = report["summary"]
        severity_colors = {
            "critical": "#dc3545",
            "error": "#fd7e14",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Codomyrmex Examples Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 3px; }}
        .issues {{ margin-top: 20px; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
        .module {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .recommendations {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>🔍 Codomyrmex Examples Validation Report</h1>
    <p><strong>Generated:</strong> {report["metadata"]["validation_timestamp"]}</p>
    <p><strong>Duration:</strong> {report["metadata"]["total_duration"]:.2f}s</p>

    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="metric"><strong>Modules:</strong> {summary["total_modules"]}</div>
        <div class="metric"><strong>Success Rate:</strong> {summary["success_rate"]:.1%}</div>
        <div class="metric"><strong>Health Score:</strong> {summary["health_score"]:.1f}/100</div>
        <div class="metric"><strong>Total Issues:</strong> {summary["total_issues"]}</div>
    </div>

    <h2>🔴 Issues by Severity</h2>
    <ul>
"""

        for severity, count in summary["severity_breakdown"].items():
            color = severity_colors.get(severity, "#6c757d")
            html += f'        <li style="color: {color}"><strong>{severity.upper()}:</strong> {count}</li>\n'

        html += "    </ul>\n\n    <h2>📋 Issues by Type</h2>\n    <ul>\n"

        for issue_type, count in summary["type_breakdown"].items():
            html += f"        <li><strong>{issue_type.replace('_', ' ').title()}:</strong> {count}</li>\n"

        html += "    </ul>\n\n    <div class=\"issues\">\n        <h2>🚨 Detailed Issues</h2>\n"

        for issue in report["issues"][:50]:  # Limit to first 50 for readability
            severity = issue["severity"]
            color = severity_colors.get(severity, "#6c757d")
            html += f'''
        <div class="issue" style="border-left-color: {color}">
            <strong>{issue["module"]}</strong> - {issue["validation_type"].replace("_", " ").title()}
            <span style="color: {color}">[{severity.upper()}]</span><br>
            {issue["message"]}
            {f'<br><small>{issue["details"]}</small>' if issue.get("details") else ''}
        </div>'''

        html += """
    </div>

    <div class="recommendations">
        <h2>💡 Recommendations</h2>
        <ul>
"""

        for rec in report["recommendations"]:
            html += f"            <li>{rec}</li>\n"

        html += "        </ul>\n    </div>\n</body>\n</html>"

        return html

    def _generate_text_summary(self, report: Dict[str, Any]) -> str:
        """Generate text summary report."""
        summary = report["summary"]

        text = f"""
Codomyrmex Examples Validation Summary
======================================

Generated: {report["metadata"]["validation_timestamp"]}
Duration: {report["metadata"]["total_duration"]:.2f}s
Modules Validated: {summary["total_modules"]}
Success Rate: {summary["success_rate"]:.1%}
Health Score: {summary["health_score"]:.1f}/100

Issues Summary:
- Critical: {summary["severity_breakdown"]["critical"]}
- Error: {summary["severity_breakdown"]["error"]}
- Warning: {summary["severity_breakdown"]["warning"]}
- Info: {summary["severity_breakdown"]["info"]}
- Total: {summary["total_issues"]}

Top Issues by Module:
"""

        # Sort modules by issue count
        module_issues = report["modules"]
        sorted_modules = sorted(module_issues.items(),
                              key=lambda x: x[1]["total"], reverse=True)

        for module, issues in sorted_modules[:10]:  # Top 10
            text += f"- {module}: {issues['total']} issues ({issues['critical']} critical, {issues['error']} errors)\n"

        text += "\nRecommendations:\n"
        for rec in report["recommendations"]:
            text += f"- {rec}\n"

        return text


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Comprehensive validation script for Codomyrmex examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_examples.py                          # Validate all with defaults
  python validate_examples.py --types execution,config # Validate only execution and config
  python validate_examples.py --parallel 8 --verbose   # Use 8 processes with verbose output
  python validate_examples.py --modules logging_monitoring,environment_setup  # Validate specific modules
  python validate_examples.py --fix                      # Attempt automatic fixes
        """
    )

    parser.add_argument(
        "--parallel", "-p",
        type=int,
        default=4,
        help="Number of parallel processes (default: 4)"
    )

    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("validation_reports"),
        help="Output directory for reports (default: validation_reports)"
    )

    parser.add_argument(
        "--types", "-t",
        type=lambda x: [ValidationType(t.strip()) for t in x.split(',')],
        default=[vt for vt in ValidationType],
        help=f"Comma-separated validation types: {', '.join([vt.value for vt in ValidationType])} (default: all)"
    )

    parser.add_argument(
        "--modules", "-m",
        type=lambda x: [m.strip() for m in x.split(',')] if x != 'all' else None,
        default=None,
        help="Comma-separated list of modules to validate (default: all)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix common issues automatically"
    )

    args = parser.parse_args()

    # Find examples root
    script_dir = Path(__file__).parent
    examples_root = script_dir

    # Initialize validator
    validator = ExamplesValidator(examples_root, args.output_dir, args.parallel)

    print(f"🚀 Codomyrmex Examples Validator")
    print(f"📂 Examples root: {examples_root}")
    print(f"🎯 Validation types: {', '.join([vt.value for vt in args.types])}")
    if args.modules:
        print(f"📦 Modules: {', '.join(args.modules)}")
        # Filter modules if specified
        validator.modules = [m for m in validator.modules if m in args.modules]

    print(f"📊 Modules to validate: {len(validator.modules)}")
    print()

    # Run validation
    start_time = time.time()
    report = validator.validate_all(args.types, args.verbose, args.fix)
    total_time = time.time() - start_time

    # Print final summary
    summary = report["summary"]
    print(f"\n🎉 Validation Complete!")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📦 Modules: {summary['total_modules']}")
    print(f"✅ Success rate: {summary['success_rate']:.1%}")
    print(f"🏥 Health score: {summary['health_score']:.1f}/100")
    print(f"🚨 Issues: {summary['total_issues']} total")

    # Exit with appropriate code
    if summary["health_score"] < 50:
        print("❌ Validation FAILED - critical issues found")
        sys.exit(1)
    elif summary["success_rate"] < 0.8:
        print("⚠️  Validation WARNING - low success rate")
        sys.exit(2)
    else:
        print("✅ Validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
