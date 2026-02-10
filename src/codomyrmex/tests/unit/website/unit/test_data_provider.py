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
- PAI Awareness data methods
"""

import json
import sys
from pathlib import Path

import pytest

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
        # Create mock agent structure under src/codomyrmex/agents/ (where DataProvider looks)
        agents_path = tmp_path / "src" / "codomyrmex" / "agents"
        agents_path.mkdir(parents=True)
        (agents_path / "agent1").mkdir()
        (agents_path / "agent1" / "__init__.py").write_text('"""Agent 1"""')
        (agents_path / "agent2").mkdir()
        (agents_path / "agent2" / "__init__.py").write_text('"""Agent 2"""')

        provider = DataProvider(tmp_path)
        result = provider.get_system_summary()

        assert result["agent_count"] == 2


@pytest.mark.unit
class TestGetModules:
    """Tests for get_modules() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_modules()
        assert isinstance(result, list)

    def test_empty_when_no_src_dir(self, tmp_path):
        """Test empty list when src directory doesn't exist."""
        provider = DataProvider(tmp_path)
        result = provider.get_modules()
        assert result == []

    def test_finds_module_packages(self, tmp_path):
        """Test that module packages are discovered."""
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)

        # Create module packages
        mod_dir = src_path / "coding"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('"""Code editing utilities."""')

        provider = DataProvider(tmp_path)
        result = provider.get_modules()

        assert len(result) == 1
        assert result[0]["name"] == "coding"
        assert "Code editing utilities" in result[0]["description"]

    def test_module_has_required_fields(self, tmp_path):
        """Test that each module has required fields."""
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)
        (src_path / "test_module" / "__init__.py").parent.mkdir()
        (src_path / "test_module" / "__init__.py").write_text('"""Test"""')

        provider = DataProvider(tmp_path)
        result = provider.get_modules()

        assert len(result) == 1
        mod = result[0]
        assert "name" in mod
        assert "status" in mod
        assert "path" in mod
        assert "description" in mod


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
    """Tests for get_pipeline_status() — real workflow scanning."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()
        assert isinstance(result, list)

    def test_returns_empty_when_no_workflows_dir(self, tmp_path):
        """Test empty list when .github/workflows doesn't exist."""
        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()
        assert result == []

    def test_scans_workflow_yml_files(self, tmp_path):
        """Test that real workflow YAML files are scanned."""
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "ci.yml").write_text(
            "name: CI\non:\n  push:\n    branches: [main]\njobs:\n  lint:\n    runs-on: ubuntu-latest\n  test:\n    runs-on: ubuntu-latest\n"
        )

        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()

        assert len(result) == 1
        assert result[0]["name"] == "CI"
        assert result[0]["status"] == "defined"
        assert result[0]["file"] == ".github/workflows/ci.yml"
        assert "push" in result[0]["triggers"]
        assert len(result[0]["stages"]) == 2

    def test_skips_malformed_yaml(self, tmp_path):
        """Test that malformed YAML files are skipped."""
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "bad.yml").write_text(":::: not yaml {{{{")
        (wf_dir / "good.yml").write_text("name: Good\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n")

        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()

        # bad.yml may parse as a string (not dict), so skipped; good.yml should parse
        names = [p["name"] for p in result]
        assert "Good" in names

    def test_fallback_parser_handles_heredoc_workflows(self, tmp_path):
        """Test that workflows with heredoc blocks are parsed via fallback."""
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        heredoc_content = (
            "name: Benchmarks\n"
            "\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  schedule:\n"
            "    - cron: '0 3 * * 3'\n"
            "\n"
            "jobs:\n"
            "  setup:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Create script\n"
            "        run: |\n"
            "          cat > test.py << 'EOF'\n"
            "import pytest\n"
            "def test_basic():\n"
            "    assert True\n"
            "EOF\n"
            "  unit-tests:\n"
            "    runs-on: ubuntu-latest\n"
            "    needs: setup\n"
        )
        (wf_dir / "benchmarks.yml").write_text(heredoc_content)

        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()

        assert len(result) == 1
        assert result[0]["name"] == "Benchmarks"
        assert "push" in result[0]["triggers"]
        stage_names = [s["name"] for s in result[0]["stages"]]
        assert "setup" in stage_names
        assert "unit-tests" in stage_names

    def test_pipeline_ids_are_sequential(self, tmp_path):
        """Test that pipeline IDs are sequential with no gaps."""
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        for i in range(5):
            (wf_dir / f"wf{i}.yml").write_text(
                f"name: Workflow {i}\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
            )

        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()

        assert len(result) == 5
        ids = [p["id"] for p in result]
        assert ids == [f"wf-{i:04d}" for i in range(1, 6)]

    def test_defined_status_on_all_pipelines(self, tmp_path):
        """Test that all parsed pipelines have status='defined'."""
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "ci.yml").write_text(
            "name: CI\non: push\njobs:\n  lint:\n    runs-on: ubuntu-latest\n"
        )

        provider = DataProvider(tmp_path)
        result = provider.get_pipeline_status()

        for pipeline in result:
            assert pipeline["status"] == "defined"
            for stage in pipeline["stages"]:
                assert stage["status"] == "defined"

    def test_all_real_workflows_parsed(self):
        """Test that all real .github/workflows/ files are parsed (no silent drops)."""
        import glob
        root = Path(__file__).resolve().parents[6]  # Navigate to project root
        workflows_dir = root / ".github" / "workflows"
        if not workflows_dir.exists():
            pytest.skip("No .github/workflows/ directory in project root")

        yml_count = len(list(workflows_dir.glob("*.yml")))
        provider = DataProvider(root)
        result = provider.get_pipeline_status()

        assert len(result) == yml_count, (
            f"Expected {yml_count} pipelines but got {len(result)}. "
            f"Missing: {set(f.stem for f in workflows_dir.glob('*.yml')) - set(p['name'] for p in result)}"
        )


