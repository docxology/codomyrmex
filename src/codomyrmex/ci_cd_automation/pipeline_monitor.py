from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import json
import time

from dataclasses import dataclass
from enum import Enum

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger







#!/usr/bin/env python3

"""Pipeline Monitoring Module for Codomyrmex CI/CD Automation.

This module provides comprehensive pipeline monitoring, health checks,
and reporting capabilities for CI/CD pipelines.
"""


logger = get_logger(__name__)

class ReportType(Enum):
    """Types of pipeline reports."""
    EXECUTION = "execution"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    SUMMARY = "summary"

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics."""
    pipeline_name: str
    total_duration: float
    stage_count: int
    job_count: int
    success_rate: float
    start_time: datetime
    end_time: Optional[datetime] = None
    error_count: int = 0
    warning_count: int = 0

@dataclass
class PipelineReport:
    """Comprehensive pipeline execution report."""
    pipeline_name: str
    execution_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    stages_executed: int
    jobs_executed: int
    jobs_passed: int
    jobs_failed: int
    jobs_skipped: int
    artifacts_created: list[str]
    metrics: dict[str, Any]
    errors: list[str]
    warnings: list[str]

class PipelineMonitor:
    """Pipeline monitoring and reporting system."""

    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize pipeline monitor.

        Args:
            workspace_dir: Directory for storing reports and metrics
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.reports_dir = self.workspace_dir / "pipeline_reports"
        self.metrics_dir = self.workspace_dir / "pipeline_metrics"
        self._ensure_directories()

        # In-memory metrics storage
        self._active_metrics: dict[str, PipelineMetrics] = {}
        self._reports: dict[str, PipelineReport] = {}

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def start_monitoring(self, pipeline_name: str) -> str:
        """Start monitoring a pipeline execution.

        Args:
            pipeline_name: Name of the pipeline being monitored

        Returns:
            Execution ID for this monitoring session
        """
        execution_id = f"{pipeline_name}_{int(time.time())}"

        metrics = PipelineMetrics(
            pipeline_name=pipeline_name,
            total_duration=0.0,
            stage_count=0,
            job_count=0,
            success_rate=0.0,
            start_time=datetime.now()
        )

        self._active_metrics[execution_id] = metrics
        logger.info(f"Started monitoring pipeline {pipeline_name} with execution ID {execution_id}")

        return execution_id

    def record_stage_completion(self, execution_id: str, stage_name: str, success: bool):
        """Record completion of a pipeline stage.

        Args:
            execution_id: Execution ID from start_monitoring
            stage_name: Name of the completed stage
            success: Whether the stage completed successfully
        """
        if execution_id not in self._active_metrics:
            logger.warning(f"No active metrics found for execution ID {execution_id}")
            return

        metrics = self._active_metrics[execution_id]
        metrics.stage_count += 1

        if not success:
            metrics.error_count += 1

        logger.debug(f"Recorded stage completion: {stage_name} (success: {success})")

    def record_job_completion(self, execution_id: str, job_name: str, success: bool):
        """Record completion of a pipeline job.

        Args:
            execution_id: Execution ID from start_monitoring
            job_name: Name of the completed job
            success: Whether the job completed successfully
        """
        if execution_id not in self._active_metrics:
            logger.warning(f"No active metrics found for execution ID {execution_id}")
            return

        metrics = self._active_metrics[execution_id]
        metrics.job_count += 1

        if not success:
            metrics.error_count += 1

        logger.debug(f"Recorded job completion: {job_name} (success: {success})")

    def finish_monitoring(self, execution_id: str, status: str = "completed") -> PipelineMetrics:
        """Finish monitoring a pipeline execution.

        Args:
            execution_id: Execution ID from start_monitoring
            status: Final status of the pipeline

        Returns:
            Final pipeline metrics
        """
        if execution_id not in self._active_metrics:
            raise CodomyrmexError(f"No active metrics found for execution ID {execution_id}")

        metrics = self._active_metrics[execution_id]
        metrics.end_time = datetime.now()

        # Calculate final metrics
        if metrics.end_time and metrics.start_time:
            metrics.total_duration = (metrics.end_time - metrics.start_time).total_seconds()

        total_jobs = metrics.job_count
        if total_jobs > 0:
            metrics.success_rate = ((total_jobs - metrics.error_count) / total_jobs) * 100

        logger.info(f"Finished monitoring pipeline {metrics.pipeline_name} - Status: {status}")

        # Clean up active metrics
        del self._active_metrics[execution_id]

        return metrics

    def generate_report(self, execution_id: str, report_type: ReportType = ReportType.EXECUTION) -> PipelineReport:
        """Generate a comprehensive pipeline report.

        Args:
            execution_id: Execution ID to generate report for
            report_type: Type of report to generate

        Returns:
            Generated pipeline report
        """
        # This would typically retrieve data from storage
        # For now, return a basic report structure

        report = PipelineReport(
            pipeline_name="example_pipeline",
            execution_id=execution_id,
            status="completed",
            start_time=datetime.now() - timedelta(minutes=5),
            end_time=datetime.now(),
            duration=300.0,
            stages_executed=3,
            jobs_executed=8,
            jobs_passed=7,
            jobs_failed=1,
            jobs_skipped=0,
            artifacts_created=["build.zip", "test-results.xml"],
            metrics={"coverage": 85.5, "performance_score": 92.3},
            errors=["Job 'test' failed due to timeout"],
            warnings=["Long execution time for build stage"]
        )

        # Save report to file
        report_file = self.reports_dir / f"report_{execution_id}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "pipeline_name": report.pipeline_name,
                "execution_id": report.execution_id,
                "status": report.status,
                "start_time": report.start_time.isoformat(),
                "end_time": report.end_time.isoformat() if report.end_time else None,
                "duration": report.duration,
                "stages_executed": report.stages_executed,
                "jobs_executed": report.jobs_executed,
                "jobs_passed": report.jobs_passed,
                "jobs_failed": report.jobs_failed,
                "artifacts_created": report.artifacts_created,
                "metrics": report.metrics,
                "errors": report.errors,
                "warnings": report.warnings
            }, f, indent=2)

        logger.info(f"Generated {report_type.value} report for execution {execution_id}")
        return report

    def get_pipeline_health(self, pipeline_name: str) -> dict[str, Any]:
        """Get health status of a pipeline.

        Args:
            pipeline_name: Name of the pipeline to check

        Returns:
            Health status information
        """
        # This would typically check actual pipeline status
        # For now, return mock health data

        return {
            "pipeline_name": pipeline_name,
            "status": "healthy",
            "last_execution": datetime.now().isoformat(),
            "success_rate": 95.5,
            "average_duration": 180.5,
            "active_executions": 0,
            "recent_failures": []
        }

    def get_metrics_summary(self, days: int = 7) -> dict[str, Any]:
        """Get summary of pipeline metrics over time.

        Args:
            days: Number of days to look back

        Returns:
            Metrics summary
        """
        # This would typically aggregate historical data
        # For now, return mock summary

        return {
            "period_days": days,
            "total_executions": 42,
            "successful_executions": 39,
            "failed_executions": 3,
            "average_success_rate": 92.8,
            "average_duration": 175.3,
            "most_active_pipeline": "main-ci",
            "trending_metrics": {
                "performance": "improving",
                "reliability": "stable",
                "coverage": "increasing"
            }
        }

def monitor_pipeline_health(pipeline_name: str, workspace_dir: Optional[str] = None) -> dict[str, Any]:
    """Monitor pipeline health and return status.

    Args:
        pipeline_name: Name of the pipeline to monitor
        workspace_dir: Workspace directory for reports

    Returns:
        Pipeline health information
    """
    monitor = PipelineMonitor(workspace_dir)
    return monitor.get_pipeline_health(pipeline_name)

def generate_pipeline_reports(
    execution_id: str,
    report_types: list[ReportType],
    workspace_dir: Optional[str] = None
) -> dict[str, PipelineReport]:
    """Generate multiple types of pipeline reports.

    Args:
        execution_id: Execution ID to generate reports for
        report_types: Types of reports to generate
        workspace_dir: Workspace directory for reports

    Returns:
        Dictionary of generated reports by type
    """
    monitor = PipelineMonitor(workspace_dir)
    reports = {}

    for report_type in report_types:
        reports[report_type.value] = monitor.generate_report(execution_id, report_type)

    return reports
