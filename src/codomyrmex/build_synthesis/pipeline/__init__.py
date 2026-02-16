"""Build pipeline orchestration components for Codomyrmex Build Synthesis.

This subpackage contains the build orchestration and pipeline execution
capabilities for automating build processes and artifact generation.

Functions:
    check_build_environment: Check if the build environment is properly configured
    run_build_command: Run a build command and return the result
    synthesize_build_artifact: Synthesize a build artifact from source code
    validate_build_output: Validate that build output meets expectations
    orchestrate_build_pipeline: Orchestrate a complete build pipeline
"""

from .build_orchestrator import (
    check_build_environment,
    orchestrate_build_pipeline,
    run_build_command,
    synthesize_build_artifact,
    validate_build_output,
)

__all__ = [
    "check_build_environment",
    "run_build_command",
    "synthesize_build_artifact",
    "validate_build_output",
    "orchestrate_build_pipeline",
]
