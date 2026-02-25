import os
import re
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


class PerformanceMixin:
    """PerformanceMixin functionality."""

    @monitor_performance("optimize_performance")
    def optimize_performance(self) -> dict[str, Any]:
        """Generate performance optimization suggestions."""
        optimizations = {
            "memory_optimizations": [],
            "cpu_optimizations": [],
            "io_optimizations": [],
            "caching_opportunities": []
        }

        try:
            # Analyze for common performance issues
            optimizations["memory_optimizations"] = self._find_memory_optimizations()
            optimizations["cpu_optimizations"] = self._find_cpu_optimizations()
            optimizations["io_optimizations"] = self._find_io_optimizations()
            optimizations["caching_opportunities"] = self._find_caching_opportunities()

        except Exception as e:
            logger.error(f"Error generating performance optimizations: {e}")

        return optimizations

    def _find_memory_optimizations(self) -> list[str]:
        """Find potential memory optimization opportunities."""
        suggestions = [
            "Use generators instead of lists for large datasets",
            "Implement object pooling for frequently created objects",
            "Use slots in classes to reduce memory overhead",
            "Consider lazy loading for expensive resources"
        ]
        return suggestions

    def _find_cpu_optimizations(self) -> list[str]:
        """Find potential CPU optimization opportunities."""
        suggestions = [
            "Cache expensive computations",
            "Use sets for membership tests instead of lists",
            "Avoid repeated string concatenations",
            "Use list comprehensions instead of loops where appropriate"
        ]
        return suggestions

    def _find_io_optimizations(self) -> list[str]:
        """Find potential I/O optimization opportunities."""
        suggestions = [
            "Batch file operations",
            "Use buffered I/O for large files",
            "Consider asynchronous I/O for network operations",
            "Use compression for large data transfers"
        ]
        return suggestions

    def _find_caching_opportunities(self) -> list[str]:
        """Find potential caching opportunities."""
        suggestions = [
            "Cache parsed configuration files",
            "Cache expensive database queries",
            "Cache computed results with TTL",
            "Use Redis/Memcached for distributed caching"
        ]
        return suggestions

    def _calculate_performance_score(self) -> float:
        """Calculate performance score based on complexity and code patterns."""
        try:
            # Get complexity data
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            if not complexity_results:
                return 80.0  # Default if no data

            # Calculate complexity metrics
            complexities = [r.get("complexity", 0) for r in complexity_results]
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0
            max_complexity = max(complexities) if complexities else 0

            # Performance anti-patterns to check
            performance_patterns = {
                'for.*for.*for': 5,  # Triple nested loops
                r'\.append\(.*for.*in': 2,  # Appending in loop (should use list comp)
                'time.sleep': 1,  # Blocking sleep
                'global ': 2,  # Global state
            }

            pattern_penalty = 0.0
            try:
                for root, _dirs, files in os.walk(self.project_root):
                    for f in files:
                        if f.endswith('.py'):
                            filepath = os.path.join(root, f)
                            try:
                                with open(filepath, encoding='utf-8', errors='ignore') as fh:
                                    content = fh.read()

                                    for pattern, penalty in performance_patterns.items():
                                        matches = re.findall(pattern, content)
                                        pattern_penalty += len(matches) * penalty
                            except OSError:
                                continue
                    if len(root.split(os.sep)) - len(str(self.project_root).split(os.sep)) > 3:
                        break
            except Exception:
                pass

            # Performance score calculation
            base_score = 100.0
            complexity_penalty = min(avg_complexity * 1.5, 25.0)
            max_complexity_penalty = min(max_complexity * 0.5, 15.0) if max_complexity > 20 else 0
            pattern_penalty = min(pattern_penalty, 25.0)

            score = max(0.0, base_score - complexity_penalty - max_complexity_penalty - pattern_penalty)
            return round(score, 1)

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 50.0
