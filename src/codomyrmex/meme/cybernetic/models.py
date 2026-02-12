"""Data models for cybernetic systems."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class FeedbackType(str, Enum):
    """Types of feedback loops."""

    POSITIVE = "positive"  # Reinforcing, destabilizing
    NEGATIVE = "negative"  # Balancing, stabilizing


@dataclass
class SystemState:
    """The state of a system being controlled.

    Attributes:
        variables: Map of variable names to values.
        timestamp: Time of measurement.
    """
    variables: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class FeedbackLoop:
    """A feedback mechanism affecting the system.

    Attributes:
        source_var: Variable being monitored.
        target_var: Variable being affected.
        gain: Amplification factor.
        feedback_type: Positive or Negative.
        delay: Time delay in loop response.
    """
    source_var: str
    target_var: str
    gain: float = 1.0
    feedback_type: FeedbackType = FeedbackType.NEGATIVE
    delay: float = 0.0


@dataclass
class Homeostat:
    """An ultrustable system maintaining essential variables within limits.

    Attributes:
        essential_vars: Variables to keep in range.
        bounds: Map of var -> (min, max).
        adaptation_rate: How fast it reconfigures when out of bounds.
    """
    essential_vars: List[str]
    bounds: Dict[str, tuple] = field(default_factory=dict)
    adaptation_rate: float = 0.1
    current_config: Dict[str, float] = field(default_factory=dict)


@dataclass
class ControlSystem:
    """A cybernetic control system (e.g. thermostat, governor).

    Attributes:
        name: System identifier.
        setpoints: Target values for variables.
        controllers: Active controllers (e.g. PIDs).
    """
    name: str
    setpoints: Dict[str, float] = field(default_factory=dict)
    active: bool = True
