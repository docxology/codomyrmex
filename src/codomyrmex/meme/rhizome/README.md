# Rhizome Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Distributed Network Analysis**

The `codomyrmex.meme.rhizome` submodule models non-hierarchical, interconnected networks of information (Deleuze & Guattari). It focuses on graph topology, connectivity, and resilience in distributed systems.

## Key Components

### 1. Data Models (`models.py`)

* **`Graph`**: The network structure.
  * `nodes`: Agents/Ideas/Servers.
  * `edges`: Connections/Relationships.
  * `topology`: Random, Scale-Free, Small-World.
* **`Node`**: A point in the network.
* **`Edge`**: A connection between nodes (weighted).

### 2. Network Logic (`network.py`)

* **`build_graph`**: Generates synthetic networks.
  * **Scale-Free**: Hub-and-spoke models (like the Web).
  * **Small-World**: High clustering, short paths (social networks).
* **`calculate_centrality`**: Identifies key nodes (influencers/hubs).

### 3. Rhizome Engine (`engine.py`)

* **`RhizomeEngine`**: Orchestrator.
  * `analyze_resilience()`: Tests robustness against node failure/attack.
  * `find_influencers()`: Returns high-centrality nodes.

## Usage

```python
from codomyrmex.meme.rhizome import RhizomeEngine

engine = RhizomeEngine()
engine.initialize_network(size=100, topology="scale_free")

# Identify key targets
influencers = engine.find_influencers(top_n=3)
print(f"Top Targets: {influencers}")
```
