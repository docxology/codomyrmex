"""
Image Generation module using Google AI (Imagen 4).
"""

from typing import Any

from codomyrmex.agents.gemini.gemini_client import GeminiClient


class ImageGenerator:
    """
    Generator for creating images using the Google AI SDK (via GeminiClient).
    Defaults to the Imagen 4 model (``imagen-4.0-generate-001``).
    """

    def __init__(self, client: GeminiClient | None = None) -> None:
        """
        Initialize the ImageGenerator.

        Args:
            client: An existing GeminiClient. If None, a new client is instantiated.
        """
        self.client = client or GeminiClient()

    def generate(
        self, prompt: str, model: str = "imagen-4.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            model: The image generation model to use. Default is Imagen 4.
            **kwargs: Additional generation parameters (e.g., number of images, aspect ratio).

        Returns:
            A list of dictionary representations of the generated image objects.
        """
        return self.client.generate_images(prompt=prompt, model=model, **kwargs)
