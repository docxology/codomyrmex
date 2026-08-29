# Codomyrmex Agents — tests/unit/audio

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: August 2026

## Purpose
Validation coverage, fixtures, and regression checks for Audio.

## Active Components
- `AGENTS.md` – Agent coordination and navigation
- `README.md` – Directory overview
- `SPEC.md` – Specification
- `PAI.md` – PAI notes
- `__init__.py` – Package marker
- `py.typed` – PEP 561 marker
- `speech_to_text/` – Speech-to-text test components
- `test_audio_exceptions.py` – Audio exception hierarchy tests
- `test_audio_streaming.py` – Audio streaming pipeline tests
- `test_codec.py` – Codec negotiation tests
- `test_edge_tts_lifecycle.py` – Edge-TTS lifecycle tests
- `test_mcp_audio.py` – MCP audio tool tests
- `test_mcp_tools.py` – MCP tool handler tests
- `test_stt_models.py` – STT data model tests
- `test_synthesizer.py` – Synthesizer tests
- `test_transcriber.py` – Transcriber tests
- `test_tts_models.py` – TTS data model tests
- `test_vad.py` – Voice activity detection tests

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `test_audio_exceptions.py`
- `test_audio_streaming.py`
- `test_codec.py`
- `test_edge_tts_lifecycle.py`
- `test_mcp_audio.py`
- `test_mcp_tools.py`
- `test_stt_models.py`
- `test_synthesizer.py`
- `test_transcriber.py`
- `test_tts_models.py`
- `test_vad.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
