"""Project Management System for Codomyrmex.

This module provides high-level project lifecycle management, including project
templates, scaffolding, and coordination of complex multi-module workflows.
"""

import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .documentation_generator import DocumentationGenerator

logger = get_logger(__name__)


class ProjectStatus(Enum):
    """Project lifecycle status."""

    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class ProjectType(Enum):
    """Types of projects supported."""

    AI_ANALYSIS = "ai_analysis"
    WEB_APPLICATION = "web_application"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    CUSTOM = "custom"


@dataclass
class ProjectTemplate:
    """Template for creating new projects."""

    name: str
    type: ProjectType
    description: str = ""
    version: str = "1.0"
    directory_structure: list[str] = field(default_factory=list)
    template_files: dict[str, str] = field(default_factory=dict)
    default_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    """Project definition."""

    name: str
    path: Path
    type: ProjectType
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    config: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    owner: str | None = None
    version: str = "0.1.0"
    metrics: dict[str, Any] = field(default_factory=dict)
    milestones: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the project to a serializable dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "type": self.type.value,
            "description": self.description,
            "status": self.status.value,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner": self.owner,
            "version": self.version,
            "metrics": self.metrics,
            "milestones": self.milestones,
        }


class ProjectManager:
    """Manages project lifecycles."""

    def __init__(self, projects_root: Path | str | None = None):
        """Initialize the project manager."""
        self.projects_root = Path(projects_root) if projects_root else Path.cwd()
        self.doc_generator = DocumentationGenerator()
        self.active_projects: dict[str, Project] = {}

    def create_project(
        self,
        name: str,
        type: ProjectType,
        description: str = "",
        path: Path | str | None = None,
    ) -> Project | None:
        """Create and scaffold a new project.

        Args:
            name: Project name (unique within this manager).
            type: Project type.
            description: Free-text description.
            path: Project directory. Defaults to ``projects_root / name``.

        Returns:
            The created project, or None if the name is already registered,
            the directory already exists, or scaffolding failed (the reason is
            logged).
        """
        if name in self.active_projects:
            logger.error("Project already registered: %s", name)
            return None

        project_path = Path(path) if path is not None else self.projects_root / name

        if project_path.exists():
            logger.error("Project directory already exists: %s", project_path)
            return None

        try:
            # Create directory structure
            project_path.mkdir(parents=True)
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "config").mkdir()
            (project_path / "docs").mkdir()

            project = Project(
                name=name,
                path=project_path,
                type=type,
                description=description,
                status=ProjectStatus.ACTIVE,
            )

            # Generate documentation
            self.doc_generator.generate_all_documentation(
                project_path=project_path,
                project_name=name,
                project_type=type.value,
                description=description,
                version=project.version,
                author="",
                created_at=datetime.now().isoformat(),
                nested_dirs=["src", "tests", "config", "docs"],
            )

            self.active_projects[name] = project
            logger.info("Created project: %s", name)
            return project

        except Exception as e:
            logger.error("Failed to create project %s: %s", name, e)
            if project_path.exists():
                shutil.rmtree(project_path)
            return None

    def get_project(self, name: str) -> Project | None:
        """Get a project by name."""
        return self.active_projects.get(name)

    def list_projects(self) -> list[Project]:
        """list all active projects."""
        return list(self.active_projects.values())

    def update_project_status(self, name: str, status: ProjectStatus) -> bool:
        """Update project status."""
        project = self.get_project(name)
        if project:
            project.status = status
            project.updated_at = datetime.now(UTC)
            logger.info("Updated status for project %s: %s", name, status.value)
            return True
        return False

    def update_project_metrics(self, name: str, metrics: dict[str, Any]) -> bool:
        """Merge ``metrics`` into the project's metrics.

        Returns:
            True if the project exists and was updated, False otherwise.
        """
        project = self.get_project(name)
        if project is None:
            return False
        project.metrics.update(metrics)
        project.updated_at = datetime.now(UTC)
        return True

    def add_project_milestone(
        self,
        name: str,
        milestone_name: str,
        milestone_data: dict[str, Any] | None = None,
    ) -> bool:
        """Record a milestone (with a ``recorded_at`` timestamp) on a project.

        Returns:
            True if the project exists and the milestone was recorded.
        """
        project = self.get_project(name)
        if project is None:
            return False
        now = datetime.now(UTC)
        project.milestones[milestone_name] = {
            **(milestone_data or {}),
            "recorded_at": now.isoformat(),
        }
        project.updated_at = now
        return True

    def get_projects_summary(self) -> dict[str, Any]:
        """Summarise the managed projects.

        Returns:
            Dictionary with ``total_projects``, ``by_status`` and ``by_type``
            (counts keyed by enum value) and ``recent_activity`` (projects
            ordered by most recent update).
        """
        projects = self.list_projects()
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for project in projects:
            by_status[project.status.value] = by_status.get(project.status.value, 0) + 1
            by_type[project.type.value] = by_type.get(project.type.value, 0) + 1

        recent = sorted(projects, key=lambda p: p.updated_at, reverse=True)
        return {
            "total_projects": len(projects),
            "by_status": by_status,
            "by_type": by_type,
            "recent_activity": [
                {
                    "name": project.name,
                    "status": project.status.value,
                    "updated_at": project.updated_at.isoformat(),
                }
                for project in recent
            ],
        }


# Global project manager instance
_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get the global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
