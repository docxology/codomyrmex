# Multimodal

**Status**: Active | **Last Updated**: March 2026

Image generation using Google's Imagen 4 model via the Gemini API. Provides a high-level `ImageGenerator` class that wraps `GeminiClient.generate_images` for text-to-image workflows.

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
| `ImageGenerator` | `image_generation` | High-level wrapper for Imagen 4 text-to-image generation |
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
    model: str = "imagen-4.0-generate-001",
    **kwargs: Any,
) -> list[dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | Text description of the image to generate |
| `model` | `str` | `"imagen-4.0-generate-001"` | Imagen model identifier |
| `**kwargs` | `Any` | -- | Additional config passed to the API (e.g., `number_of_images`, `aspect_ratio`) |

**Returns:** A list of dictionary representations of the generated image objects.

### Related GeminiClient Methods

The `GeminiClient` also exposes image editing and upscaling:

```python
def generate_images(self, prompt: str, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
def upscale_image(self, image: Any, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
def edit_image(self, prompt: str, image: Any, model: str = "imagen-latest", **kwargs) -> list[dict[str, Any]]
```

## Google AI Ultra Support

The Codomyrmex ecosystem is optimized for the **Google AI Ultra subscription** via the Gemini API.

Accessing models with an Ultra-level API key (via Google Workspace or Consumer Google One) unlocks the highest usage limits and advanced multimodal functionality:

- **Gemini Core:** Direct high-limit access to models like Gemini 1.5 Pro.
- **Advanced Video & Audio:** Natively supports long-running inference for high-definition video tools like Veo 3 / 3.1, including Flow & Whisk capabilities, intrinsically generating native audio alongside the video.
- **US Regional Previews:** Support for Deep Think Agent features and Project Mariner (automated browser tasks) are accessible exclusively for US regions.

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

See [AGENTS.md](AGENTS.md), [SPEC.md](SPEC.md), and [PAI.md](PAI.md) for companion documentation.
