# Agents Guide: Memetics

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Operational Directives**

Use the `memetics` submodule to analyze, manipulate, and generate raw informational material. This is your toolkit for "genetic engineering" of ideas.

## Capabilities

1. **Dissection**:
    * Use `MemeticEngine.dissect()` to break down user input or corpus text into atomic units.
    * Classify these units by `MemeType` (Belief, Strategy, Norm, etc.) to understand the composition of the input.

2. **Fitness Assessment**:
    * Calculate `virality_score` before deploying any output intended for persuasion.
    * Aim for high `fidelity` (accuracy of transmission) and `fecundity` (spread potential).

3. **Evolutionary Generation**:
    * When generating creative content, create a population of variants.
    * Use `MemeticEngine.evolve()` to refine these variants against a fitness function (e.g., specific keywords, sentiment constraint).

## Constraints

* **Mutation Risk**: High mutation rates can lead to `semantic_drift` where the original meaning is lost. Keep mutation rates low (0.1 - 0.3) for stability.
* **Resource Intensity**: Evolutionary algorithms can be computationally expensive. Use small population sizes (10-50) for real-time applications.

## Integration

* **With Semiotics**: Use `semiotic.SemioticAnalyzer` to verify that mutated memes still carry the intended signifier.
* **With Contagion**: Pass evolved memes to `contagion.simulation` to predict their spread.
