"""Tests for multimodal MCP tools.

Zero-mock tests for the multimodal MCP tools. Since image generation
requires Google AI SDK credentials, generation tests are skip-guarded.
"""

from __future__ import annotations

import os

import pytest

from codomyrmex.multimodal.mcp_tools import (
    multimodal_check,
    multimodal_generate_image,
)

_HAS_GOOGLE_KEY = bool(os.environ.get("GOOGLE_API_KEY"))


class TestMultimodalCheck:
    """Tests for multimodal_check."""

    def test_returns_status(self):
        """Check always returns a status key."""
        result = multimodal_check()
        assert "status" in result

    def test_backend_name(self):
        """Backend is identified as google-ai-sdk."""
        result = multimodal_check()
        assert result["backend"] == "google-ai-sdk"

    def test_available_is_bool(self):
        """available field is a boolean when status is success."""
        result = multimodal_check()
        if result["status"] == "success":
            assert isinstance(result["available"], bool)


class TestMultimodalGenerateImage:
    """Tests for multimodal_generate_image."""

    def test_empty_prompt_error(self):
        """Empty prompt returns error."""
        result = multimodal_generate_image(prompt="")
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()

    def test_whitespace_prompt_error(self):
        """Whitespace-only prompt returns error."""
        result = multimodal_generate_image(prompt="   ")
        assert result["status"] == "error"

    @pytest.mark.skipif(not _HAS_GOOGLE_KEY, reason="GOOGLE_API_KEY not set")
    def test_generate_with_key(self):
        """Actual generation when key is available."""
        result = multimodal_generate_image(
            prompt="A simple red circle on white background"
        )
        assert result["status"] == "success"
        assert isinstance(result["images"], list)
