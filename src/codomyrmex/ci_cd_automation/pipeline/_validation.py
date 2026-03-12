from typing import Any

from .models import Pipeline, PipelineJob, PipelineStage


class PipelineValidationMixin:
    """Mixin for pipeline, stage, and job validation logic."""

    def validate_pipeline_config(self, config: dict) -> tuple[bool, list[str]]:
        """
        Validate pipeline configuration with detailed error reporting.

        Args:
            config: Pipeline configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate required fields
        required_fields = ["name", "stages"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        if "name" in config and not isinstance(config["name"], str):
            errors.append("Pipeline name must be a string")

        if "stages" in config:
            if not isinstance(config["stages"], list):
                errors.append("Stages must be a list")
            else:
                # Validate each stage
                for i, stage in enumerate(config["stages"]):
                    stage_errors = self._validate_stage_config(stage, i)
                    errors.extend(stage_errors)

        # Validate triggers if present
        if "triggers" in config:
            if not isinstance(config["triggers"], list):
                errors.append("Triggers must be a list")
            else:
                valid_triggers = ["push", "pull_request", "manual", "schedule"]
                for trigger in config["triggers"]:
                    if trigger not in valid_triggers:
                        errors.append(
                            f"Invalid trigger: {trigger}. Must be one of {valid_triggers}"
                        )

        # Validate timeout if present
        if "timeout" in config and (
            not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0
        ):
            errors.append("Timeout must be a positive number")

        return len(errors) == 0, errors

    def _validate_stage_config(self, stage: dict, stage_index: int) -> list[str]:
        """Validate a single stage configuration."""
        errors = []
        prefix = f"Stage {stage_index}"

        # Validate required stage fields
        if "name" not in stage:
            errors.append(f"{prefix}: Missing required field 'name'")
        elif not isinstance(stage["name"], str):
            errors.append(f"{prefix}: Stage name must be a string")

        if "jobs" not in stage:
            errors.append(f"{prefix}: Missing required field 'jobs'")
        elif not isinstance(stage["jobs"], list):
            errors.append(f"{prefix}: Jobs must be a list")
        else:
            # Validate each job
            for j, job in enumerate(stage["jobs"]):
                job_errors = self._validate_job_config(job, stage_index, j)
                errors.extend(job_errors)

        # Validate dependencies if present
        if "dependencies" in stage:
            if not isinstance(stage["dependencies"], list):
                errors.append(f"{prefix}: Dependencies must be a list")

        return errors

    def _validate_job_config(
        self, job: dict, stage_index: int, job_index: int
    ) -> list[str]:
        """Validate a single job configuration."""
        errors = []
        prefix = f"Stage {stage_index}, Job {job_index}"

        # Validate required job fields
        if "name" not in job:
            errors.append(f"{prefix}: Missing required field 'name'")
        elif not isinstance(job["name"], str):
            errors.append(f"{prefix}: Job name must be a string")

        if "commands" not in job:
            errors.append(f"{prefix}: Missing required field 'commands'")
        elif not isinstance(job["commands"], list):
            errors.append(f"{prefix}: Commands must be a list")
        elif len(job["commands"]) == 0:
            errors.append(f"{prefix}: Commands list cannot be empty")

        # Validate optional fields
        if "timeout" in job and (
            not isinstance(job["timeout"], (int, float)) or job["timeout"] <= 0
        ):
            errors.append(f"{prefix}: Timeout must be a positive number")

        if "retry_count" in job and (
            not isinstance(job["retry_count"], int) or job["retry_count"] < 0
        ):
            errors.append(f"{prefix}: Retry count must be a non-negative integer")

        return errors

    def get_stage_dependencies(self, stages: list[dict]) -> dict[str, list[str]]:
        """
        Extract stage dependencies from stage list.

        Args:
            stages: List of stage dictionaries

        Returns:
            Dictionary mapping stage names to dependency lists
        """
        dependencies = {}
        for stage in stages:
            stage_name = stage["name"]
            deps = stage.get("dependencies", [])
            dependencies[stage_name] = deps

        return dependencies

    def validate_stage_dependencies(self, stages: list[dict]) -> tuple[bool, list[str]]:
        """
        Validate stage dependency graph.

        Args:
            stages: List of stage dictionaries

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        stage_names = {stage["name"] for stage in stages}
        dependencies = self.get_stage_dependencies(stages)

        # Check for missing dependencies
        for stage_name, deps in dependencies.items():
            for dep in deps:
                if dep not in stage_names:
                    errors.append(
                        f"Stage '{stage_name}' depends on missing stage '{dep}'"
                    )

        # Check for self-dependencies
        for stage_name, deps in dependencies.items():
            if stage_name in deps:
                errors.append(f"Stage '{stage_name}' cannot depend on itself")

        # Check for cycles (simplified check)
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:

            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for stage_name in stage_names:
            if stage_name not in visited and has_cycle(stage_name):
                errors.append(f"Cycle detected involving stage '{stage_name}'")
                break  # Only report first cycle

        return len(errors) == 0, errors
