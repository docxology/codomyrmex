"""
Shared Schema Registry for Codomyrmex

Provides standardized types used across modules to enable interoperability.
This is the Foundation layer type library that replaces per-module type definitions.
"""

from .code import (
    AnalysisResult,
    AnalysisSeverity,
    CodeEntity,
    CodeEntityType,
    SecurityFinding,
    SecuritySeverity,
    TestResult,
    TestStatus,
)
from .core import (
    Config,
    ModuleInfo,
    Notification,
    Result,
    ResultStatus,
    Task,
    TaskStatus,
    ToolDefinition,
)
from .infra import (
    BuildArtifact,
    Credential,
    Deployment,
    DeploymentStatus,
    Metric,
    MetricType,
    Permission,
    Pipeline,
    PipelineStatus,
    Resource,
    WorkflowStep,
)

__all__ = [
    # Core types
    "Result",
    "ResultStatus",
    "Task",
    "TaskStatus",
    "Config",
    "ModuleInfo",
    "ToolDefinition",
    "Notification",
    # Code types
    "CodeEntity",
    "CodeEntityType",
    "AnalysisResult",
    "AnalysisSeverity",
    "SecurityFinding",
    "SecuritySeverity",
    "TestResult",
    "TestStatus",
    # Infrastructure types
    "Deployment",
    "DeploymentStatus",
    "Pipeline",
    "PipelineStatus",
    "Resource",
    "BuildArtifact",
    "Metric",
    "MetricType",
    "Credential",
    "Permission",
    "WorkflowStep",
]

__version__ = "0.1.0"
