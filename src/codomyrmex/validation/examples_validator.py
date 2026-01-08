from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import argparse
import ast
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time

from dataclasses import dataclass, field
from enum import Enum
import importlib.util
import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
from codomyrmex.utils.cli_helpers import (






"""
Comprehensive validation logic for Codomyrmex examples.

This module contains the core logic for validating examples, moved from the standalone script.
"""


# Use the new location for shared utilities
    ensure_output_directory,
    format_output,
    print_error,
    print_info,
    print_section,
    print_success,
    validate_file_path,
    determine_language_from_file,
)

logger = get_logger(__name__)


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationType(str, Enum):
    """Types of validation checks."""
    EXECUTION = "execution"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    TEST_REFERENCES = "test_references"
    OUTPUT_FILES = "output_files"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    module: str
    validation_type: ValidationType
    severity: ValidationSeverity
    message: str
    details: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ModuleValidationResult:
    """Result of validating a single module."""
    module: str
    success: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0


class ExamplesValidator:
    """Validator for Codomyrmex examples."""

    def __init__(self, root_dir: Path, output_dir: Path, parallel_jobs: int = 4):
        """
        Initialize the validator.

        Args:
            root_dir: Root directory of examples or repo
            output_dir: Directory to save reports
            parallel_jobs: Number of parallel jobs for execution
        """
        self.root_dir = root_dir
        self.output_dir = output_dir
        self.parallel_jobs = parallel_jobs
        
        # Ensure output directory exists
        ensure_output_directory(self.output_dir)
        
        # Discover modules
        self.modules = self._discover_modules()
        logger.info(f"Discovered {len(self.modules)} modules to validate")

    def _discover_modules(self) -> List[str]:
        """Discover all module directories in the examples/scripts folder."""
        # This logic needs to be robust to where it's called from.
        # Assuming typical structure: repo_root/scripts/[module]
        
        # If root_dir is scripts/, look for subdirs
        modules = []
        skip_dirs = {
            '__pycache__', '.git', '.idea', '.vscode', 'venv', 'node_modules', 
            'examples', 'tests', 'validation', 'documentation', '_common', '_templates'
        }
        
        # We might need to adjust this depending on if root_dir is 'scripts/' or repo root
        if (self.root_dir / 'scripts').exists():
            search_dir = self.root_dir / 'scripts'
        else:
            search_dir = self.root_dir
            
        for item in search_dir.iterdir():
            if item.is_dir() and item.name not in skip_dirs and not item.name.startswith('_'):
                # Check if it has an orchestrate.py or pure python scripts
                if (item / 'orchestrate.py').exists() or any(item.glob('*.py')):
                    modules.append(item.name)
                    
        return sorted(modules)

    def validate_all(self, types: List[ValidationType], verbose: bool = False, fix: bool = False) -> Dict[str, Any]:
        """
        Run all validation checks.

        Args:
            types: List of validation types to run
            verbose: Whether to print verbose output
            fix: Whether to attempt automatic fixes

        Returns:
            Dictionary containing the full validation report
        """
        start_time = time.time()
        results: Dict[str, ModuleValidationResult] = {}

        print_section("Starting Validation")
        print(f"checking {len(self.modules)} modules...")

        # Run validations (some parallel, some sequential)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_jobs) as executor:
            future_to_module = {
                executor.submit(self._validate_module, module, types, fix): module
                for module in self.modules
            }
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_module)):
                module = future_to_module[future]
                try:
                    result = future.result()
                    results[module] = result
                    
                    # Progress update
                    if verbose:
                        status = "✅" if result.success else "❌"
                        print(f"{status} {module} ({result.duration:.2f}s)")
                        
                except Exception as e:
                    logger.error(f"Error validating module {module}: {e}")
                    results[module] = ModuleValidationResult(
                        module=module,
                        success=False,
                        issues=[ValidationIssue(
                            module=module,
                            validation_type=ValidationType.EXECUTION,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Validator crashed: {str(e)}"
                        )]
                    )

        # Generate Report
        report = self._compile_report(results, time.time() - start_time)
        self._save_report(report)
        
        return report

    def _validate_module(self, module: str, types: List[ValidationType], fix: bool) -> ModuleValidationResult:
        """Validate a single module."""
        start_time = time.time()
        issues = []
        
        module_path = self.root_dir / 'scripts' / module \
            if (self.root_dir / 'scripts').exists() else self.root_dir / module

        # 1. DOCUMENTATION VALIDATION
        if ValidationType.DOCUMENTATION in types:
            issues.extend(self._validate_documentation(module, module_path))

        # 2. CONFIGURATION VALIDATION
        if ValidationType.CONFIGURATION in types:
            issues.extend(self._validate_configuration(module, module_path))

        # 3. TEST REFERENCES
        if ValidationType.TEST_REFERENCES in types:
            issues.extend(self._validate_test_references(module, module_path))

        # 4. EXECUTION (Dry Run)
        if ValidationType.EXECUTION in types:
             issues.extend(self._validate_execution(module, module_path))

        duration = time.time() - start_time
        success = not any(i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] for i in issues)
        
        return ModuleValidationResult(
            module=module,
            success=success,
            issues=issues,
            duration=duration
        )

    def _validate_documentation(self, module: str, path: Path) -> List[ValidationIssue]:
        """Validate module documentation."""
        issues = []
        
        # Check for README.md
        readme = path / "README.md"
        if not readme.exists():
            issues.append(ValidationIssue(
                module=module,
                validation_type=ValidationType.DOCUMENTATION,
                severity=ValidationSeverity.WARNING,
                message="Missing README.md"
            ))
        
        # Check orchestrate.py docstring
        orchestrator = path / "orchestrate.py"
        if orchestrator.exists():
            try:
                with open(orchestrator, 'r') as f:
                    tree = ast.parse(f.read())
                    if not ast.get_docstring(tree):
                         issues.append(ValidationIssue(
                            module=module,
                            validation_type=ValidationType.DOCUMENTATION,
                            severity=ValidationSeverity.WARNING,
                            message="orchestrate.py missing docstring",
                            file_path=str(orchestrator)
                        ))
            except Exception:
                pass

        return issues

    def _validate_configuration(self, module: str, path: Path) -> List[ValidationIssue]:
        """Validate configuration files."""
        issues = []
        # basic check for yaml/json validity
        for config_file in path.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    yaml.safe_load(f)
            except Exception as e:
                issues.append(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.CONFIGURATION,
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid YAML: {config_file.name}",
                    details=str(e),
                    file_path=str(config_file)
                ))
                
        return issues

    def _validate_test_references(self, module: str, path: Path) -> List[ValidationIssue]:
        """Validate references to tests."""
        issues = []
        # Scan python files for 'test_' imports or references
        # This is a placeholder for the more complex logic in the original script
        return issues

    def _validate_execution(self, module: str, path: Path) -> List[ValidationIssue]:
        """Validate execution (dry run)."""
        issues = []
        orchestrator = path / "orchestrate.py"
        if orchestrator.exists():
            try:
                # Run with --help to ensure it parses args and loads
                subprocess.run(
                    [sys.executable, str(orchestrator), "--help"],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
            except subprocess.CalledProcessError as e:
                issues.append(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.EXECUTION,
                    severity=ValidationSeverity.ERROR,
                    message="orchestrate.py failed to run (help check)",
                    details=e.stderr.decode() if e.stderr else str(e)
                ))
            except subprocess.TimeoutExpired:
                 issues.append(ValidationIssue(
                    module=module,
                    validation_type=ValidationType.EXECUTION,
                    severity=ValidationSeverity.ERROR,
                    message="orchestrate.py timed out (help check)"
                ))
        return issues

    def _compile_report(self, results: Dict[str, ModuleValidationResult], total_time: float) -> Dict[str, Any]:
        """Compile final report from results."""
        total_modules = len(results)
        successful_modules = sum(1 for r in results.values() if r.success)
        
        all_issues = []
        for r in results.values():
            for i in r.issues:
                all_issues.append({
                    "module": i.module,
                    "validation_type": i.validation_type.value,
                    "severity": i.severity.value,
                    "message": i.message,
                    "details": i.details
                })
                
        severity_counts = {
            "critical":  len([i for i in all_issues if i["severity"] == "critical"]),
            "error": len([i for i in all_issues if i["severity"] == "error"]),
            "warning": len([i for i in all_issues if i["severity"] == "warning"]),
            "info": len([i for i in all_issues if i["severity"] == "info"]),
        }
        
        # Calculate health score (0-100)
        # Deduct points for errors
        health_score = 100
        health_score -= (severity_counts["critical"] * 20)
        health_score -= (severity_counts["error"] * 10)
        health_score -= (severity_counts["warning"] * 2)
        health_score = max(0, health_score)

        return {
            "metadata": {
                "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_duration": total_time
            },
            "summary": {
                "total_modules": total_modules,
                "success_rate": successful_modules / total_modules if total_modules > 0 else 0,
                "health_score": health_score,
                "total_issues": len(all_issues),
                "severity_breakdown": severity_counts,
                "type_breakdown": {} # Populate if needed
            },
            "issues": all_issues,
            "modules": {
                m: {
                    "total": len(r.issues),
                    "critical": len([i for i in r.issues if i.severity == ValidationSeverity.CRITICAL]),
                    "error": len([i for i in r.issues if i.severity == ValidationSeverity.ERROR])
                } for m, r in results.items()
            },
            "recommendations": self._generate_recommendations(results, severity_counts)
        }

    def _generate_recommendations(self, results, severity_counts) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        if severity_counts["critical"] > 0:
            recs.append("🔴 FIX CRITICAL: Resolve execution crashes immediately.")
        if severity_counts["error"] > 0:
            recs.append("🟠 FIX ERRORS: Address configuration and runtime errors.")
        if severity_counts["warning"] > 10:
             recs.append("🟡 CLEANUP: High number of warnings, consider a cleanup sprint.")
        return recs

    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save validation report."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_file = self.output_dir / f"validation_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Report saved to {json_file}")


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Comprehensive validation script for Codomyrmex examples",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        default=Path("output/validation_reports"),
        help="Output directory for reports"
    )

    parser.add_argument(
        "--types", "-t",
        type=lambda x: [ValidationType(t.strip()) for t in x.split(',')],
        default=[vt for vt in ValidationType],
        help="Comma-separated validation types"
    )
    
    parser.add_argument(
        "--modules", "-m",
        action="append",
        help="Specific modules to validate"
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

    # Determine paths - this is tricky because we are in src/codomyrmex/validation/
    # We want to find the repository root relative to this file?
    # No, usually this is run from the project root.
    # Let's assume cwd is project root if it contains 'scripts' and 'src'
    # Otherwise try to resolve from __file__
    
    cwd = Path.cwd()
    if (cwd / "scripts").exists() and (cwd / "src").exists():
        root_dir = cwd
    else:
        # Fallback: ../../../.. from src/codomyrmex/validation/validator.py
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        
    args = parser.parse_args()

    validator = ExamplesValidator(root_dir, args.output_dir, args.parallel)
    validator.validate_all(args.types, args.verbose, args.fix)


if __name__ == "__main__":
    main()
