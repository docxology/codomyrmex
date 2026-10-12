# Speech To Text — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.audio.speech_to_text`
**Status**: Active

## 1. Overview

Speech-to-text (STT) transcription module.

## 2. Architecture

### Components

| Component | Type | Description |
| ----------- | ------ | ------------- |
| `WhisperModelSize` | Class | Available Whisper model sizes. |
| `Transcriber` | Class | High-level transcription interface; accepts `WhisperModelSize` values or their string values. |
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
uv run python -m pytest tests/ -k speech_to_text -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Audio](../SPEC.md)

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)

## Input preflight

`validation.validate_audio_path(path)` requires an existing regular file with a
supported audio suffix and returns its `Path`. Missing/nonfile inputs raise
`TranscriptionError`; unsupported suffixes raise `AudioFormatError`. The helper
uses only filesystem metadata and acquires no model/native resources. Whisper
provider validation delegates to it. MCP transcription and language detection
perform this check before constructing the eager-loading `Transcriber`.
