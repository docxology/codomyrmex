# Video Generation -- Functional Specification

**Version**: v1.1.4 | **Updated**: March 2026

## Overview

Specifies the `video.generation` submodule, which provides a thin wrapper around `GeminiClient` for text-to-video generation using Google AI's Veo 2.0 model.

## Design Principles

- **Single Responsibility**: One class (`VideoGenerator`) with one public method (`generate`).
- **Dependency Injection**: Accepts an optional `GeminiClient` instance; creates one if not provided.
- **Thin Wrapper**: Delegates all API interaction to `GeminiClient.generate_videos`, adding no extra logic.

## Architecture

```
video/generation/
  __init__.py          -- Re-exports VideoGenerator
  video_generator.py   -- VideoGenerator class definition
```

## Functional Requirements

### FR-1: Video Generation from Text

- Accept a text `prompt` describing the desired video content.
- Accept an optional `model` parameter (default: `veo-2.0-generate-001`).
- Accept arbitrary `**kwargs` forwarded to the underlying client.
- Return a `list[dict[str, Any]]` of generated video representations.

### FR-2: Client Injection

- Accept an optional `GeminiClient` instance at construction time.
- If `None`, instantiate a new `GeminiClient()` with default configuration.
- Store the client as `self.client` for reuse across calls.

## Interface Contracts

### VideoGenerator

```python
class VideoGenerator:
    def __init__(self, client: GeminiClient | None = None) -> None: ...
    def generate(
        self,
        prompt: str,
        model: str = "veo-2.0-generate-001",
        **kwargs: Any,
    ) -> list[dict[str, Any]]: ...
```

### Return Type

`generate()` returns whatever `GeminiClient.generate_videos()` returns -- a list of dictionaries, each representing a video object from the Google AI API response.

## Dependencies

| Dependency | Type | Purpose |
|-----------|------|---------|
| `codomyrmex.agents.gemini.gemini_client.GeminiClient` | Internal | API client for Google AI video generation |
| `typing.Any` | Standard library | Type annotation |

## Constraints

- Requires network access to Google AI endpoints at generation time.
- Requires `GOOGLE_API_KEY` environment variable to be set (enforced by `GeminiClient`).
- No local caching of generated videos; each call hits the API.
- No retry logic; callers must implement retries if needed.
- Thread safety depends on the thread safety of the underlying `GeminiClient`.

## Navigation

- **Parent**: [video/SPEC.md](../SPEC.md)
- **RASP**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | **SPEC.md**
