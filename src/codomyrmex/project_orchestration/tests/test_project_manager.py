"""
Comprehensive unit tests for ProjectManager.

This module contains extensive unit tests for the ProjectManager class,
covering all public methods, error conditions, and edge cases.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.project_orchestration.documentation_generator import DocumentationGenerator
from codomyrmex.project_orchestration.project_manager import (
    Project,
    ProjectManager,
    ProjectStatus,
    ProjectTemplate,
    ProjectType,
)

logger = get_logger(__name__)


class TestProject:
    """Test cases for Project dataclass."""

    def test_project_creation(self):
        """Test basic Project creation."""
        project = Project(
            name="test_project",
            description="A test project",
            type=ProjectType.AI_ANALYSIS,
            status=ProjectStatus.ACTIVE,
            path="/path/to/project",
            template="ai_analysis",
            created_at=datetime.now(timezone.utc),
        )

        assert project.name == "test_project"
        assert project.description == "A test project"
        assert project.type == ProjectType.AI_ANALYSIS
        assert project.status == ProjectStatus.ACTIVE
        assert project.path == "/path/to/project"
        assert project.template == "ai_analysis"
        assert project.created_at is not None

    def test_project_defaults(self):
        """Test Project with default values."""
        project = Project(name="test_project")

        assert project.name == "test_project"
        assert project.description == ""
        assert project.type == ProjectType.CUSTOM
        assert project.status == ProjectStatus.PLANNING
        assert project.path == ""
        assert project.template is None
        assert project.created_at is not None

    def test_project_serialization(self):
        """Test Project serialization to/from dictionary."""
        project = Project(
            name="test_project",
            description="Test description",
            type=ProjectType.WEB_APPLICATION,
            status=ProjectStatus.ACTIVE,
            path="/test/path",
            template="web_template",
            tags=["web", "test"],
        )

        # Test to_dict
        project_dict = project.to_dict()
        assert project_dict["name"] == "test_project"
        assert project_dict["description"] == "Test description"
        assert project_dict["type"] == ProjectType.WEB_APPLICATION.value
        assert project_dict["status"] == ProjectStatus.ACTIVE.value
        assert project_dict["path"] == "/test/path"
        assert project_dict["template"] == "web_template"
        assert project_dict["tags"] == ["web", "test"]

        # Test from_dict
        restored_project = Project.from_dict(project_dict)
        assert restored_project.name == "test_project"
        assert restored_project.description == "Test description"
        assert restored_project.type == ProjectType.WEB_APPLICATION
        assert restored_project.status == ProjectStatus.ACTIVE
        assert restored_project.path == "/test/path"
        assert restored_project.template == "web_template"
        assert restored_project.tags == ["web", "test"]


class TestProjectTemplate:
    """Test cases for ProjectTemplate dataclass."""

    def test_project_template_creation(self):
        """Test basic ProjectTemplate creation."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            description="A test template",
            directory_structure=["src/", "tests/", "docs/"],
            required_modules=["numpy", "pandas"],
            workflows=["analysis", "testing"],
        )

        assert template.name == "test_template"
        assert template.type == ProjectType.AI_ANALYSIS
        assert template.description == "A test template"
        assert template.directory_structure == ["src/", "tests/", "docs/"]
        assert template.required_modules == ["numpy", "pandas"]
        assert template.workflows == ["analysis", "testing"]

    def test_project_template_defaults(self):
        """Test ProjectTemplate with default values."""
        template = ProjectTemplate(name="simple_template", type=ProjectType.CUSTOM)

        assert template.name == "simple_template"
        assert template.type == ProjectType.CUSTOM
        assert template.description == ""
        assert template.directory_structure == []
        assert template.required_modules == []
        assert template.workflows == []

    def test_project_template_serialization(self):
        """Test ProjectTemplate serialization to/from dictionary."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.DATA_PIPELINE,
            description="Test template",
            directory_structure=["data/", "scripts/"],
            required_modules=["pandas", "scikit-learn"],
            workflows=["data_processing", "model_training"],
        )

        # Test to_dict
        template_dict = template.to_dict()
        assert template_dict["name"] == "test_template"
        assert template_dict["type"] == ProjectType.DATA_PIPELINE.value
        assert template_dict["description"] == "Test template"
        assert template_dict["directory_structure"] == ["data/", "scripts/"]
        assert template_dict["required_modules"] == ["pandas", "scikit-learn"]
        assert template_dict["workflows"] == ["data_processing", "model_training"]

        # Test from_dict
        restored_template = ProjectTemplate.from_dict(template_dict)
        assert restored_template.name == "test_template"
        assert restored_template.type == ProjectType.DATA_PIPELINE
        assert restored_template.description == "Test template"
        assert restored_template.directory_structure == ["data/", "scripts/"]
        assert restored_template.required_modules == ["pandas", "scikit-learn"]
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
        return ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

    def test_project_manager_initialization(self, temp_dir):
        """Test ProjectManager initialization."""
        manager = ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

        assert manager.projects_dir == temp_dir / "projects"
        assert manager.templates_dir == temp_dir / "templates"
        assert manager.projects == {}
        assert manager.templates == {}
        assert hasattr(manager, 'doc_generator')

    def test_project_manager_default_directories(self):
        """Test ProjectManager with default directories."""
        manager = ProjectManager()

        assert manager.projects_dir == Path.cwd() / "projects"
        assert manager.templates_dir is not None
        assert manager.templates_dir.exists()

    def test_create_project_success(self, project_manager, temp_dir):
        """Test successful project creation."""
        project = project_manager.create_project(
            name="test_project",
            description="A test project",
            template_name="ai_analysis",
            path=str(temp_dir / "test_project"),
        )

        assert project is not None
        assert project.name == "test_project"
        assert project.description == "A test project"
        assert project.template == "ai_analysis"
        assert project.path == str(temp_dir / "test_project")
        assert project.status == ProjectStatus.PLANNING
        assert project.name in project_manager.projects

    def test_create_project_with_template(self, project_manager, temp_dir):
        """Test project creation with template."""
        # First create a template
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            description="Test template",
            directory_structure=["src/", "tests/"],
            required_modules=["numpy"],
            workflows=["analysis"],
        )
        project_manager.templates["test_template"] = template

        project = project_manager.create_project(
            name="template_project", template_name="test_template", path=str(temp_dir / "template_project")
        )

        assert project is not None
        assert project.template == "test_template"
        assert project.type == ProjectType.AI_ANALYSIS

    def test_create_project_invalid_template(self, project_manager, temp_dir):
        """Test project creation with invalid template."""
        with pytest.raises(ValueError, match="Template 'nonexistent_template' not found"):
            project_manager.create_project(
                name="invalid_project", template_name="nonexistent_template", path=str(temp_dir / "invalid_project")
            )

    def test_get_project_existing(self, project_manager, temp_dir):
        """Test getting existing project."""
        project = project_manager.create_project(name="test_project", path=str(temp_dir / "test_project"))

        retrieved_project = project_manager.get_project("test_project")

        assert retrieved_project is not None
        assert retrieved_project.name == "test_project"
        assert retrieved_project.name == project.name

    def test_get_project_nonexistent(self, project_manager):
        """Test getting non-existent project."""
        retrieved_project = project_manager.get_project("nonexistent")

        assert retrieved_project is None

    def test_list_projects(self, project_manager, temp_dir):
        """Test listing projects."""
        # Create multiple projects
        project_manager.create_project(name="project1", path=str(temp_dir / "project1"))
        project_manager.create_project(name="project2", path=str(temp_dir / "project2"))

        projects = project_manager.list_projects()

        assert len(projects) == 2
        assert "project1" in projects
        assert "project2" in projects

    def test_update_project_metrics(self, project_manager, temp_dir):
        """Test updating project metrics."""
        project_manager.create_project(name="test_project", path=str(temp_dir / "test_project"))

        # Update project metrics
        project_manager.update_project_metrics("test_project", {"test_metric": 42})

        project = project_manager.get_project("test_project")
        assert project is not None
        assert project.metrics["test_metric"] == 42

    def test_delete_project(self, project_manager, temp_dir):
        """Test deleting project."""
        project_manager.create_project(name="test_project", path=str(temp_dir / "test_project"))

        result = project_manager.delete_project("test_project")

        assert result is True
        assert "test_project" not in project_manager.projects

    def test_delete_project_nonexistent(self, project_manager):
        """Test deleting non-existent project."""
        result = project_manager.delete_project("nonexistent")

        assert result is False

    def test_get_template(self, project_manager):
        """Test getting template."""
        template = ProjectTemplate(name="test_template", type=ProjectType.AI_ANALYSIS)
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
        template1 = ProjectTemplate(name="template1", type=ProjectType.AI_ANALYSIS)
        template2 = ProjectTemplate(name="template2", type=ProjectType.DATA_PIPELINE)

        project_manager.templates["template1"] = template1
        project_manager.templates["template2"] = template2

        templates = project_manager.list_templates()

        assert len(templates) == 2
        assert "template1" in templates
        assert "template2" in templates

    def test_save_template(self, project_manager, temp_dir):
        """Test saving template to disk."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            description="Test template",
        )

        project_manager.save_template(template)

        # Check if file was created
        template_file = project_manager.templates_dir / "test_template.json"
        assert template_file.exists()

        # Check file contents
        with open(template_file) as f:
            data = json.load(f)

        assert data["name"] == "test_template"
        assert data["type"] == "ai_analysis"


