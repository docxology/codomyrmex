"""Plugin Validator for Codomyrmex Plugin System.

Validates plugins for compatibility and security.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of plugin validation."""
    valid: bool
    plugin_name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PluginValidator:
    """Validates plugins for compatibility and security."""

    def __init__(self):
        """Initialize validator."""
        self.required_methods = ["initialize", "shutdown", "info"]

    def validate(self, plugin: Any, plugin_name: str) -> ValidationResult:
        """Validate a plugin."""
        errors = []
        warnings = []

        # Check required methods
        for method in self.required_methods:
            if not hasattr(plugin, method) or not callable(getattr(plugin, method)):
                errors.append(f"Missing required method: {method}")

        # Check info property
        if hasattr(plugin, "info"):
            try:
                info = plugin.info
                if not hasattr(info, "name") or not hasattr(info, "version"):
                    errors.append("Plugin info missing required fields: name, version")
            except Exception as e:
                errors.append(f"Failed to get plugin info: {e}")

        return ValidationResult(
            valid=len(errors) == 0,
            plugin_name=plugin_name,
            errors=errors,
            warnings=warnings
        )

    def validate_all(self, plugins: Dict[str, Any]) -> List[ValidationResult]:
        """Validate multiple plugins."""
        results = []
        for name, plugin in plugins.items():
            result = self.validate(plugin, name)
            results.append(result)
        return results


# Convenience functions
def validate_plugin(plugin: Any, name: str) -> ValidationResult:
    """Validate a single plugin."""
    validator = PluginValidator()
    return validator.validate(plugin, name)
