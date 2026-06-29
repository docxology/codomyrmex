import importlib
from pathlib import Path

import pytest

from codomyrmex.system_discovery.core.health_checker import SystemHealthChecker


def test_check_core_dependencies_all_pass(capsys: pytest.CaptureFixture[str]) -> None:
    """Test check_core_dependencies when all core dependencies import successfully."""
    # We create a SystemHealthChecker instance
    checker = SystemHealthChecker(
        project_root=Path("/fake/root"),
        src_path=Path("/fake/root/src"),
        testing_path=Path("/fake/root/tests"),
    )

    # In our testing environment, all core dependencies are installed,
    # so they should all pass. We call the method and capture stdout.
    checker.check_core_dependencies()
    captured = capsys.readouterr()

    assert "Core Dependencies:" in captured.out

    expected_deps = [
        "python-dotenv",
        "cased-kit",
        "openai",
        "anthropic",
        "matplotlib",
        "numpy",
        "pytest",
        "fastapi",
    ]

    for dep in expected_deps:
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

    original_import_module = importlib.import_module

    # Mock importlib.import_module to simulate Missing deps
    def mock_import_module(name, package=None):
        if name in ("openai", "matplotlib"):
            raise ImportError(f"No module named '{name}'")
        return original_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", mock_import_module)

    checker.check_core_dependencies()
    captured = capsys.readouterr()

    assert "Core Dependencies:" in captured.out

    expected_deps_ok = [
        "python-dotenv",
        "cased-kit",
        "anthropic",
        "numpy",
        "pytest",
        "fastapi",
    ]
    expected_deps_missing = ["openai", "matplotlib"]

    for dep in expected_deps_ok:
        assert f"   OK {dep}" in captured.out
        assert f"   MISSING {dep}" not in captured.out

    for dep in expected_deps_missing:
        assert f"   MISSING {dep}" in captured.out
        assert f"   OK {dep}" not in captured.out
