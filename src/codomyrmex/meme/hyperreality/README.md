# Hyperreality Submodule

**Simulation Theory & Simulacra**

The `codomyrmex.meme.hyperreality` submodule models the layers of simulation that obscure reality (Baudrillard, Eco). It deals with simulacra—copies without originals—and the construction of artificial realities.

## Key Components

### 1. Data Models (`models.py`)

* **`Simulacrum`**: An object or entity that simulates another.
  * `fidelity`: Accuracy of the copy.
  * `order`: The order of simulacra (1st: Reflection, 2nd: Mask, 3rd: Absence, 4th: Pure Simulacrum).
* **`RealityTunnel`**: A filtered perception of reality imposed on a subject.
* **`SimulationLevel`**: Enum (Base Reality, Augmented, Virtual, Hyperreal).

### 2. Simulation Logic (`simulation.py`)

* **`assess_authenticity(object)`**: Determines if an object is real or a simulation.
* **`generate_simulacrum(target)`**: Creates a copy of a target object.

### 3. Hyperreality Engine (`engine.py`)

* **`HyperrealityEngine`**: Orchestrator.
  * `check_consensus(reality_tunnel)`: Sees if a subjective reality aligns with the consensus.
  * `superimpose(base, layer)`: Overlays a simulation on top of base reality.

## Usage

```python
from codomyrmex.meme.hyperreality import HyperrealityEngine, SimulationLevel

engine = HyperrealityEngine()

# Check simulation level
level = engine.assess_level(some_object)

if level == SimulationLevel.HYPERREAL:
    print("Warning: Object has no basis in reality.")
```
