# Cybernetic Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Control Systems & Feedback Loops**

The `codomyrmex.meme.cybernetic` submodule provides the control logic for the entire system. It uses principles from cybernetics (Wiener, Ashby) to maintain stability (homeostasis) or drive directed change (heterostasis).

## Key Components

### 1. Data Models (`models.py`)

* **`ControlSystem`**: The entity managing the loop.
  * `setpoint`: Desired state.
  * `sensor`: Input mechanism.
  * `actuator`: Output mechanism.
* **`FeedbackLoop`**: The cycle of input-process-output-input.
  * `loop_type`: Positive (amplifying) or Negative (damping).
  * `gain`: Strength of the feedback.
* **`SystemState`**: Current snapshot of the system variables.

### 2. Control Logic (`control.py`)

* **`PIDController`**: Proportional-Integral-Derivative controller implementation.
  * `compute(error)`: Returns the necessary correction.
* **`Homeostat`**: A self-regulating system that seeks stability.

### 3. Cybernetic Engine (`engine.py`)

* **`CyberneticEngine`**: Orchestrator.
  * `regulate(system)`: Applies control logic to bring a system to its setpoint.
  * `amplify(signal)`: Uses positive feedback to grow a signal.

## Usage

```python
from codomyrmex.meme.cybernetic import CyberneticEngine, PIDController

pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
engine = CyberneticEngine(controller=pid)

current_val = 0.8
target = 1.0

correction = engine.compute_correction(current_val, target)
print(f"Apply correction: {correction}")
```
