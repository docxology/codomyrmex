# Multimodal Module -- Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The multimodal module provides text-to-image generation using Google AI's Imagen 4 model via the Gemini API. It wraps the `GeminiClient` from the agents module into a high-level `ImageGenerator` class for straightforward image creation from text prompts.

## Architecture

```
multimodal/
  __init__.py            # Exports ImageGenerator
  image_generation.py    # ImageGenerator class
  PAI.md                 # PAI integration documentation
  README.md              # Module overview
  AGENTS.md              # Agent integration guide
  SPEC.md                # This file
```

### Component Diagram

```
[User / Agent]
      |
      v
[ImageGenerator]  <-- high-level facade
      |
      v
[GeminiClient]    <-- from agents.gemini.gemini_client
      |
      v
[Google AI SDK]   <-- google-genai package
      |
      v
[Imagen 4 API]   <-- remote service
```

The module follows a thin-wrapper pattern: `ImageGenerator` delegates all API communication to `GeminiClient.generate_images()`, adding only default model selection (`imagen-4.0-generate-001`) and optional client auto-instantiation.

## Data Flows

### Input

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `prompt` | `str` | Caller | Natural language description of the desired image |
| `model` | `str` | Caller (optional) | Imagen model identifier; defaults to `imagen-4.0-generate-001` |
| `**kwargs` | `Any` | Caller (optional) | Additional generation parameters (`number_of_images`, `aspect_ratio`, etc.) |
| `client` | `GeminiClient` or `None` | Constructor | Pre-configured client; auto-created if not provided |

### Output

| Output | Type | Description |
|--------|------|-------------|
| `images` | `list[dict[str, Any]]` | List of dictionary representations of generated image objects from the API |

### Error Conditions

| Condition | Behavior |
|-----------|----------|
| Missing `GEMINI_API_KEY` | `GeminiClient()` constructor raises on initialization |
| Invalid prompt | API returns error propagated through `GeminiClient` |
| Network failure | Exception raised from `google-genai` SDK |

## Public Interface

### ImageGenerator

```python
class ImageGenerator:
    def __init__(self, client: GeminiClient | None = None) -> None:
        """Initialize with optional pre-configured GeminiClient."""

    def generate(
        self,
        prompt: str,
        model: str = "imagen-4.0-generate-001",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate images from a text prompt via Imagen 4."""
```

### Module Exports (`__init__.py`)

```python
__all__ = ["ImageGenerator"]
```

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `codomyrmex.agents.gemini.gemini_client` | Internal | `GeminiClient` for Google AI SDK communication |
| `google-genai` | External (optional) | Google AI Python SDK |
| `Pillow` | External (optional) | Image processing (pulled in via agents extras) |

## Configuration

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `GEMINI_API_KEY` | Environment variable | None (required) | Google AI API key |
| `model` | `generate()` parameter | `imagen-4.0-generate-001` | Imagen model version |

No file-based configuration. All settings are passed at construction or call time.

## Constraints and Limitations

1. **Single modality**: Currently supports image generation only. No audio, video, or other modalities.
2. **External dependency**: Requires live network access to Google AI API -- no offline mode.
3. **No MCP tools**: Not auto-discovered by the MCP bridge. Must be called directly from Python.
4. **No caching**: Generated images are not cached. Repeated identical prompts produce new API calls.
5. **API rate limits**: Subject to Google AI API rate limits and quotas.
6. **Model availability**: Imagen 4 model access depends on Google AI API tier and region.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/multimodal/
```

Tests requiring a live `GEMINI_API_KEY` are guarded with `@pytest.mark.skipif`.

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
- **Module README**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
