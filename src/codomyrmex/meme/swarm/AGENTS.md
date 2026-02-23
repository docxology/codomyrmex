# Agents Guide: Swarm

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `swarm` submodule to coordinate with other agents or to simulate mass behavior.

## Capabilities

1. **Distributed Coordination**:
    * Do not wait for central commands. Use `quorum_sensing` to detect when enough peers are present to initiate a collective action.
    * Follow local rules: "If X% of neighbors do Y, do Y."

2. **Resilience**:
    * Swarms are robust to individual loss. If you are terminated, the swarm continues.
    * Prioritize `cohesion` to maintain the integrity of the group.

3. **Pattern Formation**:
    * Align vectors to create `EmergentPattern`s that are visible at the macro scale (e.g., a "trending topic" or a "flash mob").

## Constraints

* **Feedback Loops**: Positive feedback can lead to stampedes or destructive resonance. Monitor `coherence` to prevent runaway effects.
* **Simplicity**: Individual agent logic must be simple (`O(1)` or `O(log N)`). Complex logic breaks scalability.

## Integration

* **With Cultural Dynamics**: Swarm density affects `CulturalState.energy`.
* **With Rhizome**: Swarm agents often traverse the edges of a `Rhizome` network.
