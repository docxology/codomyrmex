"""Workflow generator for CI/CD platforms."""

from typing import Any

from .models import Pipeline


class WorkflowGenerator:
    """
    Generator for CI/CD platform-specific workflows (GitHub Actions, GitLab CI).
    """

    def __init__(self, platform: str):
        if platform.lower() not in ("github", "gitlab"):
            raise ValueError(f"Unsupported platform: {platform}")
        self.platform = platform.lower()

    def from_pipeline(self, pipeline: Pipeline) -> "Workflow":
        """Create a Workflow object from a Pipeline."""
        return Workflow(self.platform, pipeline)


class Workflow:
    """Represents a platform-specific CI/CD workflow."""

    def __init__(self, platform: str, pipeline: Pipeline):
        self.platform = platform
        self.pipeline = pipeline

    def to_dict(self) -> dict[str, Any]:
        """Convert the pipeline to a platform-specific dictionary."""
        if self.platform == "github":
            return self._to_github()
        elif self.platform == "gitlab":
            return self._to_gitlab()
        return {}

    def _to_github(self) -> dict[str, Any]:
        """Convert to GitHub Actions format."""
        jobs = {}
        for stage in self.pipeline.stages:
            job_name = stage.name.replace(" ", "_")
            github_job = {
                "runs-on": "ubuntu-latest",
                "steps": [{"uses": "actions/checkout@v4"}],
            }

            if stage.dependencies:
                github_job["needs"] = [
                    dep.replace(" ", "_") for dep in stage.dependencies
                ]

            steps = []
            for job in stage.jobs:
                for cmd in job.commands:
                    steps.append({"name": job.name, "run": cmd})

            github_job["steps"].extend(steps)
            jobs[job_name] = github_job

        return {
            "name": self.pipeline.name,
            "on": ["push", "pull_request"],
            "jobs": jobs,
        }

    def _to_gitlab(self) -> dict[str, Any]:
        """Convert to GitLab CI format."""
        gitlab_ci = {"stages": [s.name for s in self.pipeline.stages]}
        for stage in self.pipeline.stages:
            job_name = stage.name.replace(" ", "_")
            gitlab_ci[job_name] = {
                "stage": stage.name,
                "script": [cmd for job in stage.jobs for cmd in job.commands],
            }
            if stage.dependencies:
                gitlab_ci[job_name]["needs"] = [
                    dep.replace(" ", "_") for dep in stage.dependencies
                ]

        return gitlab_ci

    def save(self, filepath: str):
        """Save the workflow to a file."""
        import yaml

        with open(filepath, "w") as f:
            yaml.dump(self.to_dict(), f, sort_keys=False)
