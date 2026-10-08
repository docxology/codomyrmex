"""Project Management System for Codomyrmex.

This module provides high-level project lifecycle management, including project
templates, scaffolding, and coordination of complex multi-module workflows.

Persistence
-----------
Every project managed by :class:`ProjectManager` is saved as
``<project.path>/project.json`` (the JSON form of :meth:`Project.to_dict`). The
file is written when the project is created and after every status, metrics or
milestone update. A new ``ProjectManager`` registers the projects it finds as
``<projects_root>/*/project.json``; files that cannot be read are logged and
skipped. A project created with a ``path`` outside ``projects_root`` is still
saved, but only a manager whose ``projects_root`` is that path's parent finds it.
"""

import copy
import json
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from ._json_files import write_json_atomic
from .documentation_generator import DocumentationGenerator

logger = get_logger(__name__)

PROJECT_FILE_NAME = "project.json"


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


def _field(data: Mapping[str, Any], key: str, expected: type, default: Any) -> Any:
    """Return ``data[key]`` (or ``default`` when absent), checking its type."""
    value = data.get(key, default)
    if not isinstance(value, expected):
        raise ValueError(
            f"project field '{key}' must be {expected.__name__}, "
            f"got {type(value).__name__}"
        )
    return value


def _timestamp(data: Mapping[str, Any], key: str) -> datetime:
    """Parse a required, timezone-aware ISO 8601 timestamp field."""
    if key not in data:
        raise ValueError(f"project field '{key}' is missing")
    value = _field(data, key, str, None)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError(f"project field '{key}' must include a UTC offset: {value}")
    return parsed


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

    @property
    def metadata_file(self) -> Path:
        """Path of the file the project is persisted to."""
        return self.path / PROJECT_FILE_NAME

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

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Project":
        """Rebuild a project from the output of :meth:`to_dict`.

        ``name``, ``path``, ``type``, ``status``, ``created_at`` and
        ``updated_at`` are required; the other fields fall back to the dataclass
        defaults when absent.

        Raises:
            ValueError: If ``data`` is not a mapping, a required field is
                missing, a field has the wrong type, an enum value is unknown,
                or a timestamp is not timezone-aware ISO 8601.
        """
        if not isinstance(data, Mapping):
            raise ValueError("project data must be a JSON object")
        for key in ("name", "path", "type", "status"):
            if key not in data:
                raise ValueError(f"project field '{key}' is missing")
        name = _field(data, "name", str, None)
        if not name:
            raise ValueError("project field 'name' must not be empty")
        owner = data.get("owner")
        if owner is not None and not isinstance(owner, str):
            raise ValueError("project field 'owner' must be str or null")
        return cls(
            name=name,
            path=Path(_field(data, "path", str, None)),
            type=ProjectType(_field(data, "type", str, None)),
            description=_field(data, "description", str, ""),
            status=ProjectStatus(_field(data, "status", str, None)),
            config=dict(_field(data, "config", dict, {})),
            created_at=_timestamp(data, "created_at"),
            updated_at=_timestamp(data, "updated_at"),
            owner=owner,
            version=_field(data, "version", str, "0.1.0"),
            metrics=dict(_field(data, "metrics", dict, {})),
            milestones=dict(_field(data, "milestones", dict, {})),
        )


def _read_project_file(project_file: Path) -> Project:
    """Load the project saved in ``project_file``.

    The directory containing the file is the project's path; a different
    ``path`` recorded in the file (for example after the directory was moved)
    is replaced, with a warning.

    Raises:
        OSError: If the file cannot be read.
        ValueError: If it is not valid JSON or not a valid project.
    """
    with open(project_file, encoding="utf-8") as f:
        project = Project.from_dict(json.load(f))
    directory = project_file.parent
    if project.path.resolve() != directory.resolve():
        logger.warning(
            "Project '%s' in %s records path %s; using %s",
            project.name,
            project_file,
            project.path,
            directory,
        )
    project.path = directory
    return project


