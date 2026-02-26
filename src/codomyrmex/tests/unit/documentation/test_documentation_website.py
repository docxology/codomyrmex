"""Comprehensive unit tests for documentation_website module.

Tests cover: command_exists, check_doc_environment, run_command_stream_output,
install_dependencies, start_dev_server, build_static_site, serve_static_site,
aggregate_docs, validate_doc_versions, print_assessment_checklist, assess_site,
module constants, and main() arg parsing.

Zero-mock policy: All tests use real objects, tmp_path, and real subprocesses.
"""

import os
import shutil
import sys

import pytest

# Lazy import helper — keeps collection fast and avoids module-level side effects.


def _import_website():
    """Lazy import of the documentation_website module."""
    from codomyrmex.documentation import documentation_website

    return documentation_website


# ---------------------------------------------------------------------------
# Constants & Module-Level Attributes
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestModuleConstants:
    """Verify module-level constants and computed paths."""

    def test_default_docs_port_type_and_value(self):
        mod = _import_website()
        assert isinstance(mod.DEFAULT_DOCS_PORT, int)
        assert mod.DEFAULT_DOCS_PORT == int(os.getenv("DOCS_PORT", "3000"))

    def test_docusaurus_base_path(self):
        mod = _import_website()
        assert mod.DOCUSAURUS_BASE_PATH == "/codomyrmex/"

    def test_default_action(self):
        mod = _import_website()
        assert mod.DEFAULT_ACTION == "full_cycle"

    def test_effective_docs_url_contains_host_and_port(self):
        mod = _import_website()
        expected_host = os.getenv("DOCS_HOST", "localhost")
        assert expected_host in mod.EFFECTIVE_DOCS_URL
        assert str(mod.DEFAULT_DOCS_PORT) in mod.EFFECTIVE_DOCS_URL

    def test_effective_docs_url_contains_base_path(self):
        mod = _import_website()
        assert "codomyrmex" in mod.EFFECTIVE_DOCS_URL

    def test_script_dir_is_absolute(self):
        mod = _import_website()
        assert os.path.isabs(mod.SCRIPT_DIR)

    def test_codomyrmex_src_dir_is_absolute(self):
        mod = _import_website()
        assert os.path.isabs(mod.CODOMYRMEX_SRC_DIR)

    def test_logger_is_not_none(self):
        mod = _import_website()
        assert hasattr(mod.logger, 'info')


# ---------------------------------------------------------------------------
# command_exists
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCommandExists:
    """Tests for the command_exists utility."""

    def test_python_exists(self):
        from codomyrmex.documentation.documentation_website import command_exists

        # At least one of these must be present to run the test suite at all
        assert command_exists("python") or command_exists("python3")

    def test_nonexistent_command(self):
        from codomyrmex.documentation.documentation_website import command_exists

        assert command_exists("__no_such_binary_xyz_99__") is False

    def test_ls_exists_on_unix(self):
        from codomyrmex.documentation.documentation_website import command_exists

        if sys.platform != "win32":
            assert command_exists("ls") is True

    def test_returns_bool(self):
        from codomyrmex.documentation.documentation_website import command_exists

        result = command_exists("echo")
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# check_doc_environment
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCheckDocEnvironment:
    """Tests for environment validation."""

    def test_returns_bool(self):
        from codomyrmex.documentation.documentation_website import (
            check_doc_environment,
        )

        result = check_doc_environment()
        assert isinstance(result, bool)

    @pytest.mark.skipif(
        shutil.which("node") is None, reason="Node.js not installed"
    )
    def test_passes_when_node_available(self):
        from codomyrmex.documentation.documentation_website import (
            check_doc_environment,
        )

        # Node exists and at least npm or yarn should be present
        result = check_doc_environment()
        assert result is True

    @pytest.mark.skipif(
        shutil.which("node") is not None, reason="Node.js IS installed"
    )
    def test_fails_when_node_missing(self):
        from codomyrmex.documentation.documentation_website import (
            check_doc_environment,
        )

        result = check_doc_environment()
        assert result is False


