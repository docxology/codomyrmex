"""Pipeline builder for programmatic pipeline construction."""

from typing import Any
from .models import Pipeline, PipelineStage, PipelineJob

class PipelineBuilder:
    """
    Builder for CI/CD pipelines as specified in AGENTS.md.
    """

    def __init__(self, name: str):
        self.pipeline = Pipeline(name=name)

    def add_stage(self, name: str, commands: list[str], dependencies: list[str] | None = None, on_branch: str | None = None) -> 'PipelineBuilder':
        """
        Add a stage to the pipeline.

        Args:
            name: Stage name
            commands: List of commands for the single job in this stage
            dependencies: List of stage names this stage depends on
            on_branch: Optional branch constraint (simulated in variables for now)
        """
        # Create a job with the provided commands
        job = PipelineJob(name=f"{name}_job", commands=commands)
        
        # Create a stage and add the job
        stage = PipelineStage(
            name=name,
            jobs=[job],
            dependencies=dependencies or []
        )
        
        # Branch constraint logic could be expanded, for now we add to variables if present
        if on_branch:
            self.pipeline.variables[f"STAGE_{name}_BRANCH"] = on_branch
            
        self.pipeline.stages.append(stage)
        return self

    def build(self) -> Pipeline:
        """Return the constructed Pipeline object."""
        return self.pipeline

    @property
    def stages(self) -> list[str]:
        """Return names of stages added so far."""
        return [s.name for s in self.pipeline.stages]
