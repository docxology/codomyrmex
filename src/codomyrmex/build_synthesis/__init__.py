"""
Build Synthesis Module for Codomyrmex.

The Build Synthesis module is responsible for automating the build processes and
synthesizing various artifacts within the Codomyrmex ecosystem. This includes
orchestrating build pipelines, managing dependencies, and creating deployable
artifacts.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- check_build_environment
- run_build_command
- synthesize_build_artifact
- validate_build_output
- orchestrate_build_pipeline
"""

from .build_orchestrator import (
    check_build_environment,
    run_build_command,
    synthesize_build_artifact,
    validate_build_output,
    orchestrate_build_pipeline,
)

__all__ = [
    'check_build_environment',
    'run_build_command',
    'synthesize_build_artifact',
    'validate_build_output',
    'orchestrate_build_pipeline',
] 