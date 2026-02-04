# Audio Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `audio` module provides comprehensive audio processing capabilities including speech-to-text (STT) transcription using Whisper and text-to-speech (TTS) synthesis using pyttsx3 (offline) and Microsoft Edge TTS (neural, cloud-based). It supports multiple providers, graceful degradation when optional dependencies are unavailable, and exports subtitle formats (SRT/VTT).

## Key Features

- **Whisper-based transcription**: Speech-to-text via faster-whisper (CTranslate2 backend) with 99+ language support
- **Word-level timestamps**: Fine-grained timing data for each transcribed word
- **Voice activity detection (VAD)**: Filters silence and non-speech segments for cleaner output
- **Subtitle export**: Save transcriptions as SRT or VTT subtitle files
- **Offline TTS synthesis**: Text-to-speech via pyttsx3 (SAPI5/NSSpeech/espeak) with no internet required
- **Neural TTS synthesis**: High-quality speech via Microsoft Edge TTS with 300+ voices
- **Multiple audio format support**: Input: WAV, MP3, FLAC, OGG, M4A, WEBM, MP4, OPUS; Output: WAV (pyttsx3), MP3 (edge-tts)
- **Voice management**: List, filter, and select voices by language and gender
- **Configurable speech parameters**: Rate, pitch, and volume control for TTS output
- **Graceful dependency handling**: Feature availability flags (`STT_AVAILABLE`, `TTS_AVAILABLE`, `WHISPER_AVAILABLE`, `PYTTSX3_AVAILABLE`, `EDGE_TTS_AVAILABLE`) for runtime capability detection
- **Structured exception hierarchy**: Dedicated exceptions for transcription, synthesis, format, model, provider, and voice errors

## Key Components

| Component | Description |
|-----------|-------------|
| `Transcriber` | Main speech-to-text class; accepts model size configuration and provides `transcribe()` and `detect_language()` methods |
| `TranscriptionResult` | Result object containing transcribed text, segments, and subtitle export methods (`save_srt`, `save_vtt`) |
| `TranscriptionConfig` | Configuration dataclass for transcription parameters |
| `Segment` | A timed segment of transcribed audio with start/end timestamps |
| `Word` | A single word with precise timing information |
| `WhisperModelSize` | Enum for Whisper model sizes: TINY, BASE, SMALL, MEDIUM, LARGE_V3 |
| `STTProvider` | Enum for speech-to-text provider selection |
| `Synthesizer` | Main text-to-speech class; supports provider selection and voice configuration |
| `SynthesisResult` | Result object containing synthesized audio with `save()` method |
| `TTSConfig` | Configuration dataclass for synthesis parameters |
| `AudioFormat` | Enum for output audio formats |
| `VoiceInfo` | Dataclass describing an available TTS voice |
| `VoiceGender` | Enum for voice gender filtering |
| `TTSProvider` | Enum for text-to-speech provider selection |
| `AudioError` | Base exception for all audio module errors |
| `TranscriptionError` | Exception raised during STT failures |
| `SynthesisError` | Exception raised during TTS failures |

## Installation

```bash
# Install audio dependencies
uv sync --extra audio
```

## Quick Start

```python
from codomyrmex.audio import Transcriber, Synthesizer, WhisperModelSize

# Speech-to-text
transcriber = Transcriber(model_size=WhisperModelSize.BASE)
result = transcriber.transcribe("interview.mp3")
print(result.text)

# Export as subtitles
result.save_srt("subtitles.srt")

# Language detection
lang, confidence = transcriber.detect_language("audio.mp3")
print(f"Detected: {lang} ({confidence:.2%})")

# Text-to-speech (offline)
synth = Synthesizer(provider="pyttsx3")
result = synth.synthesize("Hello world!")
result.save("hello.wav")

# Text-to-speech (neural, requires internet)
synth = Synthesizer(provider="edge-tts")
result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
result.save("hello.mp3")

# List available voices
voices = synth.list_voices(language="en")
for voice in voices[:5]:
    print(f"{voice.id}: {voice.name}")
```

## Whisper Model Sizes

| Model | Parameters | VRAM | Speed | Quality |
|-------|-----------|------|-------|---------|
| tiny | 39M | ~1GB | Fastest | Basic |
| base | 74M | ~1GB | Fast | Good |
| small | 244M | ~2GB | Medium | Better |
| medium | 769M | ~5GB | Slow | Great |
| large-v3 | 1550M | ~10GB | Slowest | Best |

## Related Modules

- [llm](../llm/) - LLM infrastructure that may provide embedding models for audio metadata
- [logging_monitoring](../logging_monitoring/) - Centralized logging consumed by audio processing pipelines

## Navigation

- **Source**: [src/codomyrmex/audio/](../../../src/codomyrmex/audio/)
- **Parent**: [docs/modules/](../README.md)
