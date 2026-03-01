import os

from codomyrmex.coding.review.models import (
    ArchitectureViolation,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class ArchitectureMixin:
    """ArchitectureMixin functionality."""

    @monitor_performance("analyze_architecture_compliance")
    def analyze_architecture_compliance(self) -> list[ArchitectureViolation]:
        """Analyze architecture compliance and identify violations."""
        violations = []

        try:
            # This would typically use pyscn's system analysis
            # For now, implement basic checks
            violations.extend(self._check_layering_violations())
            violations.extend(self._check_circular_dependencies())
            violations.extend(self._check_naming_conventions())

        except Exception as e:
            logger.error(f"Error analyzing architecture compliance: {e}")

        return violations

    def _check_layering_violations(self) -> list[ArchitectureViolation]:
        """Check for layering violations in the architecture."""
        violations = []

        # Check if data access layer depends on presentation layer
        presentation_files = self._find_files_in_layer("presentation")
        data_files = self._find_files_in_layer("data")

        for data_file in data_files:
            # This is a simplified check - in reality would need AST analysis
            if self._file_imports_presentation_layer(data_file, presentation_files):
                violations.append(ArchitectureViolation(
                    file_path=data_file,
                    violation_type="layering_violation",
                    description="Data layer should not depend on presentation layer",
                    severity="high",
                    suggestion="Move shared code to a common layer or use dependency injection",
                    affected_modules=["data_access", "presentation"]
                ))

        return violations

    def _check_circular_dependencies(self) -> list[ArchitectureViolation]:
        """Check for circular dependencies."""
        violations = []

        # This would require more sophisticated analysis
        # For now, return empty list
        return violations

    def _check_naming_conventions(self) -> list[ArchitectureViolation]:
        """Check naming convention compliance."""
        violations = []

        # Check for files that don't follow naming conventions
        for root, _dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Check if test files follow naming convention
                    if 'test' in file.lower() and not file.startswith('test_') and not file.endswith('_test.py'):
                        violations.append(ArchitectureViolation(
                            file_path=file_path,
                            violation_type="naming_convention",
                            description=f"Test file '{file}' should follow naming convention (test_*.py or *_test.py)",
                            severity="low",
                            suggestion="Rename file to follow test naming conventions"
                        ))

        return violations

    def _find_files_in_layer(self, layer: str) -> list[str]:
        """Find files belonging to a specific architectural layer."""
        layer_patterns = {
            "presentation": ["ui", "interface", "view", "controller", "handler"],
            "business": ["service", "manager", "orchestrator", "engine"],
            "data": ["repository", "dao", "model", "entity"]
        }

        matching_files = []
        patterns = layer_patterns.get(layer, [])

        for root, _dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Simple pattern matching
                    for pattern in patterns:
                        if pattern.lower() in file.lower() or pattern.lower() in root.lower():
                            matching_files.append(file_path)
                            break

        return matching_files

    def _file_imports_presentation_layer(self, file_path: str, presentation_files: list[str]) -> bool:
        """Check if a file imports from presentation layer (simplified check)."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Look for import statements that might reference presentation layer
            for pres_file in presentation_files:
                pres_module = os.path.splitext(os.path.basename(pres_file))[0]
                if f"from {pres_module} import" in content or f"import {pres_module}" in content:
                    return True

        except Exception as e:
            logger.debug("Error checking layer violation for %s: %s", business_file, e)

        return False
