"""Tests for openfang exception hierarchy — zero-mock, real objects only."""

import pytest

from codomyrmex.agents.openfang.exceptions import (
    OpenFangBuildError,
    OpenFangConfigError,
    OpenFangError,
    OpenFangNotInstalledError,
    OpenFangTimeoutError,
)


class TestExceptionHierarchy:
    def test_openfang_error_is_exception(self):
        assert issubclass(OpenFangError, Exception)

    def test_not_installed_is_openfang_error(self):
        assert issubclass(OpenFangNotInstalledError, OpenFangError)

    def test_timeout_is_openfang_error(self):
        assert issubclass(OpenFangTimeoutError, OpenFangError)

    def test_build_error_is_openfang_error(self):
        assert issubclass(OpenFangBuildError, OpenFangError)

    def test_config_error_is_openfang_error(self):
        assert issubclass(OpenFangConfigError, OpenFangError)

    def test_all_are_distinct_classes(self):
        classes = [
            OpenFangError,
            OpenFangNotInstalledError,
            OpenFangTimeoutError,
            OpenFangBuildError,
            OpenFangConfigError,
        ]
        assert len(set(classes)) == 5


class TestExceptionMessages:
    def test_openfang_error_preserves_message(self):
        exc = OpenFangError("test message")
        assert str(exc) == "test message"

    def test_not_installed_preserves_message(self):
        exc = OpenFangNotInstalledError("binary not found")
        assert "binary not found" in str(exc)

    def test_timeout_preserves_message(self):
        exc = OpenFangTimeoutError("timed out after 120s")
        assert "120s" in str(exc)

    def test_build_error_preserves_message(self):
        exc = OpenFangBuildError("cargo build failed")
        assert "cargo" in str(exc)

    def test_config_error_preserves_message(self):
        exc = OpenFangConfigError("invalid config")
        assert "invalid" in str(exc)

    def test_empty_message(self):
        exc = OpenFangError("")
        assert str(exc) == ""

    def test_multiline_message(self):
        msg = "line1\nline2"
        exc = OpenFangError(msg)
        assert str(exc) == msg


class TestExceptionRaiseAndCatch:
    def test_raise_and_catch_by_base(self):
        with pytest.raises(OpenFangError):
            raise OpenFangNotInstalledError("not installed")

    def test_raise_and_catch_specific(self):
        with pytest.raises(OpenFangNotInstalledError):
            raise OpenFangNotInstalledError("not installed")

    def test_timeout_caught_by_base(self):
        with pytest.raises(OpenFangError):
            raise OpenFangTimeoutError("timeout")

    def test_build_error_caught_by_base(self):
        with pytest.raises(OpenFangError):
            raise OpenFangBuildError("build failed")

    def test_config_error_caught_by_base(self):
        with pytest.raises(OpenFangError):
            raise OpenFangConfigError("bad config")

    def test_exception_chaining(self):
        original = ValueError("root cause")
        try:
            raise OpenFangBuildError("wrapped") from original
        except OpenFangBuildError as exc:
            assert exc.__cause__ is original
