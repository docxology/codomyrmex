# Text To Speech — Functional Specification

**Module**: `codomyrmex.audio.text_to_speech`
**Status**: Active

## 1. Overview

Text-to-speech (TTS) synthesis module.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `AudioFormat` | Class | Supported audio output formats. |
| `VoiceGender` | Class | Voice gender classification. |
| `VoiceInfo` | Class | Information about an available voice. |
| `SynthesisResult` | Class | Result of text-to-speech synthesis. |
| `TTSConfig` | Class | Configuration for text-to-speech synthesis. |

## 3. API Usage

```python
from codomyrmex.audio.text_to_speech import AudioFormat
```

## 4. Dependencies

See `src/codomyrmex/audio/text_to_speech/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k text_to_speech -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Audio](../SPEC.md)
