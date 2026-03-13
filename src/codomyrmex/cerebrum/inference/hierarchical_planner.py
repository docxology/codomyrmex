"""Hierarchical free-energy planner.

Stacks multiple :class:`~codomyrmex.cerebrum.inference.free_energy_loop.FreeEnergyLoop`
instances at increasing abstraction levels.  A top level plans abstract goals;
each level's action becomes the next (lower) level's observation, implementing
temporal abstraction.

Builds on :class:`FreeEnergyLoop`, :class:`StepResult`, and
:class:`LoopResult`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from codomyrmex.cerebrum.inference.free_energy_loop import (
        FreeEnergyLoop,
        LoopResult,
    )

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PlanLevel:
    """Configuration for one level of the hierarchy.

    Attributes:
        name: Human-readable label (e.g. ``"strategic"``, ``"tactical"``).
        loop: The FreeEnergyLoop that runs at this level.
    """

    name: str
    loop: FreeEnergyLoop


@dataclass
class LevelResult:
    """Outcome of one planning level.

    Attributes:
        name: Level name.
        loop_result: Full FreeEnergyLoop result.
        output_action: The action passed down to the next level.
    """

    name: str
    loop_result: LoopResult
    output_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "converged": self.loop_result.converged,
            "steps": self.loop_result.steps,
            "final_free_energy": round(self.loop_result.final_free_energy, 6),
            "output_action": self.output_action,
            "action_history": self.loop_result.action_history,
        }


@dataclass
class HierarchicalPlan:
    """Result of hierarchical planning.

    Attributes:
        levels: Per-level results (top → bottom).
        total_steps: Sum of steps across all levels.
        all_converged: Whether every level converged.
    """

    levels: list[LevelResult] = field(default_factory=list)
    total_steps: int = 0
    all_converged: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_steps": self.total_steps,
            "all_converged": self.all_converged,
            "level_count": len(self.levels),
            "levels": [lv.to_dict() for lv in self.levels],
        }


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------


class HierarchicalPlanner:
    """Multi-level active inference planner with temporal abstraction.

    The planner runs levels from top (most abstract) to bottom (most
    concrete).  Each level's selected action is injected as the
    ``"parent_action"`` key in the next level's observation dict.

    Usage::

        from codomyrmex.cerebrum import ActiveInferenceAgent
        from codomyrmex.cerebrum.inference.free_energy_loop import FreeEnergyLoop

        agent_hi = ActiveInferenceAgent(...)
        agent_lo = ActiveInferenceAgent(...)

        planner = HierarchicalPlanner(levels=[
            PlanLevel("strategic", FreeEnergyLoop(agent_hi, max_steps=20)),
            PlanLevel("tactical",  FreeEnergyLoop(agent_lo, max_steps=50)),
        ])
        plan = planner.plan({"strategic": {"goal": "explore"}})

    Args:
        levels: Ordered list of plan levels (top-first).
        max_total_steps: Global step budget across all levels.
    """

    def __init__(
        self,
        levels: list[PlanLevel],
        max_total_steps: int = 200,
    ) -> None:
        if not levels:
            raise ValueError("At least one PlanLevel is required")
        if max_total_steps < 1:
            raise ValueError("max_total_steps must be >= 1")

        self._levels = levels
        self._max_total_steps = max_total_steps

    def plan(self, observations: dict[str, dict[str, Any]]) -> HierarchicalPlan:
        """Execute hierarchical planning.

        Args:
            observations: Mapping of level name → initial observation dict.
                          Missing levels receive ``{}``.

        Returns:
            :class:`HierarchicalPlan` with per-level results.
        """
        result = HierarchicalPlan()
        parent_action: str | None = None
        total_steps = 0
        all_converged = True

        for level in self._levels:
            obs = dict(observations.get(level.name, {}))

            # Inject parent action as temporal abstraction bridge
            if parent_action is not None:
                obs["parent_action"] = parent_action

            remaining = self._max_total_steps - total_steps
            if remaining <= 0:
                logger.warning(
                    "Step budget exhausted before level '%s'",
                    level.name,
                )
                all_converged = False
                break

            # Temporarily cap this level's max_steps
            original_max = level.loop.max_steps
            level.loop.max_steps = min(original_max, remaining)

            try:
                loop_result = level.loop.run(obs)
            finally:
                level.loop.max_steps = original_max

            total_steps += loop_result.steps

            # The last action becomes input to the next level
            output_action = (
                loop_result.action_history[-1]
                if loop_result.action_history
                else "noop"
            )

            if not loop_result.converged:
                all_converged = False

            level_result = LevelResult(
                name=level.name,
                loop_result=loop_result,
                output_action=output_action,
            )
            result.levels.append(level_result)
            parent_action = output_action

            logger.info(
                "Level '%s': %d steps, converged=%s, action='%s'",
                level.name,
                loop_result.steps,
                loop_result.converged,
                output_action,
            )

        result.total_steps = total_steps
        result.all_converged = all_converged
        return result

    @property
    def level_names(self) -> list[str]:
        """Return the names of all planning levels."""
        return [lv.name for lv in self._levels]


__all__ = [
    "HierarchicalPlan",
    "HierarchicalPlanner",
    "LevelResult",
    "PlanLevel",
]
