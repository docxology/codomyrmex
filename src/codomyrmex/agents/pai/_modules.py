"""PAI Modules Mixin for bridge integration.

Provides endpoints for introspecting Skills, Tools, Hooks, Agents, Memory,
and TELOS subsystems within PAI. Extracted from pai_bridge.py.
"""

from __future__ import annotations

import itertools

from codomyrmex.logging_monitoring import get_logger

from ._models import (
    PAIAgentInfo,
    PAIHookInfo,
    PAIMemoryStore,
    PAISkillInfo,
    PAIToolInfo,
)

logger = get_logger(__name__)


class PAIModulesMixin:
    """Mixin for discovering PAI logic modules and resources."""

    # Note: Expects self.config to be provided by the inheriting class

    # ==================================================================
    # Skill System
    # ==================================================================

    def list_skills(self) -> list[PAISkillInfo]:
        """List all installed PAI skill packs.

        Scans ``~/.claude/skills/`` for subdirectories containing
        a ``SKILL.md`` file (the PAI skill marker).
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
                file_count = sum(
                    1 for _ in itertools.islice(entry.rglob("*"), 10000) if _.is_file()
                )
                result.append(
                    PAISkillInfo(
                        name=entry.name,
                        path=str(entry),
                        has_skill_md=skill_md.is_file(),
                        has_tools=tools_dir.is_dir(),
                        has_workflows=workflows_dir.is_dir(),
                        file_count=file_count,
                    )
                )
        except OSError as exc:
            logger.warning("Failed to list skills: %s", exc)

        return result

    def get_skill_info(self, name: str) -> PAISkillInfo | None:
        """Get info for a specific skill pack by name."""
        for skill in self.list_skills():
            if skill.name == name:
                return skill
        return None

    # ==================================================================
    # Tool System
    # ==================================================================

    def list_tools(self) -> list[PAIToolInfo]:
        """List all PAI TypeScript tools in ``Tools/``."""
        tools_dir = self.config.tools_dir
        if not tools_dir.is_dir():
            return []

        result: list[PAIToolInfo] = []
        try:
            for entry in sorted(tools_dir.iterdir()):
                if entry.is_file() and entry.suffix == ".ts":
                    result.append(
                        PAIToolInfo(
                            name=entry.stem,
                            path=str(entry),
                            size_bytes=entry.stat().st_size,
                        )
                    )
        except OSError as exc:
            logger.warning("Failed to list tools: %s", exc)

        return result

    def get_tool_info(self, name: str) -> PAIToolInfo | None:
        """Get info for a specific tool by stem name."""
        for tool in self.list_tools():
            if tool.name == name:
                return tool
        return None

    # ==================================================================
    # Hook System
    # ==================================================================

    def list_hooks(self) -> list[PAIHookInfo]:
        """List all PAI hooks in ``hooks/``."""
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
                is_archived = (
                    entry.name.endswith(".v25-archived") or "-archived" in entry.name
                )
                result.append(
                    PAIHookInfo(
                        name=entry.name.split(".hook.")[0]
                        if ".hook." in entry.name
                        else entry.stem,
                        path=str(entry),
                        size_bytes=entry.stat().st_size,
                        is_archived=is_archived,
                    )
                )
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
        """List all PAI agent personality definitions."""
        agents_dir = self.config.agents_dir
        if not agents_dir.is_dir():
            return []

        result: list[PAIAgentInfo] = []
        try:
            for entry in sorted(agents_dir.iterdir()):
                if (
                    entry.is_file()
                    and entry.suffix == ".md"
                    and entry.stem not in ("README", "AGENTS")
                ):
                    result.append(
                        PAIAgentInfo(
                            name=entry.stem,
                            path=str(entry),
                            size_bytes=entry.stat().st_size,
                        )
                    )
        except OSError as exc:
            logger.warning("Failed to list agents: %s", exc)

        return result

    def get_agent_info(self, name: str) -> PAIAgentInfo | None:
        """Get info for a specific agent by name."""
        for agent in self.list_agents():
            if agent.name == name:
                return agent
        return None

    # ==================================================================
    # Memory System
    # ==================================================================

    def list_memory_stores(self) -> list[PAIMemoryStore]:
        """List all PAI memory stores (subdirectories of ``MEMORY/``)."""
        memory_dir = self.config.memory_dir
        if not memory_dir.is_dir():
            return []

        result: list[PAIMemoryStore] = []
        try:
            for entry in sorted(memory_dir.iterdir()):
                if entry.is_dir():
                    item_count = sum(
                        1
                        for _ in itertools.islice(entry.rglob("*"), 10000)
                        if _.is_file()
                    )
                    result.append(
                        PAIMemoryStore(
                            name=entry.name,
                            path=str(entry),
                            item_count=item_count,
                        )
                    )
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
    # TELOS (Deep Goal Understanding)
    # ==================================================================

    def get_telos_files(self) -> list[str]:
        """List TELOS identity files from the USER/ directory."""
        telos_dir = self.config.telos_dir
        if not telos_dir.is_dir():
            return []
        try:
            return sorted(f.name for f in telos_dir.iterdir() if f.is_file())
        except OSError as e:
            logger.warning("Failed to list TELOS files: %s", e)
            return []
