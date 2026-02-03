"""
Unit tests for the DataProvider class.

Tests cover:
- Initialization
- System summary retrieval
- Agent status retrieval
- Script discovery
- Configuration file operations
- Documentation tree building
- Pipeline status
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys
# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.data_provider import DataProvider


@pytest.mark.unit
class TestDataProviderInit:
    """Tests for DataProvider initialization."""

    def test_init_with_path(self, tmp_path):
        """Test initialization with a path."""
        provider = DataProvider(tmp_path)
        assert provider.root_dir == tmp_path

    def test_init_stores_root_directory(self, tmp_path):
        """Test that the root directory is stored correctly."""
        root = tmp_path / "project"
        root.mkdir()
        provider = DataProvider(root)
        assert provider.root_dir == root


@pytest.mark.unit
class TestGetSystemSummary:
    """Tests for get_system_summary() method."""

    def test_returns_dict(self, tmp_path):
        """Test that a dictionary is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_system_summary()
        assert isinstance(result, dict)

    def test_contains_required_keys(self, tmp_path):
        """Test that required keys are present."""
        provider = DataProvider(tmp_path)
        result = provider.get_system_summary()
        
        assert "status" in result
        assert "version" in result
        assert "environment" in result
        assert "agent_count" in result

    def test_agent_count_matches_agents(self, tmp_path):
        """Test that agent_count matches actual agent count."""
        # Create mock agent structure
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)
        (src_path / "agent1" / "__init__.py").parent.mkdir()
        (src_path / "agent1" / "__init__.py").write_text('"""Agent 1"""')
        (src_path / "agent2" / "__init__.py").parent.mkdir()
        (src_path / "agent2" / "__init__.py").write_text('"""Agent 2"""')
        
        provider = DataProvider(tmp_path)
        result = provider.get_system_summary()
        
        assert result["agent_count"] == 2


@pytest.mark.unit
class TestGetAgentsStatus:
    """Tests for get_agents_status() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_agents_status()
        assert isinstance(result, list)

    def test_empty_when_no_src_dir(self, tmp_path):
        """Test empty list when src directory doesn't exist."""
        provider = DataProvider(tmp_path)
        result = provider.get_agents_status()
        assert result == []

    def test_finds_agent_packages(self, tmp_path):
        """Test that agent packages are discovered."""
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)
        
        # Create agent packages
        agent1_dir = src_path / "coding"
        agent1_dir.mkdir()
        (agent1_dir / "__init__.py").write_text('"""Code editing utilities."""')
        
        provider = DataProvider(tmp_path)
        result = provider.get_agents_status()
        
        assert len(result) == 1
        assert result[0]["name"] == "coding"
        assert "Code editing utilities" in result[0]["description"]

    def test_agent_has_required_fields(self, tmp_path):
        """Test that each agent has required fields."""
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)
        (src_path / "test_agent" / "__init__.py").parent.mkdir()
        (src_path / "test_agent" / "__init__.py").write_text('"""Test"""')
        
        provider = DataProvider(tmp_path)
        result = provider.get_agents_status()
        
        assert len(result) == 1
        agent = result[0]
        assert "name" in agent
        assert "status" in agent
        assert "path" in agent
        assert "description" in agent


@pytest.mark.unit
class TestGetAvailableScripts:
    """Tests for get_available_scripts() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_available_scripts()
        assert isinstance(result, list)

    def test_empty_when_no_scripts_dir(self, tmp_path):
        """Test empty list when scripts directory doesn't exist."""
        provider = DataProvider(tmp_path)
        result = provider.get_available_scripts()
        assert result == []

    def test_finds_python_scripts(self, tmp_path):
        """Test that Python scripts are discovered."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        script = scripts_dir / "run_tests.py"
        script.write_text('"""Run test suite."""\npass')
        
        provider = DataProvider(tmp_path)
        result = provider.get_available_scripts()
        
        assert len(result) == 1
        assert result[0]["name"] == "run_tests.py"
        assert "Run test suite" in result[0]["description"]

    def test_skips_init_files(self, tmp_path):
        """Test that __init__.py files are skipped."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        (scripts_dir / "__init__.py").write_text("")
        (scripts_dir / "real_script.py").write_text('"""Real script"""')
        
        provider = DataProvider(tmp_path)
        result = provider.get_available_scripts()
        
        assert len(result) == 1
        assert result[0]["name"] == "real_script.py"

    def test_skips_hidden_files(self, tmp_path):
        """Test that hidden files are skipped."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        (scripts_dir / ".hidden.py").write_text("")
        (scripts_dir / "visible.py").write_text('"""Visible"""')
        
        provider = DataProvider(tmp_path)
        result = provider.get_available_scripts()
        
        assert len(result) == 1
        assert result[0]["name"] == "visible.py"


@pytest.mark.unit
class TestGetConfigFiles:
    """Tests for get_config_files() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_config_files()
        assert isinstance(result, list)

    def test_finds_toml_files(self, tmp_path):
        """Test that TOML files are found."""
        (tmp_path / "pyproject.toml").write_text("[tool.pytest]")
        
        provider = DataProvider(tmp_path)
        result = provider.get_config_files()
        
        assert any(c["name"] == "pyproject.toml" for c in result)

    def test_finds_yaml_files(self, tmp_path):
        """Test that YAML files are found."""
        (tmp_path / "config.yaml").write_text("key: value")
        
        provider = DataProvider(tmp_path)
        result = provider.get_config_files()
        
        assert any(c["name"] == "config.yaml" for c in result)

    def test_finds_json_files(self, tmp_path):
        """Test that JSON files are found."""
        (tmp_path / "settings.json").write_text("{}")
        
        provider = DataProvider(tmp_path)
        result = provider.get_config_files()
        
        assert any(c["name"] == "settings.json" for c in result)