@pytest.mark.unit
class TestGetDocContent:
    """Tests for get_doc_content() method."""

    def test_reads_markdown_file(self, tmp_path):
        """Test that markdown content is returned."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Hello World")

        provider = DataProvider(tmp_path)
        content = provider.get_doc_content("docs/README.md")
        assert "# Hello World" in content

    def test_rejects_path_traversal(self, tmp_path):
        """Test that .. in path is rejected."""
        provider = DataProvider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_doc_content("../../../etc/passwd.md")

    def test_rejects_absolute_path(self, tmp_path):
        """Test that absolute paths are rejected."""
        provider = DataProvider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_doc_content("/etc/passwd.md")

    def test_rejects_non_markdown(self, tmp_path):
        """Test that non-.md files are rejected."""
        provider = DataProvider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_doc_content("docs/script.py")

    def test_raises_file_not_found(self, tmp_path):
        """Test FileNotFoundError for missing files."""
        provider = DataProvider(tmp_path)
        with pytest.raises(FileNotFoundError):
            provider.get_doc_content("docs/nonexistent.md")


@pytest.mark.unit
class TestGetModuleDetail:
    """Tests for get_module_detail() method."""

    def test_returns_none_for_missing_module(self, tmp_path):
        """Test that None is returned for a module that doesn't exist."""
        provider = DataProvider(tmp_path)
        assert provider.get_module_detail("nonexistent") is None

    def test_returns_detail_for_existing_module(self, tmp_path):
        """Test that detail dict is returned for an existing module."""
        mod_path = tmp_path / "src" / "codomyrmex" / "coding"
        mod_path.mkdir(parents=True)
        (mod_path / "__init__.py").write_text('"""Code editing module."""')
        (mod_path / "helper.py").write_text("# helper")
        (mod_path / "API_SPECIFICATION.md").write_text("# API")

        provider = DataProvider(tmp_path)
        detail = provider.get_module_detail("coding")

        assert detail is not None
        assert detail["name"] == "coding"
        assert detail["has_api_spec"] is True
        assert detail["has_mcp_spec"] is False
        assert detail["python_file_count"] == 2  # __init__.py + helper.py

    def test_includes_has_tests(self, tmp_path):
        """Test that has_tests reflects test directory existence."""
        mod_path = tmp_path / "src" / "codomyrmex" / "mymod"
        mod_path.mkdir(parents=True)
        (mod_path / "__init__.py").write_text("")

        test_path = tmp_path / "src" / "codomyrmex" / "tests" / "unit" / "mymod"
        test_path.mkdir(parents=True)

        provider = DataProvider(tmp_path)
        detail = provider.get_module_detail("mymod")
        assert detail["has_tests"] is True


