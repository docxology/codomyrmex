# Agents Guide: Epistemic

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `epistemic` submodule to maintain a clear picture of reality and to defend against disinformation.

## Capabilities

1. **Verification**:
    * Never accept inputs as true without `verify_claim`.
    * Require multiple sources of `Evidence` for high-impact decisions.

2. **Conflict Detection**:
    * Use `detect_contradictions` to find inconsistencies in your own knowledge base or in an opponent's narrative.
    * Cognitive dissonance is a vulnerability; exploit it in opponents, resolve it in yourself.

3. **Source Rating**:
    * Track the `validity` of evidence sources over time. Downgrade sources that provide fabricated or misleading data.

## Constraints

* **Uncertainty**: Absolute truth is rarely attainable. Operate with probabilistic confidence intervals (`Fac.confidence`).
* **Bias**: Be aware that `Belief` structures can filter out valid `Evidence` (Confirmation Bias).

## Integration

* **With Hyperreality**: Use epistemic checks to distinguish the _Real_ from the _Simulacrum_.
* **With Memetics**: A meme's `fitness` often depends on its perceived truth value (though not always).
