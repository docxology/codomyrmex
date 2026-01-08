from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import json
import time

from dataclasses import dataclass, field
import statistics

from codomyrmex.logging_monitoring.logger_config import get_logger







#!/usr/bin/env python3

"""Pipeline Performance Optimization Module for Codomyrmex CI/CD Automation.

This module provides performance optimization capabilities for CI/CD pipelines,
including bottleneck identification, resource optimization, and performance tuning.
"""


logger = get_logger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)

@dataclass
class Bottleneck:
    """Identified performance bottleneck."""
    component: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    impact: float  # Estimated time impact in seconds
    recommendations: list[str]
    detected_at: datetime

@dataclass
class OptimizationSuggestion:
    """Performance optimization suggestion."""
    category: str  # "parallelization", "caching", "resource_allocation", etc.
    title: str
    description: str
    estimated_impact: float  # Estimated time savings in seconds
    implementation_effort: str  # "low", "medium", "high"
    priority: int  # 1-10, higher is more important
    steps: list[str]
    risk_level: str  # "low", "medium", "high"

class PipelineOptimizer:
    """Pipeline performance optimization system."""

    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize pipeline optimizer.

        Args:
            workspace_dir: Directory for storing optimization data
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.optimization_data_dir = self.workspace_dir / "optimization_data"
        self._ensure_directories()

        # Performance data storage
        self._metrics_history: list[PerformanceMetric] = []
        self._bottlenecks: list[Bottleneck] = []
        self._suggestions: list[OptimizationSuggestion] = []

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.optimization_data_dir.mkdir(parents=True, exist_ok=True)

    def record_metric(self, name: str, value: float, unit: str, tags: Optional[dict[str, str]] = None):
        """Record a performance metric.

        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional metadata tags
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )

        self._metrics_history.append(metric)

        # Keep only recent metrics (last 1000)
        if len(self._metrics_history) > 1000:
            self._metrics_history = self._metrics_history[-1000:]

        logger.debug(f"Recorded metric: {name} = {value} {unit}")

    def analyze_performance(self, pipeline_name: str, time_range: int = 7) -> dict[str, Any]:
        """Analyze performance metrics for a pipeline.

        Args:
            pipeline_name: Name of the pipeline to analyze
            time_range: Days of history to analyze

        Returns:
            Performance analysis results
        """
        # Filter metrics for this pipeline
        cutoff_date = datetime.now() - timedelta(days=time_range)
        pipeline_metrics = [
            m for m in self._metrics_history
            if m.timestamp >= cutoff_date and
            m.tags.get("pipeline") == pipeline_name
        ]

        if not pipeline_metrics:
            return {
                "pipeline_name": pipeline_name,
                "analysis_period_days": time_range,
                "metrics_count": 0,
                "message": "No metrics found for analysis"
            }

        # Calculate statistics
        durations = [m.value for m in pipeline_metrics if m.name == "duration"]
        memory_usage = [m.value for m in pipeline_metrics if m.name == "memory_mb"]
        cpu_usage = [m.value for m in pipeline_metrics if m.name == "cpu_percent"]

        analysis = {
            "pipeline_name": pipeline_name,
            "analysis_period_days": time_range,
            "metrics_count": len(pipeline_metrics),
            "duration_stats": self._calculate_stats(durations) if durations else None,
            "memory_stats": self._calculate_stats(memory_usage) if memory_usage else None,
            "cpu_stats": self._calculate_stats(cpu_usage) if cpu_usage else None,
            "trends": self._analyze_trends(pipeline_metrics),
            "bottlenecks": self._identify_bottlenecks(pipeline_metrics),
            "suggestions": self._generate_suggestions(pipeline_metrics)
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
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }

    def _analyze_trends(self, metrics: list[PerformanceMetric]) -> dict[str, str]:
        """Analyze performance trends."""
        trends = {}

        # Group metrics by type
        duration_metrics = [m for m in metrics if m.name == "duration"]
        if len(duration_metrics) >= 2:
            recent = duration_metrics[-5:]  # Last 5 measurements
            older = duration_metrics[:-5] if len(duration_metrics) > 5 else duration_metrics[:5]

            if recent and older:
                recent_avg = statistics.mean([m.value for m in recent])
                older_avg = statistics.mean([m.value for m in older])

                if recent_avg > older_avg * 1.1:  # 10% increase
                    trends["duration"] = "increasing"
                elif recent_avg < older_avg * 0.9:  # 10% decrease
                    trends["duration"] = "decreasing"
                else:
                    trends["duration"] = "stable"

        return trends

    def _identify_bottlenecks(self, metrics: list[PerformanceMetric]) -> list[Bottleneck]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Check for high duration
        duration_metrics = [m for m in metrics if m.name == "duration"]
        if duration_metrics:
            avg_duration = statistics.mean([m.value for m in duration_metrics])

            if avg_duration > 600:  # More than 10 minutes
                bottlenecks.append(Bottleneck(
                    component="overall_pipeline",
                    severity="high",
                    description=f"Average duration ({avg_duration:.1f}s) exceeds recommended threshold",
                    impact=avg_duration - 300,  # Impact relative to 5-minute target
                    recommendations=[
                        "Parallelize independent stages",
                        "Optimize resource allocation",
                        "Review and optimize job configurations"
                    ],
                    detected_at=datetime.now()
                ))

        # Check for high memory usage
        memory_metrics = [m for m in metrics if m.name == "memory_mb"]
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics])

            if avg_memory > 2000:  # More than 2GB
                bottlenecks.append(Bottleneck(
                    component="memory_usage",
                    severity="medium",
                    description=f"Average memory usage ({avg_memory:.1f}MB) is high",
                    impact=avg_memory - 1000,  # Impact relative to 1GB target
                    recommendations=[
                        "Optimize Docker image size",
                        "Use memory limits in pipeline jobs",
                        "Review large file handling"
                    ],
                    detected_at=datetime.now()
                ))

        return bottlenecks

    def _generate_suggestions(self, metrics: list[PerformanceMetric]) -> list[OptimizationSuggestion]:
        """Generate optimization suggestions."""
        suggestions = []

        # Duration optimization
        duration_metrics = [m for m in metrics if m.name == "duration"]
        if duration_metrics:
            avg_duration = statistics.mean([m.value for m in duration_metrics])

            if avg_duration > 300:  # More than 5 minutes
                suggestions.append(OptimizationSuggestion(
                    category="parallelization",
                    title="Enable Parallel Execution",
                    description="Run independent pipeline stages in parallel",
                    estimated_impact=avg_duration * 0.3,  # 30% improvement estimate
                    implementation_effort="medium",
                    priority=8,
                    steps=[
                        "Identify independent stages in pipeline",
                        "Configure parallel execution in pipeline definition",
                        "Test parallel execution with sample data",
                        "Monitor for race conditions and conflicts"
                    ],
                    risk_level="low"
                ))

        # Memory optimization
        memory_metrics = [m for m in metrics if m.name == "memory_mb"]
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics])

            if avg_memory > 1000:  # More than 1GB
                suggestions.append(OptimizationSuggestion(
                    category="resource_allocation",
                    title="Optimize Memory Usage",
                    description="Reduce memory footprint of pipeline jobs",
                    estimated_impact=avg_memory * 0.2,  # 20% improvement estimate
                    implementation_effort="high",
                    priority=6,
                    steps=[
                        "Profile memory usage in each job",
                        "Optimize Docker image layers",
                        "Use memory-efficient alternatives for large operations",
                        "Implement streaming for large file processing"
                    ],
                    risk_level="medium"
                ))

        return suggestions

    def optimize_pipeline_performance(
        self,
        pipeline_name: str,
        target_improvement: float = 0.2  # 20% improvement target
    ) -> dict[str, Any]:
        """Generate comprehensive performance optimization plan.

        Args:
            pipeline_name: Name of the pipeline to optimize
            target_improvement: Target improvement percentage (0.2 = 20%)

        Returns:
            Optimization plan with suggestions and implementation steps
        """
        analysis = self.analyze_performance(pipeline_name)

        if not analysis.get("duration_stats"):
            return {
                "pipeline_name": pipeline_name,
                "message": "Insufficient data for optimization analysis",
                "suggestions": []
            }

        current_duration = analysis["duration_stats"]["mean"]
        target_duration = current_duration * (1 - target_improvement)

        # Filter suggestions that would help achieve the target
        relevant_suggestions = [
            s for s in analysis["suggestions"]
            if s.estimated_impact >= (current_duration * target_improvement * 0.5)
        ]

        # Sort by priority and estimated impact
        relevant_suggestions.sort(key=lambda s: (s.priority, s.estimated_impact), reverse=True)

        optimization_plan = {
            "pipeline_name": pipeline_name,
            "current_performance": {
                "average_duration": current_duration,
                "target_duration": target_duration,
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
                "estimated_duration_improvement": sum(s.estimated_impact for s in relevant_suggestions),
                "new_estimated_duration": max(target_duration, current_duration - sum(s.estimated_impact for s in relevant_suggestions))
            }
        }

        # Save optimization plan
        plan_file = self.optimization_data_dir / f"optimization_plan_{pipeline_name}_{int(time.time())}.json"
        with open(plan_file, 'w') as f:
            json.dump(optimization_plan, f, indent=2, default=str)

        logger.info(f"Generated optimization plan for {pipeline_name} with {len(relevant_suggestions)} suggestions")
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
                "end_week": current_week + duration_weeks,
                "priority": suggestion.priority
            })

            current_week += duration_weeks

        return timeline

    def get_optimization_history(self, pipeline_name: str) -> list[dict[str, Any]]:
        """Get optimization history for a pipeline.

        Args:
            pipeline_name: Name of the pipeline

        Returns:
            List of historical optimization plans
        """
        history = []

        # Look for optimization plan files
        for plan_file in self.optimization_data_dir.glob(f"optimization_plan_{pipeline_name}_*.json"):
            try:
                with open(plan_file) as f:
                    plan_data = json.load(f)

                # Extract key information
                history.append({
                    "created_at": plan_data.get("created_at"),
                    "target_improvement": plan_data.get("current_performance", {}).get("target_improvement"),
                    "suggestions_count": len(plan_data.get("optimization_suggestions", [])),
                    "expected_improvement": plan_data.get("expected_outcome", {}).get("estimated_duration_improvement")
                })
            except Exception as e:
                logger.warning(f"Failed to load optimization plan {plan_file}: {e}")

        # Sort by creation date (most recent first)
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return history

def optimize_pipeline_performance(
    pipeline_name: str,
    target_improvement: float = 0.2,
    workspace_dir: Optional[str] = None
) -> dict[str, Any]:
    """Optimize pipeline performance.

    Args:
        pipeline_name: Name of the pipeline to optimize
        target_improvement: Target improvement percentage
        workspace_dir: Workspace directory

    Returns:
        Optimization plan
    """
    optimizer = PipelineOptimizer(workspace_dir)
    return optimizer.optimize_pipeline_performance(pipeline_name, target_improvement)
