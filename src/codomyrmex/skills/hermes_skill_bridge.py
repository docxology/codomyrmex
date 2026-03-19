"""Hermes Skill Bridge for Codomyrmex.

Bridges the Hermes agent's native skill system (``~/.hermes/skills/``) into the
Codomyrmex :class:`~codomyrmex.skills.SkillRegistry`, making every installed
Hermes skill a first-class citizen in the Codomyrmex skill ecosystem.

The bridge works without any modifications to the Hermes CLI:

1. **Discovery** — scans ``$HERMES_HOME/skills/`` (or ``~/.hermes/skills/``) and
   reads each SKILL.md / skill.yaml it finds.
2. **Registration** — wraps each skill as a :class:`HermesSkillEntry` with a
   callable ``run`` method backed by :class:`~codomyrmex.agents.hermes.hermes_client.HermesClient`.
3. **Synchronisation** — :meth:`HermesSkillBridge.sync_hermes_skills` returns a
   flat skill dict that can be merged into any Codomyrmex registry.

Typical usage::

    from codomyrmex.skills.hermes_skill_bridge import HermesSkillBridge

    bridge = HermesSkillBridge()
    skills = bridge.sync_hermes_skills()
    print(skills.keys())           # dict_keys(['geopolitical-market-sim', ...])

    entry = bridge.get_skill("geopolitical-market-sim")
    if entry:
        resp = entry.run("Use PrediHermes health")

See also:
    - :mod:`codomyrmex.agents.hermes.hermes_client` — underlying executor
    - ``docs/agents/hermes/skills.md`` — Hermes skill system overview
    - ``nativ3ai/hermes-geopolitical-market-sim`` — reference third-party skill
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from codomyrmex.agents.hermes.hermes_client import HermesClient

# Default Hermes home directory.
_DEFAULT_HERMES_HOME = Path.home() / ".hermes"


def _resolve_hermes_home() -> Path:
    """Return the resolved HERMES_HOME path.

    Respects the ``HERMES_HOME`` environment variable exactly as the Hermes CLI
    does (see ``hermes_cli/config.py`` line 37).
    """
    return Path(os.getenv("HERMES_HOME", str(_DEFAULT_HERMES_HOME))).expanduser()


def _read_skill_md(skill_dir: Path) -> dict[str, str]:
    """Extract name and description from a SKILL.md or skill.yaml file.

    Returns a dict with at least ``name`` and ``description`` keys.
    """
    data: dict[str, str] = {"name": skill_dir.name, "description": ""}

    # Try SKILL.md first (Hermes / agentskills.io standard)
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        try:
            text = skill_md.read_text(encoding="utf-8")
            # Pull the first H1 as name, and the first non-empty paragraph as description
            lines = text.splitlines()
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# ") and not data["name"] != skill_dir.name:
                    data["name"] = stripped[2:].strip()
                elif stripped and not stripped.startswith("#"):
                    if not data["description"]:
                        data["description"] = stripped
                    break
        except OSError as exc:
            logger.debug("Could not read SKILL.md at %s: %s", skill_md, exc)

    # Try skill.yaml as fallback
    skill_yaml = skill_dir / "skill.yaml"
    if skill_yaml.exists() and not data["description"]:
        try:
            import yaml  # optional dependency

            with open(skill_yaml, encoding="utf-8") as fh:
                parsed = yaml.safe_load(fh)
            if isinstance(parsed, dict):
                data.setdefault("name", parsed.get("name", skill_dir.name))
                data.setdefault(
                    "description", parsed.get("description", "")
                )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Could not parse skill.yaml at %s: %s", skill_yaml, exc)

    return data


@dataclass
class HermesSkillEntry:
    """A Hermes skill registered as a Codomyrmex skill bridge entry.

    Attributes:
        name: Canonical skill name (matches ``hermes skills list`` output).
        description: Human-readable description sourced from SKILL.md.
        skill_path: Absolute path inside ``$HERMES_HOME/skills/``.
        metadata: Additional raw metadata (category, agents config, etc.).
        _client: Lazily initialised :class:`~codomyrmex.agents.hermes.hermes_client.HermesClient`.
    """

    name: str
    description: str
    skill_path: Path
    metadata: dict[str, Any] = field(default_factory=dict)
    _client: HermesClient | None = field(default=None, init=False, repr=False)

    # ------------------------------------------------------------------
    # Client access
    # ------------------------------------------------------------------

    def _get_client(self) -> HermesClient:
        """Return a lazily-initialised :class:`HermesClient`."""
        if self._client is None:
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            self._client = HermesClient()
        return self._client

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(
        self,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> Any:
        """Execute a prompt via Hermes with this skill preloaded.

        Args:
            prompt: Natural-language instruction (may reference PrediHermes commands).
            session_id: Optional existing session to continue.
            session_name: Optional human-friendly session name.

        Returns:
            :class:`~codomyrmex.agents.core.AgentResponse` from the Hermes CLI.
        """
        client = self._get_client()
        logger.info("HermesSkillEntry.run: skill=%s, prompt=%.80s…", self.name, prompt)
        return client.chat_session(
            prompt=prompt,
            session_id=session_id,
            session_name=session_name,
            hermes_skill=self.name,
        )

    def __call__(
        self,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> Any:
        """Alias for :meth:`run` — makes the entry directly callable."""
        return self.run(prompt, session_id=session_id, session_name=session_name)


class HermesSkillBridge:
    """Bridge between the Hermes native skill directory and Codomyrmex.

    Scans ``$HERMES_HOME/skills/`` and exposes each installed skill as a
    :class:`HermesSkillEntry` with a ``run`` method backed by
    :class:`~codomyrmex.agents.hermes.hermes_client.HermesClient`.

    Args:
        hermes_home: Override the Hermes home directory (default: ``$HERMES_HOME``
            env var → ``~/.hermes``).
    """

    def __init__(self, hermes_home: Path | str | None = None) -> None:
        self._hermes_home: Path = (
            Path(hermes_home).expanduser()
            if hermes_home is not None
            else _resolve_hermes_home()
        )
        self._skills_dir: Path = self._hermes_home / "skills"
        self._cache: dict[str, HermesSkillEntry] | None = None
        logger.info(
            "HermesSkillBridge initialised: hermes_home=%s", self._hermes_home
        )

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _discover_from_filesystem(self) -> dict[str, HermesSkillEntry]:
        """Walk ``$HERMES_HOME/skills/`` and build a skill entry map."""
        entries: dict[str, HermesSkillEntry] = {}
        if not self._skills_dir.exists():
            logger.debug(
                "Hermes skills directory does not exist: %s", self._skills_dir
            )
            return entries

        # Skills are organised as skills/<category>/<name>/ or skills/<name>/
        for item in sorted(self._skills_dir.rglob("*")):
            if not item.is_dir():
                continue
            # A skill directory must contain SKILL.md or skill.yaml
            has_skill_md = (item / "SKILL.md").exists()
            has_skill_yaml = (item / "skill.yaml").exists()
            if not (has_skill_md or has_skill_yaml):
                continue

            meta = _read_skill_md(item)
            skill_name = item.name  # e.g. "geopolitical-market-sim"
            category = item.parent.name if item.parent != self._skills_dir else "uncategorised"
            entry = HermesSkillEntry(
                name=skill_name,
                description=meta.get("description", ""),
                skill_path=item,
                metadata={"category": category, "hermes_home": str(self._hermes_home)},
            )
            entries[skill_name] = entry
            logger.debug("Discovered Hermes skill: %s (%s)", skill_name, category)

        logger.info("HermesSkillBridge: discovered %d skills", len(entries))
        return entries

    def _discover_from_cli(self) -> list[str]:
        """Run ``hermes skills list`` and return skill name list.

        Returns an empty list if the Hermes CLI is unavailable.
        """
        import shutil

        if not shutil.which("hermes"):
            return []
        try:
            result = subprocess.run(
                ["hermes", "skills", "list"],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "NO_COLOR": "1"},
            )
            lines = [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            return lines
        except Exception as exc:  # noqa: BLE001
            logger.debug("hermes skills list failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync_hermes_skills(
        self, force_refresh: bool = False
    ) -> dict[str, HermesSkillEntry]:
        """Scan Hermes skills and return a canonical skill-name → entry map.

        The result is cached for the lifetime of the bridge instance. Pass
        ``force_refresh=True`` to re-scan the filesystem.

        Returns:
            Dict mapping skill name to :class:`HermesSkillEntry`.  Empty dict if
            Hermes is not installed or no skills are found.
        """
        if self._cache is not None and not force_refresh:
            return self._cache
        self._cache = self._discover_from_filesystem()
        return self._cache

    def list_hermes_skills(self) -> dict[str, HermesSkillEntry]:
        """Return a dict of all discovered Hermes skills.

        Combines filesystem discovery with optional ``hermes skills list`` CLI
        output so that embedded (CLI-only) skills are also surfaced.

        Returns:
            Dict mapping skill name → :class:`HermesSkillEntry`.
        """
        entries = self.sync_hermes_skills()

        # Supplement with CLI-listed names that may not have a readable SKILL.md
        cli_names = self._discover_from_cli()
        for name in cli_names:
            if name not in entries:
                entries[name] = HermesSkillEntry(
                    name=name,
                    description="(description unavailable — CLI-listed skill)",
                    skill_path=self._skills_dir,
                    metadata={"source": "cli"},
                )
        return entries

    def get_skill(self, name: str) -> HermesSkillEntry | None:
        """Return the :class:`HermesSkillEntry` for *name*, or ``None`` if not found.

        Args:
            name: Exact skill name as it appears in ``hermes skills list``.
        """
        return self.list_hermes_skills().get(name)

    def run_skill(
        self,
        name: str,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> Any:
        """Execute *prompt* via Hermes with skill *name* preloaded.

        Convenience wrapper around :meth:`HermesSkillEntry.run`.

        Raises:
            KeyError: If the skill *name* is not found.
        """
        skills = self.list_hermes_skills()
        if name not in skills:
            available = sorted(skills)
            raise KeyError(
                f"Hermes skill '{name}' not found. Available: {available}"
            )
        return skills[name].run(
            prompt, session_id=session_id, session_name=session_name
        )

    def refresh(self) -> None:
        """Force-refresh the skill cache from the filesystem."""
        self._cache = None
        self.sync_hermes_skills()
        logger.info("HermesSkillBridge cache refreshed")

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        count = len(self._cache) if self._cache is not None else "?"
        return (
            f"HermesSkillBridge(hermes_home={self._hermes_home!s}, "
            f"cached_skills={count})"
        )
