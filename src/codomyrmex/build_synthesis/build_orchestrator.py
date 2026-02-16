"""Backward-compatible shim for build_orchestrator.

The actual implementation has moved to ``build_synthesis.pipeline.build_orchestrator``.
This module re-exports every public name so that existing imports such as
``from codomyrmex.build_synthesis.build_orchestrator import check_build_environment``
continue to work without modification.
"""

from .pipeline.build_orchestrator import (  # noqa: F401
    check_build_environment,
    orchestrate_build_pipeline,
    run_build_command,
    synthesize_build_artifact,
    validate_build_output,
)

__all__ = [
    "check_build_environment",
    "orchestrate_build_pipeline",
    "run_build_command",
    "synthesize_build_artifact",
    "validate_build_output",
]
