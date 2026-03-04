"""MCP tool definitions for the multimodal module.

Exposes image generation capabilities via MCP tools.
Requires Google AI SDK (Gemini) credentials.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_image_generator():
    """Lazy import of ImageGenerator to avoid circular deps."""
    from codomyrmex.multimodal.image_generation import ImageGenerator

    return ImageGenerator


@mcp_tool(
    category="multimodal",
    description="Generate images from a text prompt using Imagen 4 via Google AI SDK.",
)
def multimodal_generate_image(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
) -> dict[str, Any]:
    """Generate images from a text prompt.

    Requires GOOGLE_API_KEY environment variable to be set.

    Args:
        prompt: Text description of the image to generate.
        model: Image generation model (default: imagen-4.0-generate-001).

    Returns:
        dict with keys: status, images (list of image dicts), count
    """
    try:
        if not prompt or not prompt.strip():
            return {"status": "error", "message": "prompt must not be empty"}

        gen_cls = _get_image_generator()
        generator = gen_cls()
        images = generator.generate(prompt=prompt, model=model)
        return {
            "status": "success",
            "images": images,
            "count": len(images),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="multimodal",
    description="Check if the multimodal image generation backend is available.",
)
def multimodal_check() -> dict[str, Any]:
    """Check availability of the multimodal image generation backend.

    Verifies that the Google AI SDK (GeminiClient) can be imported.

    Returns:
        dict with keys: status, available, backend
    """
    try:
        _get_image_generator()
        return {
            "status": "success",
            "available": True,
            "backend": "google-ai-sdk",
        }
    except ImportError as exc:
        return {
            "status": "success",
            "available": False,
            "backend": "google-ai-sdk",
            "message": str(exc),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