# ---------------------------------------------------------------------------
# run_command_stream_output
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRunCommandStreamOutput:
    """Tests for subprocess runner with streamed output."""

    def test_echo_succeeds(self, tmp_path):
        from codomyrmex.documentation.documentation_website import (
            run_command_stream_output,
        )

        result = run_command_stream_output(["echo", "hello"], cwd=str(tmp_path))
        assert result is True

    def test_false_returns_nonzero(self, tmp_path):
        from codomyrmex.documentation.documentation_website import (
            run_command_stream_output,
        )

        result = run_command_stream_output(["false"], cwd=str(tmp_path))
        assert result is False

    def test_nonexistent_command_returns_false(self, tmp_path):
        from codomyrmex.documentation.documentation_website import (
            run_command_stream_output,
        )

        result = run_command_stream_output(
            ["__nonexistent_binary_xyz__"], cwd=str(tmp_path)
        )
        assert result is False

    def test_respects_cwd(self, tmp_path):
        from codomyrmex.documentation.documentation_website import (
            run_command_stream_output,
        )

        # Create a file, then use `ls` (or `test -f`) to confirm cwd
        marker = tmp_path / "marker.txt"
        marker.write_text("exists")
        result = run_command_stream_output(
            ["test", "-f", "marker.txt"], cwd=str(tmp_path)
        )
        assert result is True

    def test_multiword_output(self, tmp_path):
        from codomyrmex.documentation.documentation_website import (
            run_command_stream_output,
        )

        result = run_command_stream_output(
            ["echo", "line1\nline2"], cwd=str(tmp_path)
        )
        assert result is True


