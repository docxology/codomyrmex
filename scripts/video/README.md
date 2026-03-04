# Video Generation Scripts

Thin orchestrator scripts for generating videos via Google AI (Veo 2.0) using the `codomyrmex.video` module.

## Quick Start

```bash
# Install dependencies
uv sync

# Dry run (no API key needed)
uv run python scripts/video/orchestrate.py

# Live generation
export GEMINI_API_KEY=<your-key>
uv run python scripts/video/orchestrate.py

# Override the prompt
uv run python scripts/video/orchestrate.py --prompt "A sunset over the ocean"
```

## Configuration

All generation parameters are in [`config/video/config.yaml`](../../config/video/config.yaml):

| Key | Default | Description |
|-----|---------|-------------|
| `generation.video.model` | `veo-2.0-generate-001` | Google AI model |
| `generation.video.default_prompt` | (see config) | Prompt used when no `--prompt` given |
| `generation.video.number_of_videos` | `1` | Videos per request (1–4) |
| `generation.video.aspect_ratio` | `16:9` | `"16:9"` or `"9:16"` |
| `generation.video.duration_seconds` | `5` | Video duration |
| `generation.video.output_dir` | `output/videos` | Where to save generated files |

## Scripts

| Script | Purpose |
|--------|---------|
| `orchestrate.py` | Config-driven orchestrator — run to generate videos |
| `examples/basic_usage.py` | Minimal example showing VideoGenerator API |

## Module Reference

The scripts delegate to:
- `src/codomyrmex/video/generation/video_generator.py` — `VideoGenerator` class
- `src/codomyrmex/agents/gemini/gemini_client.py` — `GeminiClient` (Google AI SDK)

See [`src/codomyrmex/video/README.md`](../../src/codomyrmex/video/README.md) for full module documentation.

## Output Files

Generated videos are saved to `output/videos/` (created automatically).
The directory is git-ignored by default.
