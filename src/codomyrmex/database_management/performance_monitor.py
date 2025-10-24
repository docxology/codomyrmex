#!/usr/bin/env python3
"""
Performance Monitoring Module for Codomyrmex Database Management.

This module provides database performance monitoring, query optimization,
and performance analytics capabilities.
"""

import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class QueryMetrics:
    """Query performance metrics."""
    query_hash: str
    query_type: str  # "SELECT", "INSERT", "UPDATE", "DELETE"
    execution_time_ms: float
    rows_affected: int
    timestamp: datetime
    query_text: str = ""
    database_name: str = ""


@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    database_name: str
    timestamp: datetime
    connections_active: int
    connections_idle: int
    queries_per_second: float
    average_query_time_ms: float
    cache_hit_ratio: float
    disk_io_mb: float


@dataclass
class PerformanceAlert:
    """Performance alert or warning."""
    alert_id: str
    severity: str  # "low", "medium", "high", "critical"
    metric_name: str
    current_value: float
    threshold_value: float
    description: str
    timestamp: datetime
    resolution_suggestions: List[str] = field(default_factory=list)


class DatabasePerformanceMonitor:
    """Database performance monitoring and optimization system."""

    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize performance monitor.

        Args:
            workspace_dir: Directory for storing performance data
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.performance_data_dir = self.workspace_dir / "db_performance"
        self._ensure_directories()

        self._query_metrics: List[QueryMetrics] = []
        self._database_metrics: List[DatabaseMetrics] = []
        self._alerts: List[PerformanceAlert] = []

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.performance_data_dir.mkdir(parents=True, exist_ok=True)

    def record_query_metrics(self, query_hash: str, metrics: Dict[str, Any]):
        """Record query performance metrics.

        Args:
            query_hash: Hash of the query
            metrics: Query performance data
        """
        query_metric = QueryMetrics(
            query_hash=query_hash,
            query_type=metrics.get("query_type", "UNKNOWN"),
            execution_time_ms=metrics.get("execution_time_ms", 0.0),
            rows_affected=metrics.get("rows_affected", 0),
            timestamp=datetime.now(),
            query_text=metrics.get("query_text", ""),
            database_name=metrics.get("database_name", "")
        )

        self._query_metrics.append(query_metric)

        # Keep only recent metrics (last 10000)
        if len(self._query_metrics) > 10000:
            self._query_metrics = self._query_metrics[-10000:]

        logger.debug(f"Recorded query metrics for {query_hash}")

    def record_database_metrics(self, database_name: str, metrics: Dict[str, Any]):
        """Record database performance metrics.

        Args:
            database_name: Name of the database
            metrics: Database performance data
        """
        db_metric = DatabaseMetrics(
            database_name=database_name,
            timestamp=datetime.now(),
            connections_active=metrics.get("connections_active", 0),
            connections_idle=metrics.get("connections_idle", 0),
            queries_per_second=metrics.get("queries_per_second", 0.0),
            average_query_time_ms=metrics.get("average_query_time_ms", 0.0),
            cache_hit_ratio=metrics.get("cache_hit_ratio", 0.0),
            disk_io_mb=metrics.get("disk_io_mb", 0.0)
        )

        self._database_metrics.append(db_metric)

        # Keep only recent metrics (last 1000)
        if len(self._database_metrics) > 1000:
            self._database_metrics = self._database_metrics[-1000:]

        logger.debug(f"Recorded database metrics for {database_name}")

    def analyze_query_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze query performance over time.

        Args:
            hours: Hours of history to analyze

        Returns:
            Query performance analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_queries = [
            q for q in self._query_metrics
            if q.timestamp >= cutoff_time
        ]

        if not recent_queries:
            return {
                "analysis_period_hours": hours,
                "queries_analyzed": 0,
                "message": "No query metrics found for analysis"
            }

        # Group by query type
        query_types = {}
        for query in recent_queries:
            if query.query_type not in query_types:
                query_types[query.query_type] = []
            query_types[query.query_type].append(query.execution_time_ms)

        # Calculate statistics for each type
        analysis = {
            "analysis_period_hours": hours,
            "queries_analyzed": len(recent_queries),
            "query_types": {}
        }

        for query_type, times in query_types.items():
            if times:
                analysis["query_types"][query_type] = {
                    "count": len(times),
                    "avg_time_ms": statistics.mean(times),
                    "median_time_ms": statistics.median(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "slow_queries": len([t for t in times if t > 1000])  # Queries > 1 second
                }

        # Identify slow queries
        slow_queries = [
            q for q in recent_queries
            if q.execution_time_ms > 1000  # More than 1 second
        ]

        analysis["slow_queries"] = [
            {
                "query_hash": q.query_hash,
                "execution_time_ms": q.execution_time_ms,
                "query_type": q.query_type,
                "timestamp": q.timestamp.isoformat(),
                "query_text": q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text
            }
            for q in slow_queries[:10]  # Top 10 slow queries
        ]

        return analysis

    def analyze_database_performance(self, database_name: str, hours: int = 24) -> Dict[str, Any]:
        """Analyze database performance over time.

        Args:
            database_name: Name of the database to analyze
            hours: Hours of history to analyze

        Returns:
            Database performance analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        db_metrics = [
            m for m in self._database_metrics
            if m.database_name == database_name and m.timestamp >= cutoff_time
        ]

        if not db_metrics:
            return {
                "database_name": database_name,
                "analysis_period_hours": hours,
                "metrics_count": 0,
                "message": "No database metrics found for analysis"
            }

        # Calculate statistics
        connections_active = [m.connections_active for m in db_metrics]
        queries_per_second = [m.queries_per_second for m in db_metrics]
        avg_query_time = [m.average_query_time_ms for m in db_metrics]

        analysis = {
            "database_name": database_name,
            "analysis_period_hours": hours,
            "metrics_count": len(db_metrics),
            "connections_stats": self._calculate_stats(connections_active) if connections_active else None,
            "query_rate_stats": self._calculate_stats(queries_per_second) if queries_per_second else None,
            "query_time_stats": self._calculate_stats(avg_query_time) if avg_query_time else None,
            "performance_issues": self._identify_performance_issues(db_metrics)
        }

        return analysis

    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
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

    def _identify_performance_issues(self, metrics: List[DatabaseMetrics]) -> List[Dict[str, Any]]:
        """Identify database performance issues."""
        issues = []

        # Check for high connection usage
        avg_connections = statistics.mean([m.connections_active for m in metrics])
        if avg_connections > 50:  # More than 50 active connections
            issues.append({
                "type": "high_connection_usage",
                "severity": "medium",
                "description": f"Average active connections ({avg_connections:.1f}) is high",
                "impact": "May indicate connection pool exhaustion",
                "recommendations": [
                    "Review connection pool configuration",
                    "Check for connection leaks in application",
                    "Consider connection pooling optimization"
                ]
            })

        # Check for slow query performance
        avg_query_time = statistics.mean([m.average_query_time_ms for m in metrics])
        if avg_query_time > 100:  # More than 100ms average
            issues.append({
                "type": "slow_queries",
                "severity": "high",
                "description": f"Average query time ({avg_query_time:.1f}ms) exceeds recommended threshold",
                "impact": "Application performance may be degraded",
                "recommendations": [
                    "Review and optimize slow queries",
                    "Add appropriate indexes",
                    "Consider query result caching"
                ]
            })

        return issues

    def check_alerts(self, database_name: str) -> List[PerformanceAlert]:
        """Check for performance alerts.

        Args:
            database_name: Name of the database to check

        Returns:
            List of active alerts
        """
        alerts = []
        current_time = datetime.now()

        # Check recent metrics for alert conditions
        recent_metrics = [
            m for m in self._database_metrics
            if m.database_name == database_name and
            m.timestamp >= current_time - timedelta(minutes=5)
        ]

        if recent_metrics:
            avg_query_time = statistics.mean([m.average_query_time_ms for m in recent_metrics])
            max_connections = max([m.connections_active for m in recent_metrics])

            # High query time alert
            if avg_query_time > 500:  # More than 500ms
                alerts.append(PerformanceAlert(
                    alert_id=f"high_query_time_{int(time.time())}",
                    severity="high",
                    metric_name="average_query_time_ms",
                    current_value=avg_query_time,
                    threshold_value=500,
                    description=f"Average query time ({avg_query_time:.1f}ms) exceeds threshold",
                    timestamp=current_time,
                    resolution_suggestions=[
                        "Review slow queries",
                        "Add database indexes",
                        "Optimize query structure"
                    ]
                ))

            # High connection usage alert
            if max_connections > 80:  # More than 80 connections
                alerts.append(PerformanceAlert(
                    alert_id=f"high_connections_{int(time.time())}",
                    severity="medium",
                    metric_name="connections_active",
                    current_value=max_connections,
                    threshold_value=80,
                    description=f"High connection usage ({max_connections} active connections)",
                    timestamp=current_time,
                    resolution_suggestions=[
                        "Review connection pool settings",
                        "Check for connection leaks",
                        "Consider load balancing"
                    ]
                ))

        return alerts

    def get_performance_report(self, database_name: str, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report.

        Args:
            database_name: Name of the database
            hours: Hours of history to include

        Returns:
            Performance report
        """
        query_analysis = self.analyze_query_performance(hours)
        db_analysis = self.analyze_database_performance(database_name, hours)
        alerts = self.check_alerts(database_name)

        report = {
            "database_name": database_name,
            "report_timestamp": datetime.now().isoformat(),
            "analysis_period_hours": hours,
            "query_performance": query_analysis,
            "database_performance": db_analysis,
            "active_alerts": len(alerts),
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "description": alert.description,
                    "timestamp": alert.timestamp.isoformat(),
                    "suggestions": alert.resolution_suggestions
                }
                for alert in alerts
            ],
            "recommendations": self._generate_recommendations(query_analysis, db_analysis, alerts)
        }

        # Save report
        report_file = self.performance_data_dir / f"performance_report_{database_name}_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Generated performance report for {database_name}")
        return report

    def _generate_recommendations(self, query_analysis: Dict, db_analysis: Dict, alerts: List) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        if query_analysis.get("slow_queries"):
            recommendations.append("Review and optimize slow queries identified in the analysis")

        if db_analysis.get("performance_issues"):
            for issue in db_analysis["performance_issues"]:
                recommendations.extend(issue.get("recommendations", []))

        if alerts:
            for alert in alerts:
                recommendations.extend(alert.resolution_suggestions)

        # Add general recommendations
        if not recommendations:
            recommendations.extend([
                "Monitor query performance regularly",
                "Review database indexes for optimization opportunities",
                "Consider connection pooling configuration",
                "Implement query result caching where appropriate"
            ])

        return list(set(recommendations))  # Remove duplicates

    def get_performance_history(self, database_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get performance history for a database.

        Args:
            database_name: Name of the database
            days: Days of history to retrieve

        Returns:
            List of historical performance data
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        history = []

        # Aggregate metrics by day
        daily_metrics = {}
        for metric in self._database_metrics:
            if metric.database_name == database_name and metric.timestamp >= cutoff_time:
                day_key = metric.timestamp.date().isoformat()

                if day_key not in daily_metrics:
                    daily_metrics[day_key] = {
                        "date": day_key,
                        "connections_active": [],
                        "queries_per_second": [],
                        "average_query_time_ms": []
                    }

                daily_metrics[day_key]["connections_active"].append(metric.connections_active)
                daily_metrics[day_key]["queries_per_second"].append(metric.queries_per_second)
                daily_metrics[day_key]["average_query_time_ms"].append(metric.average_query_time_ms)

        # Calculate daily averages
        for day_key, metrics in daily_metrics.items():
            history.append({
                "date": day_key,
                "avg_connections": statistics.mean(metrics["connections_active"]) if metrics["connections_active"] else 0,
                "avg_queries_per_second": statistics.mean(metrics["queries_per_second"]) if metrics["queries_per_second"] else 0,
                "avg_query_time_ms": statistics.mean(metrics["average_query_time_ms"]) if metrics["average_query_time_ms"] else 0
            })

        # Sort by date
        history.sort(key=lambda h: h["date"])

        return history


# Alias for backward compatibility
DatabaseMonitor = DatabasePerformanceMonitor


def monitor_database(database_name: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """Monitor database performance.

    Args:
        database_name: Name of the database to monitor
        workspace_dir: Workspace directory

    Returns:
        Monitoring results
    """
    monitor = DatabasePerformanceMonitor(workspace_dir)
    return monitor.analyze_database_performance(database_name)


def optimize_database(database_name: str, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """Optimize database performance.

    Args:
        database_name: Name of the database to optimize
        workspace_dir: Workspace directory

    Returns:
        Optimization results
    """
    monitor = DatabasePerformanceMonitor(workspace_dir)
    return monitor.get_performance_report(database_name)
