from typing import Any, Dict, Optional
import time

from codomyrmex.logging_monitoring.logger_config import get_logger














"""
Execution Monitoring

Monitors code execution status and provides execution tracking capabilities.
"""



logger = get_logger(__name__)


class ExecutionMonitor:
    """Monitor execution status and track execution metrics."""

    def __init__(self):
        """Initialize the execution monitor."""
        self.executions = []
        self.start_time = None
        self.end_time = None

    def start_execution(self, execution_id: str, language: str, code_length: int) -> None:
        """Start tracking an execution."""
        self.start_time = time.time()
        self.executions.append({
            "execution_id": execution_id,
            "language": language,
            "code_length": code_length,
            "start_time": self.start_time,
            "status": "running",
        })
        logger.info(f"Started execution {execution_id} ({language})")

    def end_execution(self, execution_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        """End tracking an execution."""
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time if self.start_time else 0

        for execution in self.executions:
            if execution["execution_id"] == execution_id:
                execution["end_time"] = self.end_time
                execution["execution_time"] = execution_time
                execution["status"] = status
                if result:
                    execution["result"] = result
                break

        logger.info(f"Ended execution {execution_id} ({status}) in {execution_time:.3f}s")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about all tracked executions."""
        if not self.executions:
            return {
                "total_executions": 0,
                "average_execution_time": 0,
                "success_count": 0,
                "error_count": 0,
            }

        completed = [e for e in self.executions if "execution_time" in e]
        success_count = sum(1 for e in completed if e.get("status") == "success")
        error_count = sum(1 for e in completed if e.get("status") != "success")

        execution_times = [e["execution_time"] for e in completed]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0

        return {
            "total_executions": len(self.executions),
            "completed_executions": len(completed),
            "average_execution_time": round(avg_time, 3),
            "success_count": success_count,
            "error_count": error_count,
        }

