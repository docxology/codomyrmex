# Audio -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Speech-to-Text
- The system shall support Whisper-based transcription via faster-whisper (CTranslate2 backend).
- The system shall support 99+ languages with automatic language detection.
- Transcription results shall include word-level timestamps and segment boundaries.
- The system shall support SRT and VTT subtitle export formats.
- Five model sizes shall be available: tiny, base, small, medium, large-v3.

### FR-2: Text-to-Speech
- The system shall support offline synthesis via pyttsx3 (SAPI5/NSSpeech/espeak).
- The system shall support neural TTS via Microsoft Edge TTS (300+ voices).
- Output formats shall include WAV (pyttsx3) and MP3 (Edge TTS).
- Voice listing and selection shall be supported with language/gender filtering.

### FR-3: Provider Availability
- The module shall gracefully handle missing dependencies via availability flags.
- `STT_AVAILABLE`, `TTS_AVAILABLE`, `WHISPER_AVAILABLE`, `PYTTSX3_AVAILABLE`, `EDGE_TTS_AVAILABLE` flags shall accurately reflect runtime availability.

### FR-4: Error Hierarchy
- Seven specialized exception types shall cover all failure modes.
- All exceptions shall extend the base `AudioError`.

## Interface Contracts

### MCP Tool Signatures

```python
def audio_get_capabilities() -> dict
def audio_list_voices(provider: str = "pyttsx3") -> dict
```

### Whisper Model Sizes

| Model | Parameters | Approximate VRAM | Relative Speed |
|-------|-----------|-----------------|----------------|
| tiny | 39M | ~1GB | Fastest |
| base | 74M | ~1GB | Fast |
| small | 244M | ~2GB | Medium |
| medium | 769M | ~5GB | Slow |
| large-v3 | 1550M | ~10GB | Slowest |

### Supported Audio Input Formats
WAV, MP3, FLAC, OGG, M4A, WEBM, MP4, OPUS

## Non-Functional Requirements

### NFR-1: Graceful Degradation
- Missing optional dependencies shall not prevent module import.
- Unavailable features shall set their class exports to `None`.

### NFR-2: Performance
- Transcription speed depends on model size and hardware (GPU recommended for large models).
- Edge TTS requires network connectivity; pyttsx3 operates fully offline.

## Testing Requirements

- All tests follow the Zero-Mock policy.
- Tests with `@pytest.mark.skipif` for Whisper, pyttsx3, and edge-tts dependencies.
- Audio format validation tested with real audio file fixtures.

## Navigation

- **Source**: [src/codomyrmex/audio/](../../../../src/codomyrmex/audio/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
