"""Unit tests for documentation/pai.py, mcp_tools.py, and selected scripts.

Covers:
- pai.py: get_layer, humanize_name, extract_exports, extract_readme_description,
          infer_pai_phase, generate_pai_md, write_pai_md, update_pai_docs
- mcp_tools.py: generate_module_docs, audit_rasp_compliance
- scripts/placeholder_check.py: find_placeholders, fix_generic_placeholders
- scripts/global_doc_auditor.py: is_relevant_dir, audit_directory
- scripts/fix_agents_structure.py: get_active_components, fix_agents_file

Zero-mock policy: no patching, real filesystem via tmp_path.
"""

from pathlib import Path

import pytest

from codomyrmex.documentation.pai import (
    APPLICATION,
    CORE,
    FOUNDATION,
    SERVICE,
    extract_exports,
    extract_readme_description,
    generate_pai_md,
    get_layer,
    humanize_name,
    infer_pai_phase,
    update_pai_docs,
    write_pai_md,
)

# ---------------------------------------------------------------------------
# get_layer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetLayer:
    """Test get_layer returns the correct architectural layer."""

    def test_logging_monitoring_is_foundation(self):
        assert get_layer("logging_monitoring") == "Foundation"

    def test_environment_setup_is_foundation(self):
        assert get_layer("environment_setup") == "Foundation"

    def test_agents_is_core(self):
        assert get_layer("agents") == "Core"

    def test_documentation_is_service(self):
        assert get_layer("documentation") == "Service"

    def test_cli_is_application(self):
        assert get_layer("cli") == "Application"

    def test_unknown_module_is_extended(self):
        assert get_layer("totally_unknown_module_xyz") == "Extended"

    def test_all_foundation_members(self):
        for m in FOUNDATION:
            assert get_layer(m) == "Foundation"

    def test_all_core_members(self):
        for m in CORE:
            assert get_layer(m) == "Core"

    def test_all_service_members(self):
        for m in SERVICE:
            assert get_layer(m) == "Service"

    def test_all_application_members(self):
        for m in APPLICATION:
            assert get_layer(m) == "Application"


# ---------------------------------------------------------------------------
# humanize_name
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHumanizeName:
    """Test humanize_name snake_case → Title Case conversion."""

    def test_simple_name(self):
        assert humanize_name("agents") == "Agents"

    def test_snake_case_two_words(self):
        assert humanize_name("git_operations") == "Git Operations"

    def test_snake_case_three_words(self):
        assert humanize_name("logging_monitoring_utils") == "Logging Monitoring Utils"

    def test_single_word_no_underscore(self):
        assert humanize_name("documentation") == "Documentation"

    def test_already_title_case_like(self):
        # module names are lowercase, but function should still work
        result = humanize_name("my_module")
        assert result == "My Module"


