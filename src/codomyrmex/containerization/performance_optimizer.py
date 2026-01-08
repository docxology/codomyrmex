from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import json
import time

from dataclasses import dataclass
import statistics

from codomyrmex.logging_monitoring.logger_config import get_logger







#!/usr/bin/env python3

Container Performance Optimization Module for Codomyrmex Containerization.

This module provides container performance optimization, resource monitoring,
and efficiency improvements.
"""

logger = get_logger(__name__)

@dataclass
class ContainerMetrics:
    """Container performance metrics."""
    container_id: str
    cpu_usage_percent: float
    memory_usage_mb: float
    network_io_bytes: int
    disk_io_bytes: int
    timestamp: datetime
    container_name: str = ""
    image_name: str = ""

@dataclass
class OptimizationSuggestion:
    """Container optimization suggestion."""
    category: str  # "resource_limits", "base_image", "layer_optimization", etc.
    title: str
    description: str
    estimated_impact: str  # "high", "medium", "low"
    implementation_effort: str  # "low", "medium", "high"
    steps: list[str]
    expected_savings: dict[str, Any]

class ContainerOptimizer:
    """Container performance optimization system."""

    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize container optimizer.

        Args:
            workspace_dir: Workspace directory for optimization data
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.optimization_data_dir = self.workspace_dir / "container_optimization"
        self._ensure_directories()

        self._metrics_history: list[ContainerMetrics] = []
        self._suggestions: list[OptimizationSuggestion] = []

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.optimization_data_dir.mkdir(parents=True, exist_ok=True)

    def record_metrics(self, container_id: str, metrics: dict[str, Any]):
        """Record container performance metrics.

        Args:
            container_id: Container ID
            metrics: Performance metrics data
        """
        metric = ContainerMetrics(
            container_id=container_id,
            cpu_usage_percent=metrics.get("cpu_percent", 0.0),
            memory_usage_mb=metrics.get("memory_mb", 0.0),
            network_io_bytes=metrics.get("network_io", 0),
            disk_io_bytes=metrics.get("disk_io", 0),
            timestamp=datetime.now(),
            container_name=metrics.get("name", ""),
            image_name=metrics.get("image", "")
        )

        self._metrics_history.append(metric)

        # Keep only recent metrics (last 1000)
        if len(self._metrics_history) > 1000:
            self._metrics_history = self._metrics_history[-1000:]

        logger.debug(f"Recorded metrics for container {container_id}")

    def analyze_performance(self, container_id: str, hours: int = 24) -> dict[str, Any]:
        """Analyze container performance over time.

        Args:
            container_id: Container ID to analyze
            hours: Hours of history to analyze

        Returns:
            Performance analysis results
        """
        # Filter metrics for this container
        cutoff_time = datetime.now() - timedelta(hours=hours)
        container_metrics = [
            m for m in self._metrics_history
            if m.container_id == container_id and m.timestamp >= cutoff_time
        ]

        if not container_metrics:
            return {
                "container_id": container_id,
                "analysis_period_hours": hours,
                "metrics_count": 0,
                "message": "No metrics found for analysis"
            }

        # Calculate statistics
        cpu_usage = [m.cpu_usage_percent for m in container_metrics]
        memory_usage = [m.memory_usage_mb for m in container_metrics]

        analysis = {
            "container_id": container_id,
            "analysis_period_hours": hours,
            "metrics_count": len(container_metrics),
            "cpu_stats": self._calculate_stats(cpu_usage) if cpu_usage else None,
            "memory_stats": self._calculate_stats(memory_usage) if memory_usage else None,
            "bottlenecks": self._identify_bottlenecks(container_metrics),
            "suggestions": self._generate_optimization_suggestions(container_metrics)
        }

        return analysis

    def _calculate_stats(self, values: list[float]) -> dict[str, float]:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {}

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values)
        }

    def _identify_bottlenecks(self, metrics: list[ContainerMetrics]) -> list[dict[str, Any]]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Check for high CPU usage
        cpu_usage = [m.cpu_usage_percent for m in metrics]
        avg_cpu = statistics.mean(cpu_usage) if cpu_usage else 0

        if avg_cpu > 80:  # More than 80% CPU usage
            bottlenecks.append({
                "type": "high_cpu_usage",
                "severity": "high",
                "description": f"Average CPU usage ({avg_cpu:.1f}%) exceeds recommended threshold",
                "impact": "Container may be CPU-bound and slow",
                "recommendations": [
                    "Increase CPU limits if appropriate",
                    "Optimize application code",
                    "Consider horizontal scaling"
                ]
            })

        # Check for high memory usage
        memory_usage = [m.memory_usage_mb for m in metrics]
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0

        if avg_memory > 1000:  # More than 1GB memory usage
            bottlenecks.append({
                "type": "high_memory_usage",
                "severity": "medium",
                "description": f"Average memory usage ({avg_memory:.1f}MB) is high",
                "impact": "Container may run out of memory under load",
                "recommendations": [
                    "Increase memory limits",
                    "Optimize memory usage in application",
                    "Use memory-efficient alternatives"
                ]
            })

        return bottlenecks

    def _generate_optimization_suggestions(self, metrics: list[ContainerMetrics]) -> list[OptimizationSuggestion]:
        """Generate container optimization suggestions."""
        suggestions = []

        # Resource optimization suggestions
        if len(metrics) > 10:
            avg_cpu = statistics.mean([m.cpu_usage_percent for m in metrics])
            avg_memory = statistics.mean([m.memory_usage_mb for m in metrics])

            if avg_cpu < 30:
                suggestions.append(OptimizationSuggestion(
                    category="resource_optimization",
                    title="Reduce CPU Allocation",
                    description="Container is under-utilizing CPU resources",
                    estimated_impact="medium",
                    implementation_effort="low",
                    steps=[
                        "Reduce CPU limits in deployment configuration",
                        "Monitor performance after changes",
                        "Adjust based on application needs"
                    ],
                    expected_savings={"resource_type": "cpu", "percentage": 20}
                ))

            if avg_memory < 200:
                suggestions.append(OptimizationSuggestion(
                    category="resource_optimization",
                    title="Reduce Memory Allocation",
                    description="Container is under-utilizing memory resources",
                    estimated_impact="medium",
                    implementation_effort="low",
                    steps=[
                        "Reduce memory limits in deployment configuration",
                        "Monitor for memory pressure",
                        "Optimize application memory usage if needed"
                    ],
                    expected_savings={"resource_type": "memory", "percentage": 30}
                ))

        # Base image optimization
        suggestions.append(OptimizationSuggestion(
            category="base_image",
            title="Use Minimal Base Images",
            description="Switch to smaller, more secure base images",
            estimated_impact="high",
            implementation_effort="medium",
            steps=[
                "Identify current base image",
                "Research minimal alternatives",
                "Test application compatibility",
                "Update Dockerfile and redeploy"
            ],
            expected_savings={"resource_type": "size", "percentage": 40}
        ))

        return suggestions

    def optimize_container_performance(
        self,
        container_id: str,
        target_improvement: float = 0.2
    ) -> dict[str, Any]:
        """Generate comprehensive container optimization plan.

        Args:
            container_id: Container ID to optimize
            target_improvement: Target improvement percentage

        Returns:
            Optimization plan
        """
        analysis = self.analyze_performance(container_id)

        if not analysis.get("cpu_stats"):
            return {
                "container_id": container_id,
                "message": "Insufficient data for optimization analysis",
                "suggestions": []
            }

        current_cpu = analysis["cpu_stats"]["mean"]
        target_cpu = current_cpu * (1 - target_improvement)

        # Filter suggestions that would help achieve the target
        relevant_suggestions = [
            s for s in analysis["suggestions"]
            if s.estimated_impact in ["high", "medium"]
        ]

        optimization_plan = {
            "container_id": container_id,
            "current_performance": {
                "average_cpu_percent": current_cpu,
                "target_cpu_percent": target_cpu,
                "target_improvement": f"{target_improvement*100:.1f}%"
            },
            "analysis_summary": {
                "bottlenecks_identified": len(analysis["bottlenecks"]),
                "suggestions_available": len(analysis["suggestions"]),
                "relevant_suggestions": len(relevant_suggestions)
            },
            "optimization_suggestions": relevant_suggestions,
            "implementation_timeline": self._create_implementation_timeline(relevant_suggestions),
            "expected_outcome": {
                "estimated_cpu_improvement": f"{target_improvement*100:.1f}%",
                "estimated_memory_savings": "20-40%"
            }
        }

        # Save optimization plan
        plan_file = self.optimization_data_dir / f"container_optimization_{container_id}_{int(time.time())}.json"
        with open(plan_file, 'w') as f:
            json.dump(optimization_plan, f, indent=2, default=str)

        logger.info(f"Generated optimization plan for container {container_id}")
        return optimization_plan

    def _create_implementation_timeline(self, suggestions: list[OptimizationSuggestion]) -> list[dict[str, Any]]:
        """Create implementation timeline for suggestions."""
        timeline = []
        current_week = 0

        for suggestion in suggestions:
            if suggestion.implementation_effort == "low":
                duration_weeks = 1
            elif suggestion.implementation_effort == "medium":
                duration_weeks = 2
            else:  # high
                duration_weeks = 3

            timeline.append({
                "suggestion": suggestion.title,
                "effort": suggestion.implementation_effort,
                "duration_weeks": duration_weeks,
                "start_week": current_week,
                "end_week": current_week + duration_weeks
            })

            current_week += duration_weeks

        return timeline

    def get_optimization_history(self, container_id: str) -> list[dict[str, Any]]:
        """Get optimization history for a container.

        Args:
            container_id: Container ID

        Returns:
            List of historical optimization plans
        """
        history = []

        # Look for optimization plan files
        for plan_file in self.optimization_data_dir.glob(f"container_optimization_{container_id}_*.json"):
            try:
                with open(plan_file) as f:
                    plan_data = json.load(f)

                history.append({
                    "created_at": plan_data.get("created_at"),
                    "suggestions_count": len(plan_data.get("optimization_suggestions", [])),
                    "expected_improvement": plan_data.get("expected_outcome", {}).get("estimated_cpu_improvement")
                })
            except Exception as e:
                logger.warning(f"Failed to load optimization plan {plan_file}: {e}")

        # Sort by creation date (most recent first)
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return history

def optimize_containers(
    container_config: dict[str, Any],
    workspace_dir: Optional[str] = None
) -> dict[str, Any]:
    """Optimize container performance.

    Args:
        container_config: Container configuration to optimize
        workspace_dir: Workspace directory

    Returns:
        Optimization results
    """
    optimizer = ContainerOptimizer(workspace_dir)

    # Extract container ID from config
    container_id = container_config.get("container_id", "unknown")

    return optimizer.optimize_container_performance(container_id)

