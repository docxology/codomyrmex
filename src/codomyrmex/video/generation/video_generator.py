"""
Video Generation module using Google AI (Veo 2.0).
"""

from typing import Any

from codomyrmex.agents.gemini.gemini_client import GeminiClient


class VideoGenerator:
    """
    Generator for creating videos using the Google AI SDK (via GeminiClient).
    Defaults to the Veo 2.0 model (``veo-2.0-generate-001``).
    """

    def __init__(self, client: GeminiClient | None = None) -> None:
        """
        Initialize the VideoGenerator.

        Args:
            client: An existing GeminiClient. If None, a new client is instantiated.
        """
        self.client = client or GeminiClient()

    def generate(
        self, prompt: str, model: str = "veo-2.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        """
        Generate videos from a text prompt.

        Args:
            prompt: Text description of the video to generate.
            model: The video generation model to use. Default is Veo 2.0.
            **kwargs: Additional generation parameters.

        Returns:
            A list of dictionary representations of the generated video objects.
        """
        return self.client.generate_videos(prompt=prompt, model=model, **kwargs)
