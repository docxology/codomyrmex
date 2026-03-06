# Audio Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Audio processing with speech-to-text (Whisper) and text-to-speech (pyttsx3, Edge TTS). Supports transcription, language detection, and voice synthesis. This specification documents the configuration schema and constraints.

## Configuration Schema

The audio module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Requires optional dependencies: `uv sync --extra audio`. Whisper model size (tiny/base/small/medium/large) affects accuracy and memory usage. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Requires optional dependencies: `uv sync --extra audio`. Whisper model size (tiny/base/small/medium/large) affects accuracy and memory usage.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/audio/SPEC.md)
