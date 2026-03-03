# Audio

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Audio module provides comprehensive audio processing capabilities including speech-to-text (STT) transcription using Whisper and text-to-speech (TTS) synthesis using pyttsx3 and Edge TTS. It supports multiple providers for flexibility between offline and cloud-based processing, with 99+ language support for transcription and 300+ neural voices for synthesis. This is an optional module requiring `uv sync --extra audio` for dependency installation.

## Architecture Overview

The module is organized into two main subpackages: `speech_to_text` for transcription and `text_to_speech` for synthesis. Both follow a provider pattern, with availability flags that allow graceful degradation when optional dependencies are not installed.

```
audio/
├── __init__.py              # Public API with conditional imports and availability flags
├── exceptions.py            # AudioError hierarchy (7 exception types)
├── mcp_tools.py             # MCP tools (audio_get_capabilities, audio_list_voices)
├── speech_to_text/          # STT submodule (Whisper-based transcription)
│   └── ...                  # Transcriber, TranscriptionResult, Segment, Word
└── text_to_speech/          # TTS submodule (pyttsx3, Edge TTS)
    └── ...                  # Synthesizer, SynthesisResult, VoiceInfo
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| OBSERVE | Analyze audio content via speech-to-text transcription | Transcriber.transcribe() |
| BUILD | Generate audio output via TTS synthesis | Synthesizer.synthesize() |
| EXECUTE | Play and process audio files, run TTS/STT pipelines | Direct Python import |

## Key Classes and Functions

### Speech-to-Text

**`Transcriber`** -- Main STT class for audio transcription with Whisper models.

```python
from codomyrmex.audio import Transcriber, WhisperModelSize

transcriber = Transcriber(model_size=WhisperModelSize.BASE)
result = transcriber.transcribe("interview.mp3")
print(result.text)
result.save_srt("subtitles.srt")
```

**`TranscriptionResult`** -- Result containing text, segments, word-level timestamps, and language detection.

**`WhisperModelSize`** -- Enum: TINY, BASE, SMALL, MEDIUM, LARGE_V3.

### Text-to-Speech

**`Synthesizer`** -- Main TTS class for speech synthesis with provider selection.

```python
from codomyrmex.audio import Synthesizer

# Offline (pyttsx3)
synth = Synthesizer(provider="pyttsx3")
result = synth.synthesize("Hello world!")
result.save("hello.wav")

# Neural (Edge TTS, requires internet)
synth = Synthesizer(provider="edge-tts")
result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
result.save("hello.mp3")
```

### Exceptions

`AudioError`, `TranscriptionError`, `SynthesisError`, `AudioFormatError`, `ModelNotLoadedError`, `ProviderNotAvailableError`, `VoiceNotFoundError`

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `audio_get_capabilities` | Report available STT and TTS providers | (none) | Safe |
| `audio_list_voices` | List available TTS voices for a provider | `provider: str = "pyttsx3"` | Safe |

## Configuration

```bash
# Install audio dependencies
uv sync --extra audio

# No environment variables required for offline usage
# Edge TTS requires internet connectivity
```

## Usage Examples

### Example 1: Transcribe with Language Detection

```python
from codomyrmex.audio import Transcriber

transcriber = Transcriber()
lang, confidence = transcriber.detect_language("audio.mp3")
print(f"Detected: {lang} ({confidence:.2%})")

result = transcriber.transcribe("audio.mp3", language=lang)
print(result.text)
```

### Example 2: List Available Voices

```python
from codomyrmex.audio import Synthesizer

synth = Synthesizer(provider="edge-tts")
voices = synth.list_voices(language="en")
for voice in voices[:5]:
    print(f"{voice.id}: {voice.name}")
```

## Error Handling

- `ProviderNotAvailableError` -- Raised when required provider dependencies are not installed
- `ModelNotLoadedError` -- Raised when the Whisper model cannot be loaded
- `AudioFormatError` -- Raised for unsupported audio format input
- `VoiceNotFoundError` -- Raised when the requested TTS voice is not available

## Related Modules

- [`video`](../video/readme.md) -- Video processing that may include audio tracks
- [`llm`](../llm/readme.md) -- LLM infrastructure for multimodal processing

## Navigation

- **Source**: [src/codomyrmex/audio/](../../../../src/codomyrmex/audio/)
- **API Spec**: [API_SPECIFICATION.md](../../../../src/codomyrmex/audio/API_SPECIFICATION.md)
- **Parent**: [All Modules](../README.md)
