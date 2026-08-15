"""Lifecycle checks for the optional Edge TTS transport."""

import socket

import pytest

from codomyrmex.audio.text_to_speech.providers import EDGE_TTS_AVAILABLE
from codomyrmex.audio.text_to_speech.providers.edge_tts_provider import (
    EdgeTTSProvider,
)

pytestmark = pytest.mark.skipif(
    not EDGE_TTS_AVAILABLE,
    reason="edge-tts is not installed",
)


class TestEdgeTTSConnectorLifecycle:
    """Ensure the provider owns and closes its network connector."""

    @pytest.mark.asyncio
    async def test_connector_is_ipv4_only(self) -> None:
        connector = EdgeTTSProvider._new_http_connector()
        try:
            assert connector._family == socket.AF_INET
        finally:
            await EdgeTTSProvider._close_http_connector(connector)

    @pytest.mark.asyncio
    async def test_connector_close_is_awaited(self) -> None:
        connector = EdgeTTSProvider._new_http_connector()

        await EdgeTTSProvider._close_http_connector(connector)

        assert connector.closed
