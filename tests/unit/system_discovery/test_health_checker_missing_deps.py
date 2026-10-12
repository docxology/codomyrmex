"""Core dependency checks in SystemHealthChecker use the declared requirements.

The checker reads the core dependencies from the installed ``codomyrmex``
distribution's metadata and looks each one up as an installed distribution,
so these tests run against the real environment instead of a fixed list.
"""

import tomllib
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

from codomyrmex.system_discovery.core.health_checker import (
    SystemHealthChecker,
    core_requirements,
    installed_versions,
)

_MISSING = "codomyrmex-test-distribution-that-is-not-installed"


def _checker(tmp_path: Path) -> SystemHealthChecker:
    return SystemHealthChecker(
        project_root=tmp_path,
        src_path=tmp_path / "src",
        testing_path=tmp_path / "tests",
    )


def _declared_core_dependencies() -> list[str]:
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)["project"]["dependencies"]


@pytest.mark.unit
def test_core_requirements_match_pyproject() -> None:
    """The installed metadata lists exactly the [project.dependencies] entries."""
    declared = _declared_core_dependencies()
    names = core_requirements()
    assert len(names) == len(declared)
    for name, requirement in zip(names, declared, strict=True):
        assert requirement.lower().startswith(name.lower())
    assert "openai" not in names  # an optional extra, not a core dependency


@pytest.mark.unit
def test_installed_versions_reports_missing_distributions() -> None:
    versions = installed_versions(["pytest", _MISSING])
    assert versions["pytest"] == pytest.__version__
    assert versions[_MISSING] is None


@pytest.mark.unit
def test_check_core_dependencies_all_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every declared core dependency is installed in the test environment."""
    _checker(tmp_path).check_core_dependencies()
    out = capsys.readouterr().out

    assert "Core Dependencies:" in out
    assert "MISSING" not in out
    for dep in core_requirements():
        assert f"   OK {dep} " in out


@pytest.mark.unit
def test_check_core_dependencies_some_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A requirement that is not installed is reported as missing."""
    _checker(tmp_path).check_core_dependencies(["pytest", _MISSING])
    out = capsys.readouterr().out

    assert f"   OK pytest {pytest.__version__}" in out
    assert f"   MISSING {_MISSING}" in out
