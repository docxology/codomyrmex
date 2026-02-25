"""
CI/CD Automation Module for Codomyrmex.

The CI/CD Automation module provides continuous integration and deployment
capabilities, including pipeline management, automated testing, deployment orchestration,
and build automation for the Codomyrmex ecosystem.

Submodules:
    build: Consolidated build capabilities.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
- Integrates with `project_orchestration` for workflow management.
- Works with `security` for security scanning in pipelines.

Available functions:
- create_pipeline: Create and configure CI/CD pipelines
- run_pipeline: Execute pipeline with full orchestration
- manage_deployments: Handle deployment orchestration
- monitor_pipeline_health: Real-time pipeline monitoring
- generate_pipeline_reports: Comprehensive pipeline analytics
- manage_environments: Environment management and promotion
- handle_rollback: Automated rollback capabilities
- optimize_pipeline_performance: Pipeline performance optimization

Data structures:
- Pipeline: CI/CD pipeline definition and configuration
- PipelineStage: Individual pipeline stage with jobs and tasks
- Deployment: Deployment configuration and status
- Environment: Target environment configuration
- PipelineReport: Pipeline execution reports and analytics
- RollbackStrategy: Rollback configuration and execution
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .deployment_orchestrator import (
    Deployment,
    DeploymentOrchestrator,
    Environment,
    manage_deployments,
)
from .exceptions import (
    ArtifactError,
    BuildError,
    DeploymentError,
    PipelineError,
    RollbackError,
    StageError,
)
from .performance_optimizer import (
    PipelineOptimizer,
    optimize_pipeline_performance,
)
from .pipeline import (
    Pipeline,
    PipelineJob,
    PipelineManager,
    PipelineStage,
    create_pipeline,
    run_pipeline,
)
from .pipeline.pipeline_monitor import (
    PipelineMonitor,
    PipelineReport,
    generate_pipeline_reports,
    monitor_pipeline_health,
)
from .rollback_manager import (
    RollbackManager,
    RollbackStrategy,
    handle_rollback,
)


def cli_commands():
    """Return CLI commands for the ci_cd_automation module."""
    return {
        "pipelines": {
            "help": "List configured CI/CD pipelines",
            "handler": lambda **kwargs: print(
                "CI/CD Pipelines:\n"
                + "\n".join(
                    f"  - {name}" for name in ["build", "test", "deploy", "release"]
                )
            ),
        },
        "status": {
            "help": "Show pipeline execution status",
            "handler": lambda **kwargs: print(
                "Pipeline Status:\n"
                "  build    : idle\n"
                "  test     : idle\n"
                "  deploy   : idle\n"
                "  release  : idle"
            ),
        },
    }


from . import build, pipeline

__all__ = [
    # CLI integration
    "cli_commands",
    # Pipeline management
    "PipelineManager",
    "create_pipeline",
    "run_pipeline",
    "Pipeline",
    "PipelineJob",
    "PipelineStage",
    # Deployment orchestration
    "DeploymentOrchestrator",
    "manage_deployments",
    "Deployment",
    "Environment",
    # Pipeline monitoring
    "PipelineMonitor",
    "monitor_pipeline_health",
    "generate_pipeline_reports",
    "PipelineReport",
    # Rollback management
    "RollbackManager",
    "handle_rollback",
    "RollbackStrategy",
    # Performance optimization
    "PipelineOptimizer",
    "optimize_pipeline_performance",
    # Submodules
    "pipeline",
    # Exceptions
    "PipelineError",
    "BuildError",
    "DeploymentError",
    "ArtifactError",
    "StageError",
    "RollbackError",
]
