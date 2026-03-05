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
    "AnalysisResult",
    "AnalysisSeverity",
    "BuildArtifact",
    # Code types
    "CodeEntity",
    "CodeEntityType",
    "Config",
    "Credential",
    # Infrastructure types
    "Deployment",
    "DeploymentStatus",
    "Metric",
    "MetricType",
    "ModuleInfo",
    "Notification",
    "Permission",
    "Pipeline",
    "PipelineStatus",
    "Resource",
    # Core types
    "Result",
    "ResultStatus",
    "SecurityFinding",
    "SecuritySeverity",
    "Task",
    "TaskStatus",
    "TestResult",
    "TestStatus",
    "ToolDefinition",
    "WorkflowStep",
]

__version__ = "0.1.0"
