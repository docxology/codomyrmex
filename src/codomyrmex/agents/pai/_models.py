"""PAI data models and constants.

Extracted from pai_bridge.py to reduce module size.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# =====================================================================
# Configuration Model
# =====================================================================


@dataclass
class PAIConfig:
    """Configuration and path layout for the PAI system.

    Attributes:
        pai_root: Root directory of the PAI system (default ``~/.claude/PAI`` for v4+, ``~/.claude/skills/PAI`` for v3 legacy).
        claude_root: Root of the Claude configuration directory (default ``~/.claude``).
    """

    pai_root: Path = field(
        default_factory=lambda: (
            Path.home() / ".claude" / "PAI"
            if (Path.home() / ".claude" / "PAI" / "SKILL.md").is_file()
            else Path.home() / ".claude" / "skills" / "PAI"
        )
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


# =====================================================================
# Data classes for structured PAI information
# =====================================================================


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
    {
        "phase": "1/7",
        "name": "OBSERVE",
        "description": "Reverse-engineer intent and create ISC (Ideal State Criteria)",
    },
    {
        "phase": "2/7",
        "name": "THINK",
        "description": "Thinking Tools assessment, Skill Check, and Capability Selection",
    },
    {"phase": "3/7", "name": "PLAN", "description": "Finalize the technical approach"},
    {
        "phase": "4/7",
        "name": "BUILD",
        "description": "Create artifacts and prepare logic",
    },
    {
        "phase": "5/7",
        "name": "EXECUTE",
        "description": "Run the work (parallel where possible)",
    },
    {
        "phase": "6/7",
        "name": "VERIFY",
        "description": "Evidence-based verification against ISC",
    },
    {
        "phase": "7/7",
        "name": "LEARN",
        "description": "Capture insights for future improvement",
    },
]

RESPONSE_DEPTH_LEVELS: list[dict[str, str]] = [
    {
        "depth": "FULL",
        "when": "Non-trivial problem solving, design, implementation",
        "format": "7 phases (Observe → Learn)",
    },
    {
        "depth": "ITERATION",
        "when": "Adjusting work in progress",
        "format": "Condensed: Change + Verify",
    },
    {
        "depth": "MINIMAL",
        "when": "Pure social (greetings, ratings)",
        "format": "Summary + Voice",
    },
]

PAI_PRINCIPLES: list[dict[str, str]] = [
    {
        "num": "1",
        "name": "User Centricity",
        "summary": "PAI is built around you, not tooling",
    },
    {
        "num": "2",
        "name": "The Foundational Algorithm",
        "summary": "Observe → Think → Plan → Build → Execute → Verify → Learn",
    },
    {
        "num": "3",
        "name": "Clear Thinking First",
        "summary": "Clarify the problem before writing the prompt",
    },
    {
        "num": "4",
        "name": "Scaffolding > Model",
        "summary": "System architecture matters more than which model you use",
    },
    {
        "num": "5",
        "name": "Deterministic Infrastructure",
        "summary": "AI is probabilistic; your infrastructure shouldn't be",
    },
    {
        "num": "6",
        "name": "Code Before Prompts",
        "summary": "If you can solve it with a bash script, don't use AI",
    },
    {
        "num": "7",
        "name": "Spec / Test / Evals First",
        "summary": "Write specifications and tests before building",
    },
    {
        "num": "8",
        "name": "UNIX Philosophy",
        "summary": "Do one thing well. Make tools composable",
    },
    {
        "num": "9",
        "name": "ENG / SRE Principles",
        "summary": "Treat AI infrastructure like production software",
    },
    {
        "num": "10",
        "name": "CLI as Interface",
        "summary": "Command-line interfaces are faster and more scriptable",
    },
    {
        "num": "11",
        "name": "Goal → Code → CLI → Prompts → Agents",
        "summary": "The decision hierarchy",
    },
    {
        "num": "12",
        "name": "Skill Management",
        "summary": "Modular capabilities that route intelligently",
    },
    {
        "num": "13",
        "name": "Memory System",
        "summary": "Everything worth knowing gets captured",
    },
    {
        "num": "14",
        "name": "Agent Personalities",
        "summary": "Specialized agents with unique voices",
    },
    {
        "num": "15",
        "name": "Science as Meta-Loop",
        "summary": "Hypothesis → Experiment → Measure → Iterate",
    },
    {
        "num": "16",
        "name": "Permission to Fail",
        "summary": "Explicit permission to say 'I don't know'",
    },
]