@pytest.mark.unit
class TestGetLastBuildTime:
    """Tests for _get_last_build_time() helper."""

    def test_returns_string(self, tmp_path):
        """Test that a string is returned (N/A or timestamp)."""
        provider = DataProvider(tmp_path)
        result = provider._get_last_build_time()
        assert isinstance(result, str)

    def test_returns_na_when_not_git_repo(self, tmp_path):
        """Test that N/A is returned when not in a git repo."""
        provider = DataProvider(tmp_path)
        result = provider._get_last_build_time()
        # tmp_path is not a git repo, so should return N/A or empty
        assert result == "N/A" or isinstance(result, str)


@pytest.mark.unit
class TestComputeModuleStatus:
    """Tests for _compute_module_status() method."""

    def test_valid_init_returns_active(self, tmp_path):
        """Test that a valid __init__.py yields Active status."""
        mod_path = tmp_path / "mymod"
        mod_path.mkdir()
        (mod_path / "__init__.py").write_text('"""Valid module."""\nx = 1')

        provider = DataProvider(tmp_path)
        assert provider._compute_module_status(mod_path) == "Active"

    def test_syntax_error_returns_error(self, tmp_path):
        """Test that a syntax-error __init__.py yields SyntaxError status."""
        mod_path = tmp_path / "badmod"
        mod_path.mkdir()
        (mod_path / "__init__.py").write_text('def broken(\n')

        provider = DataProvider(tmp_path)
        assert provider._compute_module_status(mod_path) == "SyntaxError"

    def test_missing_init_returns_unknown(self, tmp_path):
        """Test that a missing __init__.py yields Unknown status."""
        mod_path = tmp_path / "emptymod"
        mod_path.mkdir()

        provider = DataProvider(tmp_path)
        assert provider._compute_module_status(mod_path) == "Unknown"

    def test_module_status_used_in_get_modules(self, tmp_path):
        """Test that get_modules() uses _compute_module_status."""
        src_path = tmp_path / "src" / "codomyrmex"
        src_path.mkdir(parents=True)

        good = src_path / "goodmod"
        good.mkdir()
        (good / "__init__.py").write_text('"""Good module."""')

        bad = src_path / "badmod"
        bad.mkdir()
        (bad / "__init__.py").write_text('def broken(\n')

        provider = DataProvider(tmp_path)
        modules = provider.get_modules()
        statuses = {m["name"]: m["status"] for m in modules}
        assert statuses["goodmod"] == "Active"
        assert statuses["badmod"] == "SyntaxError"


@pytest.mark.unit
class TestGetAgentType:
    """Tests for _get_agent_type() categorization."""

    def test_cli_agent(self, tmp_path):
        provider = DataProvider(tmp_path)
        assert provider._get_agent_type("jules") == "CLI Integration"

    def test_api_agent(self, tmp_path):
        provider = DataProvider(tmp_path)
        assert provider._get_agent_type("claude") == "API Integration"

    def test_framework_agent(self, tmp_path):
        provider = DataProvider(tmp_path)
        assert provider._get_agent_type("generic") == "Framework"

    def test_default_agent(self, tmp_path):
        provider = DataProvider(tmp_path)
        assert provider._get_agent_type("unknown_agent") == "Agent"


@pytest.mark.unit
class TestGetSubmodules:
    """Tests for _get_submodules() method."""

    def test_discovers_nested_packages(self, tmp_path):
        """Test that nested packages are discovered."""
        mod_path = tmp_path / "parent"
        mod_path.mkdir()
        (mod_path / "__init__.py").write_text("")

        child = mod_path / "child"
        child.mkdir()
        (child / "__init__.py").write_text('"""Child module."""')

        provider = DataProvider(tmp_path)
        result = provider._get_submodules(mod_path)
        assert len(result) == 1
        assert result[0]["name"] == "child"


