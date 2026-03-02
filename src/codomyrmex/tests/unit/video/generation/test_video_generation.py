"""
Unit tests for the Video Generation module.
Zero-mock tests leveraging GeminiClient and the real Google AI API.
"""

import os

import pytest

from codomyrmex.agents.gemini.gemini_client import GeminiClient
from codomyrmex.video.generation.video_generator import VideoGenerator

_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
_skip_no_key = pytest.mark.skipif(not _GEMINI_KEY, reason="GEMINI_API_KEY not set")


class FakeGeminiClient(GeminiClient):
    """Fake GeminiClient for testing without API calls."""

    def __init__(self, config=None):
        self.calls = []

    def generate_videos(self, prompt, model="veo-latest", **kwargs):
        self.calls.append(
            {
                "method": "generate_videos",
                "prompt": prompt,
                "model": model,
                "kwargs": kwargs,
            }
        )
        return [{"video_bytes": b"fake_data"}]


class TestVideoGenerator:
    """Test suite for the VideoGenerator component."""

    def test_init_creates_default_client(self):
        """Test that init creates a GeminiClient if none is provided."""
        generator = VideoGenerator()
        assert isinstance(generator.client, GeminiClient)

    def test_init_uses_provided_client(self):
        """Test that init uses the provided client."""
        client = GeminiClient()
        generator = VideoGenerator(client=client)
        assert generator.client is client

    @_skip_no_key
    def test_generate_video_success(self):
        """Test generating a video using the real API."""
        generator = VideoGenerator()

        # Test with standard veo-2.0-generate-001 model
        results = generator.generate(
            prompt="A timelapse of a blooming rose, high definition.",
            number_of_videos=1,
            aspect_ratio="16:9",
        )

        assert isinstance(results, list)
        assert len(results) == 1
        assert (
            "video_bytes" in results[0] or "url" in results[0] or "base64" in results[0]
        )

    def test_generate_calls_client(self):
        """Test that generate calls the client with correct arguments using a fake."""
        fake_client = FakeGeminiClient()
        generator = VideoGenerator(client=fake_client)

        prompt = "test prompt"
        kwargs = {"number_of_videos": 2, "aspect_ratio": "16:9"}

        results = generator.generate(prompt=prompt, **kwargs)

        assert len(fake_client.calls) == 1
        call = fake_client.calls[0]
        assert call["method"] == "generate_videos"
        assert call["prompt"] == prompt
        assert call["model"] == "veo-2.0-generate-001"
        assert call["kwargs"] == kwargs
        assert results == [{"video_bytes": b"fake_data"}]
