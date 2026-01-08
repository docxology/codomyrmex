"""
Project Management System for Codomyrmex

This module provides high-level project lifecycle management, including project
templates, scaffolding, and coordination of complex multi-module workflows.
"""

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Import Codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

try:
    from codomyrmex.performance import monitor_performance

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
    """Brief description of decorator.

Args:
    func : Description of func

    Returns: Description of return value
"""
            return func

        return decorator

from .documentation_generator import DocumentationGenerator

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

    # Template structure
    directory_structure: list[str] = field(default_factory=list)
    template_files: dict[str, str] = field(default_factory=dict)  # src -> dest mapping

    # Default workflows
    workflows: list[str] = field(default_factory=list)

    # Required modules and dependencies
    required_modules: list[str] = field(default_factory=list)
    optional_modules: list[str] = field(default_factory=list)

    # Configuration
    default_config: dict[str, Any] = field(default_factory=dict)

    # Documentation configuration
    documentation_config: dict[str, Any] = field(default_factory=dict)
    # documentation_config structure:
    # {
    #   "nested_docs": ["src/", "config/", ...],  # directories that should have README/AGENTS
    #   "doc_templates": {  # optional template content overrides
    #     "README": "custom template...",
    #     "AGENTS": "custom template..."
    #   },
    #   "doc_variables": {  # additional variables for template substitution
    #     "custom_var": "value"
    #   }
    # }

    # Template generators for files that need generation vs copying
    template_generators: dict[str, dict[str, Any]] = field(default_factory=dict)
    # template_generators structure:
    # {
    #   "relative/path/to/file": {
    #     "template": "template_name",
    #     "variables": {...}
    #   }
    # }

    # Documentation cross-linking configuration
    doc_links: dict[str, Any] = field(default_factory=dict)
    # doc_links structure:
    # {
    #   "enabled": true,
    #   "parent_link": true,  # link to parent directory
    #   "child_links": true   # link to child directories
    # }

    # Metadata
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["type"] = self.type.value
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectTemplate":
        """Create from dictionary."""
        data = data.copy()
        if "type" in data:
            data["type"] = ProjectType(data["type"])
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class Project:
    """Represents a Codomyrmex project."""

    name: str
    description: str = ""
    type: ProjectType = ProjectType.CUSTOM
    path: str = ""  # Project root directory

    # Project lifecycle
    status: ProjectStatus = ProjectStatus.PLANNING
    version: str = "1.0.0"
    template: Optional[str] = None

    # Configuration
    config: dict[str, Any] = field(default_factory=dict)

    # Workflows and tasks
    workflows: list[str] = field(default_factory=list)  # Workflow names
    active_workflows: list[str] = field(default_factory=list)

    # Dependencies
    required_modules: list[str] = field(default_factory=list)

    # Metadata
    author: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Progress tracking
    milestones: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["type"] = self.type.value
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        """Create from dictionary."""
        data = data.copy()
        if "type" in data:
            data["type"] = ProjectType(data["type"])
        if "status" in data:
            data["status"] = ProjectStatus(data["status"])
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)

    def get_project_file_path(self) -> Path:
        """Get the path to the project configuration file."""
        return Path(self.path) / ".codomyrmex" / "project.json"

    def save(self):
        """Save project to disk."""
        project_file = self.get_project_file_path()
        project_file.parent.mkdir(parents=True, exist_ok=True)

        with open(project_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, project_path: str) -> Optional["Project"]:
        """Load project from disk."""
        project_file = Path(project_path) / ".codomyrmex" / "project.json"
        if not project_file.exists():
            return None

        try:
            with open(project_file) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load project from {project_file}: {e}")
            return None


