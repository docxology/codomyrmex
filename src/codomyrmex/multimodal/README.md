# Multimodal

**Status**: Active | **Last Updated**: March 2026

Image generation using Google's Imagen 3 model via the Gemini API. Provides a high-level `ImageGenerator` class that wraps `GeminiClient.generate_images` for text-to-image workflows.

## Quick Start

```python
import os
from codomyrmex.multimodal import ImageGenerator
from codomyrmex.agents.gemini.gemini_client import GeminiClient

client = GeminiClient(config={"gemini_api_key": os.getenv("GEMINI_API_KEY")})
generator = ImageGenerator(client=client)

images = generator.generate(
    prompt="A sunset over the ocean",
    number_of_images=1,
    aspect_ratio="1:1",
)
```

The `GEMINI_API_KEY` environment variable must be set to a valid Google AI API key.

## Installation

```bash
uv sync
```

The module depends on the `google-genai` and `Pillow` packages, which are pulled in via the `agents` extras. If they are not already installed:

```bash
pip install google-genai Pillow
```

## Core Classes

| Class | Module | Description |
|-------|--------|-------------|
| `ImageGenerator` | `image_generation` | High-level wrapper for Imagen 3 text-to-image generation |
| `GeminiClient` | `agents.gemini.gemini_client` | Underlying client that communicates with the Google AI SDK |

## API Reference

### ImageGenerator

```python
ImageGenerator(client: GeminiClient | None = None)
```

If no `client` is provided, a new `GeminiClient()` is instantiated (which reads `GEMINI_API_KEY` from the environment).

```python
def generate(
    self,
    prompt: str,
    model: str = "imagen-3.0-generate-002",
    **kwargs: Any,
) -> list[dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the image to generate |
| `model` | `str` | `"imagen-3.0-generate-002"` | Imagen model identifier |
| `**kwargs` | `Any` | -- | Additional config passed to the API (e.g., `number_of_images`, `aspect_ratio`) |

**Returns:** A list of dictionary representations of the generated image objects.

### Related GeminiClient Methods

The `GeminiClient` also exposes image editing and upscaling:

```python
def generate_images(self, prompt: str, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
def upscale_image(self, image: Any, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
def edit_image(self, prompt: str, image: Any, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI API key for authenticating with the Gemini/Imagen API |

## PAI Integration

The Multimodal module maps to the **BUILD** phase of the PAI Algorithm. Use it to generate images as part of content creation, documentation illustration, or data augmentation workflows.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/multimodal/
```

Tests that require a live `GEMINI_API_KEY` are guarded with `@pytest.mark.skipif`.

---

This module does not yet have AGENTS.md, SPEC.md, or PAI.md companion files.
