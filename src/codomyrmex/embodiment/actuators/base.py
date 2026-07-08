from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class ActuatorCommand:
    actuator_id: str
    command_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)


@dataclass
class ActuatorStatus:
    actuator_id: str
    status: str
    feedback: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)


class SimulatedActuator:
    def __init__(self, actuator_id: str) -> None:
        self.actuator_id = actuator_id
        self.is_connected = False
        self._position: Any = None

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def execute(self, command: ActuatorCommand) -> bool:
        if not self.is_connected or command.actuator_id != self.actuator_id:
            return False
        if command.command_type == "move":
            self._position = command.parameters.get("target")
        return True

    def get_status(self) -> ActuatorStatus:
        if not self.is_connected:
            return ActuatorStatus(self.actuator_id, "disconnected", {})
        return ActuatorStatus(self.actuator_id, "ok", {"position": self._position})


class MockActuator(SimulatedActuator):
    pass
