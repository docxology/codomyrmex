# speech_to_text

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for Speech To Text.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `models.py` – File
- `providers/` – Subdirectory
- `py.typed` – File
- `transcriber.py` – File
- `validation.py` — Model-independent file and format preflight
- `vad.py` – File

## Navigation

- **Parent Directory**: [audio](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Input preflight

`validation.validate_audio_path(path)` requires an existing regular file with a
supported audio suffix and returns its `Path`. Missing/nonfile inputs raise
`TranscriptionError`; unsupported suffixes raise `AudioFormatError`. The helper
uses only filesystem metadata and acquires no model/native resources. Whisper
provider validation delegates to it. MCP transcription and language detection
perform this check before constructing the eager-loading `Transcriber`.