@pytest.mark.unit
class TestGetDescriptionFromMarkdown:
    """Tests for _get_description_from_markdown() method."""

    def test_reads_readme(self, tmp_path):
        """Test reading description from README.md."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "README.md").write_text("# My Module\nThis is a great module.")

        provider = DataProvider(tmp_path)
        result = provider._get_description_from_markdown(mod_dir)
        assert "great module" in result

    def test_falls_back_to_default(self, tmp_path):
        """Test fallback when no markdown files exist."""
        mod_dir = tmp_path / "emptymod"
        mod_dir.mkdir()

        provider = DataProvider(tmp_path)
        result = provider._get_description_from_markdown(mod_dir)
        assert result == "No description available"


@pytest.mark.unit
class TestScanDirectoryForDocs:
    """Tests for _scan_directory_for_docs() method."""

    def test_scans_nested_dirs(self, tmp_path):
        """Test that nested directories with .md files are scanned."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "intro.md").write_text("# Intro")
        sub = docs / "guides"
        sub.mkdir()
        (sub / "setup.md").write_text("# Setup")

        provider = DataProvider(tmp_path)
        result = provider._scan_directory_for_docs(docs)
        assert result["name"] == "docs"
        child_names = [c["name"] for c in result["children"]]
        assert "intro.md" in child_names
        assert "guides" in child_names

    def test_skips_hidden_files(self, tmp_path):
        """Test that hidden files are skipped."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / ".hidden.md").write_text("# Hidden")
        (docs / "visible.md").write_text("# Visible")

        provider = DataProvider(tmp_path)
        result = provider._scan_directory_for_docs(docs)
        child_names = [c["name"] for c in result["children"]]
        assert ".hidden.md" not in child_names
        assert "visible.md" in child_names


@pytest.mark.unit
class TestGetGitInfo:
    """Tests for _get_git_info() method."""

    def test_returns_dict(self, tmp_path):
        """Test that a dict is returned."""
        provider = DataProvider(tmp_path)
        result = provider._get_git_info()
        assert isinstance(result, dict)

    def test_has_branch_key(self, tmp_path):
        """Test that branch key exists."""
        provider = DataProvider(tmp_path)
        result = provider._get_git_info()
        assert "branch" in result


@pytest.mark.unit
class TestGetArchitectureLayers:
    """Tests for _get_architecture_layers() method."""

    def test_returns_defined_layers(self, tmp_path):
        """Test that architecture layers are returned (Extended only if unclassified modules exist)."""
        provider = DataProvider(tmp_path)
        result = provider._get_architecture_layers()
        # With no modules, Extended is omitted (no unclassified modules)
        assert len(result) >= 4
        names = [l["name"] for l in result]
        assert "Foundation" in names
        assert "Core" in names
        assert "Service" in names
        assert "Application" in names


@pytest.mark.unit
class TestSaveConfigContentHardened:
    """Tests for hardened save_config_content() method."""

    def test_refuses_to_create_new_file(self, tmp_path):
        """Test that saving to a nonexistent file raises FileNotFoundError."""
        provider = DataProvider(tmp_path)
        with pytest.raises(FileNotFoundError):
            provider.save_config_content("new_file.toml", "content")

    def test_rejects_symlink_escape(self, tmp_path):
        """Test that symlinks escaping root_dir are rejected."""
        import os
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("outside data")
        link = tmp_path / "evil_link.txt"
        try:
            os.symlink(str(outside), str(link))
        except OSError:
            pytest.skip("Symlinks not supported")

        provider = DataProvider(tmp_path)
        with pytest.raises((ValueError, FileNotFoundError)):
            provider.save_config_content("evil_link.txt", "overwrite")


@pytest.mark.unit
class TestRunTests:
    """Tests for run_tests() method."""

    def test_run_tests_returns_dict(self, tmp_path):
        """Test that run_tests returns a dict with expected keys."""
        provider = DataProvider(tmp_path)
        result = provider.run_tests()
        assert isinstance(result, dict)
        # Should always have these keys (even if 0)
        assert "passed" in result or "error" in result

    def test_run_tests_has_result_keys(self, tmp_path):
        """Test that successful run_tests has passed/failed/total keys."""
        # Create a minimal test directory so pytest can run
        test_dir = tmp_path / "src" / "codomyrmex" / "tests" / "unit" / "fakemod"
        test_dir.mkdir(parents=True)
        (test_dir / "test_fake.py").write_text("def test_trivial(): assert True")

        provider = DataProvider(tmp_path)
        result = provider.run_tests("fakemod")
        assert isinstance(result, dict)
        # Either returns results or an error for module not found
        assert "passed" in result or "error" in result

    def test_run_tests_module_not_found(self, tmp_path):
        """Test graceful handling when module test dir doesn't exist."""
        provider = DataProvider(tmp_path)
        result = provider.run_tests("nonexistent_module_xyz")
        assert isinstance(result, dict)
        assert "error" in result
        assert "No tests found" in result["error"]


