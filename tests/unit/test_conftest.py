"""Tests for the root conftest.py."""

import os
import sys
import sysconfig
from pathlib import Path

import pytest

from codomyrmex.conftest import pytest_configure


def test_pytest_configure_not_314(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test pytest_configure when Python version is < 3.14."""
    monkeypatch.setattr(sys, "version_info", (3, 13))
    monkeypatch.delenv("HYPOTHESIS_NO_NPY", raising=False)
    config = object()

    pytest_configure(config)

    assert os.environ.get("HYPOTHESIS_NO_NPY") == "1"


def test_pytest_configure_already_imported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test pytest_configure when compression is already imported."""
    monkeypatch.setattr(sys, "version_info", (3, 14))
    monkeypatch.setitem(sys.modules, "compression", "already_imported")  # type: ignore
    monkeypatch.delenv("HYPOTHESIS_NO_NPY", raising=False)
    config = object()

    pytest_configure(config)

    assert os.environ.get("HYPOTHESIS_NO_NPY") == "1"


def test_pytest_configure_314_not_imported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test pytest_configure when Python >= 3.14 and compression not imported."""
    monkeypatch.setattr(sys, "version_info", (3, 14))
    monkeypatch.delenv("HYPOTHESIS_NO_NPY", raising=False)

    # Store old to prevent leaking compression to other tests
    old_compression = sys.modules.get("compression")

    if "compression" in sys.modules:
        monkeypatch.delitem(sys.modules, "compression")

    # Create a dummy stdlib compression module
    stdlib_path = tmp_path / "stdlib"
    stdlib_path.mkdir()
    compression_dir = stdlib_path / "compression"
    compression_dir.mkdir()
    init_file = compression_dir / "__init__.py"
    init_file.write_text("dummy_attribute = 'success'\n")

    monkeypatch.setattr(sysconfig, "get_path", lambda name: str(stdlib_path))

    config = object()

    try:
        pytest_configure(config)

        assert os.environ.get("HYPOTHESIS_NO_NPY") == "1"
        assert "compression" in sys.modules
        assert getattr(sys.modules["compression"], "dummy_attribute", None) == "success"
    finally:
        # Cleanup sys.modules
        if "compression" in sys.modules:
            del sys.modules["compression"]
        if old_compression is not None:
            sys.modules["compression"] = old_compression