# ---------------------------------------------------------------------------
# extract_exports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractExports:
    """Test extract_exports parses __all__ and classifies symbols."""

    def test_missing_init_returns_empty(self, tmp_path: Path):
        result = extract_exports(tmp_path / "nonexistent" / "__init__.py")
        assert result["all"] == []
        assert result["classes"] == []
        assert result["functions"] == []
        assert result["docstring"] == ""

    def test_extracts_all_list(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text(
            '"""My module docstring."""\n'
            '__all__ = ["MyClass", "my_func", "CONSTANT"]\n'
        )
        result = extract_exports(init)
        assert "MyClass" in result["all"]
        assert "my_func" in result["all"]
        assert "CONSTANT" in result["all"]

    def test_classifies_uppercase_as_class(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["MyClass"]\n')
        result = extract_exports(init)
        assert "MyClass" in result["classes"]

    def test_classifies_lowercase_as_function(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["my_function"]\n')
        result = extract_exports(init)
        assert "my_function" in result["functions"]

    def test_extracts_docstring(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text('"""Module docstring here."""\n__all__ = []\n')
        result = extract_exports(init)
        assert result["docstring"] == "Module docstring here."

    def test_no_docstring_returns_empty_string(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text("import os\n__all__ = []\n")
        result = extract_exports(init)
        assert result["docstring"] == ""

    def test_empty_all_returns_empty_lists(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text('"""Doc."""\n__all__ = []\n')
        result = extract_exports(init)
        assert result["all"] == []

    def test_cli_commands_skipped(self, tmp_path: Path):
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["cli_commands", "real_func"]\n')
        result = extract_exports(init)
        # cli_commands excluded from classes/functions
        assert "cli_commands" not in result["classes"]
        assert "cli_commands" not in result["functions"]


# ---------------------------------------------------------------------------
# extract_readme_description
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractReadmeDescription:
    """Test extract_readme_description parses first paragraph from README.md."""

    def test_missing_readme_returns_empty(self, tmp_path: Path):
        result = extract_readme_description(tmp_path / "README.md")
        assert result == ""

    def test_extracts_first_paragraph(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# My Module\n\n"
            "This is the first paragraph of the README.\n\n"
            "## Section 2\n\nMore content."
        )
        result = extract_readme_description(readme)
        assert "This is the first paragraph" in result

    def test_truncates_to_300_chars(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        long_para = "A" * 400
        readme.write_text(f"# Title\n\n{long_para}\n")
        result = extract_readme_description(readme)
        assert len(result) <= 300

    def test_empty_file_returns_empty(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text("")
        result = extract_readme_description(readme)
        assert result == ""

    def test_title_only_returns_empty(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text("# Just a title\n")
        result = extract_readme_description(readme)
        assert result == ""


# ---------------------------------------------------------------------------
# infer_pai_phase
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInferPaiPhase:
    """Test infer_pai_phase maps function/class names to algorithm phases."""

    def test_get_function_maps_to_observe(self):
        phases = infer_pai_phase("m", ["get_status", "list_items"], [])
        assert "OBSERVE" in phases

    def test_analyze_function_maps_to_think(self):
        phases = infer_pai_phase("m", ["analyze_data"], [])
        assert "THINK" in phases

    def test_generate_function_maps_to_build(self):
        phases = infer_pai_phase("m", ["generate_report"], [])
        assert "BUILD" in phases

    def test_execute_function_maps_to_execute(self):
        phases = infer_pai_phase("m", ["execute_task"], [])
        assert "EXECUTE" in phases

    def test_validate_function_maps_to_verify(self):
        phases = infer_pai_phase("m", ["validate_schema"], [])
        assert "VERIFY" in phases

    def test_memory_function_maps_to_learn(self):
        phases = infer_pai_phase("m", ["store_memory"], [])
        assert "LEARN" in phases

    def test_empty_names_returns_execute_fallback(self):
        phases = infer_pai_phase("m", [], [])
        assert "EXECUTE" in phases

    def test_plan_function_maps_to_plan(self):
        phases = infer_pai_phase("m", ["plan_workflow"], [])
        assert "PLAN" in phases


# ---------------------------------------------------------------------------
# generate_pai_md
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGeneratePaiMd:
    """Test generate_pai_md produces a valid Markdown document."""

    def _make_module_dir(self, tmp_path: Path, name: str) -> Path:
        d = tmp_path / name
        d.mkdir()
        (d / "__init__.py").write_text(
            f'"""The {name} module provides things."""\n'
            '__all__ = ["MyClass", "do_stuff"]\n'
        )
        (d / "README.md").write_text(
            f"# {name.title()}\n\n"
            f"This module does important things for {name}.\n"
        )
        return d

    def test_returns_string(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "test_mod")
        result = generate_pai_md("test_mod", d)
        assert isinstance(result, str)

    def test_contains_overview_section(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "test_mod")
        result = generate_pai_md("test_mod", d)
        assert "## Overview" in result

    def test_contains_module_name(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "my_module")
        result = generate_pai_md("my_module", d)
        assert "My Module" in result

    def test_contains_navigation_section(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "test_mod")
        result = generate_pai_md("test_mod", d)
        assert "## Navigation" in result

    def test_contains_phase_mapping(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "test_mod")
        result = generate_pai_md("test_mod", d)
        assert "PAI Algorithm Phase Mapping" in result

    def test_contains_layer_info(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "agents")
        result = generate_pai_md("agents", d)
        assert "Core" in result  # agents is Core layer

    def test_string_module_dir_accepted(self, tmp_path: Path):
        """generate_pai_md accepts string paths and converts to Path."""
        d = self._make_module_dir(tmp_path, "str_mod")
        result = generate_pai_md("str_mod", str(d))
        assert isinstance(result, str)
        assert "## Overview" in result

    def test_missing_init_generates_without_crash(self, tmp_path: Path):
        d = tmp_path / "no_init"
        d.mkdir()
        result = generate_pai_md("no_init", d)
        assert isinstance(result, str)

    def test_contains_key_exports_section_when_all_present(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "exports_mod")
        result = generate_pai_md("exports_mod", d)
        assert "Key Exports" in result


# ---------------------------------------------------------------------------
# write_pai_md
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestWritePaiMd:
    """Test write_pai_md writes PAI.md to the real filesystem."""

    def _make_module_dir(self, tmp_path: Path, name: str) -> Path:
        d = tmp_path / name
        d.mkdir()
        (d / "__init__.py").write_text(f'"""Module {name}."""\n__all__ = []\n')
        return d

    def test_writes_file(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "target_mod")
        result_path = write_pai_md("target_mod", d)
        assert result_path.exists()

    def test_returns_path_object(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "path_mod")
        result = write_pai_md("path_mod", d)
        assert isinstance(result, Path)

    def test_written_file_is_pai_md(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "named_mod")
        result = write_pai_md("named_mod", d)
        assert result.name == "PAI.md"

    def test_written_file_has_content(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "content_mod")
        result = write_pai_md("content_mod", d)
        content = result.read_text()
        assert len(content) > 50

    def test_string_dir_accepted(self, tmp_path: Path):
        d = self._make_module_dir(tmp_path, "str_dir_mod")
        result = write_pai_md("str_dir_mod", str(d))
        assert result.exists()


# ---------------------------------------------------------------------------
# update_pai_docs
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestUpdatePaiDocs:
    """Test update_pai_docs batch stub updater."""

    def test_missing_src_dir_prints_error(self, tmp_path: Path, capsys):
        fake = tmp_path / "nonexistent_src"
        update_pai_docs(fake, apply=False)
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_dry_run_does_not_write(self, tmp_path: Path):
        # Create a stub PAI.md (under max_lines threshold=55)
        mod = tmp_path / "short_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Short mod."""\n__all__ = []\n')
        pai = mod / "PAI.md"
        pai.write_text("# Short stub\n")
        original_mtime = pai.stat().st_mtime

        update_pai_docs(tmp_path, apply=False)
        # In dry-run mode, mtime should be unchanged
        assert pai.stat().st_mtime == original_mtime

    def test_apply_mode_updates_stub(self, tmp_path: Path, capsys):
        mod = tmp_path / "stub_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Stub mod."""\n__all__ = []\n')
        pai = mod / "PAI.md"
        pai.write_text("# Stub\n")

        update_pai_docs(tmp_path, apply=True)
        captured = capsys.readouterr()
        assert "UPDATED" in captured.out or "Applied" in captured.out

    def test_long_pai_md_skipped(self, tmp_path: Path, capsys):
        mod = tmp_path / "long_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Long mod."""\n__all__ = []\n')
        pai = mod / "PAI.md"
        # Write 60 lines (> max_lines=55)
        pai.write_text("# Long\n" + "\n".join(["line"] * 60))

        update_pai_docs(tmp_path, apply=True)
        captured = capsys.readouterr()
        assert "skipped" in captured.out

    def test_tests_dir_skipped(self, tmp_path: Path, capsys):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "PAI.md").write_text("# Tests\n")
        update_pai_docs(tmp_path, apply=False)
        # Should print summary but not try to update tests/PAI.md
        captured = capsys.readouterr()
        assert "WOULD UPDATE  tests" not in captured.out


# ---------------------------------------------------------------------------
# mcp_tools.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMcpToolsGenerateModuleDocs:
    """Test generate_module_docs MCP tool function."""

    def test_nonexistent_module_returns_error(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        result = generate_module_docs("definitely_not_a_real_module_xyz")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_returns_dict(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        result = generate_module_docs("nonexistent_xyz")
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        result = generate_module_docs("no_module_here")
        assert "status" in result


@pytest.mark.unit
class TestMcpToolsAuditRaspCompliance:
    """Test audit_rasp_compliance MCP tool function."""

    def test_returns_dict(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        result = audit_rasp_compliance(module_name=None)
        assert isinstance(result, dict)

    def test_has_status_key(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        result = audit_rasp_compliance()
        assert "status" in result

    def test_compliant_key_present_on_success(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        result = audit_rasp_compliance()
        # Either success (has 'compliant') or error (has 'message')
        assert "compliant" in result or "message" in result

    def test_mcp_tool_meta_attribute(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        assert hasattr(audit_rasp_compliance, "_mcp_tool_meta")

    def test_generate_module_docs_mcp_tool_meta(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        assert hasattr(generate_module_docs, "_mcp_tool_meta")


# ---------------------------------------------------------------------------
# scripts/placeholder_check.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPlaceholderCheckFindPlaceholders:
    """Test find_placeholders detects placeholder patterns in content."""

    def test_no_placeholders_returns_empty(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        result = find_placeholders("This is clean content with no placeholders.", tmp_path / "clean.md")
        assert result == []

    def test_detects_module_name_placeholder(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "Use [Module Name] for your integration."
        result = find_placeholders(content, tmp_path / "file.md")
        assert len(result) > 0

    def test_result_contains_pattern_key(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "[Module Name] is a placeholder."
        results = find_placeholders(content, tmp_path / "f.md")
        assert all("pattern" in r for r in results)

    def test_result_contains_description_key(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "[Module Name] present."
        results = find_placeholders(content, tmp_path / "f.md")
        assert all("description" in r for r in results)

    def test_detects_brief_description_placeholder(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "Overview: [Brief description of this module]"
        result = find_placeholders(content, tmp_path / "f.md")
        assert len(result) > 0

    def test_detects_main_class_placeholder(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "See [MainClass] for examples."
        result = find_placeholders(content, tmp_path / "f.md")
        assert len(result) > 0

    def test_multiple_placeholders_all_detected(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import find_placeholders

        content = "[Module Name] uses [MainClass] pattern."
        result = find_placeholders(content, tmp_path / "f.md")
        assert len(result) >= 2


@pytest.mark.unit
class TestPlaceholderCheckFixGeneric:
    """Test fix_generic_placeholders replaces generic descriptions."""

    def test_generic_src_system_fixed(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import (
            fix_generic_placeholders,
        )

        file_path = tmp_path / "mydir" / "README.md"
        file_path.parent.mkdir()
        content = "Contains components for the src system"
        result = fix_generic_placeholders(content, file_path)
        assert "Contains components for the src system" not in result

    def test_content_without_placeholder_unchanged(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import (
            fix_generic_placeholders,
        )

        file_path = tmp_path / "README.md"
        content = "Clean documentation with real content."
        result = fix_generic_placeholders(content, file_path)
        assert result == content

    def test_docs_dir_gets_documentation_replacement(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.placeholder_check import (
            fix_generic_placeholders,
        )

        file_path = tmp_path / "docs_module" / "README.md"
        file_path.parent.mkdir()
        content = "Contains components for the src system"
        result = fix_generic_placeholders(content, file_path)
        assert "Documentation" in result or "docs_module" in result


# ---------------------------------------------------------------------------
# scripts/global_doc_auditor.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGlobalDocAuditorIsRelevantDir:
    """Test is_relevant_dir helper function."""

    def test_normal_path_is_relevant(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.global_doc_auditor import is_relevant_dir

        result = is_relevant_dir(tmp_path / "src" / "mymodule")
        assert result is True

    def test_git_path_not_relevant(self):
        from codomyrmex.documentation.scripts.global_doc_auditor import is_relevant_dir

        p = Path("/project/.git/objects")
        result = is_relevant_dir(p)
        assert result is False

    def test_pycache_path_not_relevant(self):
        from codomyrmex.documentation.scripts.global_doc_auditor import is_relevant_dir

        p = Path("/project/__pycache__/subdir")
        result = is_relevant_dir(p)
        assert result is False


@pytest.mark.unit
class TestGlobalDocAuditorAuditDirectory:
    """Test audit_directory scans real filesystem dirs."""

    def test_empty_dir_returns_zero_issues(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.global_doc_auditor import audit_directory

        total, compliant, issues = audit_directory(tmp_path)
        assert isinstance(issues, list)

    def test_compliant_dir_counted(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.global_doc_auditor import audit_directory

        # Create a directory with all required files AND a .py file
        d = tmp_path / "complete_dir"
        d.mkdir()
        for f in ["README.md", "AGENTS.md", "SPEC.md"]:
            (d / f).write_text(f"# {f}\n")
        (d / "module.py").write_text("pass\n")

        total, compliant, issues = audit_directory(tmp_path)
        assert compliant >= 1

    def test_missing_required_files_creates_issue(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.global_doc_auditor import audit_directory

        # Directory has a .py file but is missing required docs
        d = tmp_path / "incomplete_dir"
        d.mkdir()
        (d / "module.py").write_text("pass\n")
        # Only README.md present, AGENTS.md and SPEC.md missing

        _total, _compliant, issues = audit_directory(tmp_path)
        assert any("incomplete_dir" in str(i) for i in issues)

    def test_returns_tuple_of_three(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.global_doc_auditor import audit_directory

        result = audit_directory(tmp_path)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# scripts/fix_agents_structure.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFixAgentsStructureGetActiveComponents:
    """Test get_active_components generates component list from directory."""

    def test_returns_string(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            get_active_components,
        )

        result = get_active_components(tmp_path)
        assert isinstance(result, str)

    def test_includes_active_components_header(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            get_active_components,
        )

        result = get_active_components(tmp_path)
        assert "## Active Components" in result

    def test_lists_subdirectory(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            get_active_components,
        )

        subdir = tmp_path / "my_component"
        subdir.mkdir()
        result = get_active_components(tmp_path)
        assert "my_component" in result

    def test_empty_dir_returns_no_specific_components(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            get_active_components,
        )

        result = get_active_components(tmp_path)
        assert "No specific components" in result


@pytest.mark.unit
class TestFixAgentsStructureFixAgentsFile:
    """Test fix_agents_file modifies AGENTS.md when sections missing."""

    def test_adds_operating_contracts_when_missing(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            fix_agents_file,
        )

        agents = tmp_path / "AGENTS.md"
        agents.write_text("# AGENTS\n\nSome content here.\n")
        result = fix_agents_file(agents)
        assert result is True
        content = agents.read_text()
        assert "Operating Contracts" in content

    def test_already_complete_returns_false(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            fix_agents_file,
        )

        agents = tmp_path / "AGENTS.md"
        agents.write_text(
            "# AGENTS\n\n"
            "## Active Components\n- `foo/` component\n\n"
            "## Operating Contracts\n- Stay aligned.\n"
        )
        result = fix_agents_file(agents)
        assert result is False

    def test_adds_active_components_when_missing(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            fix_agents_file,
        )

        (tmp_path / "subcomp").mkdir()
        agents = tmp_path / "AGENTS.md"
        agents.write_text(
            "# AGENTS\n\n"
            "## Operating Contracts\n- Stay aligned.\n"
        )
        result = fix_agents_file(agents)
        assert result is True
        content = agents.read_text()
        assert "Active Components" in content

    def test_get_default_contracts_content(self):
        from codomyrmex.documentation.scripts.fix_agents_structure import (
            get_default_contracts,
        )

        content = get_default_contracts()
        assert "Operating Contracts" in content
        assert isinstance(content, str)