class ProjectManager:
    """Manages project lifecycles."""

    def __init__(self, projects_root: Path | str | None = None):
        """Initialize the project manager.

        Args:
            projects_root: Directory new projects are created in by default.
                Defaults to the current working directory. Projects saved as
                ``<projects_root>/*/project.json`` are registered now;
                unreadable or invalid files are logged and skipped.
        """
        self.projects_root = Path(projects_root) if projects_root else Path.cwd()
        self.doc_generator = DocumentationGenerator()
        self.active_projects: dict[str, Project] = {}
        self._load_projects()

    def _load_projects(self) -> None:
        """Register the projects saved under ``projects_root``."""
        if not self.projects_root.is_dir():
            return
        for project_file in sorted(self.projects_root.glob(f"*/{PROJECT_FILE_NAME}")):
            try:
                project = _read_project_file(project_file)
            except (OSError, ValueError) as exc:
                logger.warning("Skipping project file %s: %s", project_file, exc)
                continue
            existing = self.active_projects.get(project.name)
            if existing is not None:
                logger.warning(
                    "Skipping project file %s: project '%s' is already loaded from %s",
                    project_file,
                    project.name,
                    existing.metadata_file,
                )
                continue
            self.active_projects[project.name] = project
            logger.info("Loaded project '%s' from %s", project.name, project_file)

    def create_project(
        self,
        name: str,
        type: ProjectType,
        description: str = "",
        path: Path | str | None = None,
    ) -> Project | None:
        """Create and scaffold a new project.

        Creates ``src/``, ``tests/``, ``config/`` and ``docs/``, generates the
        README/AGENTS documentation and saves ``project.json``.

        Args:
            name: Project name (unique within this manager).
            type: Project type.
            description: Free-text description.
            path: Project directory. Defaults to ``projects_root / name``.

        Returns:
            The created project, or None if the name is already registered,
            the directory already exists, or scaffolding failed (the reason is
            logged and the partially created directory is removed).
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
            documented = self.doc_generator.generate_all_documentation(
                project_path=project_path,
                project_name=name,
                project_type=type.value,
                description=description,
                version=project.version,
                author="",
                created_at=datetime.now().isoformat(),
                nested_dirs=["src", "tests", "config", "docs"],
            )
            if not documented:
                raise RuntimeError("documentation generation failed (see log)")

            write_json_atomic(project.metadata_file, project.to_dict())

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

    def save_project(self, name: str) -> Path:
        """Write a registered project to its ``project.json``.

        Use this after changing a :class:`Project` directly; the update
        methods of this class save automatically.

        Returns:
            The path written.

        Raises:
            KeyError: If no project named ``name`` is registered.
            TypeError: If its config, metrics or milestones hold a value that
                is not JSON-serialisable.
            ValueError: If they hold NaN or infinity.
            OSError: If the file cannot be written.
        """
        project = self.get_project(name)
        if project is None:
            raise KeyError(f"Project not registered: {name}")
        write_json_atomic(project.metadata_file, project.to_dict())
        return project.metadata_file

    def _update(self, name: str, change: Callable[[Project, datetime], None]) -> bool:
        """Apply ``change`` to a project, stamp ``updated_at`` and save it.

        ``change`` is applied to a copy that is saved first; the registered
        project is changed only after the save succeeded, so a failed save
        (unserialisable value, write error) leaves it untouched.

        Returns:
            False if no project named ``name`` is registered, True otherwise.
        """
        project = self.get_project(name)
        if project is None:
            return False
        now = datetime.now(UTC)
        updated = copy.deepcopy(project)
        change(updated, now)
        updated.updated_at = now
        write_json_atomic(updated.metadata_file, updated.to_dict())
        change(project, now)
        project.updated_at = now
        return True

    def update_project_status(self, name: str, status: ProjectStatus) -> bool:
        """Update project status and save the project.

        Returns:
            True if the project exists and was updated, False otherwise.

        Raises:
            OSError: If ``project.json`` cannot be written (the project is
                left unchanged).
        """

        def apply(project: Project, _now: datetime) -> None:
            project.status = status

        if not self._update(name, apply):
            return False
        logger.info("Updated status for project %s: %s", name, status.value)
        return True

    def update_project_metrics(self, name: str, metrics: dict[str, Any]) -> bool:
        """Merge ``metrics`` into the project's metrics and save the project.

        Returns:
            True if the project exists and was updated, False otherwise.

        Raises:
            TypeError: If a metric value is not JSON-serialisable.
            ValueError: If a metric value is NaN or infinity.
            OSError: If ``project.json`` cannot be written.
            In each case the project is left unchanged.
        """

        def apply(project: Project, _now: datetime) -> None:
            project.metrics.update(metrics)

        return self._update(name, apply)

    def add_project_milestone(
        self,
        name: str,
        milestone_name: str,
        milestone_data: dict[str, Any] | None = None,
    ) -> bool:
        """Record a milestone (with a ``recorded_at`` timestamp) and save the project.

        Returns:
            True if the project exists and the milestone was recorded.

        Raises:
            TypeError: If the milestone data is not JSON-serialisable.
            ValueError: If it contains NaN or infinity.
            OSError: If ``project.json`` cannot be written.
            In each case the project is left unchanged.
        """

        def apply(project: Project, now: datetime) -> None:
            project.milestones[milestone_name] = {
                **(milestone_data or {}),
                "recorded_at": now.isoformat(),
            }

        return self._update(name, apply)

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
