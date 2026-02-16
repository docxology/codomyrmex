# Meme Module

**Unified Memetic Warfare & Information Dynamics**

The `codomyrmex.meme` module is a comprehensive framework for modeling, analyzing, and engineering the propagation, mutation, and evolution of information units (memes) through cultural, cognitive, and network substrates. It treats ideas as living entities subject to evolutionary pressures, epidemiological spread, and cybernetic control.

## Architecture

The module is organized into 12 specialized submodules, clustered by function:

### Phase 1: Core Engine

* **`memetics`**: The fundamental physics of the system. Defines `Meme`, `Memeplex`, fitness landscapes, and genetic operators (mutation, recombination).
* **`semiotic`**: The layer of meaning and interpretation. Handles sign-signified relationships, semiotic drift, and linguistic steganography.

### Phase 2: Propagation

* **`contagion`**: Epidemiological models (SIR, SIS, SEIR) and cascade detection for tracking information spread across networks.
* **`narrative`**: Computational narratology. Models narrative arcs (Hero's Journey), archetypes, and synthetic myth generation.

### Phase 3: Dynamics

* **`cultural_dynamics`**: Macro-scale analysis of cultural trends, oscillations (zeitgeist), and power dynamics.
* **`swarm`**: Collective behavior modeling. Implements flocking algorithms, consensus mechanisms, and emergent pattern detection.
* **`neurolinguistic`**: Micro-scale cognitive engineering. Focuses on framing, linguistic patterns (Milton/Meta models), and bias exploitation.

### Phase 4: Topology

* **`ideoscape`**: Information cartography. Visualizes the "terrain" of ideas using 2D/3D mapping and projection techniques.
* **`rhizome`**: Network structure analysis. Models distributed, non-hierarchical (rhizomatic) connections and graph topology.

### Phase 5: Reality & Truth

* **`epistemic`**: Truth verification and knowledge warfare. Models facts, beliefs, evidence, and epistemic territory.
* **`hyperreality`**: Simulation theory. Models Baudrillardian simulacra, reality tunnels, and the levels of simulation.

### Phase 6: Control

* **`cybernetic`**: Second-order cybernetics and control systems. Implements feedback loops, homeostatic regulation, and autonomic control.

## Usage

```python
from codomyrmex.meme import MemeticEngine, Meme

# Initialize engine
engine = MemeticEngine()

# Dissect text into memes
text = "The quick brown fox jumps over the lazy dog."
memes = engine.dissect(text)

# Analyze fitness
for meme in memes:
    print(f"Meme: {meme.content}, Fitness: {meme.fitness}")
```
