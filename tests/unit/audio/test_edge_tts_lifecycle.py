"""Lifecycle checks for the optional Edge TTS transport."""

import socket
from pathlib import Path

import pytest

from codomyrmex.audio.exceptions import SynthesisError
from codomyrmex.audio.text_to_speech.models import TTSConfig
from codomyrmex.audio.text_to_speech.providers import EDGE_TTS_AVAILABLE
from codomyrmex.audio.text_to_speech.providers.edge_tts_provider import (
    EdgeTTSProvider,
)

pytestmark = pytest.mark.skipif(
    not EDGE_TTS_AVAILABLE,
    reason="edge-tts is not installed",
)


class TestEdgeTTSConnectorLifecycle:
    """Voice-list connectors are explicit; stream sessions own theirs."""

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

    @pytest.mark.asyncio
    async def test_synthesis_sessions_have_independent_connector_lifetimes(
        self,
    ) -> None:
        """Real library configuration allows later sessions after one closes."""
        import aiohttp

        communicate = EdgeTTSProvider._new_communicate(
            "A sentence. " * 1000, "en-US-AriaNeural", TTSConfig()
        )
        assert len(list(communicate.texts)) > 1
        assert communicate.connector is None
        assert communicate.session_timeout.sock_connect == 10
        assert communicate.session_timeout.sock_read == 60
        connectors = []
        # The installed Edge implementation opens a ClientSession for each
        # chunk/403 recovery. Exercise those actual ownership semantics without
        # replacing methods or depending on Microsoft's remote availability.
        for _ in range(2):
            async with aiohttp.ClientSession(
                connector=communicate.connector, timeout=communicate.session_timeout
            ) as session:
                connector = session.connector
                assert connector is not None
                assert not connector.closed
                connectors.append(connector)
            assert connector.closed
        assert connectors[0] is not connectors[1]

    @pytest.mark.parametrize(
        ("config", "rate", "pitch", "volume"),
        [
            (TTSConfig(), "+0%", "+0Hz", "+0%"),
            (TTSConfig(rate=1.5, pitch=1.5, volume=0.5), "+50%", "+25Hz", "-50%"),
            (TTSConfig(rate=0.5, pitch=0.5, volume=0.0), "-50%", "-25Hz", "-100%"),
        ],
    )
    def test_shared_constructor_honors_supported_prosody(
        self, config: TTSConfig, rate: str, pitch: str, volume: str
    ) -> None:
        """The real Edge request configuration honors every supported knob."""
        communicate = EdgeTTSProvider._new_communicate(
            "Configuration test", "en-US-AriaNeural", config
        )
        assert communicate.tts_config.rate == rate
        assert communicate.tts_config.pitch == pitch
        assert communicate.tts_config.volume == volume
        assert communicate.connector is None

    @pytest.mark.parametrize("volume", [-0.1, 1.1, float("nan"), float("inf")])
    def test_invalid_volume_is_rejected_without_remote_request(
        self, volume: float
    ) -> None:
        with pytest.raises(SynthesisError, match="volume"):
            EdgeTTSProvider._new_communicate(
                "Configuration test", "en-US-AriaNeural", TTSConfig(volume=volume)
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("text", ["", " \n\t"])
    async def test_empty_direct_file_synthesis_acquires_no_output(
        self, text: str, tmp_path: Path
    ) -> None:
        """Invalid text fails before the actual library can create an empty file."""
        output = tmp_path / "speech.mp3"
        provider = EdgeTTSProvider()
        with pytest.raises(SynthesisError, match="empty text"):
            await provider.synthesize_to_file_async(text, output)
        assert not output.exists()
        assert not provider._voices_loaded

    @pytest.mark.parametrize("rate", [0.0, float("nan"), 1e308, 10**1000])
    def test_unrepresentable_prosody_fails_as_synthesis_error(
        self, rate: float
    ) -> None:
        with pytest.raises(SynthesisError):
            EdgeTTSProvider._new_communicate(
                "Configuration test", "en-US-AriaNeural", TTSConfig(rate=rate)
            )