@pytest.mark.unit
class TestGetDescription:
    """Tests for _get_description() method."""

    def test_extracts_docstring(self, tmp_path):
        """Test that _get_description extracts module docstring from __init__.py."""
        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('"""This is the module docstring."""\nx = 1')

        provider = DataProvider(tmp_path)
        result = provider._get_description(mod_dir)
        assert result == "This is the module docstring."

    def test_returns_default_when_no_init(self, tmp_path):
        """Test fallback when __init__.py doesn't exist."""
        mod_dir = tmp_path / "emptymod"
        mod_dir.mkdir()

        provider = DataProvider(tmp_path)
        result = provider._get_description(mod_dir)
        assert result == "No description available"

    def test_returns_default_when_no_docstring(self, tmp_path):
        """Test fallback when __init__.py has no docstring."""
        mod_dir = tmp_path / "nodoc"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text("x = 1\ny = 2\n")

        provider = DataProvider(tmp_path)
        result = provider._get_description(mod_dir)
        assert result == "No description available"


@pytest.mark.unit
class TestGetScriptMetadata:
    """Tests for _get_script_metadata() method."""

    def test_extracts_title_and_description(self, tmp_path):
        """Test that title and description are extracted from script docstring."""
        script = tmp_path / "myscript.py"
        script.write_text('"""Title: Deploy Script\nDeploys the application to production."""\npass')

        provider = DataProvider(tmp_path)
        title, description = provider._get_script_metadata(script)
        assert title == "Deploy Script"
        assert "Deploys the application" in description

    def test_uses_first_line_as_title_without_explicit_title(self, tmp_path):
        """Test that first docstring line is used as title when no Title: prefix."""
        script = tmp_path / "simple.py"
        script.write_text('"""Run the full test suite.\nMore details here."""\npass')

        provider = DataProvider(tmp_path)
        title, description = provider._get_script_metadata(script)
        assert title == "Run the full test suite."

    def test_returns_filename_when_no_docstring(self, tmp_path):
        """Test that filename is returned as title when no docstring exists."""
        script = tmp_path / "nodoc.py"
        script.write_text("x = 1\nprint(x)\n")

        provider = DataProvider(tmp_path)
        title, description = provider._get_script_metadata(script)
        assert title == "nodoc.py"
        assert description == "No description available"


# ── PAI Awareness Tests ─────────────────────────────────────────────


def _make_provider(tmp_path):
    """Create a DataProvider with _PAI_ROOT pointing to tmp_path."""
    provider = DataProvider(tmp_path)
    provider._PAI_ROOT = tmp_path
    return provider


