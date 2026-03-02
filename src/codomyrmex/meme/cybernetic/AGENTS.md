# Codomyrmex Agents -- src/codomyrmex/meme/cybernetic

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Implements second-order cybernetic control systems with PID controllers, feedback loops, and homeostatic regulation. Manages named control variables with setpoints and computes real-time control signals to drive system variables toward targets.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `CyberneticEngine` | Orchestrator managing named PID controllers, computing control signals |
| `control.py` | `PIDController` | Proportional-Integral-Derivative controller with error tracking |
| `control.py` | `apply_control` | Apply a single feedback loop transformation (positive or negative) |
| `models.py` | `ControlSystem` | Named system with target setpoints |
| `models.py` | `SystemState` | Current measured variable values with timestamp |
| `models.py` | `FeedbackLoop` | Feedback mechanism between source and target variables |
| `models.py` | `FeedbackType` | POSITIVE (reinforcing) or NEGATIVE (balancing) |
| `models.py` | `Homeostat` | Ashby-style ultrastable system with variable bounds |

## Operating Contracts

- `CyberneticEngine.update` only processes variables present in both `setpoints` and `current_state`.
- PID integral accumulates without anti-windup; callers must manage saturation.
- `dt` is clamped to minimum 0.001 to prevent division by zero in derivative.
- `Homeostat` is defined as a data model; adaptation logic is not yet implemented.
- Positive feedback leads to exponential growth; always pair with limits or negative feedback.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (self-contained within `meme` package)
- **Used by**: Any meme sub-module needing regulation (e.g., damping contagion outbreaks, stabilizing swarm behavior)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
