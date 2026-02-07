# Speech To Text — Functional Specification

**Module**: `codomyrmex.audio.speech_to_text`
**Status**: Active

## 1. Overview

Speech-to-text (STT) transcription module.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `WhisperModelSize` | Class | Available Whisper model sizes. |
| `Word` | Class | A single word with timing information. |
| `Segment` | Class | A transcription segment (typically a sentence or phrase). |
| `TranscriptionResult` | Class | Complete transcription result. |
| `TranscriptionConfig` | Class | Configuration for transcription operations. |

## 3. API Usage

```python
from codomyrmex.audio.speech_to_text import WhisperModelSize
```

## 4. Dependencies

See `src/codomyrmex/audio/speech_to_text/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k speech_to_text -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Audio](../SPEC.md)
