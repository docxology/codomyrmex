"""
Plugin Validator for Codomyrmex Plugin System

This module provides validation logic for plugins, including metadata
checks, dependency verification, and security scanning.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Any

from ..core.plugin_registry import Plugin, PluginInfo


@dataclass
class ValidationResult:
    """Represents the results of a plugin validation."""
    valid: bool = True
    issues: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    security_score: float = 100.0



class PluginValidator:
    """
    Validator for Codomyrmex plugins.
    """

    def __init__(self):
        """Initialize the validator."""
        self.rules = []
        self.risky_imports = ['os', 'subprocess', 'shutil', 'socket', 'requests', 'urllib']
        self.suspicious_patterns = [
            (r'os\.system\(', 'Direct shell command execution'),
            (r'subprocess\.', 'Subprocess execution'),
            (r'eval\(', 'Code evaluation'),
            (r'exec\(', 'Explicit code execution'),
            (r'open\(.*w', 'Write access to filesystem'),
            (r'rm\s+-rf', 'Recursive deletion command'),
            (r'chmod', 'Permission modification'),
            (r'sk-[a-zA-Z0-9]{32}', 'Possible hardcoded API key')
        ]
        self.safe_dependencies = {"requests", "click", "pyyaml", "pytest"}
        self.risky_dependencies = {"cryptography", "paramiko", "docker", "os", "subprocess"}

    def validate(self, plugin: Plugin) -> ValidationResult:
        """Validate a plugin instance."""
        result = ValidationResult()
        required_methods = ['initialize', 'shutdown']
        for method in required_methods:
            if not hasattr(plugin, method):
                result.valid = False
                result.issues.append({
                    'type': 'compatibility',
                    'message': f"Plugin missing required method: {method}",
                    'severity': 'error'
                })
        return result

    def validate_plugin_metadata(self, metadata: dict[str, Any]) -> ValidationResult:
        """Validate plugin metadata dictionary."""
        result = ValidationResult()
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in metadata:
                result.valid = False
                result.issues.append({'type': 'metadata', 'message': f"Missing field: {field}", 'severity': 'error'})
        return result

    def check_plugin_dependencies(self, dependencies_or_info: PluginInfo | list[str],
                                 available_plugins: list[str] | None = None) -> ValidationResult:
        """Check if plugin dependencies are satisfied."""
        result = ValidationResult()
        deps = []
        if isinstance(dependencies_or_info, PluginInfo):
            deps = dependencies_or_info.dependencies
        else:
            deps = dependencies_or_info

        for dep in deps:
            # If available_plugins is provided, use it for strict check
            if available_plugins is not None:
                if dep not in available_plugins:
                    result.valid = False
                    result.issues.append({'type': 'dependency', 'message': f"Missing dependency: {dep}", 'severity': 'error'})
            else:
                # If not provided, check against risky/safe lists
                if dep in self.risky_dependencies:
                    result.warnings.append({'type': 'dependency', 'message': f"Risky dependency: {dep}", 'severity': 'warning'})
                elif dep in self.safe_dependencies:
                    pass # Explicitly safe

        return result


    def validate_dockerfile(self, content: str) -> ValidationResult:
        """Validate a plugin Dockerfile."""
        result = ValidationResult()
        if "FROM" not in content:
            result.valid = False
            result.issues.append({'type': 'docker', 'message': "Missing FROM instruction", 'severity': 'error'})

        # Security checks
        if "chmod 777" in content:
            result.valid = False
            result.issues.append({'type': 'security', 'message': "Broad permissions detected", 'severity': 'error'})
        if "USER root" in content:
            result.warnings.append({'type': 'security', 'message': "Running as root is discouraged", 'severity': 'warning'})

        return result

    def validate_plugin(self, target: Any) -> ValidationResult:
        """
        Validate a plugin (can be a file path or a plugin object).
        """
        if isinstance(target, str) and os.path.exists(target):
            return self._scan_file_security(target)
        elif hasattr(target, 'info'):
            return self.validate(target)
        else:
            return ValidationResult()

    def _scan_file_security(self, file_path: str) -> ValidationResult:
        """Perform security scan on a plugin file."""
        result = ValidationResult()
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            issues_found = 0
            for imp in self.risky_imports:
                if re.search(fr'\bimport\s+{imp}\b|\bfrom\s+{imp}\s+import\b', content):
                    result.warnings.append({'type': 'security', 'message': f"Risky import detected: {imp}", 'severity': 'warning'})
                    issues_found += 1
            for pattern, description in self.suspicious_patterns:
                if re.search(pattern, content):
                    result.issues.append({'type': 'security', 'message': f"Dangerous pattern found: {description}", 'severity': 'error'})
                    issues_found += 1
            result.security_score = max(0, 100 - (issues_found * 20))
            if issues_found > 0:
                result.valid = False
        except Exception as e:
            result.valid = False
            result.issues.append({'type': 'security', 'message': f"Error scanning file: {e}", 'severity': 'error'})
        return result


def validate_plugin(plugin: Any) -> ValidationResult:
    """Helper function for plugin validation."""
    validator = PluginValidator()
    return validator.validate_plugin(plugin)