class ProjectManager:
    """Manages Codomyrmex projects and their lifecycle."""

    def __init__(
        self, projects_dir: Optional[str] = None, templates_dir: Optional[str] = None
    ):
        """Initialize the project manager."""
        self.projects_dir = (
            Path(projects_dir) if projects_dir else Path.cwd() / "projects"
        )
        self.templates_dir = (
            Path(templates_dir)
            if templates_dir
            else Path(__file__).parent / "templates"
        )

        # Create directories if they don't exist
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Load templates and projects
        self.templates: dict[str, ProjectTemplate] = {}
        self.projects: dict[str, Project] = {}

        # Initialize documentation generator
        self.doc_generator = DocumentationGenerator(
            templates_dir=self.templates_dir / "doc_templates"
        )

        self.load_templates()
        self.load_projects()

        logger.info(
            f"ProjectManager initialized with {len(self.templates)} templates and {len(self.projects)} projects"
        )

    def load_templates(self):
        """Load project templates from disk."""
        # Load from templates directory
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file) as f:
                    data = json.load(f)
                template = ProjectTemplate.from_dict(data)
                self.templates[template.name] = template
                logger.debug(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to load template from {template_file}: {e}")

        # Create default templates if none exist
        if not self.templates:
            self._create_default_templates()

    def _create_default_templates(self):
        """Create default project templates."""
        # AI Analysis Project Template
        ai_template = ProjectTemplate(
            name="ai_analysis",
            type=ProjectType.AI_ANALYSIS,
            description="AI-powered code analysis and insights project",
            directory_structure=[
                "src/",
                "data/",
                "output/",
                "reports/",
                "config/",
                ".codomyrmex/",
            ],
            workflows=["ai-analysis", "build-and-test"],
            required_modules=[
                "ai_code_editing",
                "static_analysis",
                "data_visualization",
            ],
            optional_modules=["git_operations", "documentation"],
            default_config={
                "analysis": {
                    "include_patterns": ["*.py", "*.js", "*.ts"],
                    "exclude_patterns": ["*/node_modules/*", "*/__pycache__/*"],
                    "max_file_size": "1MB",
                },
                "ai": {"provider": "openai", "model": "gpt-3.5-turbo"},
                "output": {
                    "formats": ["json", "html", "pdf"],
                    "include_visualizations": True,
                },
            },
        )
        self.templates["ai_analysis"] = ai_template
        self.save_template(ai_template)

        # Web Application Template
        web_template = ProjectTemplate(
            name="web_application",
            type=ProjectType.WEB_APPLICATION,
            description="Full-stack web application with AI integration",
            directory_structure=[
                "frontend/",
                "backend/",
                "database/",
                "docs/",
                "tests/",
                "deploy/",
                ".codomyrmex/",
            ],
            workflows=["build-and-test", "deploy"],
            required_modules=[
                "build_synthesis",
                "code",
                "documentation",
            ],
            optional_modules=["ai_code_editing", "static_analysis", "git_operations"],
            default_config={
                "frontend": {"framework": "react", "build_tool": "vite"},
                "backend": {"framework": "fastapi", "database": "postgresql"},
                "deployment": {"target": "docker", "registry": "dockerhub"},
            },
        )
        self.templates["web_application"] = web_template
        self.save_template(web_template)

        # Data Pipeline Template
        data_template = ProjectTemplate(
            name="data_pipeline",
            type=ProjectType.DATA_PIPELINE,
            description="Data processing and analysis pipeline",
            directory_structure=[
                "pipelines/",
                "data/raw/",
                "data/processed/",
                "data/output/",
                "notebooks/",
                "config/",
                "tests/",
                ".codomyrmex/",
            ],
            workflows=["data-processing", "visualization"],
            required_modules=["data_visualization", "code"],
            optional_modules=["ai_code_editing", "pattern_matching", "performance"],
            default_config={
                "data": {
                    "input_formats": ["csv", "json", "parquet"],
                    "output_formats": ["csv", "json"],
                    "validation": True,
                },
                "processing": {
                    "parallel": True,
                    "batch_size": 1000,
                    "memory_limit": "8GB",
                },
                "visualization": {
                    "charts": ["line", "bar", "scatter", "heatmap"],
                    "export_formats": ["png", "svg", "html"],
                },
            },
        )
        self.templates["data_pipeline"] = data_template
        self.save_template(data_template)

    def save_template(self, template: ProjectTemplate):
        """Save a template to disk."""
        template_file = self.templates_dir / f"{template.name}.json"
        try:
            with open(template_file, "w") as f:
                json.dump(template.to_dict(), f, indent=2)
            logger.debug(f"Saved template: {template.name}")
        except Exception as e:
            logger.error(f"Failed to save template {template.name}: {e}")

    def load_projects(self):
        """Load projects from the projects directory."""
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project = Project.load(str(project_dir))
                if project:
                    self.projects[project.name] = project
                    logger.debug(f"Loaded project: {project.name}")

    def list_templates(self) -> list[str]:
        """List available project templates."""
        return list(self.templates.keys())

    def get_template(self, name: str) -> Optional[ProjectTemplate]:
        """Get a template by name."""
        return self.templates.get(name)

    def list_projects(self) -> list[str]:
        """List available projects."""
        return list(self.projects.keys())

    def get_project(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        return self.projects.get(name)

    @monitor_performance(function_name="create_project")
    def create_project(
        self,
        name: str,
        template_name: Optional[str] = None,
        path: Optional[str] = None,
        **kwargs,
    ) -> Project:
        """Create a new project from a template."""
        if name in self.projects:
            raise ValueError(f"Project '{name}' already exists")

        # Determine project path
        if not path:
            path = str(self.projects_dir / name)

        project_path = Path(path)
        if project_path.exists() and any(project_path.iterdir()):
            raise ValueError(f"Directory '{path}' already exists and is not empty")

        # Get template
        template = None
        if template_name:
            template = self.get_template(template_name)
            if not template:
                raise ValueError(f"Template '{template_name}' not found")

        # Create project
        project = Project(
            name=name,
            path=str(project_path),
            description=kwargs.get("description", ""),
            type=template.type if template else ProjectType.CUSTOM,
            template=template_name,
            author=kwargs.get("author", ""),
            tags=kwargs.get("tags", []),
        )

        # Apply template
        if template:
            project.required_modules = template.required_modules.copy()
            project.workflows = template.workflows.copy()
            project.config = template.default_config.copy()

            # Create directory structure
            project_path.mkdir(parents=True, exist_ok=True)
            for dir_path in template.directory_structure:
                (project_path / dir_path).mkdir(parents=True, exist_ok=True)

            # Copy template files
            template_source_dir = self.templates_dir / template_name
            if template_source_dir.exists():
                for src_pattern, dest_path in template.template_files.items():
                    src_files = template_source_dir.glob(src_pattern)
                    for src_file in src_files:
                        dest_file = project_path / dest_path / src_file.name
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dest_file)
        else:
            # Create basic structure for custom project
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / ".codomyrmex").mkdir(exist_ok=True)

        # Save project
        project.save()
        self.projects[name] = project

        # Generate documentation if template has documentation_config
        if template and template.documentation_config:
            nested_docs = template.documentation_config.get("nested_docs", [])
            doc_links = template.documentation_config.get("doc_links", {}) or template.doc_links

            success = self.doc_generator.generate_all_documentation(
                project_path=project_path,
                project_name=project.name,
                project_type=project.type.value,
                description=project.description,
                version=project.version,
                author=project.author,
                created_at=project.created_at.isoformat(),
                nested_dirs=nested_docs,
                template=template_name,
                doc_links=doc_links,
            )

            if success:
                logger.info(f"Generated documentation for project: {name}")
            else:
                logger.warning(f"Some documentation generation failed for project: {name}")
        elif template:
            # Generate basic documentation even without documentation_config
            nested_docs = [d.rstrip("/") for d in template.directory_structure if d.rstrip("/") and d != ".codomyrmex"]
            success = self.doc_generator.generate_all_documentation(
                project_path=project_path,
                project_name=project.name,
                project_type=project.type.value,
                description=project.description,
                version=project.version,
                author=project.author,
                created_at=project.created_at.isoformat(),
                nested_dirs=nested_docs,
                template=template_name,
                doc_links={"enabled": True, "parent_link": True, "child_links": True},
            )
            if success:
                logger.info(f"Generated basic documentation for project: {name}")

        logger.info(f"Created project: {name} at {path}")
        return project

    def delete_project(self, name: str, remove_files: bool = False) -> bool:
        """Delete a project."""
        project = self.get_project(name)
        if not project:
            return False

        # Remove from memory
        del self.projects[name]

        # Optionally remove files
        if remove_files:
            project_path = Path(project.path)
            if project_path.exists():
                shutil.rmtree(project_path)
                logger.info(f"Removed project files: {project.path}")

        logger.info(f"Deleted project: {name}")
        return True

    def archive_project(self, name: str, archive_path: Optional[str] = None) -> bool:
        """Archive a project."""
        project = self.get_project(name)
        if not project:
            return False

        if not archive_path:
            archive_path = str(self.projects_dir / "archives" / f"{name}.tar.gz")

        archive_dir = Path(archive_path).parent
        archive_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create archive
            import tarfile

            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(project.path, arcname=name)

            # Update project status
            project.status = ProjectStatus.ARCHIVED
            project.save()

            logger.info(f"Archived project: {name} to {archive_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to archive project {name}: {e}")
            return False

    def execute_project_workflow(
        self, project_name: str, workflow_name: str, **params
    ) -> dict[str, Any]:
        """Execute a workflow for a project."""
        project = self.get_project(project_name)
        if not project:
            return {"success": False, "error": f'Project "{project_name}" not found'}

        if workflow_name not in project.workflows:
            return {
                "success": False,
                "error": f'Workflow "{workflow_name}" not available for project "{project_name}"',
            }

        # Get workflow manager and execute
        from . import get_workflow_manager

        workflow_manager = get_workflow_manager()

        # Set project context in parameters
        project_params = {
            "project_name": project_name,
            "project_path": project.path,
            "project_config": project.config,
            **params,
        }

        return workflow_manager.execute_workflow(workflow_name, **project_params)

    def get_project_status(self, name: str) -> Optional[dict[str, Any]]:
        """Get detailed project status."""
        project = self.get_project(name)
        if not project:
            return None

        return {
            "name": project.name,
            "status": project.status.value,
            "type": project.type.value,
            "version": project.version,
            "path": project.path,
            "workflows": len(project.workflows),
            "active_workflows": len(project.active_workflows),
            "required_modules": project.required_modules,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "milestones": project.milestones,
            "metrics": project.metrics,
        }

    def update_project_metrics(self, name: str, metrics: dict[str, Any]):
        """Update project metrics."""
        project = self.get_project(name)
        if project:
            project.metrics.update(metrics)
            project.updated_at = datetime.now(timezone.utc)
            project.save()

    def add_project_milestone(
        self, name: str, milestone_name: str, milestone_data: dict[str, Any]
    ):
        """Add a milestone to a project."""
        project = self.get_project(name)
        if project:
            milestone_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            project.milestones[milestone_name] = milestone_data
            project.updated_at = datetime.now(timezone.utc)
            project.save()

    def get_projects_summary(self) -> dict[str, Any]:
        """Get summary of all projects."""
        summary = {
            "total_projects": len(self.projects),
            "by_status": {},
            "by_type": {},
            "recent_activity": [],
        }

        for project in self.projects.values():
            # Count by status
            status = project.status.value
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            # Count by type
            ptype = project.type.value
            summary["by_type"][ptype] = summary["by_type"].get(ptype, 0) + 1

            # Recent activity
            summary["recent_activity"].append(
                {
                    "name": project.name,
                    "status": status,
                    "updated_at": project.updated_at.isoformat(),
                }
            )

        # Sort recent activity
        summary["recent_activity"].sort(key=lambda x: x["updated_at"], reverse=True)
        summary["recent_activity"] = summary["recent_activity"][:10]  # Top 10

        return summary


# Global project manager instance
_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get the global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
