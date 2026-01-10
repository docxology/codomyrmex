"""
Metrics Collection

Collects and aggregates execution metrics for analysis and reporting.
"""

from typing import Any, Dict, List

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class MetricsCollector:
    """Collect and aggregate execution metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: List[Dict[str, Any]] = []

    def record_execution(self, execution_result: Dict[str, Any]) -> None:
        """Record an execution result for metrics collection."""
        metric = {
            "timestamp": execution_result.get("timestamp"),
            "language": execution_result.get("language"),
            "status": execution_result.get("status"),
            "execution_time": execution_result.get("execution_time", 0),
            "exit_code": execution_result.get("exit_code", -1),
            "resource_usage": execution_result.get("resource_usage", {}),
        }
        self.metrics.append(metric)

    def get_language_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics grouped by programming language."""
        language_stats = {}

        for metric in self.metrics:
            language = metric.get("language", "unknown")
            if language not in language_stats:
                language_stats[language] = {
                    "count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "total_execution_time": 0,
                    "average_execution_time": 0,
                }

            stats = language_stats[language]
            stats["count"] += 1
            if metric.get("status") == "success":
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            stats["total_execution_time"] += metric.get("execution_time", 0)

        # Calculate averages
        for language, stats in language_stats.items():
            if stats["count"] > 0:
                stats["average_execution_time"] = stats["total_execution_time"] / stats["count"]

        return language_stats

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all collected metrics."""
        if not self.metrics:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "average_execution_time": 0,
            }

        total = len(self.metrics)
        success_count = sum(1 for m in self.metrics if m.get("status") == "success")
        total_time = sum(m.get("execution_time", 0) for m in self.metrics)
        avg_time = total_time / total if total > 0 else 0

        return {
            "total_executions": total,
            "success_count": success_count,
            "error_count": total - success_count,
            "success_rate": round(success_count / total * 100, 2) if total > 0 else 0,
            "average_execution_time": round(avg_time, 3),
            "total_execution_time": round(total_time, 3),
        }

    def clear(self) -> None:
        """Clear all collected metrics."""
        self.metrics.clear()
