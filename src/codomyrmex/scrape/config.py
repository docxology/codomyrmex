"""Configuration management for the scrape module.

This module handles configuration loading, validation, and management
for scraping operations, including API key management and default settings.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapeConfig:
    """Configuration for scraping operations.

    Attributes:
        api_key: API key for the scraping service (e.g., Firecrawl)
        base_url: Base URL for the scraping API
        default_timeout: Default timeout for requests in seconds
        default_formats: Default formats to request
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        rate_limit: Rate limit (requests per second)
        user_agent: User agent string to use for requests
        respect_robots_txt: Whether to respect robots.txt by default
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """

    api_key: Optional[str] = None
    base_url: str = "https://api.firecrawl.dev"
    default_timeout: float = 30.0
    default_formats: list[str] = field(default_factory=lambda: ["markdown"])
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Optional[float] = None
    user_agent: str = "Codomyrmex-Scraper/0.1.0"
    respect_robots_txt: bool = True

    @classmethod
    def from_env(cls) -> "ScrapeConfig":
        """Create configuration from environment variables.

        Environment variables:
            FIRECRAWL_API_KEY: API key for Firecrawl service
            SCRAPE_BASE_URL: Base URL for scraping API (default: https://api.firecrawl.dev)
            SCRAPE_TIMEOUT: Default timeout in seconds (default: 30.0)
            SCRAPE_MAX_RETRIES: Maximum retry attempts (default: 3)
            SCRAPE_RETRY_DELAY: Delay between retries in seconds (default: 1.0)
            SCRAPE_RATE_LIMIT: Rate limit in requests per second (optional)
            SCRAPE_USER_AGENT: User agent string (optional)
            SCRAPE_RESPECT_ROBOTS_TXT: Whether to respect robots.txt (default: true)

        Returns:
            ScrapeConfig instance configured from environment
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        api_key = os.getenv("FIRECRAWL_API_KEY") or os.getenv("FC_API_KEY")
        base_url = os.getenv("SCRAPE_BASE_URL", "https://api.firecrawl.dev")
        timeout = float(os.getenv("SCRAPE_TIMEOUT", "30.0"))
        max_retries = int(os.getenv("SCRAPE_MAX_RETRIES", "3"))
        retry_delay = float(os.getenv("SCRAPE_RETRY_DELAY", "1.0"))
        rate_limit = os.getenv("SCRAPE_RATE_LIMIT")
        user_agent = os.getenv("SCRAPE_USER_AGENT", "Codomyrmex-Scraper/0.1.0")
        respect_robots = os.getenv("SCRAPE_RESPECT_ROBOTS_TXT", "true").lower() == "true"

        return cls(
            api_key=api_key,
            base_url=base_url,
            default_timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            rate_limit=float(rate_limit) if rate_limit else None,
            user_agent=user_agent,
            respect_robots_txt=respect_robots,
        )

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ScrapeValidationError: If the configuration is invalid
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        from .exceptions import ScrapeValidationError

        if not self.api_key:
            raise ScrapeValidationError(
                "API key is required. Set FIRECRAWL_API_KEY environment variable or pass api_key to ScrapeConfig."
            )

        if self.default_timeout <= 0:
            raise ScrapeValidationError(
                f"Timeout must be positive, got {self.default_timeout}",
                field="default_timeout",
                value=str(self.default_timeout),
            )

        if self.max_retries < 0:
            raise ScrapeValidationError(
                f"Max retries must be non-negative, got {self.max_retries}",
                field="max_retries",
                value=str(self.max_retries),
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result: Dict[str, any] = {
            "base_url": self.base_url,
            "default_timeout": self.default_timeout,
            "default_formats": self.default_formats,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "user_agent": self.user_agent,
            "respect_robots_txt": self.respect_robots_txt,
        }
        if self.api_key:
            result["api_key"] = "***"  # Mask API key in dict representation
        if self.rate_limit:
            result["rate_limit"] = self.rate_limit
        return result


# Global configuration instance
_config: Optional[ScrapeConfig] = None


def get_config() -> ScrapeConfig:
    """Get the global configuration instance.

    If no configuration has been set, creates one from environment variables.

    Returns:
        ScrapeConfig instance
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """
    global _config
    if _config is None:
        _config = ScrapeConfig.from_env()
    return _config


def set_config(config: ScrapeConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: ScrapeConfig instance to use globally
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:     """
    global _config
    _config = config
    logger.info("Scrape configuration updated")


def reset_config() -> None:
    """Reset the global configuration to None."""
    global _config
    _config = None
    logger.info("Scrape configuration reset")

