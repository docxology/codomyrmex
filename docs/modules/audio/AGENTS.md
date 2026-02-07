# Audio Processing Module — Agent Coordination

## Purpose

Audio processing module for Codomyrmex.

## Key Capabilities

- Audio Processing operations and management

## Agent Usage Patterns

```python
from codomyrmex.audio import *

# Agent uses audio processing capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/audio/](../../../src/codomyrmex/audio/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`AudioError`** — Base exception for all audio-related errors.
- **`TranscriptionError`** — Raised when speech-to-text transcription fails.
- **`SynthesisError`** — Raised when text-to-speech synthesis fails.
- **`AudioFormatError`** — Raised when the audio format is unsupported or invalid.
- **`ModelNotLoadedError`** — Raised when the required model is not loaded or unavailable.

### Submodules

- `speech_to_text` — Speech To Text
- `text_to_speech` — Text To Speech

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k audio -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
