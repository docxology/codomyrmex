"""
Unit tests for the Multimodal Image Generation module.
Zero-mock tests leveraging GeminiClient and the real Google AI API.
"""

import os

import pytest

from codomyrmex.agents.gemini.gemini_client import GeminiClient
from codomyrmex.multimodal.image_generation import ImageGenerator

_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
_skip_no_key = pytest.mark.skipif(not _GEMINI_KEY, reason="GEMINI_API_KEY not set")


class _StubGeminiClient(GeminiClient):
    """Concrete stub for GeminiClient — records calls, returns minimal data.

    Not a mock: does not use unittest.mock or MagicMock. It is a real
    subclass whose generate_images override is used to verify the calling
    convention of ImageGenerator without needing a live API key.
    """

    def __init__(self, config=None):
        self.calls = []

    def generate_images(self, prompt, model="imagen-latest", **kwargs):
        self.calls.append(
            {
                "method": "generate_images",
                "prompt": prompt,
                "model": model,
                "kwargs": kwargs,
            }
        )
        return [{"image_bytes": b"stub_data"}]


class TestImageGenerator:
    """Test suite for the ImageGenerator component."""

    def test_init_creates_default_client(self):
        """Test that init creates a GeminiClient if none is provided."""
        # Note: This checks strictly type, not that it's connected
        generator = ImageGenerator()
        assert isinstance(generator.client, GeminiClient)

    def test_init_uses_provided_client(self):
        """Test that init uses the provided client."""
        client = GeminiClient()
        generator = ImageGenerator(client=client)
        assert generator.client is client

    @_skip_no_key
    def test_generate_image_success(self):
        """Test generating an image using the real API."""
        generator = ImageGenerator()

        # Test with standard imagen-4.0-generate-001 model
        results = generator.generate(
            prompt="A photorealistic blue butterfly resting on a dandelion, morning light.",
            number_of_images=1,
            aspect_ratio="1:1",
        )

        assert isinstance(results, list)
        assert len(results) == 1
        assert (
            "image_bytes" in results[0] or "url" in results[0] or "base64" in results[0]
        )

    def test_generate_calls_client(self):
        """Test that generate calls the client with correct arguments using a fake."""
        fake_client = _StubGeminiClient()
        generator = ImageGenerator(client=fake_client)

        prompt = "test prompt"
        kwargs = {"number_of_images": 2, "aspect_ratio": "16:9"}

        results = generator.generate(prompt=prompt, **kwargs)

        assert len(fake_client.calls) == 1
        call = fake_client.calls[0]
        assert call["method"] == "generate_images"
        assert call["prompt"] == prompt
        assert call["model"] == "imagen-4.0-generate-001"
        assert call["kwargs"] == kwargs
        assert results == [{"image_bytes": b"stub_data"}]
