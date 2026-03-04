# Audio Generation Scripts

Thin orchestrator scripts for text-to-speech synthesis using the `codomyrmex.audio` module.

## Providers

| Provider | Quality | Internet Required | Installation |
|----------|---------|-------------------|--------------|
| `edge-tts` | Neural (high quality, 300+ voices) | Yes | `uv sync --extra audio` |
| `pyttsx3` | System voices (offline) | No | `uv sync --extra audio` |

The orchestrator tries `edge-tts` first and falls back to `pyttsx3` automatically.

## Quick Start

```bash
# Install audio extras
uv sync --extra audio

# Run orchestrator (uses config/audio/config.yaml)
uv run python scripts/audio/orchestrate.py

# Override text
uv run python scripts/audio/orchestrate.py --text "Hello, world!"

# Force offline provider
uv run python scripts/audio/orchestrate.py --provider pyttsx3

# Basic usage example
uv run python scripts/audio/examples/basic_usage.py
```

## Configuration

All parameters in [`config/audio/config.yaml`](../../config/audio/config.yaml):

| Key | Default | Description |
|-----|---------|-------------|
| `generation.tts.default_provider` | `edge-tts` | Primary TTS provider |
| `generation.tts.default_voice` | `en-US-AriaNeural` | Edge TTS voice ID |
| `generation.tts.fallback_provider` | `pyttsx3` | Used when primary unavailable |
| `generation.tts.rate` | `1.0` | Speaking rate (0.5–2.0) |
| `generation.tts.pitch` | `1.0` | Pitch adjustment |
| `generation.tts.volume` | `1.0` | Volume (0.0–1.0) |
| `generation.tts.output_dir` | `output/audio` | Where to save audio files |
| `generation.tts.default_text` | (see config) | Text for single synthesis |
| `generation.tts.batch_texts` | (list) | Texts for batch synthesis |

## Scripts

| Script | Purpose |
|--------|---------|
| `orchestrate.py` | Config-driven orchestrator — runs single + batch synthesis |
| `examples/basic_usage.py` | Minimal example showing both providers |

## Module Reference

Delegates to:
- `src/codomyrmex/audio/text_to_speech/synthesizer.py` — `Synthesizer` class
- Providers: `pyttsx3_provider.py`, `edge_tts_provider.py`

See [`src/codomyrmex/audio/README.md`](../../src/codomyrmex/audio/README.md) for full documentation.

## Output Files

Audio files are saved to `output/audio/` (created automatically, git-ignored).
