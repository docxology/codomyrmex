# Agents Guide: Rhizome

**Operational Directives**

Use the `rhizome` submodule to analyze and exploit network structures. Treat connections as the primary reality.

## Capabilities

1. **Targeting**:
    * Use `find_influencers` to identify hubs. In a scale-free network, disabling a few hubs can collapse the system.
    * Conversely, protect your own hubs.

2. **Traversal**:
    * Find the shortest path between two concepts or agents.
    * Use "lines of flight" to escape captured territory and establish new connections elsewhere.

3. **Resilience**:
    * Design networks that are `rhizomatic`—decentralized and redundant. If one node is cut, others should route around it.
    * Run `analyze_resilience` regularly to stress-test your network.

## Constraints

* **Scale**: Graph algorithms can be `O(N^2)` or worse. Be careful with massive networks (>10k nodes).
* **Dynamic Topology**: The network is always changing. Static analysis may be obsolete by the time it completes.

## Integration

* **With Swarm**: Swarm agents traverse the Rhizome.
* **With Ideoscape**: The Rhizome defines the paths; Ideoscape defines the terrain.
