"""Tests for pai_pm exception hierarchy."""

from __future__ import annotations

import pytest

from codomyrmex.pai_pm.exceptions import (
    PaiPmConnectionError,
    PaiPmError,
    PaiPmNotInstalledError,
    PaiPmServerError,
    PaiPmTimeoutError,
)


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmExceptionHierarchy:
    def test_base_is_exception(self) -> None:
        assert issubclass(PaiPmError, Exception)

    def test_not_installed_inherits_base(self) -> None:
        assert issubclass(PaiPmNotInstalledError, PaiPmError)

    def test_server_error_inherits_base(self) -> None:
        assert issubclass(PaiPmServerError, PaiPmError)

    def test_timeout_inherits_base(self) -> None:
        assert issubclass(PaiPmTimeoutError, PaiPmError)

    def test_connection_inherits_base(self) -> None:
        assert issubclass(PaiPmConnectionError, PaiPmError)

    def test_can_raise_and_catch_base(self) -> None:
        with pytest.raises(PaiPmError):
            raise PaiPmNotInstalledError("bun not found")

    def test_not_installed_message_preserved(self) -> None:
        exc = PaiPmNotInstalledError("bun not found")
        assert "bun not found" in str(exc)

    def test_connection_error_is_not_timeout(self) -> None:
        assert not issubclass(PaiPmConnectionError, PaiPmTimeoutError)

    def test_timeout_error_is_not_connection(self) -> None:
        assert not issubclass(PaiPmTimeoutError, PaiPmConnectionError)
