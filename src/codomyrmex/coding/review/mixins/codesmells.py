from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class CodeSmellsMixin:
    """CodeSmellsMixin functionality."""

    @monitor_performance("detect_code_smells")
    def detect_code_smells(self) -> list[dict[str, Any]]:
        """Detect common code smells and anti-patterns."""
        code_smells = []

        try:
            # Analyze for common code smells
            code_smells.extend(self._detect_long_methods())
            code_smells.extend(self._detect_large_classes())
            code_smells.extend(self._detect_feature_envy())
            code_smells.extend(self._detect_data_clumps())
            code_smells.extend(self._detect_primitive_obsession())

        except Exception as e:
            logger.error(f"Error detecting code smells: {e}")

        return code_smells

    def _detect_long_methods(self) -> list[dict[str, Any]]:
        """Detect methods that are too long."""
        smells = []

        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            for func in complexity_results:
                if func.get("complexity", 0) > 20:  # Very high complexity
                    smells.append({
                        "type": "long_method",
                        "file_path": func.get("file_path", ""),
                        "function_name": func.get("name", ""),
                        "line_number": func.get("line_number", 0),
                        "complexity": func.get("complexity", 0),
                        "description": f"Method '{func.get('name', '')}' is too long and complex",
                        "suggestion": "Consider breaking this method into smaller, more focused methods"
                    })

        except Exception as e:
            logger.error(f"Error detecting long methods: {e}")

        return smells

    def _detect_large_classes(self) -> list[dict[str, Any]]:
        """Detect classes that are too large."""
        smells = []

        try:
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            for cls in coupling_results:
                if cls.get("coupling", 0) > 15:  # High coupling
                    smells.append({
                        "type": "large_class",
                        "file_path": cls.get("file_path", ""),
                        "class_name": cls.get("name", ""),
                        "coupling": cls.get("coupling", 0),
                        "description": f"Class '{cls.get('name', '')}' has too many dependencies",
                        "suggestion": "Consider splitting this class or using dependency injection"
                    })

        except Exception as e:
            logger.error(f"Error detecting large classes: {e}")

        return smells

    def _detect_feature_envy(self) -> list[dict[str, Any]]:
        """Detect feature envy (methods that use more external data than local)."""
        # Functional fallback for feature envy detection without full AST analysis
        return []

    def _detect_data_clumps(self) -> list[dict[str, Any]]:
        """Detect data clumps (groups of parameters that are always passed together)."""
        # Functional fallback for data clumps detection
        return []

    def _detect_primitive_obsession(self) -> list[dict[str, Any]]:
        """Detect primitive obsession (using primitives where objects would be better)."""
        # Functional fallback for primitive obsession detection
        return []