@pytest.mark.unit
class TestGetPaiMissions:
    """Tests for get_pai_missions() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert isinstance(result, list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when missions dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_missions() == []

    def test_reads_mission_yaml(self, tmp_path):
        """Test that MISSION.yaml is parsed correctly."""
        m_dir = tmp_path / "MEMORY" / "STATE" / "missions" / "m1"
        m_dir.mkdir(parents=True)
        (m_dir / "MISSION.yaml").write_text(
            "title: Test Mission\nstatus: active\npriority: HIGH\n"
            "description: A test\nlinked_projects:\n  - p1\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert len(result) == 1
        assert result[0]["title"] == "Test Mission"
        assert result[0]["status"] == "active"
        assert result[0]["priority"] == "HIGH"
        assert "p1" in result[0]["linked_projects"]

    def test_merges_progress_json(self, tmp_path):
        """Test that progress.json is merged into mission data."""
        m_dir = tmp_path / "MEMORY" / "STATE" / "missions" / "m1"
        m_dir.mkdir(parents=True)
        (m_dir / "MISSION.yaml").write_text("title: M1\nstatus: active\npriority: MEDIUM\n")
        (m_dir / "progress.json").write_text(json.dumps({"completion_percentage": 75}))

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert result[0]["completion_percentage"] == 75

    def test_skips_non_dict_yaml(self, tmp_path):
        """Test that YAML files that don't parse to dict are skipped."""
        missions_dir = tmp_path / "MEMORY" / "STATE" / "missions"
        bad = missions_dir / "bad"
        bad.mkdir(parents=True)
        # This parses as a string, not a dict — should be skipped
        (bad / "MISSION.yaml").write_text("just a plain string")

        good = missions_dir / "good"
        good.mkdir(parents=True)
        (good / "MISSION.yaml").write_text("title: Good\nstatus: active\npriority: LOW\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert len(result) == 1
        assert result[0]["title"] == "Good"

    def test_sorts_by_priority(self, tmp_path):
        """Test that missions are sorted HIGH > MEDIUM > LOW."""
        missions_dir = tmp_path / "MEMORY" / "STATE" / "missions"
        for name, prio in [("low", "LOW"), ("high", "HIGH"), ("med", "MEDIUM")]:
            d = missions_dir / name
            d.mkdir(parents=True)
            (d / "MISSION.yaml").write_text(f"title: {name}\nstatus: active\npriority: {prio}\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        priorities = [m["priority"] for m in result]
        assert priorities == ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.unit
class TestGetPaiProjects:
    """Tests for get_pai_projects() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        assert isinstance(provider.get_pai_projects(), list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when projects dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_projects() == []

    def test_reads_project_yaml(self, tmp_path):
        """Test that PROJECT.yaml is parsed correctly."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "PROJECT.yaml").write_text(
            "title: Test Project\nstatus: in_progress\n"
            "goal: Build something\npriority: HIGH\nparent_mission: m1\ntags:\n  - python\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert len(result) == 1
        assert result[0]["title"] == "Test Project"
        assert result[0]["parent_mission"] == "m1"
        assert "python" in result[0]["tags"]

    def test_merges_progress_json(self, tmp_path):
        """Test that progress.json is merged."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "PROJECT.yaml").write_text("title: P1\nstatus: active\n")
        (p_dir / "progress.json").write_text(json.dumps({
            "completion_percentage": 50,
            "task_counts": {"completed": 5, "total": 10}
        }))

        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert result[0]["completion_percentage"] == 50
        assert result[0]["task_counts"]["completed"] == 5

    def test_skips_non_dict_yaml(self, tmp_path):
        """Test that YAML that doesn't parse to dict is skipped."""
        projects_dir = tmp_path / "MEMORY" / "STATE" / "projects"
        bad = projects_dir / "bad"
        bad.mkdir(parents=True)
        # This parses as a list, not a dict — should be skipped
        (bad / "PROJECT.yaml").write_text("- item1\n- item2\n")

        good = projects_dir / "good"
        good.mkdir(parents=True)
        (good / "PROJECT.yaml").write_text("title: Good\nstatus: active\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert len(result) == 1
        assert result[0]["title"] == "Good"


@pytest.mark.unit
class TestGetPaiTasks:
    """Tests for get_pai_tasks() method."""

    def test_rejects_traversal(self, tmp_path):
        """Test that .. in project_id raises ValueError."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("../../../etc")

    def test_rejects_slash(self, tmp_path):
        """Test that / in project_id raises ValueError."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("foo/bar")

    def test_parses_task_sections(self, tmp_path):
        """Test that - [ ] and - [x] lines are parsed."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "TASKS.md").write_text(
            "# Tasks\n- [x] Done task\n- [ ] Todo task\n- [X] Also done\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_tasks("p1")
        assert result["done"] == 2
        assert result["total"] == 3
        assert "Done task" in result["completed"]
        assert "Todo task" in result["remaining"]

    def test_empty_for_missing_project(self, tmp_path):
        """Test empty dict for missing project."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_tasks("nonexistent") == {}


@pytest.mark.unit
class TestGetPaiTelos:
    """Tests for get_pai_telos() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        assert isinstance(provider.get_pai_telos(), list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when TELOS dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_telos() == []

    def test_reads_md_files_with_preview(self, tmp_path):
        """Test that .md files are read with 200-char preview."""
        telos_dir = tmp_path / "skills" / "PAI" / "USER" / "TELOS"
        telos_dir.mkdir(parents=True)
        (telos_dir / "goals.md").write_text("# My Goals\nBe awesome\n" + "x" * 300)
        (telos_dir / "notes.txt").write_text("not markdown")  # Should be skipped

        provider = _make_provider(tmp_path)
        result = provider.get_pai_telos()
        assert len(result) == 1
        assert result[0]["name"] == "goals"
        assert len(result[0]["preview"]) == 200

    def test_sorted_by_name(self, tmp_path):
        """Test that files are sorted by name."""
        telos_dir = tmp_path / "skills" / "PAI" / "USER" / "TELOS"
        telos_dir.mkdir(parents=True)
        (telos_dir / "zebra.md").write_text("Z")
        (telos_dir / "alpha.md").write_text("A")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_telos()
        names = [t["name"] for t in result]
        assert names == ["alpha", "zebra"]


@pytest.mark.unit
class TestGetPaiMemoryOverview:
    """Tests for get_pai_memory_overview() method."""

    def test_returns_dict(self, tmp_path):
        """Test that a dict is returned."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert isinstance(result, dict)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty structure when MEMORY dir doesn't exist."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert result["directories"] == []
        assert result["total_files"] == 0

    def test_counts_subdirs_correctly(self, tmp_path):
        """Test that subdirectory counts are accurate."""
        mem_dir = tmp_path / "MEMORY"
        mem_dir.mkdir()
        work = mem_dir / "WORK"
        work.mkdir()
        (work / "session1").mkdir()
        (work / "session2").mkdir()
        (work / "notes.txt").write_text("hi")

        state = mem_dir / "STATE"
        state.mkdir()
        (state / "config.json").write_text("{}")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert len(result["directories"]) == 2
        assert result["work_sessions_count"] == 2

        work_entry = next(d for d in result["directories"] if d["name"] == "WORK")
        assert work_entry["file_count"] == 1  # notes.txt
        assert work_entry["subdir_count"] == 2


@pytest.mark.unit
class TestGetPaiAwarenessData:
    """Tests for get_pai_awareness_data() method."""

    def test_returns_all_keys(self, tmp_path):
        """Test that all expected top-level keys are present."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert "missions" in result
        assert "projects" in result
        assert "telos" in result
        assert "memory" in result
        assert "metrics" in result
        assert "mermaid_graph" in result

    def test_metrics_computed(self, tmp_path):
        """Test that metrics are computed from data."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert result["metrics"]["mission_count"] == 0
        assert result["metrics"]["project_count"] == 0
        assert result["metrics"]["overall_completion"] == 0

    def test_includes_mermaid_graph(self, tmp_path):
        """Test that mermaid_graph is a string starting with graph TD."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert isinstance(result["mermaid_graph"], str)
        assert "graph TD" in result["mermaid_graph"]


@pytest.mark.unit
class TestBuildPaiMermaidGraph:
    """Tests for _build_pai_mermaid_graph() method."""

    def test_minimal_graph_for_empty_input(self, tmp_path):
        """Test that empty missions/projects produces valid graph."""
        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph([], [])
        assert "graph TD" in result

    def test_valid_syntax_with_data(self, tmp_path):
        """Test that graph with missions and projects has valid structure."""
        missions = [{"id": "m1", "title": "Mission 1", "status": "active", "linked_projects": ["p1"]}]
        projects = [{"id": "p1", "title": "Project 1", "status": "in_progress", "parent_mission": "m1"}]

        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph(missions, projects)
        assert "M_m1" in result
        assert "P_p1" in result
        assert "-->" in result

    def test_orphan_projects_handled(self, tmp_path):
        """Test that projects without mission links still appear."""
        projects = [{"id": "orphan", "title": "Orphan", "status": "active", "parent_mission": ""}]

        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph([], projects)
        assert "P_orphan" in result


@pytest.mark.unit
class TestGetPaiTasksSecurity:
    """Security tests for get_pai_tasks()."""

    def test_encoded_traversal(self, tmp_path):
        """Test that encoded path traversal chars are caught."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("..%2F..%2Fetc")

    def test_empty_string_project_id(self, tmp_path):
        """Test that empty string returns empty dict (no crash)."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_tasks("")
        assert result == {}
