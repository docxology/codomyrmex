"""Vision-Language Model client using Ollama.

Provides image analysis via local Ollama VLM models (llava, bakllava).

Example::

    client = VLMClient()
    response = client.analyze_image("photo.jpg", "What is in this image?")
    print(response.text)
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any

from .models import VLMConfig, VLMResponse

logger = logging.getLogger(__name__)


class VLMClient:
    """Client for Vision-Language Models via Ollama.

    Connects to a local Ollama server and sends images with prompts
    to VLM models like ``llava`` or ``bakllava``.

    Args:
        config: VLM configuration.

    Example::

        client = VLMClient(VLMConfig(model_name="bakllava"))
        if client.is_available():
            response = client.analyze_image("img.png", "Describe this image")
    """

    def __init__(self, config: VLMConfig | None = None) -> None:
        self._config = config or VLMConfig()

    @property
    def config(self) -> VLMConfig:
        """Return the client configuration."""
        return self._config

    @property
    def base_url(self) -> str:
        """Return the Ollama API base URL."""
        return f"http://{self._config.host}:{self._config.port}"

    def is_available(self) -> bool:
        """Check if the Ollama server is reachable and the model exists.

        Returns:
            ``True`` if the server responds and the model is available.
        """
        try:
            import urllib.request

            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                models = [
                    m.get("name", "").split(":")[0] for m in data.get("models", [])
                ]
                return self._config.model_name in models
        except Exception as _exc:
            return False

    def analyze_image(
        self,
        image_path: str | Path,
        prompt: str = "Describe this image in detail.",
    ) -> VLMResponse:
        """Analyze an image with a VLM prompt.

        Args:
            image_path: Path to the image file.
            prompt: Text prompt for the VLM.

        Returns:
            A :class:`VLMResponse` with the generated text.

        Raises:
            FileNotFoundError: If the image file doesn't exist.
            RuntimeError: If the Ollama request fails.
        """
        path = Path(image_path)
        if not path.exists():
            msg = f"Image not found: {path}"
            raise FileNotFoundError(msg)

        image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")

        return self._call_ollama(prompt, images=[image_b64])

    def extract_text(self, image_path: str | Path) -> str:
        """Extract text content from an image (OCR-like via VLM).

        Args:
            image_path: Path to the image.

        Returns:
            Extracted text string.
        """
        response = self.analyze_image(
            image_path,
            prompt="Extract and return ALL text content visible in this image. "
            "Return only the text, preserving layout where possible.",
        )
        return response.text

    def describe_for_annotation(
        self,
        image_path: str | Path,
        prompt: str = "",
    ) -> VLMResponse:
        """Analyze an image and return structured annotation data.

        Args:
            image_path: Path to the image.
            prompt: Custom prompt (defaults to annotation prompt).

        Returns:
            A :class:`VLMResponse` with structured annotation text.
        """
        annotation_prompt = prompt or (
            "Analyze this image and identify all notable objects, text, "
            "and visual elements. For each element, provide:\n"
            "- label: what it is\n"
            "- approximate_position: top-left/center/bottom-right etc.\n"
            "- confidence: high/medium/low\n"
            "- attributes: color, size, or other notable properties\n"
            "Format as a JSON array."
        )
        return self.analyze_image(image_path, annotation_prompt)

    def _call_ollama(
        self,
        prompt: str,
        images: list[str] | None = None,
    ) -> VLMResponse:
        """Make a request to the Ollama API.

        Args:
            prompt: Text prompt.
            images: list of base64-encoded images.

        Returns:
            A :class:`VLMResponse`.

        Raises:
            RuntimeError: If the request fails.
        """
        import urllib.request

        payload: dict[str, Any] = {
            "model": self._config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self._config.temperature,
                "num_predict": self._config.max_tokens,
            },
        }
        if images:
            payload["images"] = images

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self._config.timeout) as resp:
                result = json.loads(resp.read())
                return VLMResponse(
                    text=result.get("response", ""),
                    model=result.get("model", self._config.model_name),
                    metadata={
                        "total_duration": result.get("total_duration", 0),
                        "eval_count": result.get("eval_count", 0),
                    },
                )
        except Exception as exc:
            msg = f"Ollama request failed: {exc}"
            raise RuntimeError(msg) from exc


__all__ = ["VLMClient"]
