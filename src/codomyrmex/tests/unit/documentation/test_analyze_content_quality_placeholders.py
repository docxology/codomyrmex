"""Unit tests for scripts/documentation/analyze_content_quality placeholder logic."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(scope="module")
def analyze_module():
    script = REPO_ROOT / "scripts" / "documentation" / "analyze_content_quality.py"
    assert script.is_file(), f"missing {script}"
    spec = importlib.util.spec_from_file_location(
        "analyze_content_quality", script
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_count_placeholder_signals_ignores_prose_todo(analyze_module) -> None:
    text = "Record outcomes and update TODO queues when necessary.\n"
    assert analyze_module.count_placeholder_signals(text) == 0


@pytest.mark.unit
def test_count_placeholder_signals_counts_task_todo(analyze_module) -> None:
    assert analyze_module.count_placeholder_signals("TODO: wire auth\n") == 1
    assert analyze_module.count_placeholder_signals("- TODO: item\n") == 1
    assert analyze_module.count_placeholder_signals("<!-- TODO: fix -->\n") == 1


@pytest.mark.unit
def test_count_placeholder_signals_ignores_example_com(analyze_module) -> None:
    text = "curl https://example.com/api/v1\n"
    assert analyze_module.count_placeholder_signals(text) == 0


@pytest.mark.unit
def test_count_placeholder_signals_bracket_tags(analyze_module) -> None:
    assert analyze_module.count_placeholder_signals("see [TBD] for now") == 1
    assert analyze_module.count_placeholder_signals("[WIP] section") == 1
