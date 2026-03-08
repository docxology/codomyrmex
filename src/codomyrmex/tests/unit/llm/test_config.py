"""Tests for llm.config module."""

import json
import os
from pathlib import Path
from unittest import mock

import pytest

from codomyrmex.llm.config import (
    LLMConfig,
    LLMConfigPresets,
    get_config,
    reset_config,
    set_config,
)


@pytest.mark.unit
class TestLLMConfigInit:
    """Test suite for LLMConfig initialization."""

    def test_default_init(self):
        """Test initialization with default values."""
        config = LLMConfig()

        assert config.model == LLMConfig.DEFAULT_MODEL
        assert config.temperature == LLMConfig.DEFAULT_TEMPERATURE
        assert config.max_tokens == LLMConfig.DEFAULT_MAX_TOKENS
        assert config.top_p == LLMConfig.DEFAULT_TOP_P
        assert config.top_k == LLMConfig.DEFAULT_TOP_K
        assert config.timeout == LLMConfig.DEFAULT_TIMEOUT
        # Base URL might come from env, so check it matches default logic or is set
        assert config.base_url is not None

        # Check derived paths
        assert isinstance(config.output_root, Path)
        assert isinstance(config.test_results_dir, Path)
        assert config.test_results_dir == config.output_root / "test_results"

    def test_init_with_args(self):
        """Test initialization with explicit arguments."""
        config = LLMConfig(
            model="custom-model",
            temperature=0.5,
            max_tokens=500,
            top_p=0.8,
            top_k=20,
            timeout=60,
            base_url="http://custom:11434",
            output_root="/tmp/custom_root",
        )

        assert config.model == "custom-model"
        assert config.temperature == 0.5
        assert config.max_tokens == 500
        assert config.top_p == 0.8
        assert config.top_k == 20
        assert config.timeout == 60
        assert config.base_url == "http://custom:11434"
        assert str(config.output_root) == "/tmp/custom_root"


@pytest.mark.unit
class TestLLMConfigEnvVars:
    """Test suite for environment variable handling in LLMConfig."""

    def test_env_var_overrides(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("LLM_MODEL", "env-model")
        monkeypatch.setenv("LLM_TEMPERATURE", "1.5")
        monkeypatch.setenv("LLM_MAX_TOKENS", "2000")
        monkeypatch.setenv("LLM_TOP_P", "0.95")
        monkeypatch.setenv("LLM_TOP_K", "100")
        monkeypatch.setenv("LLM_TIMEOUT", "120")
        monkeypatch.setenv("LLM_BASE_URL", "http://env:11434")
        monkeypatch.setenv("LLM_OUTPUT_ROOT", "/tmp/env_root")

        config = LLMConfig()

        assert config.model == "env-model"
        assert config.temperature == 1.5
        assert config.max_tokens == 2000
        assert config.top_p == 0.95
        assert config.top_k == 100
        assert config.timeout == 120
        assert config.base_url == "http://env:11434"
        assert str(config.output_root) == "/tmp/env_root"

    def test_env_var_invalid_types(self, monkeypatch):
        """Test graceful handling of invalid environment variable types."""
        monkeypatch.setenv("LLM_TEMPERATURE", "not-a-float")
        monkeypatch.setenv("LLM_MAX_TOKENS", "not-an-int")

        config = LLMConfig()

        # Should fall back to defaults
        assert config.temperature == LLMConfig.DEFAULT_TEMPERATURE
        assert config.max_tokens == LLMConfig.DEFAULT_MAX_TOKENS


@pytest.mark.unit
class TestLLMConfigMethods:
    """Test suite for LLMConfig methods."""

    def test_get_generation_options(self):
        """Test generation options dictionary creation."""
        config = LLMConfig(temperature=0.7, top_p=0.9, top_k=40, max_tokens=100)
        options = config.get_generation_options()

        assert options == {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 100,
        }

    def test_get_client_kwargs(self):
        """Test client kwargs dictionary creation."""
        config = LLMConfig(base_url="http://test:11434", model="test-model", timeout=30)
        kwargs = config.get_client_kwargs()

        assert kwargs == {
            "base_url": "http://test:11434",
            "model": "test-model",
            "timeout": 30,
        }

    def test_to_dict(self):
        """Test dictionary representation of config."""
        config = LLMConfig(model="dict-test")
        d = config.to_dict()

        assert d["model"] == "dict-test"
        assert "temperature" in d
        assert "output_root" in d
        assert isinstance(d["output_root"], str)


@pytest.mark.unit
class TestLLMConfigPersistence:
    """Test suite for saving and loading configuration."""

    def test_save_and_load_config(self, tmp_path):
        """Test saving config to file and loading it back."""
        config_file = tmp_path / "test_config.json"

        original_config = LLMConfig(
            model="persist-test", temperature=0.123, output_root=tmp_path
        )

        original_config.save_config(config_file)

        assert config_file.exists()

        loaded_config = LLMConfig.from_file(config_file)

        assert loaded_config.model == original_config.model
        assert loaded_config.temperature == original_config.temperature
        assert str(loaded_config.output_root) == str(original_config.output_root)

    def test_save_default_path(self, tmp_path):
        """Test saving to default path inside output_root."""
        # We need to mock _ensure_directories to avoid creating real dirs in protected spots
        # or use a tmp_path as output_root
        config = LLMConfig(output_root=tmp_path)

        # Should save to tmp_path/config.json
        config.save_config()

        expected_file = tmp_path / "config.json"
        assert expected_file.exists()


@pytest.mark.unit
class TestGlobalConfig:
    """Test suite for global configuration management."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def teardown_method(self):
        """Reset config after each test."""
        reset_config()

    def test_get_config_creates_default(self):
        """Test get_config creates a new instance if none exists."""
        config = get_config()
        assert isinstance(config, LLMConfig)

        # Should return same instance on second call
        assert get_config() is config

    def test_set_config(self):
        """Test setting a custom global config."""
        custom_config = LLMConfig(model="global-test")
        set_config(custom_config)

        assert get_config() is custom_config
        assert get_config().model == "global-test"

    def test_reset_config(self):
        """Test resetting global config."""
        config1 = get_config()
        reset_config()
        config2 = get_config()

        assert config1 is not config2


@pytest.mark.unit
class TestLLMConfigPresets:
    """Test suite for configuration presets."""

    def test_creative_preset(self):
        """Test creative preset values."""
        config = LLMConfigPresets.creative()
        assert config.temperature > 0.7  # Should be high
        assert config.top_p > 0.9

    def test_precise_preset(self):
        """Test precise preset values."""
        config = LLMConfigPresets.precise()
        assert config.temperature < 0.5  # Should be low
        assert config.top_k < 40

    def test_fast_preset(self):
        """Test fast preset values."""
        config = LLMConfigPresets.fast()
        assert config.max_tokens < 1000
        assert config.timeout < 30

    def test_comprehensive_preset(self):
        """Test comprehensive preset values."""
        config = LLMConfigPresets.comprehensive()
        assert config.max_tokens >= 2000