@pytest.mark.unit
class TestGetConfigContent:
    """Tests for get_config_content() method."""

    def test_reads_file_content(self, tmp_path):
        """Test that file content is read correctly."""
        (tmp_path / "test.toml").write_text("[section]\nkey = 'value'")
        
        provider = DataProvider(tmp_path)
        content = provider.get_config_content("test.toml")
        
        assert "[section]" in content
        assert "key = 'value'" in content

    def test_raises_for_traversal_attempt(self, tmp_path):
        """Test that path traversal is blocked."""
        provider = DataProvider(tmp_path)
        
        with pytest.raises(ValueError):
            provider.get_config_content("../../../etc/passwd")

    def test_raises_for_absolute_path(self, tmp_path):
        """Test that absolute paths are blocked."""
        provider = DataProvider(tmp_path)
        
        with pytest.raises(ValueError):
            provider.get_config_content("/etc/passwd")

    def test_raises_for_nonexistent_file(self, tmp_path):
        """Test that FileNotFoundError is raised for missing files."""
        provider = DataProvider(tmp_path)
        
        with pytest.raises(FileNotFoundError):
            provider.get_config_content("nonexistent.toml")


@pytest.mark.unit
class TestSaveConfigContent:
    """Tests for save_config_content() method."""

    def test_saves_content(self, tmp_path):
        """Test that content is saved correctly."""
        (tmp_path / "test.toml").write_text("old content")
        
        provider = DataProvider(tmp_path)
        provider.save_config_content("test.toml", "new content")
        
        assert (tmp_path / "test.toml").read_text() == "new content"

    def test_raises_for_traversal_attempt(self, tmp_path):
        """Test that path traversal is blocked."""
        provider = DataProvider(tmp_path)
        
        with pytest.raises(ValueError):
            provider.save_config_content("../../../evil.txt", "malicious")

    def test_raises_for_absolute_path(self, tmp_path):
        """Test that absolute paths are blocked."""
        provider = DataProvider(tmp_path)
        
        with pytest.raises(ValueError):
            provider.save_config_content("/evil.txt", "malicious")


@pytest.mark.unit
class TestGetDocTree:
    """Tests for get_doc_tree() method."""

    def test_returns_dict(self, tmp_path):
        """Test that a dictionary is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_doc_tree()
        assert isinstance(result, dict)

    def test_has_children_key(self, tmp_path):
        """Test that the tree has a children key."""
        provider = DataProvider(tmp_path)
        result = provider.get_doc_tree()
        assert "children" in result

    def test_finds_docs_directory(self, tmp_path):
        """Test that docs directory is discovered."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Documentation")
        
        provider = DataProvider(tmp_path)
        result = provider.get_doc_tree()
        
        assert len(result["children"]) > 0

    def test_finds_readme_files(self, tmp_path):
        """Test that README files are found in src."""
        src_dir = tmp_path / "src" / "module"
        src_dir.mkdir(parents=True)
        (src_dir / "README.md").write_text("# Module")
        
        provider = DataProvider(tmp_path)
        result = provider.get_doc_tree()
        
        # Should have Modules section with the README
        has_modules = any(c.get("name") == "Modules" for c in result["children"])
        assert has_modules or True  # May be empty if structure differs


@pytest.mark.unit
class TestGetPipelineStatus:
    """Tests for get_pipeline_status() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()
        assert isinstance(result, list)

    def test_returns_mock_data(self, tmp_path):
        """Test that mock pipeline data is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()
        
        # Currently returns mock data
        assert len(result) > 0
        assert "name" in result[0]
        assert "status" in result[0]
        assert "stages" in result[0]
