"""
Gradual rollout management.

Provides a RolloutManager for controlling staged feature flag rollouts with
pause, advance, and status inspection capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RolloutState(Enum):
    """Lifecycle states of a rollout."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"


@dataclass
class RolloutConfig:
    """Configuration for a gradual rollout.

    Attributes:
        stages: List of rollout percentages (e.g. [5, 25, 50, 100]).
        stage_delay_seconds: Minimum seconds between automatic stage advances.
    """
    stages: list[float] = field(default_factory=lambda: [5.0, 25.0, 50.0, 100.0])
    stage_delay_seconds: float = 3600.0

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.stages:
            raise ValueError("stages must contain at least one percentage value")
        for pct in self.stages:
            if not (0.0 < pct <= 100.0):
                raise ValueError(f"Each stage must be in (0, 100], got {pct}")


@dataclass
class RolloutStatus:
    """Snapshot of a rollout's current state.

    Attributes:
        flag_name: The flag this rollout controls.
        state: Current lifecycle state.
        current_stage_index: Index into the config's stages list.
        current_percentage: The active rollout percentage.
        started_at: When the rollout was created.
        updated_at: When the rollout was last modified.
        metadata: Arbitrary extra data attached to the rollout.
    """
    flag_name: str
    state: RolloutState
    current_stage_index: int
    current_percentage: float
    started_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class RolloutManager:
    """Manages gradual rollouts for feature flags.

    Tracks per-flag rollout state and allows advancing through staged
    percentages, pausing, and inspecting status.
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._rollouts: dict[str, _RolloutEntry] = {}

    def create_rollout(self, flag_name: str, config: RolloutConfig) -> RolloutStatus:
        """Create a new rollout for a flag.

        If a rollout already exists for the flag it is replaced.

        Args:
            flag_name: The feature flag to roll out.
            config: The staged rollout configuration.

        Returns:
            The initial RolloutStatus.
        """
        now = datetime.now()
        entry = _RolloutEntry(
            flag_name=flag_name,
            config=config,
            state=RolloutState.ACTIVE,
            current_stage_index=0,
            started_at=now,
            updated_at=now,
        )
        self._rollouts[flag_name] = entry
        return self._to_status(entry)

    def advance_rollout(self, flag_name: str) -> RolloutStatus:
        """Advance the rollout to the next stage.

        Args:
            flag_name: The feature flag to advance.

        Returns:
            The updated RolloutStatus.

        Raises:
            KeyError: If no rollout exists for the flag.
            RuntimeError: If the rollout is not in an advanceable state.
        """
        entry = self._get_entry(flag_name)
        if entry.state not in (RolloutState.ACTIVE, RolloutState.PAUSED):
            raise RuntimeError(
                f"Cannot advance rollout in state {entry.state.value}"
            )

        next_index = entry.current_stage_index + 1
        if next_index >= len(entry.config.stages):
            entry.state = RolloutState.COMPLETED
        else:
            entry.current_stage_index = next_index
            entry.state = RolloutState.ACTIVE

        entry.updated_at = datetime.now()
        return self._to_status(entry)

    def get_rollout_status(self, flag_name: str) -> RolloutStatus:
        """Return the current status of a flag's rollout.

        Args:
            flag_name: The feature flag to query.

        Returns:
            The current RolloutStatus.

        Raises:
            KeyError: If no rollout exists for the flag.
        """
        return self._to_status(self._get_entry(flag_name))

    def pause_rollout(self, flag_name: str) -> RolloutStatus:
        """Pause an active rollout.

        Args:
            flag_name: The feature flag to pause.

        Returns:
            The updated RolloutStatus.

        Raises:
            KeyError: If no rollout exists for the flag.
            RuntimeError: If the rollout is not active.
        """
        entry = self._get_entry(flag_name)
        if entry.state != RolloutState.ACTIVE:
            raise RuntimeError(
                f"Can only pause an active rollout, current state: {entry.state.value}"
            )
        entry.state = RolloutState.PAUSED
        entry.updated_at = datetime.now()
        return self._to_status(entry)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_entry(self, flag_name: str) -> _RolloutEntry:
        """get Entry ."""
        try:
            return self._rollouts[flag_name]
        except KeyError:
            raise KeyError(f"No rollout found for flag: {flag_name}") from None

    @staticmethod
    def _to_status(entry: _RolloutEntry) -> RolloutStatus:
        """to Status ."""
        pct = entry.config.stages[entry.current_stage_index]
        return RolloutStatus(
            flag_name=entry.flag_name,
            state=entry.state,
            current_stage_index=entry.current_stage_index,
            current_percentage=pct,
            started_at=entry.started_at,
            updated_at=entry.updated_at,
        )


@dataclass
class _RolloutEntry:
    """Internal mutable storage for a rollout."""
    flag_name: str
    config: RolloutConfig
    state: RolloutState
    current_stage_index: int
    started_at: datetime
    updated_at: datetime


__all__ = [
    "RolloutConfig",
    "RolloutManager",
    "RolloutState",
    "RolloutStatus",
]
