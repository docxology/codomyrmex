"""Data models for the audio streaming subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StreamState(Enum):
    """State of a streaming session."""

    IDLE = "idle"
    CONNECTING = "connecting"
    STREAMING = "streaming"
    PAUSED = "paused"
    CLOSED = "closed"


@dataclass(frozen=True)
class StreamConfig:
    """Configuration for an audio streaming session.

    Attributes:
        host: WebSocket server hostname.
        port: WebSocket server port.
        sample_rate: Audio sample rate in Hz.
        channels: Number of audio channels.
        chunk_size_ms: Duration of each audio chunk in milliseconds.
        language: Language code for transcription (None = auto-detect).
        vad_enabled: Whether to enable Voice Activity Detection pre-filter.
    """

    host: str = "localhost"
    port: int = 8891
    sample_rate: int = 16000
    channels: int = 1
    chunk_size_ms: int = 100
    language: str | None = None
    vad_enabled: bool = True


@dataclass
class AudioChunk:
    """A chunk of audio data for streaming.

    Attributes:
        data: Raw audio bytes.
        sequence: Sequence number for ordering.
        timestamp_ms: Timestamp in milliseconds from stream start.
        is_speech: Whether VAD detected speech in this chunk.
        codec: Codec used for this chunk.
    """

    data: bytes
    sequence: int = 0
    timestamp_ms: float = 0.0
    is_speech: bool = True
    codec: str = "pcm"


@dataclass
class TranscriptionEvent:
    """A transcription result event from the streaming pipeline.

    Attributes:
        text: The transcribed text.
        is_final: Whether this is a final transcription (vs. partial).
        confidence: Transcription confidence score (0–1).
        start_ms: Start timestamp in the audio stream.
        end_ms: End timestamp in the audio stream.
        language: Detected language code.
        metadata: Additional metadata.
    """

    text: str
    is_final: bool = False
    confidence: float = 0.0
    start_ms: float = 0.0
    end_ms: float = 0.0
    language: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "AudioChunk",
    "StreamConfig",
    "StreamState",
    "TranscriptionEvent",
]
