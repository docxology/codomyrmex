from .models import Pipeline


class PipelineOptimizationMixin:
    """Mixin for pipeline scheduling and parallel optimization."""

    def optimize_pipeline_schedule(self, pipeline: Pipeline) -> dict:
        """
        Optimize pipeline execution schedule for parallelism.

        Args:
            pipeline: Pipeline to optimize

        Returns:
            Optimized pipeline configuration
        """
        # Analyze stage dependencies
        stage_deps = {}
        for stage in pipeline.stages:
            stage_deps[stage.name] = stage.dependencies

        # Calculate parallelism opportunities
        independent_stages = []
        sequential_stages = []

        for stage_name, deps in stage_deps.items():
            if not deps:
                independent_stages.append(stage_name)
            else:
                sequential_stages.append((stage_name, deps))

        # Group stages by dependency levels
        execution_levels = self._calculate_execution_levels(pipeline.stages, stage_deps)

        optimization = {
            "parallel_stages": len(independent_stages),
            "sequential_chains": len(sequential_stages),
            "execution_levels": execution_levels,
            "estimated_parallelism": len(execution_levels[0])
            if execution_levels
            else 0,
            "optimization_suggestions": [],
        }

        # Add optimization suggestions
        if len(independent_stages) > 1:
            optimization["optimization_suggestions"].append(
                f"Consider running {len(independent_stages)} independent stages in parallel"
            )

        max_level_size = (
            max(len(level) for level in execution_levels) if execution_levels else 0
        )
        if max_level_size > 1:
            optimization["optimization_suggestions"].append(
                f"Maximum parallelism: {max_level_size} stages can run concurrently"
            )

        return optimization

    def _calculate_execution_levels(
        self, stages: list, dependencies: dict
    ) -> list[list[str]]:
        """Calculate execution levels for optimal parallelism."""
        # Kahn's algorithm for topological levels
        in_degree = {stage.name: len(stage.dependencies) for stage in stages}
        queue = [stage.name for stage in stages if in_degree[stage.name] == 0]
        levels = []

        while queue:
            level = []
            next_queue = []

            for stage_name in queue:
                level.append(stage_name)

                # Find stages that depend on this one
                for other_stage in stages:
                    if stage_name in other_stage.dependencies:
                        in_degree[other_stage.name] -= 1
                        if in_degree[other_stage.name] == 0:
                            next_queue.append(other_stage.name)

            if level:
                levels.append(sorted(level))
            queue = next_queue

        return levels
