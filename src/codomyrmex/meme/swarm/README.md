# Swarm Submodule

**Collective Intelligence & Emergence**

The `codomyrmex.meme.swarm` submodule models decentralized, self-organizing systems. It implements algorithms for flocking, consensus, and emergent behavior, simulating how individual agents (or ideas) coordinate without a central commander.

## Key Components

### 1. Data Models (`models.py`)

* **`SwarmAgent`**: An autonomous unit with local rules.
  * `position`, `velocity`: State vectors in the abstract or physical space.
  * `state`: Internal mode (foraging, defending, voting).
* **`SwarmState`**: Aggregate properties of the swarm (centroid, coherence).
* **`EmergentPattern`**: Recognized macro-structures (vortex, line, cluster).

### 2. Flocking (`flocking.py`)

* **`update_flock`**: Implementation of Reynolds' Boids algorithm.
  * **Separation**: Avoid crowding neighbors.
  * **Alignment**: Steer towards average heading of neighbors.
  * **Cohesion**: Steer towards average position of neighbors.

### 3. Consensus (`consensus.py`)

* **`reach_consensus`**: Distributed agreement protocol.
* **`quorum_sensing`**: Density-dependent behavior switching.

### 4. Swarm Engine (`engine.py`)

* **`SwarmEngine`**: Simulation runner.
  * `step()`: Advance the physics/logic of the swarm.

## Usage

```python
from codomyrmex.meme.swarm import SwarmEngine, FlockingParams

engine = SwarmEngine(num_agents=100)

# Simulate 50 steps
for _ in range(50):
    state = engine.step()
    print(f"Coherence: {state.coherence}")

```