class TestProjectManagerIntegration:
    """Integration tests for ProjectManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_full_project_lifecycle(self, temp_dir):
        """Test complete project lifecycle: create, update metrics, delete."""
        manager = ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

        # Create project
        project = manager.create_project(
            name="lifecycle_test",
            description="Test project for lifecycle",
            template_name="ai_analysis",
            path=str(temp_dir / "lifecycle_test"),
        )

        assert project is not None
        assert project.name == "lifecycle_test"
        assert project.name in manager.projects

        # Update project metrics
        manager.update_project_metrics("lifecycle_test", {"test": "value"})
        project = manager.get_project("lifecycle_test")
        assert project.metrics["test"] == "value"

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
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

        # Create template
        template = ProjectTemplate(
            name="integration_template",
            type=ProjectType.WEB_APPLICATION,
            description="Integration test template",
            directory_structure=["src/", "static/"],
            required_modules=["flask", "jinja2"],
            workflows=["build", "deploy"],
        )

        manager.save_template(template)
        manager.templates["integration_template"] = template

        # Create project using template
        project = manager.create_project(
            name="integration_project", template_name="integration_template", path=str(temp_dir / "integration_project")
        )

        assert project is not None
        assert project.template == "integration_template"
        assert project.type == ProjectType.WEB_APPLICATION

        # Verify template is available
        retrieved_template = manager.get_template("integration_template")
        assert retrieved_template is not None
        assert retrieved_template.name == "integration_template"

    def test_persistence_integration(self, temp_dir):
        """Test persistence integration between projects and templates."""
        manager1 = ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

        # Create template and project
        template = ProjectTemplate(name="persistence_template", type=ProjectType.AI_ANALYSIS)
        manager1.save_template(template)
        manager1.templates["persistence_template"] = template

        manager1.create_project(
            name="persistence_project", template_name="persistence_template", path=str(temp_dir / "persistence_project")
        )

        # Create new manager instance (simulates restart)
        manager2 = ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

        # Verify template and project are loaded
        assert "persistence_template" in manager2.templates
        assert "persistence_project" in manager2.projects

        # Verify project details
        loaded_project = manager2.get_project("persistence_project")
        assert loaded_project is not None
        assert loaded_project.name == "persistence_project"
        assert loaded_project.template == "persistence_template"


class TestDocumentationGenerator:
    """Test cases for DocumentationGenerator class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def doc_generator(self, temp_dir):
        """Create a DocumentationGenerator instance for testing."""
        templates_dir = temp_dir / "doc_templates"
        templates_dir.mkdir(parents=True)
        return DocumentationGenerator(templates_dir=templates_dir)

    def test_documentation_generator_initialization(self, temp_dir):
        """Test DocumentationGenerator initialization."""
        templates_dir = temp_dir / "doc_templates"
        generator = DocumentationGenerator(templates_dir=templates_dir)
        
        assert generator.templates_dir == templates_dir
        assert templates_dir.exists()

    def test_generate_root_readme(self, doc_generator, temp_dir):
        """Test root README generation."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        result = doc_generator.generate_root_readme(
            project_path=project_path,
            project_name="test_project",
            project_type="ai_analysis",
            description="Test project",
            version="1.0.0",
            author="Test Author",
            created_at="2025-01-01T00:00:00+00:00",
        )

        assert result is True
        readme_path = project_path / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "test_project" in content
        assert "Test project" in content
        assert "1.0.0" in content

    def test_generate_root_agents(self, doc_generator, temp_dir):
        """Test root AGENTS generation."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        result = doc_generator.generate_root_agents(
            project_path=project_path,
            project_name="test_project",
            project_type="ai_analysis",
            description="Test project",
            nested_dirs=["src/", "config/"],
        )

        assert result is True
        agents_path = project_path / "AGENTS.md"
        assert agents_path.exists()
        content = agents_path.read_text()
        assert "test_project" in content
        assert "Test project" in content

    def test_generate_nested_readme(self, doc_generator, temp_dir):
        """Test nested README generation."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()
        src_path = project_path / "src"
        src_path.mkdir()

        result = doc_generator.generate_nested_readme(
            dir_path=src_path,
            dir_name="src",
            project_name="test_project",
            project_type="ai_analysis",
            parent_path=project_path,
        )

        assert result is True
        readme_path = src_path / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "src" in content
        assert "test_project" in content

    def test_generate_nested_agents(self, doc_generator, temp_dir):
        """Test nested AGENTS generation."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()
        src_path = project_path / "src"
        src_path.mkdir()

        result = doc_generator.generate_nested_agents(
            dir_path=src_path,
            dir_name="src",
            project_name="test_project",
            project_type="ai_analysis",
            parent_path=project_path,
        )

        assert result is True
        agents_path = src_path / "AGENTS.md"
        assert agents_path.exists()
        content = agents_path.read_text()
        assert "src" in content
        assert "test_project" in content

    def test_variable_substitution(self, doc_generator, temp_dir):
        """Test variable substitution in templates."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()

        # Create a simple template
        template_content = "Project: {{project_name}}, Type: {{project_type}}, Version: {{version}}"
        template_file = doc_generator.templates_dir / "README.template.md"
        template_file.write_text(template_content)

        result = doc_generator.generate_root_readme(
            project_path=project_path,
            project_name="my_project",
            project_type="data_pipeline",
            description="Test",
            version="2.0.0",
            author="Author",
            created_at="2025-01-01T00:00:00+00:00",
        )

        assert result is True
        readme_path = project_path / "README.md"
        content = readme_path.read_text()
        assert "my_project" in content
        assert "data_pipeline" in content
        assert "2.0.0" in content
        assert "{{project_name}}" not in content

    def test_generate_all_documentation(self, doc_generator, temp_dir):
        """Test generating all documentation."""
        project_path = temp_dir / "test_project"
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "config").mkdir()

        result = doc_generator.generate_all_documentation(
            project_path=project_path,
            project_name="test_project",
            project_type="ai_analysis",
            description="Test project",
            version="1.0.0",
            author="Test Author",
            created_at="2025-01-01T00:00:00+00:00",
            nested_dirs=["src", "config"],
            doc_links={"enabled": True, "parent_link": True, "child_links": True},
        )

        assert result is True
        assert (project_path / "README.md").exists()
        assert (project_path / "AGENTS.md").exists()
        assert (project_path / "src" / "README.md").exists()
        assert (project_path / "src" / "AGENTS.md").exists()
        assert (project_path / "config" / "README.md").exists()
        assert (project_path / "config" / "AGENTS.md").exists()

    def test_directory_purpose_mapping(self, doc_generator):
        """Test directory purpose mapping."""
        assert doc_generator._get_directory_purpose("src", "ai_analysis") == "Source code and implementation files"
        assert doc_generator._get_directory_purpose("config", "ai_analysis") == "Configuration files and settings"
        assert doc_generator._get_directory_purpose("data", "ai_analysis") == "Data files and datasets"
        assert doc_generator._get_directory_purpose("unknown", "ai_analysis") == "Files and resources for unknown"


class TestTemplateConfiguration:
    """Test cases for template configuration features."""

    def test_template_with_documentation_config(self):
        """Test ProjectTemplate with documentation_config."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            documentation_config={
                "nested_docs": ["src/", "config/"],
                "doc_links": {"enabled": True, "parent_link": True, "child_links": True},
            },
        )

        assert template.documentation_config["nested_docs"] == ["src/", "config/"]
        assert template.documentation_config["doc_links"]["enabled"] is True

    def test_template_with_template_generators(self):
        """Test ProjectTemplate with template_generators."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            template_generators={
                "README.md": {"template": "custom_readme", "variables": {"custom": "value"}},
            },
        )

        assert "README.md" in template.template_generators
        assert template.template_generators["README.md"]["template"] == "custom_readme"

    def test_template_with_doc_links(self):
        """Test ProjectTemplate with doc_links."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            doc_links={"enabled": True, "parent_link": False, "child_links": True},
        )

        assert template.doc_links["enabled"] is True
        assert template.doc_links["parent_link"] is False

    def test_template_serialization_with_new_fields(self):
        """Test template serialization with new configuration fields."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.DATA_PIPELINE,
            documentation_config={"nested_docs": ["data/"]},
            template_generators={"config.yaml": {"template": "config"}},
            doc_links={"enabled": True},
        )

        template_dict = template.to_dict()
        assert "documentation_config" in template_dict
        assert "template_generators" in template_dict
        assert "doc_links" in template_dict

        restored = ProjectTemplate.from_dict(template_dict)
        assert restored.documentation_config == {"nested_docs": ["data/"]}
        assert restored.template_generators == {"config.yaml": {"template": "config"}}


class TestProjectManagerDocumentationIntegration:
    """Test cases for ProjectManager integration with documentation generation."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def project_manager(self, temp_dir):
        """Create a ProjectManager instance for testing."""
        return ProjectManager(
            projects_dir=temp_dir / "projects", templates_dir=temp_dir / "templates"
        )

    def test_create_project_with_documentation_config(self, project_manager, temp_dir):
        """Test project creation with documentation_config generates nested docs."""
        template = ProjectTemplate(
            name="test_template",
            type=ProjectType.AI_ANALYSIS,
            directory_structure=["src/", "config/"],
            documentation_config={
                "nested_docs": ["src/", "config/"],
                "doc_links": {"enabled": True, "parent_link": True, "child_links": True},
            },
        )
        project_manager.save_template(template)
        project_manager.templates["test_template"] = template

        project = project_manager.create_project(
            name="doc_test_project",
            template_name="test_template",
            path=str(temp_dir / "doc_test_project"),
        )

        assert project is not None
        project_path = Path(project.path)
        assert (project_path / "README.md").exists()
        assert (project_path / "AGENTS.md").exists()
        assert (project_path / "src" / "README.md").exists()
        assert (project_path / "src" / "AGENTS.md").exists()
        assert (project_path / "config" / "README.md").exists()
        assert (project_path / "config" / "AGENTS.md").exists()

    def test_create_project_without_documentation_config(self, project_manager, temp_dir):
        """Test project creation without documentation_config still generates basic docs."""
        template = ProjectTemplate(
            name="simple_template",
            type=ProjectType.AI_ANALYSIS,
            directory_structure=["src/"],
        )
        project_manager.save_template(template)
        project_manager.templates["simple_template"] = template

        project = project_manager.create_project(
            name="simple_project",
            template_name="simple_template",
            path=str(temp_dir / "simple_project"),
        )

        assert project is not None
        project_path = Path(project.path)
        # Should still generate root docs
        assert (project_path / "README.md").exists()
        assert (project_path / "AGENTS.md").exists()
        # Should generate nested docs based on directory_structure
        assert (project_path / "src" / "README.md").exists()
        assert (project_path / "src" / "AGENTS.md").exists()

    def test_create_project_custom_template(self, project_manager, temp_dir):
        """Test project creation with custom template (no template_name)."""
        project = project_manager.create_project(
            name="custom_project",
            path=str(temp_dir / "custom_project"),
        )

        assert project is not None
        assert project.template is None
        # Should not generate docs for custom projects without template
        project_path = Path(project.path)
        # Only .codomyrmex directory should exist
        assert (project_path / ".codomyrmex").exists()


if __name__ == "__main__":
    pytest.main([__file__])
