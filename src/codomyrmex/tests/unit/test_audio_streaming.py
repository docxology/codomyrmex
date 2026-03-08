"""Tests for audio.streaming — server, client, codec negotiation.

Zero-Mock: All tests use real server/client objects with real
chunk processing and codec negotiation.
"""

from __future__ import annotations

import pytest

from codomyrmex.audio.streaming.client import AudioStreamClient
from codomyrmex.audio.streaming.codec import (
    AudioCodec,
    CodecCapabilities,
    CodecNegotiator,
)
from codomyrmex.audio.streaming.models import (
    AudioChunk,
    StreamConfig,
    StreamState,
    TranscriptionEvent,
)
from codomyrmex.audio.streaming.server import AudioStreamServer

# ── Codec negotiation ─────────────────────────────────────────────────


class TestCodecNegotiator:
    """Verify codec negotiation between client and server."""

    def test_common_codec_selected(self) -> None:
        client = CodecCapabilities(supported=[AudioCodec.OPUS, AudioCodec.WAV])
        server = CodecCapabilities(supported=[AudioCodec.WAV, AudioCodec.PCM])
        result = CodecNegotiator.negotiate(client, server)
        assert result.success is True
        assert result.codec == AudioCodec.WAV

    def test_preferred_codec_wins(self) -> None:
        client = CodecCapabilities(
            supported=[AudioCodec.OPUS, AudioCodec.WAV],
            preferred=AudioCodec.WAV,
        )
        server = CodecCapabilities(
            supported=[AudioCodec.OPUS, AudioCodec.WAV],
        )
        result = CodecNegotiator.negotiate(client, server)
        assert result.codec == AudioCodec.WAV

    def test_no_common_codec_fails(self) -> None:
        client = CodecCapabilities(supported=[AudioCodec.OPUS])
        server = CodecCapabilities(supported=[AudioCodec.MP3])
        result = CodecNegotiator.negotiate(client, server)
        assert result.success is False
        assert "No common codec" in result.reason

    def test_highest_sample_rate_chosen(self) -> None:
        client = CodecCapabilities(sample_rates=[16000, 44100, 48000])
        server = CodecCapabilities(sample_rates=[16000, 44100])
        result = CodecNegotiator.negotiate(client, server)
        assert result.sample_rate == 44100

    def test_highest_channel_count_chosen(self) -> None:
        client = CodecCapabilities(channels=[1, 2])
        server = CodecCapabilities(channels=[1])
        result = CodecNegotiator.negotiate(client, server)
        assert result.channels == 1

    def test_priority_order_when_no_preference(self) -> None:
        client = CodecCapabilities(
            supported=[AudioCodec.PCM, AudioCodec.OPUS, AudioCodec.WAV]
        )
        server = CodecCapabilities(
            supported=[AudioCodec.PCM, AudioCodec.OPUS, AudioCodec.WAV]
        )
        result = CodecNegotiator.negotiate(client, server)
        assert result.codec == AudioCodec.OPUS  # Highest priority


# ── Data models ───────────────────────────────────────────────────────


class TestStreamModels:
    """Verify data model construction."""

    def test_stream_config_defaults(self) -> None:
        cfg = StreamConfig()
        assert cfg.host == "localhost"
        assert cfg.port == 8891
        assert cfg.sample_rate == 16000

    def test_audio_chunk_properties(self) -> None:
        chunk = AudioChunk(data=b"\x00" * 100, sequence=1, timestamp_ms=50.0)
        assert len(chunk.data) == 100
        assert chunk.sequence == 1

    def test_transcription_event_properties(self) -> None:
        event = TranscriptionEvent(text="hello world", is_final=True, confidence=0.99)
        assert event.text == "hello world"
        assert event.is_final is True


# ── Server ────────────────────────────────────────────────────────────


class TestAudioStreamServer:
    """Verify server chunk processing and session management."""

    def test_initial_state(self) -> None:
        server = AudioStreamServer()
        assert server.state == StreamState.IDLE
        assert server.session_count == 0
        assert server.chunks_received == 0

    def test_process_chunk_creates_session(self) -> None:
        server = AudioStreamServer()
        chunk = AudioChunk(data=b"\x00" * 100)
        server.process_chunk(chunk, session_id="s1")
        assert server.session_count == 1
        assert server.chunks_received == 1

    def test_process_chunk_returns_event_after_threshold(self) -> None:
        config = StreamConfig(chunk_size_ms=1000)  # Threshold = 1
        server = AudioStreamServer(config=config)
        chunk = AudioChunk(data=b"\x00" * 100, timestamp_ms=0.0)
        event = server.process_chunk(chunk, session_id="s1")
        assert event is not None
        assert event.is_final is True

    def test_multiple_sessions_independent(self) -> None:
        server = AudioStreamServer()
        server.process_chunk(AudioChunk(data=b"\x00"), session_id="a")
        server.process_chunk(AudioChunk(data=b"\x00"), session_id="b")
        assert server.session_count == 2

    def test_get_session_info_existing(self) -> None:
        server = AudioStreamServer()
        server.process_chunk(AudioChunk(data=b"\x00" * 10), session_id="s1")
        info = server.get_session_info("s1")
        assert info["exists"] is True
        assert info["total_bytes"] == 10

    def test_get_session_info_nonexistent(self) -> None:
        server = AudioStreamServer()
        info = server.get_session_info("nope")
        assert info["exists"] is False


# ── Client ────────────────────────────────────────────────────────────


class TestAudioStreamClient:
    """Verify client connection, sending, and event receiving."""

    @pytest.mark.asyncio
    async def test_connect_negotiates_codec(self) -> None:
        client = AudioStreamClient()
        server_caps = CodecCapabilities(supported=[AudioCodec.PCM, AudioCodec.OPUS])
        result = await client.connect(server_capabilities=server_caps)
        assert result.success is True
        assert client.state == StreamState.STREAMING

    @pytest.mark.asyncio
    async def test_connect_twice_raises(self) -> None:
        client = AudioStreamClient()
        await client.connect()
        with pytest.raises(RuntimeError, match="Already connected"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_send_chunk_increments_counter(self) -> None:
        client = AudioStreamClient()
        await client.connect()
        client.send_chunk(AudioChunk(data=b"\x00" * 50))
        client.send_chunk(AudioChunk(data=b"\x00" * 50))
        assert client.chunks_sent == 2

    def test_send_chunk_without_connect_raises(self) -> None:
        client = AudioStreamClient()
        with pytest.raises(RuntimeError, match="not connected"):
            client.send_chunk(AudioChunk(data=b"\x00"))

    def test_receive_event_stored(self) -> None:
        client = AudioStreamClient()
        event = TranscriptionEvent(text="hello", is_final=True)
        client.receive_event(event)
        assert len(client.events_received) == 1
        assert client.events_received[0].text == "hello"

    @pytest.mark.asyncio
    async def test_disconnect(self) -> None:
        client = AudioStreamClient()
        await client.connect()
        await client.disconnect()
        assert client.state == StreamState.CLOSED
