"""Tests for video MCP tools."""

from __future__ import annotations


class TestVideoGetConfig:
    """Tests for video_get_config MCP tool."""

    def test_get_config_returns_success(self):
        from codomyrmex.video.mcp_tools import video_get_config

        result = video_get_config()
        assert result["status"] == "success"
        assert "config" in result
        assert result["valid"] is True

    def test_get_config_has_expected_keys(self):
        from codomyrmex.video.mcp_tools import video_get_config

        result = video_get_config()
        config = result["config"]
        assert "default_output_format" in config
        assert "default_codec" in config
        assert "default_fps" in config
        assert "thumbnail_width" in config

    def test_get_config_default_values(self):
        from codomyrmex.video.mcp_tools import video_get_config

        result = video_get_config()
        config = result["config"]
        assert config["default_output_format"] == "mp4"
        assert config["default_fps"] == 30


class TestVideoListFormats:
    """Tests for video_list_formats MCP tool."""

    def test_list_formats_success(self):
        from codomyrmex.video.mcp_tools import video_list_formats

        result = video_list_formats()
        assert result["status"] == "success"
        assert len(result["video_codecs"]) > 0
        assert len(result["audio_codecs"]) > 0
        assert len(result["filters"]) > 0

    def test_list_formats_codec_structure(self):
        from codomyrmex.video.mcp_tools import video_list_formats

        result = video_list_formats()
        codec = result["video_codecs"][0]
        assert "name" in codec
        assert "value" in codec


class TestVideoCheckAvailability:
    """Tests for video_check_availability MCP tool."""

    def test_availability_returns_booleans(self):
        from codomyrmex.video.mcp_tools import video_check_availability

        result = video_check_availability()
        assert result["status"] == "success"
        assert isinstance(result["processing"], bool)
        assert isinstance(result["extraction"], bool)
        assert isinstance(result["analysis"], bool)
        assert isinstance(result["pil"], bool)
