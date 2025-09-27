"""
CI/CD Automation Module for Codomyrmex.

The CI/CD Automation module provides comprehensive continuous integration and deployment
capabilities, including pipeline management, automated testing, deployment orchestration,
and build automation for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
- Integrates with `project_orchestration` for workflow management.
- Works with `security_audit` for security scanning in pipelines.

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

from .pipeline_manager import (
    PipelineManager,
    create_pipeline,
    run_pipeline,
    Pipeline,
    PipelineStage,
)

from .deployment_orchestrator import (
    DeploymentOrchestrator,
    manage_deployments,
    Deployment,
    Environment,
)

from .pipeline_monitor import (
    PipelineMonitor,
    monitor_pipeline_health,
    generate_pipeline_reports,
    PipelineReport,
)

from .rollback_manager import (
    RollbackManager,
    handle_rollback,
    RollbackStrategy,
)

from .performance_optimizer import (
    PipelineOptimizer,
    optimize_pipeline_performance,
)

__all__ = [
    # Pipeline management
    "PipelineManager",
    "create_pipeline",
    "run_pipeline",
    "Pipeline",
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
]
