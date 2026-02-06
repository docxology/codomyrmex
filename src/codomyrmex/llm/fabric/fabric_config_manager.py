"""Fabric Config Manager for Codomyrmex LLM module.

Manages configuration for Fabric AI framework integration.
"""

import json
import os
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class FabricPattern:
    """Represents a Fabric pattern."""
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class FabricConfig:
    """Fabric configuration."""
    api_key: str | None = None
    default_model: str = "gpt-4"
    patterns_dir: str | None = None
    custom_patterns: dict[str, FabricPattern] = field(default_factory=dict)


class FabricConfigManager:
    """Manages Fabric configuration and patterns."""

    def __init__(self, config_path: str | None = None):
        """Initialize config manager."""
        self.config_path = config_path or os.path.expanduser("~/.config/fabric/config.json")
        self.config = self._load_config()
        self.patterns: dict[str, FabricPattern] = {}

    def _load_config(self) -> FabricConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                return FabricConfig(
                    api_key=data.get("api_key"),
                    default_model=data.get("default_model", "gpt-4"),
                    patterns_dir=data.get("patterns_dir")
                )
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        return FabricConfig()

    def save_config(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({
                "api_key": self.config.api_key,
                "default_model": self.config.default_model,
                "patterns_dir": self.config.patterns_dir
            }, f, indent=2)

    def get_pattern(self, name: str) -> FabricPattern | None:
        """Get a pattern by name."""
        return self.patterns.get(name)

    def add_pattern(self, pattern: FabricPattern):
        """Add a custom pattern."""
        self.patterns[pattern.name] = pattern
        self.config.custom_patterns[pattern.name] = pattern

    def list_patterns(self) -> list[str]:
        """List available patterns."""
        return list(self.patterns.keys())


# Convenience functions
def get_fabric_config() -> FabricConfig:
    """Get Fabric configuration."""
    manager = FabricConfigManager()
    return manager.config
