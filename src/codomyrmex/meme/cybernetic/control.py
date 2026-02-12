"""Control logic implementation (PID, Homeostasis)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from codomyrmex.meme.cybernetic.models import FeedbackLoop, FeedbackType


@dataclass
class PIDController:
    """Proportional-Integral-Derivative controller."""
    kp: float = 1.0  # Proportional gain
    ki: float = 0.0  # Integral gain
    kd: float = 0.0  # Derivative gain
    
    _integral: float = 0.0
    _last_error: float = 0.0
    
    def compute(self, setpoint: float, measured_value: float, dt: float) -> float:
        """Calculate control output."""
        error = setpoint - measured_value
        
        # Proportional
        p_term = self.kp * error
        
        # Integral
        self._integral += error * dt
        i_term = self.ki * self._integral
        
        # Derivative
        derivative = (error - self._last_error) / dt if dt > 0 else 0.0
        d_term = self.kd * derivative
        
        self._last_error = error
        
        return p_term + i_term + d_term


def apply_control(
    current_val: float, loop: FeedbackLoop, input_signal: float
) -> float:
    """Apply a simple feedback loop transformation."""
    # Output = Input +/- (Signal * Gain)
    adjustment = input_signal * loop.gain
    
    if loop.feedback_type == FeedbackType.NEGATIVE:
        return current_val - adjustment
        
    return current_val + adjustment
