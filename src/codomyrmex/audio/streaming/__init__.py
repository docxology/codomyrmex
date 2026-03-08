"""Audio streaming subpackage for real-time STT/TTS over WebSockets.

Provides:
- ``AudioStreamServer``: WebSocket server routing audio chunks to STT.
- ``AudioStreamClient``: Client for sending audio and receiving transcriptions.
- ``CodecNegotiator``: Audio format negotiation between client/server.
"""

from .client import AudioStreamClient
from .codec import AudioCodec, CodecCapabilities, CodecNegotiator, NegotiationResult
from .models import AudioChunk, StreamConfig, TranscriptionEvent
from .server import AudioStreamServer

__all__ = [
    "AudioChunk",
    "AudioCodec",
    "AudioStreamClient",
    "AudioStreamServer",
    "CodecCapabilities",
    "CodecNegotiator",
    "NegotiationResult",
    "StreamConfig",
    "TranscriptionEvent",
]