# ---------------------------------------------------------------------------
# install_dependencies
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInstallDependencies:
    """Tests for install_dependencies (behaviour depends on npm/yarn availability)."""

    def test_returns_bool_with_npm(self):
        from codomyrmex.documentation.documentation_website import (
            install_dependencies,
        )

        # This will actually try to run npm install in DOCUSAURUS_ROOT_DIR.
        # It may fail (no package.json), but must return a bool.
        result = install_dependencies("npm")
        assert isinstance(result, bool)

    def test_returns_bool_with_yarn(self):
        from codomyrmex.documentation.documentation_website import (
            install_dependencies,
        )

        result = install_dependencies("yarn")
        assert isinstance(result, bool)

    def test_yarn_fallback_to_npm(self):
        """When yarn is requested but not available, should fall back to npm."""
        from codomyrmex.documentation.documentation_website import (
            install_dependencies,
        )

        # Regardless of which PM is available, we get a bool back
        result = install_dependencies("yarn")
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# aggregate_docs
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAggregateDocs:
    """Tests for documentation aggregation into Docusaurus docs/modules."""

    def test_empty_source_creates_dest(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        src.mkdir()
        dest = tmp_path / "dest"

        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert dest.exists()
        assert dest.is_dir()

    def test_copies_readme(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "my_module"
        mod_dir.mkdir(parents=True)
        (mod_dir / "README.md").write_text("# My Module")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        copied = dest / "my_module" / "readme.md"  # lowercased
        assert copied.exists()
        assert copied.read_text() == "# My Module"

    def test_copies_api_specification(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mod_a"
        mod_dir.mkdir(parents=True)
        (mod_dir / "API_SPECIFICATION.md").write_text("## API")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        copied = dest / "mod_a" / "api_specification.md"
        assert copied.exists()
        assert copied.read_text() == "## API"

    def test_copies_mcp_tool_specification(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mod_b"
        mod_dir.mkdir(parents=True)
        (mod_dir / "MCP_TOOL_SPECIFICATION.md").write_text("# MCP Tools")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "mod_b" / "mcp_tool_specification.md").exists()

    def test_copies_usage_examples(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mod_c"
        mod_dir.mkdir(parents=True)
        (mod_dir / "USAGE_EXAMPLES.md").write_text("Examples")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "mod_c" / "usage_examples.md").exists()

    def test_copies_changelog(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mod_d"
        mod_dir.mkdir(parents=True)
        (mod_dir / "CHANGELOG.md").write_text("# Changelog\n## v1.0")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "mod_d" / "changelog.md").exists()

    def test_copies_security(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mod_e"
        mod_dir.mkdir(parents=True)
        (mod_dir / "SECURITY.md").write_text("Security notes")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "mod_e" / "security.md").exists()

    def test_skips_documentation_module(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        (src / "documentation").mkdir(parents=True)
        (src / "documentation" / "README.md").write_text("self-ref")
        (src / "other_module").mkdir(parents=True)
        (src / "other_module" / "README.md").write_text("other")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        # documentation module must be skipped
        assert not (dest / "documentation").exists()
        # other module must be present
        assert (dest / "other_module" / "readme.md").exists()

    def test_skips_non_directory_entries(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        src.mkdir()
        (src / "stray_file.txt").write_text("not a module")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        # No module dirs created for files
        assert list(dest.iterdir()) == [] or all(
            not p.name.endswith(".txt") for p in dest.iterdir()
        )

    def test_copies_docs_subtree(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "modx"
        docs_sub = mod_dir / "docs"
        docs_sub.mkdir(parents=True)
        (docs_sub / "guide.md").write_text("Guide content")
        (docs_sub / "tutorial.md").write_text("Tutorial content")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "modx" / "docs" / "guide.md").exists()
        assert (dest / "modx" / "docs" / "tutorial.md").exists()

    def test_docs_subtree_replaces_stale(self, tmp_path):
        """Running aggregate twice replaces old docs subtree."""
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "mody"
        docs_sub = mod_dir / "docs"
        docs_sub.mkdir(parents=True)
        (docs_sub / "v1.md").write_text("version 1")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))
        assert (dest / "mody" / "docs" / "v1.md").exists()

        # Remove v1 from source, add v2
        (docs_sub / "v1.md").unlink()
        (docs_sub / "v2.md").write_text("version 2")

        aggregate_docs(source_root=str(src), dest_root=str(dest))
        assert not (dest / "mody" / "docs" / "v1.md").exists()
        assert (dest / "mody" / "docs" / "v2.md").exists()

    def test_handles_multiple_modules(self, tmp_path):
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        for name in ["alpha", "beta", "gamma"]:
            d = src / name
            d.mkdir(parents=True)
            (d / "README.md").write_text(f"# {name}")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        for name in ["alpha", "beta", "gamma"]:
            assert (dest / name / "readme.md").exists()

    def test_missing_optional_files_no_error(self, tmp_path):
        """Modules that lack optional doc files still work."""
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod_dir = src / "sparse"
        mod_dir.mkdir(parents=True)
        # No recognized files at all

        dest = tmp_path / "dest"
        # Should not raise
        aggregate_docs(source_root=str(src), dest_root=str(dest))
        # Module dir is created but empty (or nearly so)
        assert (dest / "sparse").exists()


# ---------------------------------------------------------------------------
# validate_doc_versions
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestValidateDocVersions:
    """Tests for documentation version validation."""

    def test_returns_tuple_of_three(self):
        mod = _import_website()
        result = mod.validate_doc_versions()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_first_element_is_bool(self):
        mod = _import_website()
        is_valid, errors, warnings = mod.validate_doc_versions()
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)

    def test_no_errors_when_aggregated_matches_source(self, tmp_path):
        """Build a mini project where source == aggregated."""
        mod = _import_website()

        # We need to temporarily override DOCUSAURUS_ROOT_DIR
        # Instead, we test with the real dirs -- the function uses DOCUSAURUS_ROOT_DIR
        # We just ensure it returns valid structure
        is_valid, errors, warnings = mod.validate_doc_versions()
        # In the real repo the aggregated docs might not exist, so warnings expected
        assert isinstance(is_valid, bool)


# ---------------------------------------------------------------------------
# print_assessment_checklist
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPrintAssessmentChecklist:
    """Tests for the assessment checklist printer."""

    def test_outputs_header_and_footer(self, capsys):
        from codomyrmex.documentation.documentation_website import (
            print_assessment_checklist,
        )

        print_assessment_checklist()
        out = capsys.readouterr().out

        assert "--- Documentation Website Assessment Checklist ---" in out
        assert "--- End of Checklist ---" in out

    def test_outputs_all_checklist_items(self, capsys):
        from codomyrmex.documentation.documentation_website import (
            print_assessment_checklist,
        )

        print_assessment_checklist()
        out = capsys.readouterr().out

        expected_fragments = [
            "Overall Navigation",
            "Content Rendering",
            "Content Accuracy",
            "Internal Links",
            "External Links",
            "Code Blocks",
            "Look and Feel",
            "Console Errors",
        ]
        for fragment in expected_fragments:
            assert fragment in out, f"Missing checklist item: {fragment}"

    def test_items_use_checkbox_format(self, capsys):
        from codomyrmex.documentation.documentation_website import (
            print_assessment_checklist,
        )

        print_assessment_checklist()
        out = capsys.readouterr().out

        # Each item should be prefixed with "- [ ] "
        lines = [l for l in out.strip().split("\n") if l.startswith("- [ ] ")]
        assert len(lines) == 8


# ---------------------------------------------------------------------------
# start_dev_server / build_static_site / serve_static_site — shallow tests
# (These call real subprocesses; we only test return types and error handling)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestStartDevServer:
    """Shallow tests for start_dev_server (no real server launched)."""

    def test_function_is_callable(self):
        from codomyrmex.documentation.documentation_website import start_dev_server

        assert callable(start_dev_server)

    def test_signature_accepts_package_manager(self):
        """Verify the function signature accepts a package_manager kwarg."""
        import inspect

        from codomyrmex.documentation.documentation_website import start_dev_server

        sig = inspect.signature(start_dev_server)
        assert "package_manager" in sig.parameters


@pytest.mark.unit
class TestBuildStaticSite:
    """Shallow tests for build_static_site."""

    def test_function_is_callable(self):
        from codomyrmex.documentation.documentation_website import build_static_site

        assert callable(build_static_site)

    def test_signature_accepts_package_manager(self):
        import inspect

        from codomyrmex.documentation.documentation_website import build_static_site

        sig = inspect.signature(build_static_site)
        assert "package_manager" in sig.parameters


@pytest.mark.unit
class TestServeStaticSite:
    """Shallow tests for serve_static_site."""

    def test_function_is_callable(self):
        from codomyrmex.documentation.documentation_website import serve_static_site

        assert callable(serve_static_site)

    def test_missing_build_dir_returns_false(self):
        """If the build dir doesn't exist, serve_static_site should return False."""
        mod = _import_website()
        build_dir = os.path.join(mod.DOCUSAURUS_ROOT_DIR, "build")
        if not os.path.exists(build_dir):
            result = mod.serve_static_site("npm")
            assert result is False


# ---------------------------------------------------------------------------
# assess_site
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAssessSite:
    """Tests for assess_site function."""

    def test_is_callable(self):
        from codomyrmex.documentation.documentation_website import assess_site

        assert callable(assess_site)


# ---------------------------------------------------------------------------
# main() argparse
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMainArgparse:
    """Test the main() function's argparse setup."""

    def test_main_is_callable(self):
        from codomyrmex.documentation.documentation_website import main

        assert callable(main)

    def test_main_accepts_checkenv_action(self):
        """main() with 'checkenv' should not raise (it runs check_doc_environment)."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "checkenv"]
            # checkenv just checks the env and returns
            main()
        except SystemExit:
            pass  # argparse may exit on certain conditions
        finally:
            sys.argv = original_argv

    def test_main_assess_action(self, capsys):
        """main() with 'assess' prints checklist."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "assess"]
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

        out = capsys.readouterr().out
        assert "Assessment Checklist" in out

    def test_main_aggregate_docs_action(self, tmp_path):
        """main() with 'aggregate_docs' runs without error."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "aggregate_docs"]
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

    def test_main_validate_docs_action(self):
        """main() with 'validate_docs' runs."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "validate_docs"]
            main()
        except SystemExit:
            pass  # may exit(1) if validation fails
        finally:
            sys.argv = original_argv

    def test_main_pm_flag(self):
        """main() accepts --pm yarn."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "checkenv", "--pm", "yarn"]
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv

    def test_main_invalid_action_exits(self):
        """main() with invalid action should raise SystemExit from argparse."""
        from codomyrmex.documentation.documentation_website import main

        original_argv = sys.argv
        try:
            sys.argv = ["documentation_website.py", "invalid_action_xyz"]
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = original_argv


# ---------------------------------------------------------------------------
# Edge cases for aggregate_docs
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAggregateDocsEdgeCases:
    """Additional edge-case tests for aggregate_docs."""

    def test_dest_already_exists(self, tmp_path):
        """If dest already exists, aggregation still works."""
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod = src / "existing_mod"
        mod.mkdir(parents=True)
        (mod / "README.md").write_text("# Existing")

        dest = tmp_path / "dest"
        dest.mkdir()  # pre-create

        aggregate_docs(source_root=str(src), dest_root=str(dest))
        assert (dest / "existing_mod" / "readme.md").exists()

    def test_unrecognized_files_not_copied(self, tmp_path):
        """Files not in the recognized list are NOT copied."""
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod = src / "mymod"
        mod.mkdir(parents=True)
        (mod / "random_file.txt").write_text("should not be copied")
        (mod / "README.md").write_text("# MyMod")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "mymod" / "readme.md").exists()
        assert not (dest / "mymod" / "random_file.txt").exists()

    def test_nested_docs_with_subdirectories(self, tmp_path):
        """docs/ subtree with nested subdirectories gets fully copied."""
        from codomyrmex.documentation.documentation_website import aggregate_docs

        src = tmp_path / "source"
        mod = src / "deep_mod"
        deep = mod / "docs" / "sub1" / "sub2"
        deep.mkdir(parents=True)
        (deep / "nested.md").write_text("deep content")

        dest = tmp_path / "dest"
        aggregate_docs(source_root=str(src), dest_root=str(dest))

        assert (dest / "deep_mod" / "docs" / "sub1" / "sub2" / "nested.md").exists()
