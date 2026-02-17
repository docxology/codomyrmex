"""PAI system discovery, validation, and operations bridge.

Comprehensive bridge between Codomyrmex and the
`Personal AI Infrastructure <https://github.com/danielmiessler/Personal_AI_Infrastructure>`_
(PAI) by Daniel Miessler.

**Upstream**: https://github.com/danielmiessler/Personal_AI_Infrastructure
**Local install**: ``~/.claude/skills/PAI/``

This module discovers the PAI installation and exposes programmatic access to
every PAI subsystem:

- **The Algorithm** — 7-phase structured response protocol
- **Skill System** — Modular capability packs (CORE, Agents, Art, Browser, …)
- **Tool System** — Bun/TypeScript CLI tools (``Tools/*.ts``)
- **Hook System** — Event-driven lifecycle hooks (``hooks/*.hook.ts``)
- **Agent System** — Personality-based agent definitions (``agents/*.md``)
- **Memory System** — Three-tier learning storage (``MEMORY/``)
- **Security System** — Command validation and policy enforcement
- **TELOS** — Deep goal understanding files (Mission, Goals, Beliefs, …)
- **Settings** — Configuration and environment variables

All methods use **real filesystem operations** — zero mocks.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Upstream repository reference
PAI_UPSTREAM_URL = "https://github.com/danielmiessler/Personal_AI_Infrastructure"
PAI_UPSTREAM_LICENSE = "MIT"


# =====================================================================
# Data classes for structured PAI information
# =====================================================================


@dataclass
class PAIConfig:
    """Configuration and path layout for the PAI system.

    Attributes:
        pai_root: Root directory of the PAI skill (default ``~/.claude/skills/PAI``).
        claude_root: Root of the Claude configuration directory (default ``~/.claude``).
    """

    pai_root: Path = field(
        default_factory=lambda: Path.home() / ".claude" / "skills" / "PAI"
    )
    claude_root: Path = field(default_factory=lambda: Path.home() / ".claude")

    # ---- derived paths ------------------------------------------------

    @property
    def skill_md(self) -> Path:
        """Path to the core Algorithm / SKILL.md file."""
        return self.pai_root / "SKILL.md"

    @property
    def skills_dir(self) -> Path:
        """Root-level skills directory (houses skill packs like CORE, Agents, Art)."""
        # Upstream uses ~/.claude/skills/ for top-level skill packs
        return self.claude_root / "skills"

    @property
    def tools_dir(self) -> Path:
        """PAI Tools directory containing TypeScript CLI tools."""
        return self.pai_root / "Tools"

    @property
    def agents_dir(self) -> Path:
        """Agent personality definitions directory."""
        return self.claude_root / "agents"

    @property
    def agents_md(self) -> Path:
        """PAI Agent System specification document."""
        return self.pai_root / "PAIAGENTSYSTEM.md"

    @property
    def memory_dir(self) -> Path:
        """Memory system root directory."""
        return self.claude_root / "MEMORY"

    @property
    def hooks_dir(self) -> Path:
        """Hook system directory."""
        return self.claude_root / "hooks"

    @property
    def security_dir(self) -> Path:
        """Security system directory."""
        return self.pai_root / "PAISECURITYSYSTEM"

    @property
    def settings_json(self) -> Path:
        """Claude settings.json path."""
        return self.claude_root / "settings.json"

    @property
    def desktop_config(self) -> Path:
        """Claude Desktop MCP configuration path."""
        return self.claude_root / "claude_desktop_config.json"

    @property
    def components_dir(self) -> Path:
        """Components directory (Algorithm sub-components)."""
        return self.pai_root / "Components"

    # TELOS files live in the USER/ directory
    @property
    def telos_dir(self) -> Path:
        """TELOS identity directory (USER/)."""
        return self.claude_root / "USER"


@dataclass(frozen=True)
class PAISkillInfo:
    """Metadata about a discovered PAI skill pack."""

    name: str
    path: str
    has_skill_md: bool
    has_tools: bool
    has_workflows: bool
    file_count: int


@dataclass(frozen=True)
class PAIToolInfo:
    """Metadata about a discovered PAI tool."""

    name: str
    path: str
    size_bytes: int


@dataclass(frozen=True)
class PAIHookInfo:
    """Metadata about a discovered PAI hook."""

    name: str
    path: str
    size_bytes: int
    is_archived: bool


@dataclass(frozen=True)
class PAIAgentInfo:
    """Metadata about a discovered PAI agent personality."""

    name: str
    path: str
    size_bytes: int


@dataclass(frozen=True)
class PAIMemoryStore:
    """Metadata about a PAI memory store (subdirectory)."""

    name: str
    path: str
    item_count: int


# =====================================================================
# Algorithm constants (from The Algorithm v0.2.25)
# =====================================================================

ALGORITHM_PHASES: list[dict[str, str]] = [
    {"phase": "1/7", "name": "OBSERVE", "description": "Reverse-engineer intent and create ISC (Ideal State Criteria)"},
    {"phase": "2/7", "name": "THINK", "description": "Thinking Tools assessment, Skill Check, and Capability Selection"},
    {"phase": "3/7", "name": "PLAN", "description": "Finalize the technical approach"},
    {"phase": "4/7", "name": "BUILD", "description": "Create artifacts and prepare logic"},
    {"phase": "5/7", "name": "EXECUTE", "description": "Run the work (parallel where possible)"},
    {"phase": "6/7", "name": "VERIFY", "description": "Evidence-based verification against ISC"},
    {"phase": "7/7", "name": "LEARN", "description": "Capture insights for future improvement"},
]

RESPONSE_DEPTH_LEVELS: list[dict[str, str]] = [
    {"depth": "FULL", "when": "Non-trivial problem solving, design, implementation", "format": "7 phases (Observe → Learn)"},
    {"depth": "ITERATION", "when": "Adjusting work in progress", "format": "Condensed: Change + Verify"},
    {"depth": "MINIMAL", "when": "Pure social (greetings, ratings)", "format": "Summary + Voice"},
]

PAI_PRINCIPLES: list[dict[str, str]] = [
    {"num": "1", "name": "User Centricity", "summary": "PAI is built around you, not tooling"},
    {"num": "2", "name": "The Foundational Algorithm", "summary": "Observe → Think → Plan → Build → Execute → Verify → Learn"},
    {"num": "3", "name": "Clear Thinking First", "summary": "Clarify the problem before writing the prompt"},
    {"num": "4", "name": "Scaffolding > Model", "summary": "System architecture matters more than which model you use"},
    {"num": "5", "name": "Deterministic Infrastructure", "summary": "AI is probabilistic; your infrastructure shouldn't be"},
    {"num": "6", "name": "Code Before Prompts", "summary": "If you can solve it with a bash script, don't use AI"},
    {"num": "7", "name": "Spec / Test / Evals First", "summary": "Write specifications and tests before building"},
    {"num": "8", "name": "UNIX Philosophy", "summary": "Do one thing well. Make tools composable"},
    {"num": "9", "name": "ENG / SRE Principles", "summary": "Treat AI infrastructure like production software"},
    {"num": "10", "name": "CLI as Interface", "summary": "Command-line interfaces are faster and more scriptable"},
    {"num": "11", "name": "Goal → Code → CLI → Prompts → Agents", "summary": "The decision hierarchy"},
    {"num": "12", "name": "Skill Management", "summary": "Modular capabilities that route intelligently"},
    {"num": "13", "name": "Memory System", "summary": "Everything worth knowing gets captured"},
    {"num": "14", "name": "Agent Personalities", "summary": "Specialized agents with unique voices"},
    {"num": "15", "name": "Science as Meta-Loop", "summary": "Hypothesis → Experiment → Measure → Iterate"},
    {"num": "16", "name": "Permission to Fail", "summary": "Explicit permission to say 'I don't know'"},
]


# =====================================================================
# PAIBridge — the main bridge class
# =====================================================================


class PAIBridge:
    """Bridge between Codomyrmex and the PAI system.

    Discovers, validates, and provides programmatic access to every PAI
    subsystem using real filesystem inspection — no mock objects.

    Example::

        bridge = PAIBridge()
        if bridge.is_installed():
            for skill in bridge.list_skills():
                print(f"{skill.name}: {skill.file_count} files")

    See Also:
        - Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure
        - Local install path: ``~/.claude/skills/PAI/``
    """

    def __init__(self, config: PAIConfig | None = None) -> None:
        self.config = config or PAIConfig()

    # ==================================================================
    # Discovery & Status
    # ==================================================================

    def is_installed(self) -> bool:
        """Return ``True`` if the PAI SKILL.md exists on disk."""
        return self.config.skill_md.is_file()

    def get_status(self) -> dict[str, Any]:
        """Return a comprehensive status dictionary for the PAI installation.

        Returns:
            Dictionary with keys: ``installed``, ``pai_root``, ``upstream``,
            ``components``, ``settings``.
        """
        installed = self.is_installed()
        return {
            "installed": installed,
            "pai_root": str(self.config.pai_root),
            "upstream": PAI_UPSTREAM_URL,
            "components": self.get_components() if installed else {},
            "settings": self._load_settings() if installed else None,
        }

    def get_components(self) -> dict[str, dict[str, Any]]:
        """Enumerate PAI components and count their items.

        Returns:
            Dictionary mapping component name → info dict with keys
            ``exists`` (bool), ``count`` (int), ``path`` (str).
        """
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
        """Return the 7 phases of The Algorithm (v0.2.25).

        These are the canonical phases from upstream PAI:
        OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
        """
        return list(ALGORITHM_PHASES)

    @staticmethod
    def get_response_depth_levels() -> list[dict[str, str]]:
        """Return the 3 response depth levels (FULL, ITERATION, MINIMAL)."""
        return list(RESPONSE_DEPTH_LEVELS)

    @staticmethod
    def get_principles() -> list[dict[str, str]]:
        """Return the 16 PAI Principles."""
        return list(PAI_PRINCIPLES)

    def get_algorithm_version(self) -> str | None:
        """Parse the Algorithm version from SKILL.md, if present.

        Returns:
            Version string (e.g. ``"v0.2.25"``) or ``None``.
        """
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
    # Skill System
    # ==================================================================

    def list_skills(self) -> list[PAISkillInfo]:
        """List all installed PAI skill packs.

        Scans ``~/.claude/skills/`` for subdirectories containing
        a ``SKILL.md`` file (the PAI skill marker).

        Returns:
            List of :class:`PAISkillInfo` objects, sorted by name.
        """
        skills_dir = self.config.skills_dir
        if not skills_dir.is_dir():
            return []

        result: list[PAISkillInfo] = []
        try:
            for entry in sorted(skills_dir.iterdir()):
                if not entry.is_dir():
                    continue
                skill_md = entry / "SKILL.md"
                tools_dir = entry / "Tools"
                workflows_dir = entry / "Workflows"
                file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                result.append(PAISkillInfo(
                    name=entry.name,
                    path=str(entry),
                    has_skill_md=skill_md.is_file(),
                    has_tools=tools_dir.is_dir(),
                    has_workflows=workflows_dir.is_dir(),
                    file_count=file_count,
                ))
        except OSError as exc:
            logger.warning("Failed to list skills: %s", exc)

        return result

    def get_skill_info(self, name: str) -> PAISkillInfo | None:
        """Get info for a specific skill pack by name.

        Args:
            name: Skill pack name (e.g. ``"CORE"``, ``"Agents"``, ``"Art"``).

        Returns:
            :class:`PAISkillInfo` or ``None`` if not found.
        """
        for skill in self.list_skills():
            if skill.name == name:
                return skill
        return None

    # ==================================================================
    # Tool System
    # ==================================================================

    def list_tools(self) -> list[PAIToolInfo]:
        """List all PAI TypeScript tools in ``Tools/``.

        Returns:
            List of :class:`PAIToolInfo` objects for each ``.ts`` file.
        """
        tools_dir = self.config.tools_dir
        if not tools_dir.is_dir():
            return []

        result: list[PAIToolInfo] = []
        try:
            for entry in sorted(tools_dir.iterdir()):
                if entry.is_file() and entry.suffix == ".ts":
                    result.append(PAIToolInfo(
                        name=entry.stem,
                        path=str(entry),
                        size_bytes=entry.stat().st_size,
                    ))
        except OSError as exc:
            logger.warning("Failed to list tools: %s", exc)

        return result

    def get_tool_info(self, name: str) -> PAIToolInfo | None:
        """Get info for a specific tool by stem name (e.g. ``"AddTask"``)."""
        for tool in self.list_tools():
            if tool.name == name:
                return tool
        return None

    # ==================================================================
    # Hook System
    # ==================================================================

    def list_hooks(self) -> list[PAIHookInfo]:
        """List all PAI hooks in ``hooks/``.

        Hooks respond to lifecycle events — session start, tool use, task
        completion, etc. Archived hooks (``*.v25-archived``) are flagged.

        Returns:
            List of :class:`PAIHookInfo` objects.
        """
        hooks_dir = self.config.hooks_dir
        if not hooks_dir.is_dir():
            return []

        result: list[PAIHookInfo] = []
        try:
            for entry in sorted(hooks_dir.iterdir()):
                if not entry.is_file():
                    continue
                if ".hook." not in entry.name:
                    continue
                is_archived = entry.name.endswith(".v25-archived") or "-archived" in entry.name
                result.append(PAIHookInfo(
                    name=entry.name.split(".hook.")[0] if ".hook." in entry.name else entry.stem,
                    path=str(entry),
                    size_bytes=entry.stat().st_size,
                    is_archived=is_archived,
                ))
        except OSError as exc:
            logger.warning("Failed to list hooks: %s", exc)

        return result

    def list_active_hooks(self) -> list[PAIHookInfo]:
        """List only non-archived (active) hooks."""
        return [h for h in self.list_hooks() if not h.is_archived]

    def get_hook_info(self, name: str) -> PAIHookInfo | None:
        """Get info for a specific hook by name."""
        for hook in self.list_hooks():
            if hook.name == name:
                return hook
        return None

    # ==================================================================
    # Agent System
    # ==================================================================

    def list_agents(self) -> list[PAIAgentInfo]:
        """List all PAI agent personality definitions.

        Agents are Markdown files in ``~/.claude/agents/`` defining
        specialized AI personalities (Engineer, Architect, Pentester, etc.).

        Returns:
            List of :class:`PAIAgentInfo` objects.
        """
        agents_dir = self.config.agents_dir
        if not agents_dir.is_dir():
            return []

        result: list[PAIAgentInfo] = []
        try:
            for entry in sorted(agents_dir.iterdir()):
                if entry.is_file() and entry.suffix == ".md" and entry.stem not in ("README", "AGENTS"):
                    result.append(PAIAgentInfo(
                        name=entry.stem,
                        path=str(entry),
                        size_bytes=entry.stat().st_size,
                    ))
        except OSError as exc:
            logger.warning("Failed to list agents: %s", exc)

        return result

    def get_agent_info(self, name: str) -> PAIAgentInfo | None:
        """Get info for a specific agent by name (e.g. ``"Engineer"``)."""
        for agent in self.list_agents():
            if agent.name == name:
                return agent
        return None

    # ==================================================================
    # Memory System
    # ==================================================================

    def list_memory_stores(self) -> list[PAIMemoryStore]:
        """List all PAI memory stores (subdirectories of ``MEMORY/``).

        The PAI memory system uses a three-tier architecture (hot/warm/cold)
        with phase-based learning directories:
        AGENTS, History, LEARNING, PAISYSTEMUPDATES, RELATIONSHIP,
        RESEARCH, SECURITY, STATE, etc.

        Returns:
            List of :class:`PAIMemoryStore` objects.
        """
        memory_dir = self.config.memory_dir
        if not memory_dir.is_dir():
            return []

        result: list[PAIMemoryStore] = []
        try:
            for entry in sorted(memory_dir.iterdir()):
                if entry.is_dir():
                    item_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                    result.append(PAIMemoryStore(
                        name=entry.name,
                        path=str(entry),
                        item_count=item_count,
                    ))
        except OSError as exc:
            logger.warning("Failed to list memory stores: %s", exc)

        return result

    def get_memory_info(self, store_name: str) -> PAIMemoryStore | None:
        """Get info for a specific memory store by name."""
        for store in self.list_memory_stores():
            if store.name == store_name:
                return store
        return None

    # ==================================================================
    # Security System
    # ==================================================================

    def get_security_config(self) -> dict[str, Any]:
        """Read the PAI security system configuration.

        Returns:
            Dictionary with ``exists``, ``path``, ``files`` (list of names),
            and ``patterns`` (parsed YAML/JSON if available).
        """
        sec_dir = self.config.security_dir
        if not sec_dir.is_dir():
            return {"exists": False, "path": str(sec_dir), "files": [], "patterns": None}

        files: list[str] = []
        try:
            files = sorted(f.name for f in sec_dir.iterdir() if f.is_file())
        except OSError:
            pass

        return {
            "exists": True,
            "path": str(sec_dir),
            "files": files,
            "patterns": self._try_read_json(sec_dir / "patterns.yaml"),
        }

    # ==================================================================
    # TELOS (Deep Goal Understanding)
    # ==================================================================

    def get_telos_files(self) -> list[str]:
        """List TELOS identity files from the USER/ directory.

        The upstream TELOS system defines 10 files:
        MISSION.md, GOALS.md, PROJECTS.md, BELIEFS.md, MODELS.md,
        STRATEGIES.md, NARRATIVES.md, LEARNED.md, CHALLENGES.md, IDEAS.md

        Returns:
            List of filenames found in the TELOS/USER directory.
        """
        telos_dir = self.config.telos_dir
        if not telos_dir.is_dir():
            return []
        try:
            return sorted(f.name for f in telos_dir.iterdir() if f.is_file())
        except OSError:
            return []

    # ==================================================================
    # Settings & MCP
    # ==================================================================

    def get_settings(self) -> dict[str, Any] | None:
        """Load and return parsed settings.json.

        Returns:
            Parsed settings dictionary, or ``None`` if unavailable.
        """
        return self._load_settings()

    def get_pai_env(self) -> dict[str, str]:
        """Extract PAI-specific environment variables from settings.

        Returns:
            Dictionary of PAI environment variables (e.g. ``PAI_DIR``,
            ``PAI_CONFIG_DIR``, ``CLAUDE_CODE_MAX_OUTPUT_TOKENS``).
        """
        settings = self._load_settings()
        if settings is None:
            return {}
        return dict(settings.get("env", {}))

    def get_mcp_registration(self) -> dict[str, Any] | None:
        """Read MCP server registrations from ``claude_desktop_config.json``.

        Returns:
            Parsed config dict, or ``None`` if the file doesn't exist.
        """
        cfg_path = self.config.desktop_config
        if not cfg_path.is_file():
            return None
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
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
            except OSError:
                pass
        return {"exists": exists, "count": count, "path": str(path)}

    def _load_settings(self) -> dict[str, Any] | None:
        """Load ``settings.json`` from PAI root or claude root."""
        for candidate in (
            self.config.pai_root / "settings.json",
            self.config.settings_json,
        ):
            if candidate.is_file():
                try:
                    return json.loads(candidate.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Failed to read settings %s: %s", candidate, exc)
        return None

    def _try_read_json(self, path: Path) -> dict[str, Any] | None:
        """Attempt to read a JSON/YAML-like file, returning None on failure."""
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
        except (json.JSONDecodeError, OSError):
            return None
