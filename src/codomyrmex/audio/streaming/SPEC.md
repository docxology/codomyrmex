# Audio Streaming Specification

**Version**: v1.1.9 | **Status**: Active

## Architecture

```
audio/streaming/
├── __init__.py   # Package exports
├── models.py     # StreamConfig, AudioChunk, TranscriptionEvent, StreamState
├── server.py     # AudioStreamServer — WebSocket server with session management
├── client.py     # AudioStreamClient — client with codec negotiation
└── codec.py      # CodecNegotiator — priority-based format negotiation
```

## Codec Negotiation

Priority order (highest quality → most compatible):

1. OPUS → 2. FLAC → 3. WAV → 4. OGG_VORBIS → 5. MP3 → 6. PCM

Selection strategy:

1. Prefer explicit client/server preferences if shared
2. Otherwise pick highest-priority common codec
3. Negotiate highest common sample rate and channel count

## Server Processing

- Maintains per-session state (`_StreamSession`)
- Segments audio based on `chunk_size_ms` threshold
- Returns `TranscriptionEvent` when segments complete
- Thread-safe session management

## Data Flow

```
Client → [AudioChunk] → Server.process_chunk() → [TranscriptionEvent] → Client
         codec.negotiate()
```

## Error Handling

- `RuntimeError` for server already running / client not connected
- `ImportError` for missing `websockets` dependency
- `FileNotFoundError` for missing audio files in `chunks_from_file()`
