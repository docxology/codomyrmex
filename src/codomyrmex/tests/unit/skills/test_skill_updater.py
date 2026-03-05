"""Tests for skill_updater — SKILL.md tool table regeneration.

Tests category inference, table replacement logic, and file handling.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.skills.skill_updater import (
    _infer_category,
    update_skill_md,
)

# ── Category Inference ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_infer_category_git():
    """Git-related tool names should return 'Git'."""
    assert _infer_category("git_status") == "Git"
    assert _infer_category("get_git_log") == "Git"


@pytest.mark.unit
def test_infer_category_file_ops():
    """Read/write/list tools should return 'File Ops'."""
    assert _infer_category("read_file") == "File Ops"
    assert _infer_category("write_output") == "File Ops"
    assert _infer_category("list_modules") == "File Ops"


@pytest.mark.unit
def test_infer_category_code_analysis():
    """Analyze/search tools should return 'Code Analysis'."""
    assert _infer_category("analyze_project") == "Code Analysis"
    assert _infer_category("search_codebase") == "Code Analysis"


@pytest.mark.unit
def test_infer_category_pai():
    """PAI-related tools should return 'PAI'."""
    assert _infer_category("pai_status") == "PAI"
    assert _infer_category("pai_awareness") == "PAI"


@pytest.mark.unit
def test_infer_category_execution():
    """Run tools should return 'Execution'."""
    assert _infer_category("run_command") == "Execution"
    assert _infer_category("run_tests") == "Execution"


@pytest.mark.unit
def test_infer_category_data():
    """JSON/checksum tools should return 'Data'."""
    assert _infer_category("json_query") == "Data"
    assert _infer_category("checksum_file") == "Data"


@pytest.mark.unit
def test_infer_category_llm():
    """Ask tools should return 'LLM'."""
    assert _infer_category("ask") == "LLM"
    assert _infer_category("ask_llm") == "LLM"


@pytest.mark.unit
def test_infer_category_memory():
    """Memory tools should return 'Memory'."""
    assert _infer_category("store_memory") == "Memory"
    assert _infer_category("search_memories") == "Memory"


@pytest.mark.unit
def test_infer_category_security():
    """Scan/audit tools should return 'Security'."""
    assert _infer_category("scan_secrets") == "Security"
    assert _infer_category("audit_code") == "Security"


@pytest.mark.unit
def test_infer_category_visualization():
    """Report tools should return 'Visualization'."""
    assert _infer_category("generate_report") == "Visualization"


@pytest.mark.unit
def test_infer_category_general():
    """Unknown tool names should return 'General'."""
    assert _infer_category("some_unique_tool") == "General"
    assert _infer_category("foo_bar") == "General"


# ── Update Logic ─────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_update_skill_md_file_not_found():
    """update_skill_md should return 1 if file doesn't exist."""
    result = update_skill_md(Path("/tmp/nonexistent/SKILL.md"))
    assert result == 1


@pytest.mark.unit
def test_update_skill_md_no_table_marker():
    """update_skill_md should return 1 if no table marker found."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# SKILL.md\n\n## Tools (0)\n\nNo table here.\n")
        f.flush()
        result = update_skill_md(Path(f.name))
        assert result == 1
    Path(f.name).unlink(missing_ok=True)
