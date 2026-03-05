"""Base classes for actuator controllers."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActuatorCommand:
    """Base class for actuator commands."""

    actuator_id: str
    command_type: str
    parameters: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ActuatorStatus:
    """Base class for actuator status reporting."""

    actuator_id: str
    status: str
    feedback: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class ActuatorController(ABC):
    """Abstract base class for all actuator controllers."""

    def __init__(self, actuator_id: str) -> None:
        self.actuator_id = actuator_id
        self._is_connected = False
        self._last_command: ActuatorCommand | None = None

    @property
    def is_connected(self) -> bool:
        """Return True if the actuator is connected and ready."""
        return self._is_connected

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the physical or simulated actuator."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the actuator."""

    @abstractmethod
    def execute(self, command: ActuatorCommand) -> bool:
        """Execute a command on the actuator."""

    @abstractmethod
    def get_status(self) -> ActuatorStatus:
        """Get the current status of the actuator."""


class MockActuator(ActuatorController):
    """A generic mock actuator for testing without hardware."""

    def __init__(self, actuator_id: str) -> None:
        super().__init__(actuator_id)
        self.current_state: dict[str, Any] = {"position": 0.0, "velocity": 0.0}

    def connect(self) -> bool:
        self._is_connected = True
        return True

    def disconnect(self) -> None:
        self._is_connected = False

    def execute(self, command: ActuatorCommand) -> bool:
        if not self.is_connected:
            return False
        self._last_command = command
        if command.command_type == "move":
            self.current_state["position"] = command.parameters.get(
                "target", self.current_state["position"]
            )
        return True

    def get_status(self) -> ActuatorStatus:
        return ActuatorStatus(
            actuator_id=self.actuator_id,
            status="ok" if self.is_connected else "disconnected",
            feedback=self.current_state.copy(),
        )
