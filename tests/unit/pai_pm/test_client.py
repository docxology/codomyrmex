"""Tests for PaiPmClient — always-running subset (no server required)."""

from __future__ import annotations

import pytest

from codomyrmex.pai_pm.client import PaiPmClient
from codomyrmex.pai_pm.exceptions import PaiPmConnectionError


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmClientInstantiation:
    def test_instantiates_with_defaults(self) -> None:
        client = PaiPmClient()
        assert client is not None

    def test_instantiates_with_custom_url(self) -> None:
        client = PaiPmClient(base_url="http://127.0.0.1:19997")
        assert client._base_url == "http://127.0.0.1:19997"

    def test_trailing_slash_stripped(self) -> None:
        client = PaiPmClient(base_url="http://127.0.0.1:19997/")
        assert not client._base_url.endswith("/")

    def test_custom_timeout_stored(self) -> None:
        client = PaiPmClient(timeout=99)
        assert client._timeout == 99


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmClientConnectionError:
    """health() must raise PaiPmConnectionError when server is not running."""

    def test_health_raises_on_unreachable_port(self) -> None:
        client = PaiPmClient(base_url="http://127.0.0.1:19997", timeout=2)
        with pytest.raises(PaiPmConnectionError):
            client.health()

    def test_get_state_raises_on_unreachable_port(self) -> None:
        client = PaiPmClient(base_url="http://127.0.0.1:19997", timeout=2)
        with pytest.raises(PaiPmConnectionError):
            client.get_state()

    def test_list_missions_raises_on_unreachable_port(self) -> None:
        client = PaiPmClient(base_url="http://127.0.0.1:19997", timeout=2)
        with pytest.raises(PaiPmConnectionError):
            client.list_missions()
