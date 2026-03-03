# Video Generation

**Version**: v1.0.8 | **Updated**: March 2026

## Overview

The `video.generation` submodule provides text-to-video generation capabilities powered by Google AI's Veo 2.0 model. It wraps the `GeminiClient` from `codomyrmex.agents.gemini` to expose a focused video generation interface.

## PAI Integration

| Phase | Tool / Class | Usage |
|-------|-------------|-------|
| BUILD | `VideoGenerator.generate` | Generate video content from text prompts via Veo 2.0 |
| EXECUTE | `VideoGenerator` | Instantiate with optional pre-configured `GeminiClient` |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `VideoGenerator` | Class | Text-to-video generator using Google AI (Veo 2.0) |

## Quick Start

```python
from codomyrmex.video.generation import VideoGenerator

# Default client (requires GOOGLE_API_KEY env var)
gen = VideoGenerator()
results = gen.generate("A time-lapse of a blooming flower in a garden")

# Use a specific model
results = gen.generate(
    prompt="Ocean waves crashing on a rocky coastline at sunset",
    model="veo-2.0-generate-001",
)
```

To inject an existing client:

```python
from codomyrmex.agents.gemini.gemini_client import GeminiClient
from codomyrmex.video.generation import VideoGenerator

client = GeminiClient()
gen = VideoGenerator(client=client)
results = gen.generate("A drone flyover of a mountain range")
```

## Architecture

```
video/generation/
  __init__.py          -- Re-exports VideoGenerator
  video_generator.py   -- VideoGenerator class (Veo 2.0 wrapper)
```

## MCP Tools

This submodule does not expose MCP tools directly. Video generation is accessed programmatically through `VideoGenerator`.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/video/generation/ -v
```

Requires `GOOGLE_API_KEY` environment variable for integration tests. Unit tests that call the API are gated with `@pytest.mark.skipif`.

## Navigation

- **Parent**: [video/README.md](../README.md)
- **Siblings**: [processing/](../processing/), [extraction/](../extraction/), [analysis/](../analysis/)
- **RASP**: **README.md** | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
