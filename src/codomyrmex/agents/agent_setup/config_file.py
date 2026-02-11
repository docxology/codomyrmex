"""YAML configuration file persistence for agent credentials.

Default location: ``~/.codomyrmex/agents.yaml``

Schema::

    agents:
      claude:
        api_key: sk-ant-...
        model: claude-3-opus-20240229
      ollama:
        base_url: http://localhost:11434
        default_model: llama3.2
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

DEFAULT_CONFIG_PATH = Path("~/.codomyrmex/agents.yaml").expanduser()

# All agent sections that may appear in the YAML
_AGENT_SECTIONS = [
    "claude", "codex", "o1", "deepseek", "qwen",
    "jules", "opencode", "gemini", "mistral_vibe", "every_code",
    "ollama",
]


def _ensure_yaml():
    """Import PyYAML, falling back gracefully."""
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for config file support. "
            "Install with: uv pip install pyyaml"
        )


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load agent config from a YAML file.

    Args:
        path: Config file path (default ``~/.codomyrmex/agents.yaml``).

    Returns:
        Parsed config dict. Returns ``{"agents": {}}`` if file does not exist.
    """
    yaml = _ensure_yaml()
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH

    if not config_path.exists():
        logger.debug("Config file not found: %s — returning empty config", config_path)
        return {"agents": {}}

    with open(config_path) as fh:
        data = yaml.safe_load(fh) or {}

    if "agents" not in data:
        data["agents"] = {}

    return data


def save_config(data: dict[str, Any], path: Path | str | None = None) -> Path:
    """Save agent config to a YAML file.

    Creates parent directories if needed. Writes with restricted
    permissions (``0o600``) since the file may contain API keys.

    Args:
        data: Config dict to persist.
        path: Destination path (default ``~/.codomyrmex/agents.yaml``).

    Returns:
        Resolved path that was written.
    """
    yaml = _ensure_yaml()
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)

    # Restrict permissions — file may contain secrets
    try:
        config_path.chmod(0o600)
    except OSError:
        pass  # Windows or other OS where chmod is limited

    logger.info("Config saved to %s", config_path)
    return config_path


def merge_with_env(config: dict[str, Any]) -> dict[str, str]:
    """Merge YAML config values into a flat env-style dict.

    Returns a dict suitable for passing to ``AgentConfig()`` as keyword
    overrides or for setting environment variables temporarily.

    The mapping follows AgentConfig field conventions, e.g.
    ``config["agents"]["claude"]["api_key"]`` → ``{"claude_api_key": "..."}``
    """
    flat: dict[str, str] = {}
    agents = config.get("agents", {})

    for section_name, section_data in agents.items():
        if not isinstance(section_data, dict):
            continue
        for key, value in section_data.items():
            if value is not None:
                flat_key = f"{section_name}_{key}"
                flat[flat_key] = str(value)

    return flat
