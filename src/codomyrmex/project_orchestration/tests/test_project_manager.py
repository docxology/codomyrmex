"""
Comprehensive unit tests for ProjectManager.

This module contains extensive unit tests for the ProjectManager class,
covering all public methods, error conditions, and edge cases.
"""

import pytest
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.project_orchestration.project_manager import (
    ProjectManager,
    Project,
    ProjectTemplate,
    ProjectStatus,
    ProjectType
)


class TestProject:
    """Test cases for Project dataclass."""
    
    def test_project_creation(self):
        """Test basic Project creation."""
        project = Project(
            name="test_project",
            description="A test project",
            project_type=ProjectType.AI_ANALYSIS,
            status=ProjectStatus.ACTIVE,
            path="/path/to/project",
            template_name="ai_analysis",
            created_at=datetime.now(timezone.utc)
        )
        
        assert project.name == "test_project"
        assert project.description == "A test project"
        assert project.project_type == ProjectType.AI_ANALYSIS
        assert project.status == ProjectStatus.ACTIVE
        assert project.path == "/path/to/project"
        assert project.template_name == "ai_analysis"
        assert project.created_at is not None
    
    def test_project_defaults(self):
        """Test Project with default values."""
        project = Project(name="test_project")
        
        assert project.name == "test_project"
        assert project.description == ""
        assert project.project_type == ProjectType.GENERAL
        assert project.status == ProjectStatus.PLANNING
        assert project.path is None
        assert project.template_name is None
        assert project.created_at is not None
    
    def test_project_serialization(self):
        """Test Project serialization to/from dictionary."""
        project = Project(
            name="test_project",
            description="Test description",
            project_type=ProjectType.WEB_APPLICATION,
            status=ProjectStatus.ACTIVE,
            path="/test/path",
            template_name="web_template",
            tags=["web", "test"],
            metadata={"key": "value"}
        )
        
        # Test to_dict
        project_dict = project.to_dict()
        assert project_dict["name"] == "test_project"
        assert project_dict["description"] == "Test description"
        assert project_dict["project_type"] == ProjectType.WEB_APPLICATION.value
        assert project_dict["status"] == ProjectStatus.ACTIVE.value
        assert project_dict["path"] == "/test/path"
        assert project_dict["template_name"] == "web_template"
        assert project_dict["tags"] == ["web", "test"]
        assert project_dict["metadata"] == {"key": "value"}
        
        # Test from_dict
        restored_project = Project.from_dict(project_dict)
        assert restored_project.name == "test_project"
        assert restored_project.description == "Test description"
        assert restored_project.project_type == ProjectType.WEB_APPLICATION
        assert restored_project.status == ProjectStatus.ACTIVE
        assert restored_project.path == "/test/path"
        assert restored_project.template_name == "web_template"
        assert restored_project.tags == ["web", "test"]
        assert restored_project.metadata == {"key": "value"}


class TestProjectTemplate:
    """Test cases for ProjectTemplate dataclass."""
    
    def test_project_template_creation(self):
        """Test basic ProjectTemplate creation."""
        template = ProjectTemplate(
            name="test_template",
            project_type=ProjectType.AI_ANALYSIS,
            description="A test template",
            directory_structure=["src/", "tests/", "docs/"],
            files_to_create=["README.md", "requirements.txt"],
            dependencies=["numpy", "pandas"],
            workflows=["analysis", "testing"]
        )
        
        assert template.name == "test_template"
        assert template.project_type == ProjectType.AI_ANALYSIS
        assert template.description == "A test template"
        assert template.directory_structure == ["src/", "tests/", "docs/"]
        assert template.files_to_create == ["README.md", "requirements.txt"]
        assert template.dependencies == ["numpy", "pandas"]
        assert template.workflows == ["analysis", "testing"]
    
    def test_project_template_defaults(self):
        """Test ProjectTemplate with default values."""
        template = ProjectTemplate(name="simple_template")
        
        assert template.name == "simple_template"
        assert template.project_type == ProjectType.GENERAL
        assert template.description == ""
        assert template.directory_structure == []
        assert template.files_to_create == []
        assert template.dependencies == []
        assert template.workflows == []
    
    def test_project_template_serialization(self):
        """Test ProjectTemplate serialization to/from dictionary."""
        template = ProjectTemplate(
            name="test_template",
            project_type=ProjectType.DATA_PIPELINE,
            description="Test template",
            directory_structure=["data/", "scripts/"],
            files_to_create=["config.yaml"],
            dependencies=["pandas", "scikit-learn"],
            workflows=["data_processing", "model_training"]
        )
        
        # Test to_dict
        template_dict = template.to_dict()
        assert template_dict["name"] == "test_template"
        assert template_dict["project_type"] == ProjectType.DATA_PIPELINE.value
        assert template_dict["description"] == "Test template"
        assert template_dict["directory_structure"] == ["data/", "scripts/"]
        assert template_dict["files_to_create"] == ["config.yaml"]
        assert template_dict["dependencies"] == ["pandas", "scikit-learn"]
        assert template_dict["workflows"] == ["data_processing", "model_training"]
        
        # Test from_dict
        restored_template = ProjectTemplate.from_dict(template_dict)
        assert restored_template.name == "test_template"
        assert restored_template.project_type == ProjectType.DATA_PIPELINE
        assert restored_template.description == "Test template"
        assert restored_template.directory_structure == ["data/", "scripts/"]
        assert restored_template.files_to_create == ["config.yaml"]
        assert restored_template.dependencies == ["pandas", "scikit-learn"]
        assert restored_template.workflows == ["data_processing", "model_training"]


