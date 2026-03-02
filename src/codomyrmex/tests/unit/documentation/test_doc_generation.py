"""Unit tests for documentation generation functions.

Tests cover: generate_pai_md, extract_exports, extract_readme_description,
humanize_name, get_layer, infer_pai_phase, update_pai_docs, and the
generate_module_docs MCP tool.

Zero-mock policy: All tests use real filesystem via tmp_path fixtures.
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestExtractExports:
    """Test extract_exports parsing of __init__.py files."""

    def test_extracts_all_list(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        init = tmp_path / "__init__.py"
        init.write_text(
            '"""Module docstring."""\n\n'
            '__all__ = ["MyClass", "helper_func", "another_func"]\n'
        )
        result = extract_exports(init)
        assert result["all"] == ["MyClass", "helper_func", "another_func"]

    def test_classifies_classes_and_functions(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        init = tmp_path / "__init__.py"
        init.write_text(
            '"""Docstring."""\n'
            '__all__ = ["MyClass", "AnotherClass", "my_func"]\n'
        )
        result = extract_exports(init)
        assert "MyClass" in result["classes"]
        assert "AnotherClass" in result["classes"]
        assert "my_func" in result["functions"]

    def test_extracts_docstring(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        init = tmp_path / "__init__.py"
        init.write_text('"""This is the module docstring."""\n')
        result = extract_exports(init)
        assert result["docstring"] == "This is the module docstring."

    def test_missing_file_returns_empty(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        missing = tmp_path / "nonexistent" / "__init__.py"
        result = extract_exports(missing)
        assert result["all"] == []
        assert result["classes"] == []
        assert result["functions"] == []
        assert result["docstring"] == ""

    def test_no_all_list_returns_empty_exports(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        init = tmp_path / "__init__.py"
        init.write_text('"""Docstring."""\nimport os\n')
        result = extract_exports(init)
        assert result["all"] == []

    def test_syntax_error_raises(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_exports

        init = tmp_path / "__init__.py"
        init.write_text("def broken(\n")
        with pytest.raises(SyntaxError):
            extract_exports(init)


@pytest.mark.unit
class TestExtractReadmeDescription:
    """Test extract_readme_description from README.md files."""

    def test_extracts_first_paragraph(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_readme_description

        readme = tmp_path / "README.md"
        readme.write_text("# My Module\n\nThis is the first paragraph.\n\n## Details\n")
        desc = extract_readme_description(readme)
        assert desc == "This is the first paragraph."

    def test_missing_readme_returns_empty(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_readme_description

        missing = tmp_path / "README.md"
        desc = extract_readme_description(missing)
        assert desc == ""

    def test_multiline_first_paragraph(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_readme_description

        readme = tmp_path / "README.md"
        readme.write_text("# Title\n\nFirst line of paragraph.\nSecond line.\n\n## Next\n")
        desc = extract_readme_description(readme)
        assert "First line" in desc
        assert "Second line" in desc

    def test_truncates_at_300_chars(self, tmp_path: Path):
        from codomyrmex.documentation.pai import extract_readme_description

        readme = tmp_path / "README.md"
        long_text = "A" * 400
        readme.write_text(f"# Title\n\n{long_text}\n\n## Next\n")
        desc = extract_readme_description(readme)
        assert len(desc) <= 300


@pytest.mark.unit
class TestHumanizeName:
    """Test humanize_name utility."""

    def test_snake_case_to_title(self):
        from codomyrmex.documentation.pai import humanize_name

        assert humanize_name("my_module") == "My Module"

    def test_single_word(self):
        from codomyrmex.documentation.pai import humanize_name

        assert humanize_name("agents") == "Agents"

    def test_multiple_underscores(self):
        from codomyrmex.documentation.pai import humanize_name

        assert humanize_name("ci_cd_automation") == "Ci Cd Automation"


@pytest.mark.unit
class TestGetLayer:
    """Test get_layer module classification."""

    def test_foundation_layer(self):
        from codomyrmex.documentation.pai import get_layer

        assert get_layer("logging_monitoring") == "Foundation"
        assert get_layer("environment_setup") == "Foundation"

    def test_core_layer(self):
        from codomyrmex.documentation.pai import get_layer

        assert get_layer("agents") == "Core"
        assert get_layer("static_analysis") == "Core"

    def test_service_layer(self):
        from codomyrmex.documentation.pai import get_layer

        assert get_layer("documentation") == "Service"
        assert get_layer("orchestrator") == "Service"

    def test_application_layer(self):
        from codomyrmex.documentation.pai import get_layer

        assert get_layer("cli") == "Application"
        assert get_layer("system_discovery") == "Application"

    def test_unknown_module_returns_extended(self):
        from codomyrmex.documentation.pai import get_layer

        assert get_layer("unknown_future_module") == "Extended"


@pytest.mark.unit
class TestInferPaiPhase:
    """Test infer_pai_phase mapping logic."""

    def test_observe_phase_detected(self):
        from codomyrmex.documentation.pai import infer_pai_phase

        phases = infer_pai_phase("my_mod", ["get_data", "list_items"], [])
        assert "OBSERVE" in phases

    def test_verify_phase_detected(self):
        from codomyrmex.documentation.pai import infer_pai_phase

        phases = infer_pai_phase("my_mod", ["validate_config", "check_status"], [])
        assert "VERIFY" in phases

    def test_build_phase_detected(self):
        from codomyrmex.documentation.pai import infer_pai_phase

        phases = infer_pai_phase("my_mod", ["generate_report", "create_artifact"], [])
        assert "BUILD" in phases

    def test_empty_functions_defaults_to_execute(self):
        from codomyrmex.documentation.pai import infer_pai_phase

        phases = infer_pai_phase("my_mod", [], [])
        assert "EXECUTE" in phases

    def test_multiple_phases_inferred(self):
        from codomyrmex.documentation.pai import infer_pai_phase

        phases = infer_pai_phase(
            "my_mod",
            ["get_data", "generate_output", "validate_result"],
            []
        )
        assert "OBSERVE" in phases
        assert "BUILD" in phases
        assert "VERIFY" in phases


@pytest.mark.unit
class TestGeneratePaiMd:
    """Test generate_pai_md document generation."""

    def _make_module(self, tmp_path: Path) -> tuple[str, Path]:
        """Create a minimal module directory for PAI.md generation."""
        mod = tmp_path / "test_module"
        mod.mkdir()
        (mod / "__init__.py").write_text(
            '"""Test module for PAI generation."""\n\n'
            '__all__ = ["TestClass", "helper_func"]\n'
        )
        (mod / "README.md").write_text(
            "# Test Module\n\nProvides testing utilities for the platform.\n"
        )
        return "test_module", mod

    def test_generates_markdown_string(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_module_header(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert "Personal AI Infrastructure" in result
        assert "Test Module" in result

    def test_contains_phase_mapping_table(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert "## PAI Algorithm Phase Mapping" in result
        assert "| Phase |" in result

    def test_contains_key_exports_table(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert "## Key Exports" in result
        assert "`TestClass`" in result
        assert "`helper_func`" in result

    def test_contains_architecture_role(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert "## Architecture Role" in result
        assert "Extended Layer" in result

    def test_contains_navigation_section(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        name, mod_dir = self._make_module(tmp_path)
        result = generate_pai_md(name, mod_dir)
        assert "## Navigation" in result
        assert "PAI.md" in result
        assert "README.md" in result

    def test_empty_module_still_generates(self, tmp_path: Path):
        from codomyrmex.documentation.pai import generate_pai_md

        mod = tmp_path / "empty_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        result = generate_pai_md("empty_mod", mod)
        assert isinstance(result, str)
        assert "empty_mod" in result.lower() or "Empty Mod" in result


@pytest.mark.unit
class TestUpdatePaiDocs:
    """Test update_pai_docs batch updating."""

    def test_nonexistent_dir_handled(self, tmp_path: Path, capsys):
        from codomyrmex.documentation.pai import update_pai_docs

        fake = tmp_path / "does_not_exist"
        update_pai_docs(fake)
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_dry_run_does_not_write(self, tmp_path: Path):
        from codomyrmex.documentation.pai import update_pai_docs

        mod = tmp_path / "my_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Module."""\n')
        (mod / "PAI.md").write_text("# Stub\n")

        original_content = (mod / "PAI.md").read_text()
        update_pai_docs(tmp_path, apply=False)
        assert (mod / "PAI.md").read_text() == original_content

    def test_apply_writes_updated_content(self, tmp_path: Path):
        from codomyrmex.documentation.pai import update_pai_docs

        mod = tmp_path / "my_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Module."""\n')
        (mod / "PAI.md").write_text("# Stub\n")

        update_pai_docs(tmp_path, apply=True)
        content = (mod / "PAI.md").read_text()
        assert "Personal AI Infrastructure" in content

    def test_skips_non_stub_files(self, tmp_path: Path, capsys):
        from codomyrmex.documentation.pai import update_pai_docs

        mod = tmp_path / "rich_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Rich."""\n')
        # Write a PAI.md with more than MAX_STUB_LINES (55) lines
        long_content = "\n".join([f"Line {i}" for i in range(60)])
        (mod / "PAI.md").write_text(long_content)

        update_pai_docs(tmp_path, apply=True)
        # Should not be updated
        assert (mod / "PAI.md").read_text() == long_content


@pytest.mark.unit
class TestGenerateModuleDocsMcpTool:
    """Test the generate_module_docs MCP tool function."""

    def test_nonexistent_module_returns_error(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        result = generate_module_docs("totally_fake_module_xyz_12345")
        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_returns_dict_structure(self):
        from codomyrmex.documentation.mcp_tools import generate_module_docs

        result = generate_module_docs("nonexistent_module_abc")
        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result


@pytest.mark.unit
class TestAuditRaspComplianceMcpTool:
    """Test the audit_rasp_compliance MCP tool function."""

    def test_returns_dict_with_status(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        result = audit_rasp_compliance()
        assert isinstance(result, dict)
        assert "status" in result

    def test_result_contains_compliant_field(self):
        from codomyrmex.documentation.mcp_tools import audit_rasp_compliance

        result = audit_rasp_compliance()
        if result["status"] == "success":
            assert "compliant" in result
            assert "missing_count" in result
