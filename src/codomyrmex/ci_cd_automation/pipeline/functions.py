"""Convenience functions for pipeline creation and execution."""

from .manager import PipelineManager
from .models import Pipeline


def create_pipeline(config_path: str) -> Pipeline:
    """
    Convenience function to create a pipeline from configuration.

    Args:
        config_path: Path to pipeline configuration file

    Returns:
        Pipeline: Created pipeline
    """
    manager = PipelineManager()
    return manager.create_pipeline(config_path)


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
