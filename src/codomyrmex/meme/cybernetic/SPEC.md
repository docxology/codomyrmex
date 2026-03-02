# Cybernetic -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Implements second-order cybernetic control systems with PID controllers, feedback loops, and homeostatic regulation. Models system state as named variables with setpoints, and applies proportional-integral-derivative control to drive variables toward targets.

## Architecture

Controller-based feedback regulation pattern. `CyberneticEngine` manages named `PIDController` instances and computes control signals by comparing current `SystemState` variables against `ControlSystem` setpoints. `apply_control` applies individual feedback loop transformations (positive or negative).

## Key Classes

### `CyberneticEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_controller` | `var_name: str, kp, ki, kd: float` | `None` | Register a PID controller for a named variable |
| `update` | `system: ControlSystem, current_state: SystemState` | `dict[str, float]` | Compute control signals for all controlled variables |

### `PIDController`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compute` | `setpoint: float, measured_value: float, dt: float` | `float` | Calculate PID control output from error, integral, and derivative terms |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `SystemState` | `variables: dict[str, float], timestamp: float` | Current measured state of the system |
| `FeedbackLoop` | `source_var, target_var, gain, feedback_type, delay` | A feedback mechanism between two variables |
| `FeedbackType` | `POSITIVE, NEGATIVE` | Feedback loop classification (reinforcing vs. balancing) |
| `Homeostat` | `essential_vars, bounds, adaptation_rate, current_config` | Ashby-style ultrastable system maintaining variables within bounds |
| `ControlSystem` | `name, setpoints: dict[str, float], active: bool` | Named control system with target setpoints |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `apply_control` | `current_val: float, loop: FeedbackLoop, input_signal: float` | `float` | Apply a single feedback loop transformation (add or subtract gain-weighted signal) |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`time`, `dataclasses`, `enum`)

## Constraints

- `dt` is clamped to minimum 0.001 to prevent division by zero in derivative calculation.
- PID integral term accumulates without anti-windup; callers must manage saturation externally.
- `Homeostat` is defined as a data model but adaptation logic is not yet implemented.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `CyberneticEngine.update` silently skips variables not present in both `setpoints` and `current_state`.
- PID derivative term returns 0.0 when `dt <= 0`.
