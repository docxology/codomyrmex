"""WebSocket audio streaming client.

Connects to an :class:`AudioStreamServer`, sends audio chunks,
and receives transcription events.

Example::

    client = AudioStreamClient(StreamConfig())
    await client.connect()
    event = client.send_chunk(AudioChunk(data=b"..."))
"""

from __future__ import annotations

import logging
from pathlib import Path

from .codec import AudioCodec, CodecCapabilities, CodecNegotiator, NegotiationResult
from .models import AudioChunk, StreamConfig, StreamState, TranscriptionEvent

logger = logging.getLogger(__name__)


class AudioStreamClient:
    """Client for streaming audio to an :class:`AudioStreamServer`.

    Args:
        config: Streaming configuration.
        capabilities: Client-side codec capabilities.

    Example::

        client = AudioStreamClient(StreamConfig())
        await client.connect()
        for chunk in audio_chunks:
            event = client.send_chunk(chunk)
            if event:
                print(event.text)
    """

    def __init__(
        self,
        config: StreamConfig | None = None,
        capabilities: CodecCapabilities | None = None,
    ) -> None:
        self._config = config or StreamConfig()
        self._capabilities = capabilities or CodecCapabilities(
            supported=[AudioCodec.PCM, AudioCodec.WAV, AudioCodec.OPUS],
            preferred=AudioCodec.OPUS,
        )
        self._state = StreamState.IDLE
        self._negotiation: NegotiationResult | None = None
        self._chunks_sent: int = 0
        self._events_received: list[TranscriptionEvent] = []

    @property
    def config(self) -> StreamConfig:
        """Return the client configuration."""
        return self._config

    @property
    def state(self) -> StreamState:
        """Return the current client state."""
        return self._state

    @property
    def capabilities(self) -> CodecCapabilities:
        """Return the client's codec capabilities."""
        return self._capabilities

    @property
    def negotiation(self) -> NegotiationResult | None:
        """Return the codec negotiation result."""
        return self._negotiation

    @property
    def chunks_sent(self) -> int:
        """Total chunks sent."""
        return self._chunks_sent

    @property
    def events_received(self) -> list[TranscriptionEvent]:
        """All transcription events received."""
        return list(self._events_received)

    async def connect(
        self, server_capabilities: CodecCapabilities | None = None
    ) -> NegotiationResult:
        """Connect to the streaming server and negotiate codec.

        Args:
            server_capabilities: Server capabilities for negotiation.

        Returns:
            The :class:`NegotiationResult`.

        Raises:
            RuntimeError: If already connected.
        """
        if self._state == StreamState.STREAMING:
            msg = "Already connected"
            raise RuntimeError(msg)

        server_caps = server_capabilities or CodecCapabilities()
        self._negotiation = CodecNegotiator.negotiate(self._capabilities, server_caps)
        self._state = StreamState.STREAMING

        logger.info(
            "Connected: %s at %dHz",
            self._negotiation.codec.value,
            self._negotiation.sample_rate,
        )
        return self._negotiation

    def send_chunk(self, chunk: AudioChunk) -> None:
        """Send an audio chunk to the server.

        Args:
            chunk: The audio chunk to send.

        Raises:
            RuntimeError: If not connected.
        """
        if self._state != StreamState.STREAMING:
            msg = "Client is not connected"
            raise RuntimeError(msg)

        self._chunks_sent += 1
        logger.debug("Sent chunk #%d (%d bytes)", self._chunks_sent, len(chunk.data))

    def receive_event(self, event: TranscriptionEvent) -> None:
        """Process a received transcription event.

        Args:
            event: The transcription event.
        """
        self._events_received.append(event)
        logger.debug("Received event: %s (final=%s)", event.text[:50], event.is_final)

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        self._state = StreamState.CLOSED
        logger.info(
            "Disconnected after %d chunks, %d events",
            self._chunks_sent,
            len(self._events_received),
        )

    def chunks_from_file(
        self,
        file_path: str | Path,
        chunk_size: int = 4096,
    ) -> list[AudioChunk]:
        """Read an audio file and split it into chunks.

        Args:
            file_path: Path to the audio file.
            chunk_size: Size of each chunk in bytes.

        Returns:
            List of :class:`AudioChunk` objects.
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"Audio file not found: {path}"
            raise FileNotFoundError(msg)

        data = path.read_bytes()
        chunks: list[AudioChunk] = []
        for i in range(0, len(data), chunk_size):
            chunk_data = data[i : i + chunk_size]
            chunks.append(
                AudioChunk(
                    data=chunk_data,
                    sequence=len(chunks),
                    timestamp_ms=len(chunks) * (self._config.chunk_size_ms),
                )
            )
        return chunks


__all__ = ["AudioStreamClient"]
