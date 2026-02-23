# Cultural Dynamics Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Macro-Scale Cultural Modeling**

The `codomyrmex.meme.cultural_dynamics` submodule tracks the large-scale movements of ideology and power in a population. It models culture as a dynamic system subject to oscillation, momentum, and inertia.

## Key Components

### 1. Data Models (`models.py`)

* **`CulturalState`**: Snapshot of the collective consciousness at a point in time.
  * `dimensions`: Map of current values (e.g., Liberty/Authority, Tradition/Innovation).
  * `momentum`: Rate of change in each dimension.
  * `energy`: Intensity of discourse.
* **`Trajectory`**: Sequence of states over time.
* **`PowerMap`**: Graph of influence and capital flow.
* **`Signal`**: Key events driving cultural shifts.

### 2. Oscillation (`oscillation.py`)

* **`detect_oscillation`**: Identifies cyclic trends (e.g., generational shifts).
* **`backlash_model`**: Predicts the "rubber-band" reaction to rapid cultural change.

### 3. Power Analysis (`power.py`)

* **`map_power_dynamics`**: Visualizes where influence lies in the network.
* **`centrality_scores`**: Measures the importance of nodes.

### 4. Dynamics Engine (`engine.py`)

* **`CulturalDynamicsEngine`**: Orchestrator.
  * `zeitgeist_trajectory(signals)`: Computes the current path of the culture.
  * `mutation_probability(state)`: Estimates how likely radical new ideas are to take hold based on societal tension ("energy").

## Usage

```python
from codomyrmex.meme.cultural_dynamics import CulturalDynamicsEngine, Signal

engine = CulturalDynamicsEngine()

# Input signals
signals = [
    Signal(source="News", content="Scandal", strength=0.8, valence=-1.0, dimension="trust"),
    # ...
]

# Calculate trajectory
traj = engine.zeitgeist_trajectory(signals)

print(f"Current Trust Trend: {traj.trend_vector['trust']}")
```
