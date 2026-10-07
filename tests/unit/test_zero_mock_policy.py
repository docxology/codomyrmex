"""Repository-wide guard for the zero-mock testing policy.

docs/development/testing-strategy.md ("Zero-Mock Policy (clarified)") forbids
unittest.mock / pytest-mock and replacing behaviour with
``monkeypatch.setattr``; test doubles must be named ``Fake*``. The document
said CI greps for forbidden imports, but no workflow did. This module is that
check:

* unittest.mock, pytest_mock and the ``mocker`` fixture are rejected outright;
* ``monkeypatch.setattr`` calls and hand-rolled ``Mock*`` classes are held to
  the per-file counts that existed when this guard was added (a ratchet): a
  file may never rise above its baseline and files not listed may not use them
  at all. Prefer ``setenv``/``delenv``/``chdir``/``tmp_path`` or a real
  implementation, and lower the baseline in the same change that removes a use
  (``test_baselines_have_no_slack`` enforces this).
"""

from __future__ import annotations

import ast
import functools

import pytest
from tests.support.repo_paths import REPO_ROOT

TESTS = REPO_ROOT / "tests"
FORBIDDEN_MODULES = ("unittest.mock", "pytest_mock", "mock")

# Per-file baselines (relative to the repository root) when the guard landed.
MONKEYPATCH_SETATTR_BASELINE: dict[str, int] = {
    "tests/integration/calendar_integration/test_mcp_tools.py": 1,
    "tests/integration/hermes/test_gateway_context_summarization.py": 1,
    "tests/integration/hermes/test_gateway_coverage_loop.py": 6,
    "tests/integration/hermes/test_gateway_delegation.py": 1,
    "tests/integration/hermes/test_gateway_interactive_scaffolding.py": 1,
    "tests/integration/hermes/test_gateway_mcp_new_tools.py": 8,
    "tests/integration/hermes/test_gateway_resource_monitoring.py": 1,
    "tests/integration/hermes/test_gateway_task_scheduler.py": 2,
    "tests/integration/hermes/test_gateway_unified_traceability.py": 1,
    "tests/integration/hermes/test_gateway_workflow_loop.py": 1,
    "tests/integration/hermes/test_rotation.py": 3,
    "tests/unit/agentic_memory/test_cognilayer_bridge.py": 6,
    "tests/unit/agents/hermes/test_mcp_tools.py": 6,
    "tests/unit/agents/hermes/test_new_client_methods.py": 3,
    "tests/unit/agents/hermes/test_provider_router.py": 2,
    "tests/unit/agents/pai/test_pai_webhook_hardening.py": 1,
    "tests/unit/agents/test_hermes_client_execution.py": 2,
    "tests/unit/agents/test_mission_control_client.py": 1,
    "tests/unit/calendar_integration/test_mcp_tools.py": 2,
    "tests/unit/cloud/test_mcp_tools.py": 9,
    "tests/unit/colony_kernel/test_mcp_tools.py": 1,
    "tests/unit/hermes/test_hermes_client.py": 2,
    "tests/unit/hermes/test_hermes_mcp_tools_extended.py": 9,
    "tests/unit/manuscript/test_figures.py": 4,
    "tests/unit/scrape/test_scrape_core.py": 1,
    "tests/unit/skills/test_hermes_skill_bridge.py": 1,
    "tests/unit/system_discovery/test_health_checker_missing_deps.py": 2,
    "tests/unit/system_discovery/test_profilers.py": 16,
    "tests/unit/templating/test_init.py": 1,
    "tests/unit/test_conftest.py": 4,
}

MOCK_CLASS_BASELINE: dict[str, int] = {
    "tests/integration/hermes/test_gateway_automated_healing.py": 1,
    "tests/integration/hermes/test_gateway_interactive_scaffolding.py": 1,
    "tests/unit/agents/hermes/test_provider_router.py": 1,
    "tests/unit/agents/pooling/test_pooling.py": 1,
    "tests/unit/agents/test_agent_lifecycle_zeromock.py": 1,
    "tests/unit/agents/test_orchestration.py": 1,
    "tests/unit/cloud/test_mcp_tools.py": 10,
    "tests/unit/containerization/test_containerization.py": 1,
    "tests/unit/plugin_system/test_plugin_registry.py": 1,
    "tests/unit/streaming/test_streaming_async.py": 3,
}