class TestProjectManager:
    """Test cases for ProjectManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def project_manager(self, temp_dir):
        """Create a ProjectManager instance for testing."""
        return ProjectManager(projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates")
    
    def test_project_manager_initialization(self, temp_dir):
        """Test ProjectManager initialization."""
        manager = ProjectManager(
            projects_dir=temp_dir / "projects",
            templates_dir=temp_dir / "templates"
        )
        
        assert manager.projects_dir == temp_dir / "projects"
        assert manager.templates_dir == temp_dir / "templates"
        assert manager.projects == {}
        assert manager.templates == {}
        assert manager.logger is not None
    
    def test_project_manager_default_directories(self):
        """Test ProjectManager with default directories."""
        manager = ProjectManager()
        
        assert manager.projects_dir == Path.cwd() / "projects"
        assert manager.templates_dir is not None
        assert manager.templates_dir.exists()
    
    def test_create_project_success(self, project_manager):
        """Test successful project creation."""
        project = project_manager.create_project(
            name="test_project",
            description="A test project",
            template_name="ai_analysis",
            path="/path/to/project"
        )
        
        assert project is not None
        assert project.name == "test_project"
        assert project.description == "A test project"
        assert project.template_name == "ai_analysis"
        assert project.path == "/path/to/project"
        assert project.status == ProjectStatus.PLANNING
        assert project.id in project_manager.projects
    
    def test_create_project_with_template(self, project_manager):
        """Test project creation with template."""
        # First create a template
        template = ProjectTemplate(
            name="test_template",
            project_type=ProjectType.AI_ANALYSIS,
            description="Test template",
            directory_structure=["src/", "tests/"],
            files_to_create=["README.md"],
            dependencies=["numpy"],
            workflows=["analysis"]
        )
        project_manager.templates["test_template"] = template
        
        project = project_manager.create_project(
            name="template_project",
            template_name="test_template"
        )
        
        assert project is not None
        assert project.template_name == "test_template"
        assert project.project_type == ProjectType.AI_ANALYSIS
    
    def test_create_project_invalid_template(self, project_manager):
        """Test project creation with invalid template."""
        project = project_manager.create_project(
            name="invalid_project",
            template_name="nonexistent_template"
        )
        
        # Should still create project but with default values
        assert project is not None
        assert project.name == "invalid_project"
        assert project.template_name == "nonexistent_template"
        assert project.project_type == ProjectType.GENERAL
    
    def test_get_project_existing(self, project_manager):
        """Test getting existing project."""
        project = project_manager.create_project(name="test_project")
        
        retrieved_project = project_manager.get_project("test_project")
        
        assert retrieved_project is not None
        assert retrieved_project.name == "test_project"
        assert retrieved_project.id == project.id
    
    def test_get_project_nonexistent(self, project_manager):
        """Test getting non-existent project."""
        retrieved_project = project_manager.get_project("nonexistent")
        
        assert retrieved_project is None
    
    def test_list_projects(self, project_manager):
        """Test listing projects."""
        # Create multiple projects
        project1 = project_manager.create_project(name="project1")
        project2 = project_manager.create_project(name="project2")
        
        projects = project_manager.list_projects()
        
        assert len(projects) == 2
        assert "project1" in projects
        assert "project2" in projects
    
    def test_list_projects_by_status(self, project_manager):
        """Test listing projects by status."""
        # Create projects with different statuses
        project1 = project_manager.create_project(name="project1")
        project1.status = ProjectStatus.ACTIVE
        
        project2 = project_manager.create_project(name="project2")
        project2.status = ProjectStatus.COMPLETED
        
        # List all projects
        all_projects = project_manager.list_projects()
        assert len(all_projects) == 2
        
        # List active projects
        active_projects = project_manager.list_projects(status=ProjectStatus.ACTIVE)
        assert len(active_projects) == 1
        assert active_projects[0].name == "project1"
        
        # List completed projects
        completed_projects = project_manager.list_projects(status=ProjectStatus.COMPLETED)
        assert len(completed_projects) == 1
        assert completed_projects[0].name == "project2"
    
    def test_update_project(self, project_manager):
        """Test updating project."""
        project = project_manager.create_project(name="test_project")
        
        # Update project
        updated_project = project_manager.update_project(
            "test_project",
            description="Updated description",
            status=ProjectStatus.ACTIVE,
            metadata={"key": "value"}
        )
        
        assert updated_project is not None
        assert updated_project.description == "Updated description"
        assert updated_project.status == ProjectStatus.ACTIVE
        assert updated_project.metadata == {"key": "value"}
    
    def test_update_project_nonexistent(self, project_manager):
        """Test updating non-existent project."""
        updated_project = project_manager.update_project("nonexistent")
        
        assert updated_project is None
    
    def test_delete_project(self, project_manager):
        """Test deleting project."""
        project = project_manager.create_project(name="test_project")
        
        result = project_manager.delete_project("test_project")
        
        assert result is True
        assert "test_project" not in project_manager.projects
    
    def test_delete_project_nonexistent(self, project_manager):
        """Test deleting non-existent project."""
        result = project_manager.delete_project("nonexistent")
        
        assert result is False
    
    def test_create_template(self, project_manager):
        """Test creating template."""
        template = ProjectTemplate(
            name="test_template",
            project_type=ProjectType.AI_ANALYSIS,
            description="Test template"
        )
        
        result = project_manager.create_template(template)
        
        assert result is True
        assert "test_template" in project_manager.templates
    
    def test_get_template(self, project_manager):
        """Test getting template."""
        template = ProjectTemplate(name="test_template")
        project_manager.templates["test_template"] = template
        
        retrieved_template = project_manager.get_template("test_template")
        
        assert retrieved_template is not None
        assert retrieved_template.name == "test_template"
    
    def test_get_template_nonexistent(self, project_manager):
        """Test getting non-existent template."""
        retrieved_template = project_manager.get_template("nonexistent")
        
        assert retrieved_template is None
    
    def test_list_templates(self, project_manager):
        """Test listing templates."""
        # Create multiple templates
        template1 = ProjectTemplate(name="template1")
        template2 = ProjectTemplate(name="template2")
        
        project_manager.templates["template1"] = template1
        project_manager.templates["template2"] = template2
        
        templates = project_manager.list_templates()
        
        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates
    
    def test_scaffold_project_directory(self, project_manager, temp_dir):
        """Test scaffolding project directory."""
        # Create template with directory structure
        template = ProjectTemplate(
            name="test_template",
            directory_structure=["src/", "tests/", "docs/"],
            files_to_create=["README.md", "requirements.txt"],
            dependencies=["numpy", "pandas"]
        )
        
        project_path = temp_dir / "test_project"
        
        result = project_manager.scaffold_project_directory(
            project_path,
            template,
            {"project_name": "Test Project"}
        )
        
        assert result is True
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "docs").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "requirements.txt").exists()
    
    def test_scaffold_project_directory_existing(self, project_manager, temp_dir):
        """Test scaffolding project directory when it already exists."""
        # Create existing directory
        project_path = temp_dir / "existing_project"
        project_path.mkdir()
        
        template = ProjectTemplate(name="test_template")
        
        result = project_manager.scaffold_project_directory(
            project_path,
            template,
            {}
        )
        
        # Should fail because directory exists
        assert result is False
    
    def test_save_project(self, project_manager, temp_dir):
        """Test saving project to disk."""
        project = project_manager.create_project(name="test_project")
        
        result = project_manager.save_project(project)
        
        assert result is True
        
        # Check if file was created
        project_file = project_manager.projects_dir / f"{project.id}.json"
        assert project_file.exists()
        
        # Check file contents
        with open(project_file, 'r') as f:
            data = json.load(f)
        
        assert data["name"] == "test_project"
        assert data["id"] == project.id
    
    def test_load_project(self, project_manager, temp_dir):
        """Test loading project from disk."""
        # Create project file manually
        project_data = {
            "id": "test_id",
            "name": "test_project",
            "description": "Test description",
            "project_type": "ai_analysis",
            "status": "planning",
            "path": "/test/path",
            "template_name": "ai_analysis",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": None,
            "tags": [],
            "metadata": {}
        }
        
        project_file = project_manager.projects_dir / "test_id.json"
        project_manager.projects_dir.mkdir(parents=True, exist_ok=True)
        
        with open(project_file, 'w') as f:
            json.dump(project_data, f)
        
        # Load project
        project = project_manager.load_project("test_id")
        
        assert project is not None
        assert project.name == "test_project"
        assert project.id == "test_id"
    
    def test_load_project_nonexistent(self, project_manager):
        """Test loading non-existent project."""
        project = project_manager.load_project("nonexistent")
        
        assert project is None
    
    def test_save_template(self, project_manager, temp_dir):
        """Test saving template to disk."""
        template = ProjectTemplate(
            name="test_template",
            project_type=ProjectType.AI_ANALYSIS,
            description="Test template"
        )
        
        result = project_manager.save_template(template)
        
        assert result is True
        
        # Check if file was created
        template_file = project_manager.templates_dir / "test_template.json"
        assert template_file.exists()
        
        # Check file contents
        with open(template_file, 'r') as f:
            data = json.load(f)
        
        assert data["name"] == "test_template"
        assert data["project_type"] == "ai_analysis"
    
    def test_load_template(self, project_manager, temp_dir):
        """Test loading template from disk."""
        # Create template file manually
        template_data = {
            "name": "test_template",
            "project_type": "ai_analysis",
            "description": "Test template",
            "directory_structure": [],
            "files_to_create": [],
            "dependencies": [],
            "workflows": []
        }
        
        template_file = project_manager.templates_dir / "test_template.json"
        project_manager.templates_dir.mkdir(parents=True, exist_ok=True)
        
        with open(template_file, 'w') as f:
            json.dump(template_data, f)
        
        # Load template
        template = project_manager.load_template("test_template")
        
        assert template is not None
        assert template.name == "test_template"
        assert template.project_type == ProjectType.AI_ANALYSIS
    
    def test_load_template_nonexistent(self, project_manager):
        """Test loading non-existent template."""
        template = project_manager.load_template("nonexistent")
        
        assert template is None


class TestProjectManagerIntegration:
    """Integration tests for ProjectManager."""
    
    def test_full_project_lifecycle(self, temp_dir):
        """Test complete project lifecycle: create, update, delete."""
        manager = ProjectManager(
            projects_dir=temp_dir / "projects",
            templates_dir=temp_dir / "templates"
        )
        
        # Create project
        project = manager.create_project(
            name="lifecycle_test",
            description="Test project for lifecycle",
            template_name="ai_analysis"
        )
        
        assert project is not None
        assert project.name == "lifecycle_test"
        assert project.id in manager.projects
        
        # Update project
        updated_project = manager.update_project(
            "lifecycle_test",
            description="Updated description",
            status=ProjectStatus.ACTIVE
        )
        
        assert updated_project is not None
        assert updated_project.description == "Updated description"
        assert updated_project.status == ProjectStatus.ACTIVE
        
        # List projects
        projects = manager.list_projects()
        assert len(projects) == 1
        assert "lifecycle_test" in projects
        
        # Delete project
        result = manager.delete_project("lifecycle_test")
        assert result is True
        assert "lifecycle_test" not in manager.projects
    
    def test_template_and_project_integration(self, temp_dir):
        """Test integration between templates and projects."""
        manager = ProjectManager(
            projects_dir=temp_dir / "projects",
            templates_dir=temp_dir / "templates"
        )
        
        # Create template
        template = ProjectTemplate(
            name="integration_template",
            project_type=ProjectType.WEB_APPLICATION,
            description="Integration test template",
            directory_structure=["src/", "static/"],
            files_to_create=["index.html", "style.css"],
            dependencies=["flask", "jinja2"],
            workflows=["build", "deploy"]
        )
        
        result = manager.create_template(template)
        assert result is True
        
        # Create project using template
        project = manager.create_project(
            name="integration_project",
            template_name="integration_template"
        )
        
        assert project is not None
        assert project.template_name == "integration_template"
        assert project.project_type == ProjectType.WEB_APPLICATION
        
        # Verify template is available
        retrieved_template = manager.get_template("integration_template")
        assert retrieved_template is not None
        assert retrieved_template.name == "integration_template"
    
    def test_persistence_integration(self, temp_dir):
        """Test persistence integration between projects and templates."""
        manager1 = ProjectManager(
            projects_dir=temp_dir / "projects",
            templates_dir=temp_dir / "templates"
        )
        
        # Create template and project
        template = ProjectTemplate(name="persistence_template")
        manager1.create_template(template)
        
        project = manager1.create_project(
            name="persistence_project",
            template_name="persistence_template"
        )
        
        # Create new manager instance (simulates restart)
        manager2 = ProjectManager(
            projects_dir=temp_dir / "projects",
            templates_dir=temp_dir / "templates"
        )
        
        # Verify template and project are loaded
        assert "persistence_template" in manager2.templates
        assert "persistence_project" in manager2.projects
        
        # Verify project details
        loaded_project = manager2.get_project("persistence_project")
        assert loaded_project is not None
        assert loaded_project.name == "persistence_project"
        assert loaded_project.template_name == "persistence_template"


if __name__ == "__main__":
    pytest.main([__file__])
