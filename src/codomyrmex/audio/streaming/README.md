# Audio Streaming

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

**Module**: `codomyrmex.audio.streaming` | **Status**: Active

## Overview

Real-time audio streaming subsystem for bi-directional WebSocket audio transcription. Provides server/client architecture with codec negotiation, session management, and Voice Activity Detection integration.

## Key Exports

- **`AudioStreamServer`** — WebSocket server for audio chunk processing and transcription.
- **`AudioStreamClient`** — Client for sending audio and receiving transcription events.
- **`CodecNegotiator`** — Audio format negotiation between client/server.
- **`AudioCodec`** — Supported codecs: PCM, WAV, OPUS, MP3, OGG_VORBIS, FLAC.
- **`CodecCapabilities`** — Client/server codec capability description.
- **`NegotiationResult`** — Result of codec negotiation.
- **`AudioChunk`** — A chunk of audio data with sequencing and timestamps.
- **`StreamConfig`** — Streaming session configuration.
- **`TranscriptionEvent`** — Real-time transcription result.

## Quick Start

```python
from codomyrmex.audio.streaming import (
    AudioStreamServer, AudioStreamClient, StreamConfig, AudioChunk
)

server = AudioStreamServer(StreamConfig(port=8891))
chunk = AudioChunk(data=b"\x00" * 100, sequence=0)
event = server.process_chunk(chunk, session_id="demo")
```

## Navigation

- **📁 Parent**: [Audio](../README.md)
- **🏠 Root**: [codomyrmex](../../../../README.md)
