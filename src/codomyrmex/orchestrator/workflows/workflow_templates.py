"""Pre-built workflow templates.

Common workflows: CI/CD, code review, data pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.orchestrator.workflows.workflow_engine import (
    WorkflowRunner,
    WorkflowStep,
)

logger = get_logger(__name__)


@dataclass
class WorkflowTemplate:
    """A reusable workflow template.

    Attributes:
        name: Template name.
        description: Template description.
        steps: Template step definitions.
    """

    name: str
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)

    def instantiate(
        self,
        overrides: dict[str, Callable[..., Any]] | None = None,
    ) -> WorkflowRunner:
        """Create a WorkflowRunner from this template.

        Args:
            overrides: Map step name → action callable.

        Returns:
            Configured ``WorkflowRunner``.
        """
        overrides = overrides or {}
        runner = WorkflowRunner()

        for step_def in self.steps:
            name = step_def["name"]
            action = overrides.get(name, step_def.get("action"))
            runner.add_step(WorkflowStep(
                name=name,
                action=action,
                depends_on=step_def.get("depends_on", []),
            ))

        return runner


def ci_cd_template() -> WorkflowTemplate:
    """CI/CD pipeline template: lint → build → test → deploy."""
    return WorkflowTemplate(
        name="ci_cd",
        description="Standard CI/CD pipeline",
        steps=[
            {"name": "lint", "depends_on": []},
            {"name": "build", "depends_on": ["lint"]},
            {"name": "test", "depends_on": ["build"]},
            {"name": "deploy", "depends_on": ["test"]},
        ],
    )


def code_review_template() -> WorkflowTemplate:
    """Code review template: generate → test → review → merge."""
    return WorkflowTemplate(
        name="code_review",
        description="Automated code review pipeline",
        steps=[
            {"name": "generate", "depends_on": []},
            {"name": "test", "depends_on": ["generate"]},
            {"name": "review", "depends_on": ["test"]},
            {"name": "merge", "depends_on": ["review"]},
        ],
    )


def data_pipeline_template() -> WorkflowTemplate:
    """Data pipeline template: ingest → validate → transform → export."""
    return WorkflowTemplate(
        name="data_pipeline",
        description="ETL data pipeline",
        steps=[
            {"name": "ingest", "depends_on": []},
            {"name": "validate", "depends_on": ["ingest"]},
            {"name": "transform", "depends_on": ["validate"]},
            {"name": "export", "depends_on": ["transform"]},
        ],
    )


__all__ = [
    "WorkflowTemplate",
    "ci_cd_template",
    "code_review_template",
    "data_pipeline_template",
]
