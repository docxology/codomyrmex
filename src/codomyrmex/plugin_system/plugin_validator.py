from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import json
import logging
import os
import re

from dataclasses import dataclass, field
import hashlib
import importlib.util
import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger






"""
Plugin Validator for Codomyrmex Plugin System

This module provides validation and security scanning
for plugins before they are loaded into the system.
"""


# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of plugin validation."""
    plugin_path: str
    is_valid: bool
    security_score: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_issue(self, severity: str, category: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Add a validation issue."""
        issue = {
            "severity": severity,
            "category": category,
            "message": message,
            "details": details or {}
        }

        if severity == "error":
            self.issues.append(issue)
            self.is_valid = False
        elif severity == "warning":
            self.warnings.append(issue)

        # Adjust security score
        if severity == "error":
            self.security_score -= 20
        elif severity == "warning":
            self.security_score -= 5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_path": self.plugin_path,
            "is_valid": self.is_valid,
            "security_score": max(0.0, min(100.0, self.security_score)),
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings),
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations
        }


class PluginValidator:
    """
    Comprehensive plugin validator with security scanning capabilities.

    Performs static analysis, dependency checking, security scanning,
    and compatibility validation for plugin safety and reliability.
    """

    def __init__(self):
        """Initialize the plugin validator."""
        self.risky_imports = {
            'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
            'eval', 'exec', 'compile', '__import__', 'importlib.import_module',
            'sys.modules', 'sys.path', 'builtins', 'pickle.loads', 'pickle.load',
            'yaml.load', 'yaml.unsafe_load'
        }

        self.suspicious_patterns = [
            r'\b(rm\s+-rf\s+/|\brm\s+-rf\s+\$HOME)',
            r'\bchmod\s+777\b',
            r'\bpasswd\b|\bshadow\b',
            r'\b/etc/passwd\b|\b/etc/shadow\b',
            r'\b~/.ssh\b|\b~/.aws\b',
            r'\bPRIVATE_KEY\b|\bSECRET_KEY\b|\bAPI_KEY\b',
            r'\bsocket\.',  # Network operations
            r'\bthreading\.|\bmultiprocessing\.',  # Multi-threading
        ]

    def validate_plugin(self, plugin_path: str) -> ValidationResult:
        """
        Perform validation of a plugin.

        Args:
            plugin_path: Path to the plugin file or directory

        Returns:
            ValidationResult with detailed findings
        """
        plugin_path = Path(plugin_path)
        result = ValidationResult(
            plugin_path=str(plugin_path),
            is_valid=True,
            security_score=100.0
        )

        try:
            # Basic file validation
            self._validate_file_structure(plugin_path, result)

            # Security analysis
            self._analyze_security(plugin_path, result)

            # Code quality checks
            self._analyze_code_quality(plugin_path, result)

            # Metadata validation
            self._validate_metadata(plugin_path, result)

            # Generate recommendations
            self._generate_recommendations(result)

        except Exception as e:
            logger.error(f"Error during plugin validation: {e}")
            result.add_issue("error", "validation_error", f"Validation failed: {e}")

        return result

    def check_plugin_security(self, plugin_path: str) -> List[str]:
        """
        Perform security-focused validation of a plugin.

        Args:
            plugin_path: Path to the plugin

        Returns:
            List of security issues found
        """
        result = self.validate_plugin(plugin_path)
        issues = []

        for issue in result.issues + result.warnings:
            if issue["category"] in ["security", "suspicious_code", "unsafe_import"]:
                issues.append(f"{issue['severity'].upper()}: {issue['message']}")

        return issues

    def validate_plugin_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Validate plugin metadata.

        Args:
            metadata: Plugin metadata dictionary

        Returns:
            List of validation errors
        """
        errors = []
        required_fields = ["name", "version", "description", "author", "entry_point"]

        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        # Validate version format
        if "version" in metadata:
            version = metadata["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                errors.append("Version must be in format x.y.z")

        # Validate entry point
        if "entry_point" in metadata:
            entry_point = metadata["entry_point"]
            if not entry_point.endswith('.py'):
                errors.append("Entry point must be a Python file (.py)")

        return errors

    def check_plugin_dependencies(self, dependencies: List[str]) -> List[str]:
        """
        Check if plugin dependencies are safe and available.

        Args:
            dependencies: List of dependency package names

        Returns:
            List of dependency issues
        """
        issues = []

        risky_packages = {
            "cryptography": "May contain cryptographic functions",
            "requests": "Network operations enabled",
            "paramiko": "SSH client functionality",
            "fabric": "Remote execution capabilities",
            "docker": "Container management",
            "kubernetes": "Cluster management",
            "boto3": "AWS API access",
            "google-cloud": "Google Cloud API access"
        }

        for dep in dependencies:
            if dep in risky_packages:
                issues.append(f"Risky dependency '{dep}': {risky_packages[dep]}")

        return issues

    def _validate_file_structure(self, plugin_path: Path, result: ValidationResult) -> None:
        """Validate plugin file structure."""
        if not plugin_path.exists():
            result.add_issue("error", "file_structure", f"Plugin path does not exist: {plugin_path}")
            return

        if plugin_path.is_file():
            if not plugin_path.suffix == '.py':
                result.add_issue("error", "file_structure", "Plugin must be a Python file (.py)")
            return

        # Directory plugin
        if plugin_path.is_dir():
            py_files = list(plugin_path.glob("*.py"))
            if not py_files:
                result.add_issue("error", "file_structure", "Plugin directory contains no Python files")

            # Check for __init__.py
            init_file = plugin_path / "__init__.py"
            if not init_file.exists():
                result.add_issue("warning", "file_structure", "Plugin directory missing __init__.py")

    def _analyze_security(self, plugin_path: Path, result: ValidationResult) -> None:
        """Analyze plugin for security issues."""
        if plugin_path.is_file():
            files_to_check = [plugin_path]
        else:
            files_to_check = list(plugin_path.glob("*.py"))

        for file_path in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check for risky imports
                for risky_import in self.risky_imports:
                    if risky_import in content:
                        result.add_issue(
                            "warning", "unsafe_import",
                            f"Potentially unsafe import '{risky_import}' in {file_path.name}",
                            {"file": file_path.name, "import": risky_import}
                        )

                # Check for suspicious patterns
                for pattern in self.suspicious_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        result.add_issue(
                            "error", "suspicious_code",
                            f"Suspicious code pattern found in {file_path.name}: {pattern}",
                            {"file": file_path.name, "pattern": pattern, "matches": matches}
                        )

                # Check for hardcoded secrets
                secrets_pattern = r'(?i)(api_key|secret|password|token)\s*[=:]\s*["\'][^"\']+["\']'
                secret_matches = re.findall(secrets_pattern, content)
                if secret_matches:
                    result.add_issue(
                        "error", "hardcoded_secrets",
                        f"Potential hardcoded secrets found in {file_path.name}",
                        {"file": file_path.name, "matches": secret_matches}
                    )

                # Check for excessive file operations
                file_ops = len(re.findall(r'\bopen\s*\(', content))
                if file_ops > 10:
                    result.add_issue(
                        "warning", "excessive_file_ops",
                        f"High number of file operations in {file_path.name} ({file_ops})",
                        {"file": file_path.name, "operations": file_ops}
                    )

            except Exception as e:
                result.add_issue("error", "analysis_error", f"Could not analyze {file_path.name}: {e}")

    def _analyze_code_quality(self, plugin_path: Path, result: ValidationResult) -> None:
        """Analyze plugin code quality."""
        if plugin_path.is_file():
            files_to_check = [plugin_path]
        else:
            files_to_check = list(plugin_path.glob("*.py"))

        total_lines = 0
        total_functions = 0
        total_classes = 0

        for file_path in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                file_lines = len([line for line in lines if line.strip()])
                total_lines += file_lines

                # Count functions and classes
                functions = len(re.findall(r'\bdef\s+\w+', content))
                classes = len(re.findall(r'\bclass\s+\w+', content))
                total_functions += functions
                total_classes += classes

                # Check function length
                function_blocks = re.findall(r'def\s+\w+.*?:.*?(?=\n\S|\n\n|\Z)', content, re.DOTALL)
                for block in function_blocks:
                    lines_in_function = len(block.split('\n'))
                    if lines_in_function > 50:
                        result.add_issue(
                            "warning", "long_function",
                            f"Very long function in {file_path.name} ({lines_in_function} lines)",
                            {"file": file_path.name, "lines": lines_in_function}
                        )

            except Exception as e:
                result.add_issue("warning", "quality_check_error", f"Could not analyze quality for {file_path.name}: {e}")

        # Overall quality checks
        if total_lines > 1000:
            result.add_issue("warning", "large_plugin", f"Plugin is quite large ({total_lines} lines)")

        if total_functions == 0:
            result.add_issue("warning", "no_functions", "Plugin contains no functions")

    def _validate_metadata(self, plugin_path: Path, result: ValidationResult) -> None:
        """Validate plugin metadata."""
        metadata_files = ["plugin.json", "plugin.yaml", "plugin.yml", "setup.py", "pyproject.toml"]

        metadata_found = False
        for metadata_file in metadata_files:
            metadata_path = plugin_path / metadata_file if plugin_path.is_dir() else plugin_path.parent / metadata_file

            if metadata_path.exists():
                metadata_found = True

                try:
                    if metadata_file.endswith('.json'):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                    elif metadata_file.endswith(('.yaml', '.yml')):
                        with open(metadata_path, 'r') as f:
                            metadata = yaml.safe_load(f)
                    elif metadata_file == 'setup.py':
                        # Extract metadata from setup.py (simplified)
                        metadata = {"name": "unknown", "version": "0.0.0"}
                    else:
                        continue

                    # Validate metadata
                    metadata_errors = self.validate_plugin_metadata(metadata)
                    for error in metadata_errors:
                        result.add_issue("error", "metadata", error)

                    # Check dependencies
                    if "dependencies" in metadata:
                        dep_issues = self.check_plugin_dependencies(metadata["dependencies"])
                        for issue in dep_issues:
                            result.add_issue("warning", "dependencies", issue)

                except Exception as e:
                    result.add_issue("error", "metadata", f"Could not parse {metadata_file}: {e}")

        if not metadata_found:
            result.add_issue("warning", "metadata", "No plugin metadata file found")

    def _generate_recommendations(self, result: ValidationResult) -> None:
        """Generate recommendations based on validation results."""
        recommendations = []

        if result.security_score < 50:
            recommendations.append("Plugin has significant security issues - consider code review")
        elif result.security_score < 80:
            recommendations.append("Address security warnings to improve plugin safety")

        if len(result.issues) > 5:
            recommendations.append("Plugin has many validation issues - consider refactoring")

        if not any(issue["category"] == "metadata" for issue in result.issues):
            recommendations.append("Ensure plugin has proper metadata and documentation")

        if any(issue["category"] == "unsafe_import" for issue in result.issues):
            recommendations.append("Review and minimize use of potentially unsafe imports")

        if any(issue["category"] == "suspicious_code" for issue in result.issues):
            recommendations.append("Remove or secure suspicious code patterns")

        result.recommendations = recommendations


# Convenience functions

def validate_plugin(plugin_path: str) -> ValidationResult:
    """
    Convenience function to validate a plugin.

    Args:
        plugin_path: Path to the plugin

    Returns:
        ValidationResult
    """
    validator = PluginValidator()
    return validator.validate_plugin(plugin_path)


def check_plugin_security(plugin_path: str) -> List[str]:
    """
    Convenience function to check plugin security.

    Args:
        plugin_path: Path to the plugin

    Returns:
        List of security issues
    """
    validator = PluginValidator()
    return validator.check_plugin_security(plugin_path)


def validate_plugin_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Convenience function to validate plugin metadata.

    Args:
        metadata: Plugin metadata

    Returns:
        List of validation errors
    """
    validator = PluginValidator()
    return validator.validate_plugin_metadata(metadata)
