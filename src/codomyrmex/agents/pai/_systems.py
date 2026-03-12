"""PAI Systems Mixin for bridge integration.

Provides core system status, config, security, and algorithm methods.
Extracted from pai_bridge.py.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

from ._models import ALGORITHM_PHASES, PAI_PRINCIPLES, RESPONSE_DEPTH_LEVELS

logger = get_logger(__name__)

# Upstream repository reference
PAI_UPSTREAM_URL = "https://github.com/danielmiessler/Personal_AI_Infrastructure"


class PAISystemsMixin:
    """Mixin for PAI system-level state and config operations."""

    # Note: Expects self.config to be provided by the inheriting class

    # ==================================================================
    # Discovery & Status
    # ==================================================================

    def is_installed(self) -> bool:
        """Return ``True`` if the PAI SKILL.md exists on disk."""
        return self.config.skill_md.is_file()

    def get_status(self) -> dict[str, Any]:
        """Return a comprehensive status dictionary for the PAI installation."""
        installed = self.is_installed()
        return {
            "installed": installed,
            "pai_root": str(self.config.pai_root),
            "upstream": PAI_UPSTREAM_URL,
            "components": self.get_components() if installed else {},
            "settings": self._load_settings() if installed else None,
        }

    def get_components(self) -> dict[str, dict[str, Any]]:
        """Enumerate PAI components and count their items."""
        components: dict[str, dict[str, Any]] = {}

        components["algorithm"] = {
            "exists": self.config.skill_md.is_file(),
            "count": 1 if self.config.skill_md.is_file() else 0,
            "path": str(self.config.skill_md),
        }
        components["skills"] = self._dir_info(self.config.skills_dir)
        components["tools"] = self._dir_info(self.config.tools_dir)
        components["agents"] = self._dir_info(self.config.agents_dir)
        components["memory"] = self._dir_info(self.config.memory_dir)
        components["hooks"] = self._dir_info(self.config.hooks_dir)
        components["security"] = self._dir_info(self.config.security_dir)
        components["components"] = self._dir_info(self.config.components_dir)

        return components

    # ==================================================================
    # Algorithm Operations
    # ==================================================================

    @staticmethod
    def get_algorithm_phases() -> list[dict[str, str]]:
        """Return the 7 phases of The Algorithm."""
        return list(ALGORITHM_PHASES)

    @staticmethod
    def get_response_depth_levels() -> list[dict[str, str]]:
        """Return the 3 response depth levels."""
        return list(RESPONSE_DEPTH_LEVELS)

    @staticmethod
    def get_principles() -> list[dict[str, str]]:
        """Return the 16 PAI Principles."""
        return list(PAI_PRINCIPLES)

    def get_algorithm_version(self) -> str | None:
        """Parse the Algorithm version from SKILL.md, if present."""
        skill_path = self.config.skill_md
        if not skill_path.is_file():
            return None
        try:
            content = skill_path.read_text(encoding="utf-8")
            match = re.search(r"v\d+\.\d+(?:\.\d+)?", content)
            return match.group(0) if match else None
        except OSError as exc:
            logger.warning("Failed to read SKILL.md: %s", exc)
            return None

    # ==================================================================
    # Security System
    # ==================================================================

    def get_security_config(self) -> dict[str, Any]:
        """Read the PAI security system configuration."""
        sec_dir = self.config.security_dir
        if not sec_dir.is_dir():
            return {
                "exists": False,
                "path": str(sec_dir),
                "files": [],
                "patterns": None,
            }

        files: list[str] = []
        try:
            files = sorted(f.name for f in sec_dir.iterdir() if f.is_file())
        except OSError as e:
            logger.warning("Failed to list security config files in %s: %s", sec_dir, e)

        return {
            "exists": True,
            "path": str(sec_dir),
            "files": files,
            "patterns": self._try_read_json(sec_dir / "patterns.yaml"),
        }

    # ==================================================================
    # Settings & MCP
    # ==================================================================

    def get_settings(self) -> dict[str, Any] | None:
        """Load and return parsed settings.json."""
        return self._load_settings()

    def get_pai_env(self) -> dict[str, str]:
        """Extract PAI-specific environment variables from settings."""
        settings = self._load_settings()
        if settings is None:
            return {}
        return dict(settings.get("env", {}))

    def get_mcp_registration(self) -> dict[str, Any] | None:
        """Read MCP server registrations from ``claude_desktop_config.json``."""
        cfg_path = self.config.desktop_config
        if not cfg_path.is_file():
            return None
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read MCP config: %s", exc)
            return None

    def has_codomyrmex_mcp(self) -> bool:
        """Return ``True`` if codomyrmex is registered as an MCP server."""
        config = self.get_mcp_registration()
        if config is None:
            return False
        servers = config.get("mcpServers", {})
        return "codomyrmex" in servers

    # ==================================================================
    # Internals
    # ==================================================================

    def _dir_info(self, path: Path) -> dict[str, Any]:
        """Return exists/count/path dict for a directory."""
        exists = path.is_dir()
        count = 0
        if exists:
            try:
                count = sum(1 for _ in path.iterdir())
            except OSError as e:
                logger.warning("Failed to count entries in %s: %s", path, e)

        return {"exists": exists, "count": count, "path": str(path)}

    def _load_settings(self) -> dict[str, Any] | None:
        """Load ``settings.json`` from PAI root or claude root."""
        for candidate in (
            self.config.pai_root / "settings.json",
            self.config.settings_json,
        ):
            if candidate.is_file():
                try:
                    return json.loads(candidate.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Failed to read settings %s: %s", candidate, exc)
        return None

    def _try_read_json(self, path: Path) -> dict[str, Any] | None:
        """Attempt to read a JSON/YAML-like file, returning None on failure."""
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to read JSON file %s: %s", path, e)
            return None
