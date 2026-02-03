# audio

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The audio module provides comprehensive audio processing capabilities including speech-to-text (STT) transcription and text-to-speech (TTS) synthesis. It supports multiple providers for flexibility between offline and cloud-based processing.

## Features

### Speech-to-Text (STT)
- **Whisper transcription** via faster-whisper (CTranslate2 backend)
- 99+ languages supported
- Word-level timestamps
- Voice activity detection (VAD) filtering
- Export to SRT/VTT subtitle formats
- Batch transcription support

### Text-to-Speech (TTS)
- **Offline synthesis** via pyttsx3 (SAPI5/NSSpeech/espeak)
- **Neural TTS** via Microsoft Edge TTS (300+ voices, free)
- Multiple output formats (WAV, MP3)
- Voice listing and selection
- Rate, pitch, and volume control

## Installation

```bash
# Install audio dependencies
uv sync --extra audio
```

## Quick Start

### Speech-to-Text

```python
from codomyrmex.audio import Transcriber, WhisperModelSize

# Basic transcription
transcriber = Transcriber()
result = transcriber.transcribe("interview.mp3")
print(result.text)

# With larger model for better accuracy
transcriber = Transcriber(model_size=WhisperModelSize.LARGE_V3)
result = transcriber.transcribe("spanish.wav", language="es")

# Export to subtitles
result.save_srt("subtitles.srt")
result.save_vtt("subtitles.vtt")

# Language detection
lang, confidence = transcriber.detect_language("audio.mp3")
print(f"Detected: {lang} ({confidence:.2%})")
```

### Text-to-Speech

```python
from codomyrmex.audio import Synthesizer

# Offline synthesis (fast, no internet required)
synth = Synthesizer(provider="pyttsx3")
result = synth.synthesize("Hello world!")
result.save("hello.wav")

# Neural TTS (high quality, requires internet)
synth = Synthesizer(provider="edge-tts")
result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
result.save("hello.mp3")

# List available voices
voices = synth.list_voices(language="en")
for voice in voices[:5]:
    print(f"{voice.id}: {voice.name}")
```

## Directory Contents

- `__init__.py` - Main module exports
- `exceptions.py` - Audio-specific exception classes
- `README.md` - This file
- `SPEC.md` - Technical specification
- `AGENTS.md` - AI agent guidance
- `PAI.md` - Programmable AI Interface
- `API_SPECIFICATION.md` - Detailed API reference
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tools
- `speech_to_text/` - STT submodule
- `text_to_speech/` - TTS submodule

## Supported Formats

### Input (STT)
WAV, MP3, FLAC, OGG, M4A, WEBM, MP4, OPUS

### Output (TTS)
- pyttsx3: WAV
- edge-tts: MP3

## Model Sizes (Whisper)

| Model | Parameters | VRAM | Speed | Quality |
|-------|-----------|------|-------|---------|
| tiny | 39M | ~1GB | Fastest | Basic |
| base | 74M | ~1GB | Fast | Good |
| small | 244M | ~2GB | Medium | Better |
| medium | 769M | ~5GB | Slow | Great |
| large-v3 | 1550M | ~10GB | Slowest | Best |

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
