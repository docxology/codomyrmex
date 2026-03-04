# Audio Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Audio processing with speech-to-text (Whisper) and text-to-speech (pyttsx3, Edge TTS). Supports transcription, language detection, and voice synthesis.

## Configuration Options

The audio module operates with sensible defaults and does not require environment variable configuration. Requires optional dependencies: `uv sync --extra audio`. Whisper model size (tiny/base/small/medium/large) affects accuracy and memory usage.

## MCP Tools

This module exposes 2 MCP tool(s):

- `audio_transcribe`
- `audio_synthesize`

## PAI Integration

PAI agents invoke audio tools through the MCP bridge. Requires optional dependencies: `uv sync --extra audio`. Whisper model size (tiny/base/small/medium/large) affects accuracy and memory usage.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep audio

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/audio/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
