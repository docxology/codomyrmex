"""Tests for codomyrmex.agents.agentic_seek.agentic_seek_client.

Zero-mock tests covering class structure, method signatures,
config.ini parsing (with real temp files), and environment validation.
"""

import os
import tempfile

import pytest

from codomyrmex.agents.agentic_seek.agent_types import AgenticSeekConfig
from codomyrmex.agents.agentic_seek.agentic_seek_client import AgenticSeekClient

# ===================================================================
# Class structure
# ===================================================================

class TestAgenticSeekClientStructure:
    """Verify the client is importable and has expected methods."""

    def test_class_importable(self):
        assert AgenticSeekClient is not None

    def test_has_execute_impl(self):
        assert hasattr(AgenticSeekClient, "_execute_impl")

    def test_has_stream_impl(self):
        assert hasattr(AgenticSeekClient, "_stream_impl")

    def test_has_get_available_agents(self):
        assert hasattr(AgenticSeekClient, "get_available_agents")

    def test_has_classify_query(self):
        assert hasattr(AgenticSeekClient, "classify_query")

    def test_has_get_agent_status(self):
        assert hasattr(AgenticSeekClient, "get_agent_status")

    def test_has_validate_environment(self):
        assert hasattr(AgenticSeekClient, "validate_environment")

    def test_has_parse_config_ini(self):
        assert hasattr(AgenticSeekClient, "parse_config_ini")

    def test_instantiation(self):
        client = AgenticSeekClient()
        assert client is not None

    def test_instantiation_with_config(self):
        client = AgenticSeekClient(config={"agentic_seek_path": "/tmp"})
        assert client is not None


# ===================================================================
# get_available_agents
# ===================================================================

class TestGetAvailableAgents:
    def test_returns_all_five(self):
        client = AgenticSeekClient()
        agents = client.get_available_agents()
        assert len(agents) == 5

    def test_returns_list(self):
        client = AgenticSeekClient()
        agents = client.get_available_agents()
        assert isinstance(agents, list)


# ===================================================================
# classify_query
# ===================================================================

class TestClassifyQuery:
    def test_coder(self):
        client = AgenticSeekClient()
        from codomyrmex.agents.agentic_seek.agent_types import AgenticSeekAgentType
        result = client.classify_query("Write a Python script")
        assert result is AgenticSeekAgentType.CODER

    def test_casual(self):
        client = AgenticSeekClient()
        from codomyrmex.agents.agentic_seek.agent_types import AgenticSeekAgentType
        result = client.classify_query("Hi there")
        assert result is AgenticSeekAgentType.CASUAL


# ===================================================================
# validate_environment
# ===================================================================

class TestValidateEnvironment:
    def test_returns_dict(self):
        client = AgenticSeekClient()
        result = client.validate_environment()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        client = AgenticSeekClient()
        result = client.validate_environment()
        expected_keys = {"docker", "docker_compose", "ollama", "python", "uv", "repo_exists"}
        assert expected_keys == set(result.keys())

    def test_values_are_booleans(self):
        client = AgenticSeekClient()
        result = client.validate_environment()
        for key, val in result.items():
            assert isinstance(val, bool), f"{key} is not bool: {val}"


# ===================================================================
# parse_config_ini
# ===================================================================

class TestParseConfigIni:
    """Test config.ini parsing with real temporary files."""

    def _write_config(self, content: str) -> str:
        """Write content to a temp file and return the path."""
        fd, path = tempfile.mkstemp(suffix=".ini")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_basic_config(self):
        path = self._write_config(
            "[MAIN]\n"
            "is_local = True\n"
            "provider_name = ollama\n"
            "provider_model = deepseek-r1:14b\n"
            "provider_server_address = http://127.0.0.1:11434\n"
            "agent_name = Friday\n"
            "\n"
            "[BROWSER]\n"
            "headless_browser = True\n"
            "stealth_mode = False\n"
        )
        try:
            cfg = AgenticSeekClient.parse_config_ini(path)
            assert isinstance(cfg, AgenticSeekConfig)
            assert cfg.is_local is True
            assert cfg.provider_name == "ollama"
            assert cfg.agent_name == "Friday"
            assert cfg.stealth_mode is False
        finally:
            os.unlink(path)

    def test_api_provider_config(self):
        path = self._write_config(
            "[MAIN]\n"
            "is_local = False\n"
            "provider_name = openai\n"
            "provider_model = gpt-3.5-turbo\n"
            "agent_name = Jarvis\n"
            "languages = en zh fr\n"
            "\n"
            "[BROWSER]\n"
            "headless_browser = False\n"
        )
        try:
            cfg = AgenticSeekClient.parse_config_ini(path)
            assert cfg.is_local is False
            assert cfg.provider_name == "openai"
            assert cfg.languages == ["en", "zh", "fr"]
            assert cfg.headless_browser is False
        finally:
            os.unlink(path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            AgenticSeekClient.parse_config_ini("/nonexistent/config.ini")

    def test_missing_main_section_raises(self):
        path = self._write_config("[BROWSER]\nheadless_browser = True\n")
        try:
            with pytest.raises(ValueError, match="MAIN"):
                AgenticSeekClient.parse_config_ini(path)
        finally:
            os.unlink(path)

    def test_defaults_for_missing_keys(self):
        path = self._write_config("[MAIN]\nprovider_name = ollama\n")
        try:
            cfg = AgenticSeekClient.parse_config_ini(path)
            assert cfg.is_local is True  # default
            assert cfg.provider_model == "deepseek-r1:14b"  # default
            assert cfg.agent_name == "Friday"  # default
        finally:
            os.unlink(path)

    def test_boolean_parsing_variants(self):
        path = self._write_config(
            "[MAIN]\n"
            "is_local = yes\n"
            "speak = 1\n"
            "listen = false\n"
            "\n"
            "[BROWSER]\n"
        )
        try:
            cfg = AgenticSeekClient.parse_config_ini(path)
            assert cfg.is_local is True
            assert cfg.speak is True
            assert cfg.listen is False
        finally:
            os.unlink(path)

    def test_comma_separated_languages(self):
        path = self._write_config(
            "[MAIN]\n"
            "languages = en, zh, fr\n"
            "\n"
            "[BROWSER]\n"
        )
        try:
            cfg = AgenticSeekClient.parse_config_ini(path)
            assert cfg.languages == ["en", "zh", "fr"]
        finally:
            os.unlink(path)


# ===================================================================
# Module-level import
# ===================================================================

class TestModuleImport:
    """Verify the module re-export from __init__.py."""

    def test_import_from_init(self):
        from codomyrmex.agents.agentic_seek import AgenticSeekClient as C
        assert C is AgenticSeekClient

    def test_import_router(self):
        from codomyrmex.agents.agentic_seek import AgenticSeekRouter
        assert AgenticSeekRouter is not None

    def test_import_executor(self):
        from codomyrmex.agents.agentic_seek import AgenticSeekCodeExecutor
        assert AgenticSeekCodeExecutor is not None

    def test_import_planner(self):
        from codomyrmex.agents.agentic_seek import AgenticSeekTaskPlanner
        assert AgenticSeekTaskPlanner is not None
