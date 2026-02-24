"""Unit tests for configuration management."""

import os

import pytest

from codomyrmex.scrape.config import ScrapeConfig, get_config, reset_config, set_config
from codomyrmex.scrape.exceptions import ScrapeValidationError


@pytest.mark.unit
class TestScrapeConfig:
    """Test ScrapeConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ScrapeConfig()
        assert config.api_key is None
        assert config.base_url == "https://api.firecrawl.dev"
        assert config.default_timeout == 30.0
        assert config.max_retries == 3
        assert config.respect_robots_txt is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = ScrapeConfig(
            api_key="test-key",
            base_url="https://custom.api.com",
            default_timeout=60.0,
            max_retries=5,
        )
        assert config.api_key == "test-key"
        assert config.base_url == "https://custom.api.com"
        assert config.default_timeout == 60.0
        assert config.max_retries == 5

    def test_from_env(self):
        """Test creating config from environment variables."""
        orig_api = os.environ.get("FIRECRAWL_API_KEY")
        orig_timeout = os.environ.get("SCRAPE_TIMEOUT")
        orig_retries = os.environ.get("SCRAPE_MAX_RETRIES")
        try:
            os.environ["FIRECRAWL_API_KEY"] = "env-key"
            os.environ["SCRAPE_TIMEOUT"] = "45.0"
            os.environ["SCRAPE_MAX_RETRIES"] = "5"

            config = ScrapeConfig.from_env()
            assert config.api_key == "env-key"
            assert config.default_timeout == 45.0
            assert config.max_retries == 5
        finally:
            for key, orig in [
                ("FIRECRAWL_API_KEY", orig_api),
                ("SCRAPE_TIMEOUT", orig_timeout),
                ("SCRAPE_MAX_RETRIES", orig_retries),
            ]:
                if orig is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig

    def test_from_env_fc_api_key(self):
        """Test creating config from FC_API_KEY environment variable."""
        orig_fc = os.environ.get("FC_API_KEY")
        orig_firecrawl = os.environ.get("FIRECRAWL_API_KEY")
        try:
            os.environ["FC_API_KEY"] = "fc-key"
            os.environ.pop("FIRECRAWL_API_KEY", None)

            config = ScrapeConfig.from_env()
            assert config.api_key == "fc-key"
        finally:
            if orig_fc is None:
                os.environ.pop("FC_API_KEY", None)
            else:
                os.environ["FC_API_KEY"] = orig_fc
            if orig_firecrawl is None:
                os.environ.pop("FIRECRAWL_API_KEY", None)
            else:
                os.environ["FIRECRAWL_API_KEY"] = orig_firecrawl

    def test_from_env_respect_robots_txt(self):
        """Test respect_robots_txt from environment."""
        orig = os.environ.get("SCRAPE_RESPECT_ROBOTS_TXT")
        try:
            os.environ["SCRAPE_RESPECT_ROBOTS_TXT"] = "false"
            config = ScrapeConfig.from_env()
            assert config.respect_robots_txt is False

            os.environ["SCRAPE_RESPECT_ROBOTS_TXT"] = "true"
            config = ScrapeConfig.from_env()
            assert config.respect_robots_txt is True
        finally:
            if orig is None:
                os.environ.pop("SCRAPE_RESPECT_ROBOTS_TXT", None)
            else:
                os.environ["SCRAPE_RESPECT_ROBOTS_TXT"] = orig

    def test_validate_without_api_key(self):
        """Test validation without API key."""
        config = ScrapeConfig(api_key=None)
        with pytest.raises(ScrapeValidationError):
            config.validate()

    def test_validate_with_api_key(self):
        """Test validation with API key."""
        config = ScrapeConfig(api_key="test-key")
        # Should not raise
        config.validate()

    def test_validate_invalid_timeout(self):
        """Test validation with invalid timeout."""
        config = ScrapeConfig(api_key="test-key", default_timeout=-1.0)
        with pytest.raises(ScrapeValidationError):
            config.validate()

    def test_validate_invalid_retries(self):
        """Test validation with invalid retries."""
        config = ScrapeConfig(api_key="test-key", max_retries=-1)
        with pytest.raises(ScrapeValidationError):
            config.validate()

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = ScrapeConfig(api_key="test-key", default_timeout=60.0)
        result = config.to_dict()
        assert "api_key" in result
        assert result["api_key"] == "***"  # Masked
        assert result["default_timeout"] == 60.0
        assert result["base_url"] == "https://api.firecrawl.dev"


@pytest.mark.unit
class TestConfigFunctions:
    """Test global config functions."""

    def test_get_config_default(self):
        """Test getting default config."""
        reset_config()
        config = get_config()
        assert isinstance(config, ScrapeConfig)

    def test_set_config(self):
        """Test setting global config."""
        reset_config()
        config = ScrapeConfig(api_key="test-key")
        set_config(config)
        assert get_config() == config

    def test_reset_config(self):
        """Test resetting global config."""
        config = ScrapeConfig(api_key="test-key")
        set_config(config)
        reset_config()
        # After reset, get_config should create a new instance
        new_config = get_config()
        # They should be different instances
        assert new_config is not config

