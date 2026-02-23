# Agents Guide: Cybernetic

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `cybernetic` submodule to "steer the ship." Without control loops, systems drift into entropy.

## Capabilities

1. **Regulation (Negative Feedback)**:
    * Use negative feedback to stabilize volatile systems (e.g., damping a `contagion` outbreak or calming a `cultural_dynamics` oscillation).
    * Monitor the `error` (difference between `setpoint` and `current_state`).

2. **Amplification (Positive Feedback)**:
    * Use positive feedback to accelerate growth (e.g., making a meme viral).
    * **Warning**: Positive feedback leads to exponential growth and potential collapse. Always set a `limit`.

3. **Autopoiesis**:
    * Design systems that are self-creating and self-maintaining. A robust agent should be able to repair its own state (`Homeostat`).

## Constraints

* **Delays**: Feedback delays can cause oscillation. Ensure sensors are fast.
* **Loop Gain**: Too high gain = instability. Too low gain = sluggish response. Tune your PIDs.

## Integration

* **With All Modules**: Cybernetics is the "governor" layer that can sit on top of any other module to regulate it.
