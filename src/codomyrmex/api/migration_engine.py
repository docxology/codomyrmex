"""Migration engine for API version transitions.

Generates migration plans, validates migration paths,
and applies transformations for version upgrades.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MigrationAction(Enum):
    """Types of migration actions."""

    RENAME = "rename"
    REMOVE = "remove"
    ADD_PARAM = "add_param"
    CHANGE_TYPE = "change_type"
    DEPRECATE = "deprecate"
    REPLACE = "replace"


@dataclass
class MigrationStep:
    """A single migration step.

    Attributes:
        action: Type of migration action.
        target: Affected API element.
        old_value: Previous value/name.
        new_value: New value/name.
        description: Human-readable description.
        breaking: Whether this is a breaking change.
    """

    action: MigrationAction
    target: str
    old_value: str = ""
    new_value: str = ""
    description: str = ""
    breaking: bool = False


@dataclass
class MigrationPlan:
    """Complete migration plan between versions.

    Attributes:
        from_version: Source version.
        to_version: Target version.
        steps: Ordered migration steps.
        generated_at: Plan generation time.
    """

    from_version: str
    to_version: str
    steps: list[MigrationStep] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)

    @property
    def step_count(self) -> int:
        """Execute Step Count operations natively."""
        return len(self.steps)

    @property
    def breaking_count(self) -> int:
        """Execute Breaking Count operations natively."""
        return sum(1 for s in self.steps if s.breaking)

    @property
    def is_safe(self) -> bool:
        """Execute Is Safe operations natively."""
        return self.breaking_count == 0


class MigrationEngine:
    """Generate and manage API migration plans.

    Example::

        engine = MigrationEngine()
        engine.add_rename("search", "search_code", "0.9.0", "1.0.0")
        plan = engine.generate_plan("0.9.0", "1.0.0")
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._steps: list[MigrationStep] = []
        self._plans: dict[str, MigrationPlan] = {}

    @property
    def total_steps(self) -> int:
        """Execute Total Steps operations natively."""
        return len(self._steps)

    def add_rename(
        self, old_name: str, new_name: str,
        from_version: str = "", to_version: str = "",
    ) -> None:
        """Record a rename migration."""
        self._steps.append(MigrationStep(
            action=MigrationAction.RENAME,
            target=old_name,
            old_value=old_name,
            new_value=new_name,
            description=f"Renamed '{old_name}' to '{new_name}'",
            breaking=True,
        ))

    def add_removal(self, name: str, from_version: str = "") -> None:
        """Record a removal."""
        self._steps.append(MigrationStep(
            action=MigrationAction.REMOVE,
            target=name,
            old_value=name,
            description=f"Removed '{name}'",
            breaking=True,
        ))

    def add_deprecation(
        self, name: str, replacement: str = "",
        from_version: str = "",
    ) -> None:
        """Record a deprecation."""
        desc = f"Deprecated '{name}'"
        if replacement:
            desc += f", use '{replacement}' instead"
        self._steps.append(MigrationStep(
            action=MigrationAction.DEPRECATE,
            target=name,
            new_value=replacement,
            description=desc,
            breaking=False,
        ))

    def add_replacement(
        self, old_name: str, new_name: str,
    ) -> None:
        """Record a full replacement."""
        self._steps.append(MigrationStep(
            action=MigrationAction.REPLACE,
            target=old_name,
            old_value=old_name,
            new_value=new_name,
            description=f"Replaced '{old_name}' with '{new_name}'",
            breaking=True,
        ))

    def generate_plan(self, from_version: str, to_version: str) -> MigrationPlan:
        """Generate a migration plan."""
        plan = MigrationPlan(
            from_version=from_version,
            to_version=to_version,
            steps=list(self._steps),
        )
        key = f"{from_version}→{to_version}"
        self._plans[key] = plan
        return plan

    def to_markdown(self, plan: MigrationPlan) -> str:
        """Render migration plan as markdown."""
        lines = [
            f"# Migration Guide: {plan.from_version} → {plan.to_version}",
            "",
            f"**Steps**: {plan.step_count} | "
            f"**Breaking**: {plan.breaking_count}",
            "",
        ]

        if plan.breaking_count > 0:
            lines.extend([
                "> [!WARNING]",
                f"> This migration contains {plan.breaking_count} breaking change(s).",
                "",
            ])

        for i, step in enumerate(plan.steps, 1):
            icon = "🔴" if step.breaking else "🟢"
            lines.append(f"{i}. {icon} **{step.action.value}**: {step.description}")

        return "\n".join(lines)


__all__ = [
    "MigrationAction",
    "MigrationEngine",
    "MigrationPlan",
    "MigrationStep",
]
