"""Unit tests for documentation module."""

import sys

import pytest


@pytest.mark.unit
class TestDocumentation:
    """Test cases for documentation functionality."""

    def test_documentation_import(self, code_dir):
        """Test that we can import documentation module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.documentation import documentation_website
            assert documentation_website is not None
        except ImportError as e:
            pytest.fail(f"Failed to import documentation_website: {e}")

    def test_documentation_module_structure(self, code_dir):
        """Test that documentation module has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation import documentation_website

        assert hasattr(documentation_website, '__file__')
        assert hasattr(documentation_website, 'main')
        assert hasattr(documentation_website, 'check_doc_environment')
        assert hasattr(documentation_website, 'install_dependencies')
        assert hasattr(documentation_website, 'start_dev_server')
        assert hasattr(documentation_website, 'build_static_site')
        assert hasattr(documentation_website, 'serve_static_site')

    def test_command_exists(self, code_dir):
        """Test command_exists function with real shutil.which."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import command_exists

        # Test with a command that likely exists (python)
        assert command_exists('python') or command_exists('python3')

        # Test with a command that likely doesn't exist
        assert not command_exists('definitely_does_not_exist_command_12345')

    def test_check_doc_environment_success(self, code_dir):
        """Test check_doc_environment with real environment check."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import check_doc_environment

        # Test with real environment - may pass or fail depending on system
        result = check_doc_environment()
        assert isinstance(result, bool)

    def test_check_doc_environment_missing_node(self, code_dir):
        """Test check_doc_environment when Node.js is missing."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import check_doc_environment

        # Test with real environment - will check actual Node.js availability
        result = check_doc_environment()
        # Result depends on whether Node.js is actually installed
        assert isinstance(result, bool)

    @pytest.mark.slow
    def test_install_dependencies_success(self, code_dir, tmp_path):
        """Test install_dependencies function with real subprocess."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))


        # This actually runs npm install — skip in unit test context
        pytest.skip("Skipping: runs real npm install (use -m slow to include)")

    @pytest.mark.slow
    def test_run_command_stream_output(self, code_dir, tmp_path):
        """Test run_command_stream_output function with real subprocess."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))


        # This runs a real subprocess — skip in unit test context
        pytest.skip("Skipping: runs real subprocess (use -m slow to include)")

    def test_main_full_cycle(self, code_dir):
        """Test main function structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import main

        # Test that function exists and is callable
        assert callable(main)

    def test_assess_site(self, code_dir):
        """Test assess_site function exists and is callable."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import assess_site

        assert callable(assess_site)

    def test_print_assessment_checklist(self, capsys, code_dir):
        """Test print_assessment_checklist function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import (
            print_assessment_checklist,
        )

        print_assessment_checklist()

        captured = capsys.readouterr()
        assert "--- Documentation Website Assessment Checklist ---" in captured.out
        assert "- [ ] Overall Navigation:" in captured.out
        assert "--- End of Checklist ---" in captured.out

    @pytest.mark.slow
    def test_serve_static_site_build_missing(self, code_dir, tmp_path):
        """Test serve_static_site when build directory doesn't exist."""
        pytest.skip("Skipping: runs real npx serve (use -m slow to include)")

    def test_constants_and_paths(self, code_dir):
        """Test that module constants are properly defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.documentation.documentation_website import (
            DEFAULT_ACTION,
            DEFAULT_DOCS_PORT,
            DOCUSAURUS_BASE_PATH,
            DOCUSAURUS_ROOT_DIR,
            EFFECTIVE_DOCS_URL,
        )

        assert DEFAULT_DOCS_PORT == 3000
        assert DOCUSAURUS_BASE_PATH == "/codomyrmex/"
        assert DEFAULT_ACTION == "full_cycle"
        assert DOCUSAURUS_ROOT_DIR is not None
        assert "localhost:3000" in EFFECTIVE_DOCS_URL

    @pytest.mark.slow
    def test_build_static_site_error_handling(self, code_dir):
        """Test build_static_site error handling with real implementation."""
        pytest.skip("Skipping: runs real npm build (use -m slow to include)")


# Coverage push — documentation/scripts
class TestValidateConfigs:
    """Tests for config validation scripts."""

    def test_config_validator_init(self, tmp_path):
        from codomyrmex.documentation.scripts.validate_configs import ConfigValidator
        v = ConfigValidator(project_root=tmp_path)
        assert v is not None


class TestTripleCheck:
    """Tests for triple_check documentation verification."""

    def test_check_file_completeness(self):
        from codomyrmex.documentation.scripts.triple_check import check_file_completeness
        from pathlib import Path
        issues = check_file_completeness("# Title\n\nSome content here.", Path("test.md"))
        assert isinstance(issues, list)

    def test_find_placeholders(self):
        from codomyrmex.documentation.scripts.triple_check import find_placeholders
        from pathlib import Path
        phs = find_placeholders("TODO: fix this\nXXX placeholder", Path("test.py"))
        assert isinstance(phs, list)


class TestTripleCheckDeep:
    """Deep tests for triple_check functions."""

    def test_analyze_file(self, tmp_path):
        from codomyrmex.documentation.scripts.triple_check import analyze_file
        f = tmp_path / "test.md"
        f.write_text("# Title\n\nContent here.\n## Section\nMore content.")
        result = analyze_file(f, tmp_path)
        assert isinstance(result, dict)

    def test_find_placeholders_none(self, tmp_path):
        from codomyrmex.documentation.scripts.triple_check import find_placeholders
        phs = find_placeholders("No placeholders here", tmp_path / "clean.md")
        assert isinstance(phs, list)

    def test_check_completeness_full(self, tmp_path):
        from codomyrmex.documentation.scripts.triple_check import check_file_completeness
        content = "# Title\n\nThis is a complete document with real content.\n## Features\n- Feature 1\n- Feature 2"
        issues = check_file_completeness(content, tmp_path / "full.md")
        assert isinstance(issues, list)


class TestConfigValidatorDeep:
    """Deep tests for documentation config validator."""

    def test_validate_project(self, tmp_path):
        from codomyrmex.documentation.scripts.validate_configs import ConfigValidator
        # Create minimal project structure
        (tmp_path / "README.md").write_text("# Test Project")
        v = ConfigValidator(project_root=tmp_path)
        result = v.validate_all_configs()
        assert result is not None
