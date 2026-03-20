"""HermesSkillBridge — discover and run Hermes skills from Codomyrmex.

Bridges the Hermes agent's skill ecosystem into the Codomyrmex
:mod:`codomyrmex.skills` registry so that any installed Hermes skill can be
invoked via the standard :class:`HermesClient` session interface.

Typical usage::

    from codomyrmex.skills import HermesSkillBridge

    bridge = HermesSkillBridge()
    skills = bridge.list_hermes_skills()
    result = bridge.run_skill("geopolitical_market_sim", "What is the BTC dump probability?")

"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class HermesSkillEntry:
    """A single Hermes skill, runnable via :class:`HermesClient`.

    Attributes:
        name: Canonical CLI skill name (e.g. ``"geopolitical_market_sim"``).
        description: Human-readable description sourced from the skill manifest.
        skill_path: Absolute path to the skill directory, if discoverable.
        metadata: Raw dict of any extra manifest keys.
        hermes_skill_id: The ``-s`` flag value passed to ``hermes chat``.
    """

    name: str
    description: str = ""
    skill_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    hermes_skill_id: str = ""

    def __post_init__(self) -> None:
        if not self.hermes_skill_id:
            self.hermes_skill_id = self.name

    def run(
        self,
        prompt: str,
        session_id: str | None = None,
        timeout: int = 180,
    ) -> dict[str, Any]:
        """Execute this skill with *prompt*.

        Delegates to :meth:`HermesSkillBridge.run_skill`.

        Args:
            prompt: Natural-language prompt to send to the skill.
            session_id: Continue an existing session (optional).
            timeout: Subprocess timeout in seconds (default 180).

        Returns:
            dict with keys: ``status``, ``content``, ``session_id``, ``error``.

        """
        from codomyrmex.skills.hermes_skill_bridge import HermesSkillBridge  # self-call

        bridge = HermesSkillBridge()
        return bridge.run_skill(
            self.name, prompt, session_id=session_id, timeout=timeout
        )


# ---------------------------------------------------------------------------
# Bridge class
# ---------------------------------------------------------------------------


class HermesSkillBridge:
    """Discover and invoke Hermes skills from within the Codomyrmex framework.

    The bridge inspects ``~/.hermes/skills/`` (or *hermes_home*) for locally
    installed skills and exposes them as :class:`HermesSkillEntry` objects
    that can be run via :class:`~codomyrmex.agents.hermes.HermesClient`.

    Args:
        hermes_home: Override for the Hermes home directory.  Defaults to
            ``~/.hermes``.

    """

    def __init__(self, hermes_home: str | Path | None = None) -> None:
        self._hermes_home = Path(hermes_home or Path.home() / ".hermes").expanduser()
        self._skills_dir = self._hermes_home / "skills"
        self._hermes_bin: str | None = shutil.which("hermes")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_hermes_skills(self) -> list[HermesSkillEntry]:
        """Return skill entries discovered via ``hermes skills list``.

        Falls back to filesystem scan when the CLI is unavailable.

        Returns:
            List of :class:`HermesSkillEntry` objects.  May be empty.

        """
        if self._hermes_bin:
            try:
                return self._list_via_cli()
            except Exception as exc:
                logger.warning(
                    "hermes skills list failed, falling back to FS scan: %s", exc
                )
        return self._list_via_filesystem()

    def sync_hermes_skills(
        self,
        hermes_home: str | Path | None = None,
    ) -> dict[str, HermesSkillEntry]:
        """Scan *hermes_home*/skills/ and build a name → entry mapping.

        Args:
            hermes_home: Override the home directory for this call only.

        Returns:
            Dict mapping skill name → :class:`HermesSkillEntry`.

        """
        home = Path(hermes_home or self._hermes_home).expanduser()
        skills_dir = home / "skills"
        entries: dict[str, HermesSkillEntry] = {}

        if not skills_dir.exists():
            logger.info("Hermes skills directory not found: %s", skills_dir)
            return entries

        for candidate in sorted(skills_dir.iterdir()):
            if not candidate.is_dir():
                continue
            entry = self._parse_skill_dir(candidate)
            if entry:
                entries[entry.name] = entry
                logger.debug("Discovered Hermes skill: %s @ %s", entry.name, candidate)

        logger.info("Synced %d Hermes skills from %s", len(entries), skills_dir)
        return entries

    def get_skill(self, name: str) -> HermesSkillEntry | None:
        """Look up a single skill by name.

        Args:
            name: Skill name (case-insensitive, underscores/hyphens normalised).

        Returns:
            :class:`HermesSkillEntry` if found, else ``None``.

        """
        normalized = _normalize_name(name)
        for entry in self.list_hermes_skills():
            if _normalize_name(entry.name) == normalized:
                return entry
        return None

    def run_skill(
        self,
        name: str,
        prompt: str,
        session_id: str | None = None,
        timeout: int = 180,
    ) -> dict[str, Any]:
        """Run a Hermes skill by name.

        Resolves the skill's CLI preload name, then delegates to
        :meth:`HermesClient.chat_session`.

        Args:
            name: Skill name (as returned by :meth:`list_hermes_skills`).
            prompt: Natural-language prompt.
            session_id: Continue an existing session (optional).
            timeout: Subprocess timeout in seconds.

        Returns:
            dict with keys: ``status``, ``content``, ``session_id``, ``error``.

        """
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        entry = self.get_skill(name)
        skill_id = entry.hermes_skill_id if entry else name

        client = HermesClient(config={"hermes_timeout": timeout})
        response = client.chat_session(
            prompt=prompt,
            session_id=session_id,
            hermes_skill=skill_id,
        )
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "session_id": response.metadata.get("session_id"),
            "error": response.error,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _list_via_cli(self) -> list[HermesSkillEntry]:
        """Parse ``hermes skills list`` output into entries."""
        env = {"NO_COLOR": "1"}
        import os

        env.update(os.environ)
        result = subprocess.run(
            [self._hermes_bin, "skills", "list"],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
        lines = result.stdout.splitlines()
        entries: list[HermesSkillEntry] = []
        for line in lines:
            # Table rows:  │ skill_name  │ category  │ …
            if "│" not in line:
                continue
            parts = [p.strip() for p in line.split("│") if p.strip()]
            if not parts or parts[0].lower() in ("name", "skill", ""):
                continue
            skill_name = parts[0]
            if not skill_name or skill_name.startswith("-"):
                continue
            description = parts[2] if len(parts) > 2 else ""
            skill_path = self._skills_dir / skill_name
            entries.append(
                HermesSkillEntry(
                    name=skill_name,
                    description=description,
                    skill_path=skill_path if skill_path.exists() else None,
                    hermes_skill_id=skill_name,
                )
            )
        return entries

    def _list_via_filesystem(self) -> list[HermesSkillEntry]:
        """Discover skills by scanning the skills directory on disk."""
        if not self._skills_dir.exists():
            return []
        entries: list[HermesSkillEntry] = []
        for candidate in sorted(self._skills_dir.iterdir()):
            if candidate.is_dir():
                entry = self._parse_skill_dir(candidate)
                if entry:
                    entries.append(entry)
        return entries

    @staticmethod
    def _parse_skill_dir(path: Path) -> HermesSkillEntry | None:
        """Build a :class:`HermesSkillEntry` from a skill directory."""
        if not path.is_dir():
            return None

        # Try reading skill.yaml / skill.json
        description = ""
        metadata: dict[str, Any] = {}

        for manifest_name in ("skill.yaml", "skill.yml", "skill.json", "README.md"):
            manifest = path / manifest_name
            if manifest.exists():
                try:
                    content = manifest.read_text(encoding="utf-8", errors="replace")
                    if manifest_name.endswith((".yaml", ".yml")):
                        import yaml  # type: ignore[import-untyped]

                        data = yaml.safe_load(content) or {}
                        description = data.get("description", "")
                        metadata = data
                    elif manifest_name == "README.md":
                        # First non-empty line after the title
                        for line in content.splitlines():
                            stripped = line.strip().lstrip("#").strip()
                            if stripped:
                                description = stripped[:120]
                                break
                except Exception:
                    pass
                break

        return HermesSkillEntry(
            name=path.name,
            description=description,
            skill_path=path,
            metadata=metadata,
            hermes_skill_id=path.name,
        )


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _normalize_name(name: str) -> str:
    """Normalise a skill name for comparison (lower-case, underscores)."""
    return name.lower().replace("-", "_").replace(" ", "_")