def _test_modules() -> list[tuple[str, ast.Module]]:
    modules = []
    for path in sorted(TESTS.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        modules.append((path.relative_to(REPO_ROOT).as_posix(), tree))
    return modules


def _is_forbidden(module: str) -> bool:
    return any(
        module == name or module.startswith(name + ".") for name in FORBIDDEN_MODULES
    )


def _count(tree: ast.Module) -> tuple[int, int, list[str]]:
    setattr_calls = mock_classes = 0
    forbidden: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            forbidden += [a.name for a in node.names if _is_forbidden(a.name)]
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and _is_forbidden(node.module)
        ):
            forbidden.append(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(arg.arg == "mocker" for arg in node.args.args):
                forbidden.append(f"mocker fixture in {node.name}()")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "setattr"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "monkeypatch"
        ):
            setattr_calls += 1
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Mock"):
            mock_classes += 1
    return setattr_calls, mock_classes, forbidden


@functools.cache
def _counts() -> dict[str, tuple[int, int, list[str]]]:
    # Parsed lazily (not at import) so xdist workers that never run these
    # tests do not pay for parsing the whole test tree during collection.
    return {path: _count(tree) for path, tree in _test_modules()}


@pytest.mark.unit
def test_test_tree_is_scanned() -> None:
    assert len(_counts()) > 1000


@pytest.mark.unit
def test_no_mock_libraries() -> None:
    offenders = [
        f"{path}: {name}" for path, counts in _counts().items() for name in counts[2]
    ]
    assert not offenders, "mock libraries are not allowed:\n" + "\n".join(offenders)


@pytest.mark.unit
def test_monkeypatch_setattr_and_mock_classes_do_not_grow() -> None:
    grown = []
    for path, (setattr_calls, mock_classes, _) in _counts().items():
        allowed = MONKEYPATCH_SETATTR_BASELINE.get(path, 0)
        if setattr_calls > allowed:
            grown.append(
                f"{path}: monkeypatch.setattr x{setattr_calls} (baseline {allowed})"
            )
        allowed = MOCK_CLASS_BASELINE.get(path, 0)
        if mock_classes > allowed:
            grown.append(f"{path}: Mock* classes x{mock_classes} (baseline {allowed})")
    assert not grown, (
        "zero-mock policy: use setenv/delenv/chdir/tmp_path, a real "
        "implementation, or a documented Fake* double instead:\n" + "\n".join(grown)
    )


@pytest.mark.unit
def test_baselines_have_no_slack() -> None:
    """Baselines must equal current counts so removed uses cannot creep back."""
    counts = _counts()
    slack = []
    for name, baseline, index in (
        ("monkeypatch.setattr", MONKEYPATCH_SETATTR_BASELINE, 0),
        ("Mock* classes", MOCK_CLASS_BASELINE, 1),
    ):
        for path, allowed in baseline.items():
            current = counts[path][index] if path in counts else 0
            if current < allowed:
                slack.append(f"{path}: {name} x{current} (baseline {allowed})")
    assert not slack, (
        "lower (or delete) these baseline entries in "
        "tests/unit/test_zero_mock_policy.py:\n" + "\n".join(slack)
    )


@pytest.mark.unit
def test_detector_recognises_each_pattern() -> None:
    sample = ast.parse(
        "from unittest.mock import MagicMock\n"
        "import pytest_mock\n"
        "class MockClient: ...\n"
        "def test_x(monkeypatch, mocker):\n"
        "    monkeypatch.setattr(obj, 'run', lambda: 1)\n"
        "    monkeypatch.setenv('A', '1')\n"
    )
    setattr_calls, mock_classes, forbidden = _count(sample)
    assert (setattr_calls, mock_classes) == (1, 1)
    assert len(forbidden) == 3
