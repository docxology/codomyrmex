# Audio -- Agent Integration Guide

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Audio module provides agents with audio processing capabilities, allowing them to check available STT/TTS providers and list available voices for synthesis.

## Available MCP Tools

### audio_get_capabilities

Report which speech-to-text and text-to-speech providers are installed and ready to use.

**Parameters:** None

**Returns:** Dictionary with `stt_providers` (list), `tts_providers` (list), and `ready` (bool).

### audio_list_voices

List available text-to-speech voices for a given provider.

**Parameters:**
- `provider` (str, default: "pyttsx3") -- TTS provider to query ("pyttsx3" or "edge-tts")

**Returns:** Dictionary with voice details (id, name, locale/languages) for the selected provider.

## Agent Interaction Patterns

### OBSERVE Phase
Use `audio_get_capabilities` to check what audio processing is available before attempting transcription or synthesis tasks.

### BUILD Phase
Use `audio_list_voices` to select an appropriate voice before generating speech output. Consider language and locale requirements.

## Trust Level

Both MCP tools are classified as **Safe** -- they perform read-only capability and voice listing operations.

## Optional Dependencies

Audio functionality requires `uv sync --extra audio`. When dependencies are not installed, capability checks return empty provider lists and the `ready` flag is `false`.

## Navigation

- **Source**: [src/codomyrmex/audio/](../../../../src/codomyrmex/audio/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
