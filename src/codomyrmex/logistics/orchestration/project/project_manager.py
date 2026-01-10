"""Project Management System for Codomyrmex.

This module provides high-level project lifecycle management, including project
templates, scaffolding, and coordination of complex multi-module workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import shutil
import logging

from codomyrmex.logging_monitoring.logger_config import get_logger
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
    directory_structure: List[str] = field(default_factory=list)
    template_files: Dict[str, str] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    """Project definition."""
    name: str
    path: Path
    type: ProjectType
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    owner: Optional[str] = None
    version: str = "0.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
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
            "version": self.version
        }


class ProjectManager:
    """Manages project lifecycles."""

    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize the project manager."""
        self.projects_root = projects_root or Path.cwd()
        self.doc_generator = DocumentationGenerator()
        self.active_projects: Dict[str, Project] = {}

    def create_project(self, name: str, type: ProjectType, description: str = "") -> Optional[Project]:
        """Create a new project."""
        project_path = self.projects_root / name
        
        if project_path.exists():
            logger.error(f"Project directory already exists: {project_path}")
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
                status=ProjectStatus.ACTIVE
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
                nested_dirs=["src", "tests", "config", "docs"]
            )
            
            self.active_projects[name] = project
            logger.info(f"Created project: {name}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {e}")
            if project_path.exists():
                shutil.rmtree(project_path)
            return None

    def get_project(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        return self.active_projects.get(name)

    def list_projects(self) -> List[Project]:
        """List all active projects."""
        return list(self.active_projects.values())

    def update_project_status(self, name: str, status: ProjectStatus) -> bool:
        """Update project status."""
        project = self.get_project(name)
        if project:
            project.status = status
            project.updated_at = datetime.now(timezone.utc)
            logger.info(f"Updated status for project {name}: {status.value}")
            return True
        return False


# Global project manager instance
_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get the global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager

