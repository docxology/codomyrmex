import importlib
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.health_checker import SystemHealthChecker


def test_check_core_dependencies_all_pass(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """All mapped dependencies report OK when every import succeeds."""
    import types

    checker = SystemHealthChecker(
        project_root=Path("/fake/root"),
        src_path=Path("/fake/root/src"),
        testing_path=Path("/fake/root/tests"),
    )

    from codomyrmex.system_discovery.core.health_checker import _DEP_MAPPING

    # Force every mapped dependency to import successfully so the test is
    # independent of which optional extras the local environment installs.
    stub = types.ModuleType("stub")
    monkeypatch.setattr(importlib, "import_module", lambda name, package=None: stub)

    checker.check_core_dependencies()
    captured = capsys.readouterr()

    assert "Core Dependencies:" in captured.out

    for dep in _DEP_MAPPING:
        assert f"   OK {dep}" in captured.out
        assert f"   MISSING {dep}" not in captured.out


def test_check_core_dependencies_some_missing(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test check_core_dependencies when some dependencies raise ImportError."""
    checker = SystemHealthChecker(
        project_root=Path("/fake/root"),
        src_path=Path("/fake/root/src"),
        testing_path=Path("/fake/root/tests"),
    )

    import types

    # Mock importlib.import_module: openai/matplotlib fail; everything else
    # succeeds deterministically regardless of local extras.
    stub = types.ModuleType("stub")

    def mock_import_module(name, package=None):
        if name in ("openai", "matplotlib"):
            raise ImportError(f"No module named '{name}'")
        return stub

    monkeypatch.setattr(importlib, "import_module", mock_import_module)

    checker.check_core_dependencies()
    captured = capsys.readouterr()

    assert "Core Dependencies:" in captured.out

    from codomyrmex.system_discovery.core.health_checker import _DEP_MAPPING

    expected_deps_ok = [
        dep for dep in _DEP_MAPPING if dep not in ("openai", "matplotlib")
    ]
    expected_deps_missing = ["openai", "matplotlib"]

    for dep in expected_deps_ok:
        assert f"   OK {dep}" in captured.out
        assert f"   MISSING {dep}" not in captured.out

    for dep in expected_deps_missing:
        assert f"   MISSING {dep}" in captured.out
        assert f"   OK {dep}" not in captured.out
