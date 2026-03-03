"""Configuration for the aider module."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AiderConfig:
    """Configuration for aider operations."""

    model: str = field(
        default_factory=lambda: os.getenv("AIDER_MODEL", "claude-sonnet-4-6")
    )
    anthropic_api_key: str = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "")
    )
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    timeout: int = field(default_factory=lambda: int(os.getenv("AIDER_TIMEOUT", "300")))

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_any_key(self) -> bool:
        return self.has_anthropic_key or self.has_openai_key


def get_config() -> AiderConfig:
    """Return an AiderConfig populated from environment variables."""
    return AiderConfig()
