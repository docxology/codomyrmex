"""PAI system discovery, validation, and operations bridge.

Comprehensive bridge between Codomyrmex and the
`Personal AI Infrastructure <https://github.com/danielmiessler/Personal_AI_Infrastructure>`_
(PAI) by Daniel Miessler.

**Upstream**: https://github.com/danielmiessler/Personal_AI_Infrastructure
**Local install**: ``~/.claude/PAI/`` (v4+) or ``~/.claude/skills/PAI/`` (v3 legacy)

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

from codomyrmex.logging_monitoring import get_logger

from ._models import (
    ALGORITHM_PHASES,
    PAI_PRINCIPLES,
    RESPONSE_DEPTH_LEVELS,
    PAIAgentInfo,
    PAIConfig,
    PAIHookInfo,
    PAIMemoryStore,
    PAISkillInfo,
    PAIToolInfo,
)
from ._modules import PAIModulesMixin
from ._systems import PAI_UPSTREAM_URL, PAISystemsMixin

logger = get_logger(__name__)

# Expose constants at module level for compatibility
PAI_UPSTREAM_LICENSE = "MIT"


class PAIBridge(PAISystemsMixin, PAIModulesMixin):
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
        - Local install path (v4+): ``~/.claude/PAI/``
        - Local install path (v3 legacy): ``~/.claude/skills/PAI/``
    """

    def __init__(self, config: PAIConfig | None = None) -> None:
        self.config = config or PAIConfig()

# Export symbols
__all__ = [
    "ALGORITHM_PHASES",
    "PAI_PRINCIPLES",
    "PAI_UPSTREAM_LICENSE",
    "PAI_UPSTREAM_URL",
    "RESPONSE_DEPTH_LEVELS",
    "PAIAgentInfo",
    "PAIBridge",
    "PAIConfig",
    "PAIHookInfo",
    "PAIMemoryStore",
    "PAISkillInfo",
    "PAIToolInfo",
]
