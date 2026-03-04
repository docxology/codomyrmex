# AGENTS.md — Audio Generation Scripts

## Purpose
Runnable entry points for TTS audio generation. Agents use these to produce speech audio from text.

## Key Entry Points

| Script | When to Use |
|--------|-------------|
| `orchestrate.py` | Config-driven synthesis (single + batch) |
| `examples/basic_usage.py` | Minimal API demonstration, both providers |

## Execution Contract

- **No API key needed**: Both providers (edge-tts and pyttsx3) are free
- **Requires audio extras**: `uv sync --extra audio`
- **Soft skip** if audio extras not installed (exit 0, not error)
- **Configurable via**: `config/audio/config.yaml`
- **Output destination**: `output/audio/` (relative to repo root)

## Provider Selection Logic

```
default_provider (from config, default: "edge-tts")
  → try to initialize
  → if ProviderNotAvailableError: try fallback_provider (default: "pyttsx3")
  → if both fail: print_error + return False
```

## Agent Guidelines

1. **Prefer edge-tts** for production audio — higher quality, 300+ neural voices
2. **Use pyttsx3** for CI/offline environments — no internet required
3. **Voice IDs for edge-tts** follow pattern `{lang}-{Name}Neural`, e.g. `en-US-AriaNeural`
4. **SynthesisResult.save(path)** saves audio bytes to the given path
5. **Never mock the Synthesizer** in tests — use `ProviderNotAvailableError` guards
