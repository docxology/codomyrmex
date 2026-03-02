"""CyberneticEngine — orchestrator for system control."""

from __future__ import annotations

import time

from codomyrmex.meme.cybernetic.control import PIDController
from codomyrmex.meme.cybernetic.models import (
    ControlSystem,
    SystemState,
)


class CyberneticEngine:
    """Engine for managing cybernetic systems and feedback loops."""

    def __init__(self):
        self._controllers: dict[str, PIDController] = {}
        self._last_tick = time.time()

    def add_controller(self, var_name: str, kp: float = 1.0, ki: float = 0.1, kd: float = 0.0):
        """Register a PID controller for a specific variable."""
        self._controllers[var_name] = PIDController(kp, ki, kd)

    def update(self, system: ControlSystem, current_state: SystemState) -> dict[str, float]:
        """Update control outputs based on current state and setpoints.

        Returns:
            Dict of control signals (adjustments) for each variable.
        """
        now = time.time()
        dt = now - self._last_tick
        if dt <= 0:
            dt = 0.001  # Prevent div/0

        outputs = {}

        for var, setpoint in system.setpoints.items():
            if var in self._controllers and var in current_state.variables:
                pid = self._controllers[var]
                measured = current_state.variables[var]

                # Compute required adjustment signal
                signal = pid.compute(setpoint, measured, dt)
                outputs[var] = signal

        self._last_tick = now
        return outputs
