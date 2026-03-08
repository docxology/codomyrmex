# Audio Streaming — Agentic Guide

**Module**: `codomyrmex.audio.streaming` | **Version**: v1.1.9

## Quick Reference

```python
from codomyrmex.audio.streaming import AudioStreamServer, AudioStreamClient, StreamConfig
```

## Agent Instructions

1. **Server**: Use `AudioStreamServer.process_chunk()` for direct chunk processing
2. **Client**: Call `connect()` before `send_chunk()`; catch `RuntimeError` if not connected
3. **Codec**: `CodecNegotiator.negotiate()` returns `NegotiationResult` with `success` flag
4. **Sessions**: Server tracks independent sessions by `session_id`
5. **VAD**: Use `audio.speech_to_text.vad.VoiceActivityDetector` for pre-filtering chunks

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/test_audio_streaming.py -v --no-cov
```
