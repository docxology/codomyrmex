# audio

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Audio.

## Directory Contents

- `AGENTS.md` – File
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `py.typed` – File
- `speech_to_text` – Subdirectory
- `test_audio_exceptions.py` – File
- `test_audio_streaming.py` – File
- `test_codec.py` – File
- `test_edge_tts_lifecycle.py` – File
- `test_mcp_tools.py` – File
- `test_stt_models.py` – File
- `test_synthesizer.py` – File
- `test_transcriber.py` – File
- `test_tts_models.py` – File
- `test_vad.py` – File

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Model-independent input and lifecycle checks

`test_input_preflight.py` runs real MCP functions in a fresh subprocess with an
empty Hugging Face cache and offline mode. Invalid inputs must produce path/format
errors without acquiring models or creating cache/output directories.
`test_edge_tts_lifecycle.py` checks actual session-owned connector lifetimes and
finite socket timeouts, independently of remote Edge service availability.

```bash
uv run --locked pytest -q tests/unit/audio/test_input_preflight.py tests/unit/audio/test_edge_tts_lifecycle.py
```

The capability subprocess control compares actual installed backend metadata to
the public `whisper` provider entry and checks that `faster_whisper`, CTranslate2,
and PyAV were not imported by discovery.

Edge request configuration controls verify default, accelerated/raised-pitch,
and slowed/lowered-pitch cases against the real library's rate/pitch/volume fields.
Invalid volume fails before construction, and empty direct-file calls cannot
create zero-byte output artifacts.
