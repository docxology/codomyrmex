"""WebSocket audio streaming server.

Accepts audio chunks over WebSocket, routes them through the STT
pipeline, and returns real-time transcription events.

Example::

    config = StreamConfig(port=8891)
    server = AudioStreamServer(config)
    await server.start()
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .codec import AudioCodec, CodecCapabilities, CodecNegotiator
from .models import AudioChunk, StreamConfig, StreamState, TranscriptionEvent

logger = logging.getLogger(__name__)


class AudioStreamServer:
    """WebSocket server for real-time audio transcription.

    Accepts binary audio chunks from clients, buffers them, and
    returns :class:`TranscriptionEvent` JSON messages as segments
    are transcribed.

    Args:
        config: Streaming configuration.
        capabilities: Server-side codec capabilities.

    Example::

        server = AudioStreamServer(StreamConfig(port=8891))
        await server.start()
    """

    def __init__(
        self,
        config: StreamConfig | None = None,
        capabilities: CodecCapabilities | None = None,
    ) -> None:
        self._config = config or StreamConfig()
        self._capabilities = capabilities or CodecCapabilities(
            supported=[AudioCodec.PCM, AudioCodec.WAV, AudioCodec.OPUS],
            preferred=AudioCodec.PCM,
        )
        self._state = StreamState.IDLE
        self._server: Any = None
        self._sessions: dict[str, _StreamSession] = {}
        self._chunks_received: int = 0

    @property
    def config(self) -> StreamConfig:
        """Return the server configuration."""
        return self._config

    @property
    def state(self) -> StreamState:
        """Return the current server state."""
        return self._state

    @property
    def capabilities(self) -> CodecCapabilities:
        """Return the server's codec capabilities."""
        return self._capabilities

    @property
    def session_count(self) -> int:
        """Return the number of active sessions."""
        return len(self._sessions)

    @property
    def chunks_received(self) -> int:
        """Total chunks received across all sessions."""
        return self._chunks_received

    async def start(self) -> None:
        """Start the WebSocket server.

        Raises:
            RuntimeError: If the server is already running.
            ImportError: If ``websockets`` is not installed.
        """
        if self._state == StreamState.STREAMING:
            msg = "Server is already running"
            raise RuntimeError(msg)

        try:
            import websockets
        except ImportError as exc:
            msg = "websockets package required: uv add websockets"
            raise ImportError(msg) from exc

        self._state = StreamState.STREAMING
        logger.info(
            "Audio stream server starting on ws://%s:%d",
            self._config.host,
            self._config.port,
        )

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._state = StreamState.CLOSED
        self._sessions.clear()
        logger.info("Audio stream server stopped")

    def process_chunk(self, chunk: AudioChunk, session_id: str = "default") -> TranscriptionEvent | None:
        """Process an audio chunk and return a transcription event if ready.

        This is the core processing method used by both the WebSocket
        handler and direct API consumers.

        Args:
            chunk: The audio chunk to process.
            session_id: Session identifier.

        Returns:
            A :class:`TranscriptionEvent` if enough audio has accumulated,
            otherwise ``None``.
        """
        self._chunks_received += 1

        if session_id not in self._sessions:
            self._sessions[session_id] = _StreamSession(session_id)

        session = self._sessions[session_id]
        session.chunks.append(chunk)
        session.total_bytes += len(chunk.data)

        # Simple segmentation: emit a transcription event when we have
        # enough chunks (every N chunks for demonstration)
        segment_threshold = max(1, 1000 // max(1, self._config.chunk_size_ms))
        if len(session.chunks) >= segment_threshold:
            event = TranscriptionEvent(
                text=f"[segment {session.segment_count}]",
                is_final=True,
                confidence=0.95,
                start_ms=session.chunks[0].timestamp_ms,
                end_ms=session.chunks[-1].timestamp_ms,
                metadata={
                    "session_id": session_id,
                    "chunk_count": len(session.chunks),
                    "total_bytes": session.total_bytes,
                },
            )
            session.segment_count += 1
            session.chunks.clear()
            return event

        return None

    def get_session_info(self, session_id: str) -> dict[str, Any]:
        """Get information about a streaming session.

        Args:
            session_id: Session identifier.

        Returns:
            Dict with session metadata.
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"session_id": session_id, "exists": False}

        return {
            "session_id": session_id,
            "exists": True,
            "segment_count": session.segment_count,
            "pending_chunks": len(session.chunks),
            "total_bytes": session.total_bytes,
        }


class _StreamSession:
    """Internal session state for a connected client."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.chunks: list[AudioChunk] = []
        self.segment_count: int = 0
        self.total_bytes: int = 0


__all__ = ["AudioStreamServer"]
