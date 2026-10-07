"""Convenience functions for pipeline creation, validation and execution."""

import os
from collections.abc import Mapping
from typing import Any

from .manager import PipelineManager
from .models import Pipeline


def create_pipeline(config: str | os.PathLike[str] | Mapping[str, Any]) -> Pipeline:
    """
    Convenience function to create a pipeline from configuration.

    Args:
        config: Path to a pipeline configuration file (YAML or JSON), or the
            configuration itself as a mapping.

    Returns:
        Pipeline: Created pipeline
    """
    manager = PipelineManager()
    return manager.create_pipeline(config)


def validate_pipeline_config(config: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a pipeline configuration mapping.

    Args:
        config: Pipeline configuration (``name``, ``stages`` with ``jobs`` that
            each define a non-empty ``commands`` list, optional ``triggers``
            and ``timeout``).

    Returns:
        tuple of (is_valid, list_of_errors)
    """
    return PipelineManager().validate_pipeline_config(dict(config))


def run_pipeline(
    pipeline_name: str,
    config_path: str | None = None,
    variables: dict[str, str] | None = None,
) -> Pipeline:
    """
    Convenience function to run a pipeline.

    Args:
        pipeline_name: Name of the pipeline to run
        config_path: Path to pipeline config (if not already loaded)
        variables: Runtime variables

    Returns:
        Pipeline: Pipeline execution results
    """
    manager = PipelineManager()

    if config_path:
        manager.create_pipeline(config_path)

    return manager.run_pipeline(pipeline_name, variables)
