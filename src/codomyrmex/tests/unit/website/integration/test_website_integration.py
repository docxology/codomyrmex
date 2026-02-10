"""
Integration tests for the Website module.

Tests cover:
- Full website generation flow
- API endpoint responses
- End-to-end functionality
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.data_provider import DataProvider
from codomyrmex.website.generator import WebsiteGenerator
from codomyrmex.website.server import WebsiteServer


@pytest.mark.integration
class TestFullWebsiteGeneration:
    """Integration tests for complete website generation."""

    @pytest.fixture
    def project_structure(self, tmp_path):
        """Create a mock project structure for testing."""
        # Create directories
        (tmp_path / "src" / "codomyrmex").mkdir(parents=True)
        (tmp_path / "scripts").mkdir()
        (tmp_path / "docs").mkdir()

        # Create some mock modules
        module1 = tmp_path / "src" / "codomyrmex" / "coding"
        module1.mkdir()
        (module1 / "__init__.py").write_text('"""Code editing module."""')

        module2 = tmp_path / "src" / "codomyrmex" / "llm"
        module2.mkdir()
        (module2 / "__init__.py").write_text('"""LLM integration module."""')

        # Create some mock scripts
        (tmp_path / "scripts" / "run_tests.py").write_text('"""Run test suite."""\nprint("Running tests")')
        (tmp_path / "scripts" / "deploy.py").write_text('"""Deploy application."""\nprint("Deploying")')

        # Create config files
        (tmp_path / "pyproject.toml").write_text('[tool.pytest]\ntestpaths = ["tests"]')
        (tmp_path / "config.yaml").write_text('debug: true\nenv: development')

        # Create docs
        (tmp_path / "docs" / "README.md").write_text('# Documentation\n\nWelcome!')

        return tmp_path

    def test_data_provider_collects_all_data(self, project_structure):
        """Test that DataProvider collects data from all sources."""
        provider = DataProvider(project_structure)

        # Test system summary
        system = provider.get_system_summary()
        assert system["module_count"] == 2
        # agent_count will be 0 since no agents dir structure in mock
        assert system["agent_count"] == 0

        # Test modules (formerly agents)
        modules = provider.get_modules()
        assert len(modules) == 2
        module_names = {m["name"] for m in modules}
        assert "coding" in module_names
        assert "llm" in module_names

        # Test scripts
        scripts = provider.get_available_scripts()
        assert len(scripts) == 2
        script_names = {s["name"] for s in scripts}
        assert "run_tests.py" in script_names
        assert "deploy.py" in script_names

        # Test config files
        configs = provider.get_config_files()
        config_names = {c["name"] for c in configs}
        assert "pyproject.toml" in config_names
        assert "config.yaml" in config_names

        # Test doc tree
        doc_tree = provider.get_doc_tree()
        assert doc_tree["name"] == "Documentation"
        assert len(doc_tree["children"]) > 0

    def test_generator_creates_all_pages(self, project_structure):
        """Test that generator creates all expected pages."""
        output_dir = project_structure / "website_output"

        generator = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(project_structure)
        )

        # Run generation
        generator.generate()

        # Verify all pages were created
        expected_pages = [
            "index.html",
            "health.html",
            "modules.html",
            "scripts.html",
            "chat.html",
            "agents.html",
            "config.html",
            "docs.html",
            "pipelines.html"
        ]

        for page in expected_pages:
            assert (output_dir / page).exists(), f"Missing page: {page}"

    def test_generated_pages_contain_data(self, project_structure):
        """Test that generated pages contain expected data."""
        output_dir = project_structure / "website_output"

        generator = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(project_structure)
        )
        generator.generate()

        # Check index.html contains module count
        index_content = (output_dir / "index.html").read_text()
        assert "2" in index_content or "Active" in index_content or "Modules" in index_content

        # Check modules.html contains module names
        modules_content = (output_dir / "modules.html").read_text()
        assert "coding" in modules_content or "llm" in modules_content

        # Check scripts.html contains script names
        scripts_content = (output_dir / "scripts.html").read_text()
        assert "run_tests" in scripts_content or "deploy" in scripts_content


@pytest.mark.integration
class TestConfigOperations:
    """Integration tests for configuration file operations."""

    def test_read_and_write_config(self, tmp_path):
        """Test reading and writing configuration files."""
        # Create initial config
        config_file = tmp_path / "test_config.toml"
        config_file.write_text('[section]\nkey = "original"')

        provider = DataProvider(tmp_path)

        # Read config
        content = provider.get_config_content("test_config.toml")
        assert 'key = "original"' in content

        # Write new content
        provider.save_config_content("test_config.toml", '[section]\nkey = "modified"')

        # Verify write
        new_content = provider.get_config_content("test_config.toml")
        assert 'key = "modified"' in new_content


@pytest.mark.integration
class TestDocumentationTree:
    """Integration tests for documentation tree building."""

    def test_nested_doc_structure(self, tmp_path):
        """Test that nested documentation structure is captured."""
        # Create nested docs
        docs = tmp_path / "docs"
        docs.mkdir()

        (docs / "README.md").write_text("# Main Docs")

        getting_started = docs / "getting-started"
        getting_started.mkdir()
        (getting_started / "installation.md").write_text("# Installation")
        (getting_started / "quickstart.md").write_text("# Quick Start")

        api_docs = docs / "api"
        api_docs.mkdir()
        (api_docs / "endpoints.md").write_text("# API Endpoints")

        provider = DataProvider(tmp_path)
        tree = provider.get_doc_tree()

        # Verify structure
        assert tree["name"] == "Documentation"
        assert len(tree["children"]) > 0

        # Find docs node
        docs_node = None
        for child in tree["children"]:
            if child.get("name") == "docs":
                docs_node = child
                break

        assert docs_node is not None

        # Check for nested directories
        child_names = {c.get("name") for c in docs_node.get("children", [])}
        assert "README.md" in child_names or len(child_names) > 0


@pytest.mark.integration
class TestAssetsCopying:
    """Integration tests for assets copying."""

    def test_assets_copied_correctly(self, tmp_path):
        """Test that all assets are copied to output directory."""
        # Get the real module directory to use actual templates
        module_dir = Path(__file__).resolve().parent.parent.parent

        output_dir = tmp_path / "website_output"

        generator = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(tmp_path)
        )

        # The assets should be copied from the actual module
        if generator.assets_dir.exists():
            generator.generate()

            # Verify assets directory exists in output
            if (generator.assets_dir / "css").exists():
                assert (output_dir / "assets" / "css").exists()
            if (generator.assets_dir / "js").exists():
                assert (output_dir / "assets" / "js").exists()


@pytest.mark.integration
class TestWebsiteServerIntegration:
    """Integration tests for the HTTP server."""

    def test_server_class_attributes(self):
        """Test that server has required class attributes."""
        assert hasattr(WebsiteServer, 'root_dir')
        assert hasattr(WebsiteServer, 'data_provider')

    def test_server_methods_exist(self):
        """Test that all handler methods exist."""
        assert hasattr(WebsiteServer, 'do_GET')
        assert hasattr(WebsiteServer, 'do_POST')
        assert hasattr(WebsiteServer, 'handle_execute')
        assert hasattr(WebsiteServer, 'handle_chat')
        assert hasattr(WebsiteServer, 'handle_refresh')
        assert hasattr(WebsiteServer, 'handle_status')
        assert hasattr(WebsiteServer, 'handle_health')
        assert hasattr(WebsiteServer, 'handle_tests_run')
        assert hasattr(WebsiteServer, 'handle_config_list')
        assert hasattr(WebsiteServer, 'handle_config_get')
        assert hasattr(WebsiteServer, 'handle_config_save')
        assert hasattr(WebsiteServer, 'handle_docs_list')
        assert hasattr(WebsiteServer, 'handle_docs_get')
        assert hasattr(WebsiteServer, 'handle_modules_list')
        assert hasattr(WebsiteServer, 'handle_module_detail')
        assert hasattr(WebsiteServer, 'handle_agents_list')
        assert hasattr(WebsiteServer, 'handle_scripts_list')
        assert hasattr(WebsiteServer, 'handle_pipelines_list')

    def test_deprecated_methods_removed(self):
        """Test that deprecated methods have been removed."""
        assert not hasattr(DataProvider, 'get_agents_status')
        assert not hasattr(DataProvider, '_count_agents')
        assert not hasattr(DataProvider, '_get_script_docstring')


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_config_traversal_blocked(self, tmp_path):
        """Test that path traversal is blocked in config operations."""
        provider = DataProvider(tmp_path)

        # Create a sensitive file outside the expected path
        sensitive = tmp_path.parent / "sensitive.txt"
        if sensitive.parent.exists():
            sensitive.write_text("secret data")

        # Attempt traversal
        with pytest.raises(ValueError):
            provider.get_config_content("../sensitive.txt")

        with pytest.raises(ValueError):
            provider.save_config_content("../sensitive.txt", "malicious")

    def test_absolute_path_blocked(self, tmp_path):
        """Test that absolute paths are blocked."""
        provider = DataProvider(tmp_path)

        with pytest.raises(ValueError):
            provider.get_config_content("/etc/passwd")

        with pytest.raises(ValueError):
            provider.save_config_content("/tmp/evil.txt", "malicious")

    def test_docs_endpoint_traversal_blocked(self, tmp_path):
        """Test that path traversal is blocked on docs endpoint."""
        provider = DataProvider(tmp_path)

        with pytest.raises(ValueError):
            provider.get_doc_content("../../../etc/passwd.md")

        with pytest.raises(ValueError):
            provider.get_doc_content("/etc/passwd.md")

    def test_docs_endpoint_rejects_non_markdown(self, tmp_path):
        """Test that docs endpoint rejects non-.md files."""
        provider = DataProvider(tmp_path)

        with pytest.raises(ValueError):
            provider.get_doc_content("src/script.py")
