# Video Generation -- Agent Coordination

**Version**: v1.1.9 | **Updated**: March 2026

## Overview

Agent-facing reference for the `video.generation` submodule. Provides text-to-video generation via Google AI Veo 2.0, accessed through the `VideoGenerator` class.

## Key Files

| File | Class / Export | Role |
|------|---------------|------|
| `video_generator.py` | `VideoGenerator` | Wraps `GeminiClient.generate_videos` for text-to-video generation |
| `video_generator.py` | `VideoGenerator.__init__` | Accepts optional `GeminiClient`; instantiates a new one if `None` |
| `video_generator.py` | `VideoGenerator.generate` | Accepts `prompt` (str), `model` (str, default `veo-2.0-generate-001`), returns `list[dict]` |
| `__init__.py` | `VideoGenerator` | Re-exported for `from codomyrmex.video.generation import VideoGenerator` |

## MCP Tools Available

None. This submodule has no `mcp_tools.py` and is not auto-discovered via the MCP bridge.

## Agent Instructions

1. **Instantiation**: Create `VideoGenerator()` for default Gemini client, or pass a pre-configured `GeminiClient` instance.
2. **Prompt quality**: Provide descriptive, specific text prompts for better video generation results.
3. **Model selection**: The default model is `veo-2.0-generate-001`. Override via the `model` parameter if newer models become available.
4. **Return format**: `generate()` returns a `list[dict[str, Any]]` -- each dict represents a generated video object from the Google AI response.
5. **Error handling**: Failures propagate from `GeminiClient`; wrap calls in try/except when used in automated pipelines.

## Operating Contracts

- Requires `GOOGLE_API_KEY` environment variable (via `GeminiClient`).
- Network access to Google AI APIs is required at generation time.
- No local file I/O is performed by this module; callers handle persistence of returned video data.
- No MCP tool registration; this module is consumed as a Python library only.

## Common Patterns

```python
# Agent workflow: generate and persist
from codomyrmex.video.generation import VideoGenerator

gen = VideoGenerator()
videos = gen.generate("Underwater coral reef with tropical fish")
for i, video in enumerate(videos):
    # Process video dict as needed
    print(f"Video {i}: {video}")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Notes |
|-----------|-------------|-------|
| Engineer | Full | Primary consumer for video generation workflows |
| Architect | Read-only | Architecture review of generation pipeline |
| QA Tester | Full | Integration testing with API |
| Designer | Full | Content generation for visual assets |

## Navigation

- **Parent**: [video/AGENTS.md](../AGENTS.md)
- **RASP**: [README.md](README.md) | **AGENTS.md** | [SPEC.md](SPEC.md)
