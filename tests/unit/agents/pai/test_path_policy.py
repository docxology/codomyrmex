"""MCP filesystem capability-root regression tests."""

import os

import pytest

from codomyrmex.agents.pai.mcp.path_policy import (
    PathPolicyError,
    guard_tool_arguments,
)


def test_relative_path_is_normalized_inside_current_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = guard_tool_arguments("codomyrmex.read_file", {"path": "nested.txt"})
    assert result["path"] == str(tmp_path / "nested.txt")


def test_path_outside_root_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(PathPolicyError, match="outside"):
        guard_tool_arguments("codomyrmex.read_file", {"path": os.devnull})


def test_explicit_additional_root_is_allowed(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    monkeypatch.setenv("CODOMYRMEX_MCP_ALLOWED_ROOTS", str(workspace))
    result = guard_tool_arguments("codomyrmex.list_directory", {"path": str(workspace)})
    assert result["path"] == str(workspace)


def test_workflow_project_root_is_guarded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(PathPolicyError, match="outside"):
        guard_tool_arguments("codomyrmex.list_workflows", {"project_root": os.devnull})


def test_non_path_tools_are_unchanged():
    arguments = {"module_name": "logging_monitoring"}
    assert guard_tool_arguments("codomyrmex.module_info", arguments) == arguments


@pytest.mark.parametrize(
    ("tool_name", "field"),
    [
        ("codomyrmex.document_read", "path"),
        ("codomyrmex.generate_chart", "output_path"),
        ("codomyrmex.export_dashboard", "output_dir"),
    ],
)
def test_dynamic_path_like_arguments_are_guarded(tool_name, field, tmp_path):
    with pytest.raises(PathPolicyError, match="outside"):
        guard_tool_arguments(tool_name, {field: os.devnull})


def test_path_lists_are_normalized(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = guard_tool_arguments(
        "codomyrmex.document_search", {"files": ["one.md", "two.md"]}
    )
    assert result["files"] == [str(tmp_path / "one.md"), str(tmp_path / "two.md")]
