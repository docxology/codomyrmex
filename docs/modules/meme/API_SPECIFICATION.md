# Meme - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Meme module. This is a comprehensive framework for modeling, analyzing, and engineering the propagation, mutation, and evolution of information units (memes) through cultural, cognitive, and network substrates. The module is organized into 12 specialized submodules across 5 phases.

## Module Organization

The API is organized by phase, matching the module's internal architecture:

- **Phase 1 -- Core Engine**: `memetics`, `semiotic`
- **Phase 2 -- Propagation**: `contagion`, `narrative`
- **Phase 3 -- Dynamics**: `cultural_dynamics`, `swarm`, `neurolinguistic`
- **Phase 4 -- Topology**: `hyperreality`, `ideoscape`, `rhizome`
- **Phase 5 -- Truth & Control**: `epistemic`, `cybernetic`

---

## Phase 1: Core Engine

### Submodule: `memetics`

Core memetic engine for modeling memes as discrete replicable information units with fitness, mutation rates, and transmission vectors.

#### Exported Classes

- **`Meme`** -- A discrete, replicable information unit with content and fitness metrics.
- **`Memeplex`** -- A co-adapted complex of memes that replicate together.
- **`MemeticCode`** -- Encoding of a meme's genetic structure for mutation and recombination.
- **`FitnessMap`** -- Landscape mapping meme variants to their fitness scores.
- **`MemeticEngine`** -- Main engine for dissecting text into memes and analyzing fitness.

#### Exported Functions

- **`semantic_drift(meme, magnitude)`** -- Apply semantic drift mutation to a meme.
- **`recombine(meme_a, meme_b)`** -- Recombine two memes to produce offspring.
- **`splice(meme, donor)`** -- Splice genetic material from a donor meme.
- **`virality_score(meme)`** -- Calculate the virality fitness score of a meme.
- **`robustness_score(meme)`** -- Calculate the robustness/fidelity score of a meme.
- **`decay_rate(meme)`** -- Calculate the temporal decay rate of a meme.

### Submodule: `semiotic`

Computational semiotics for sign-signified relationships, semiotic drift, and linguistic encoding.

#### Exported Classes

- **`Sign`** -- A semiotic sign with signifier, signified, and referent.
- **`SignType`** -- Enumeration of sign types (icon, index, symbol).
- **`DriftReport`** -- Report on semiotic drift over time.
- **`SemanticTerritory`** -- Bounded semantic region in meaning-space.
- **`SemioticAnalyzer`** -- Engine for analyzing sign relationships and drift.
- **`SemioticEncoder`** -- Encoder for steganographic embedding of meaning.
- **`MnemonicDevice`** -- Memory aid construction for meme retention.

---

## Phase 2: Propagation

### Submodule: `contagion`

Epidemiological models and cascade detection for tracking information spread across networks.

#### Exported Classes

- **`ContagionModel`** -- Base model for information contagion dynamics.
- **`PropagationTrace`** -- Trace of how information propagated through a network.
- **`Cascade`** -- A detected information cascade event.
- **`CascadeType`** -- Enumeration of cascade types.
- **`ResonanceMap`** -- Map of resonance patterns across a population.
- **`CascadeDetector`** -- Detector for identifying cascades in propagation data.
- **`SIRModel`** -- Susceptible-Infected-Recovered epidemiological model.
- **`SISModel`** -- Susceptible-Infected-Susceptible model (no immunity).
- **`SEIRModel`** -- Susceptible-Exposed-Infected-Recovered model (with latency).

#### Exported Functions

- **`detect_cascades(traces)`** -- Detect cascade events from propagation traces.
- **`run_simulation(model, steps)`** -- Run a contagion simulation for a given number of steps.

### Submodule: `narrative`

Computational narratology for modeling narrative arcs, archetypes, and synthetic myth generation.

#### Exported Classes

- **`Narrative`** -- A complete narrative structure with characters, events, and arcs.
- **`NarrativeArc`** -- A shaped curve describing the tension/resolution pattern of a story.
- **`Archetype`** -- A Jungian archetype (Hero, Shadow, Mentor, etc.).
- **`NarrativeTemplate`** -- Reusable template for narrative construction.
- **`NarrativeEngine`** -- Engine for analyzing and generating narratives.

#### Exported Functions

- **`heros_journey_arc()`** -- Returns the Hero's Journey narrative arc structure.
- **`freytag_pyramid_arc()`** -- Returns Freytag's Pyramid (exposition, rising, climax, falling, denouement).
- **`fichtean_curve_arc()`** -- Returns the Fichtean Curve arc (crisis-driven structure).
- **`synthesize_myth(archetypes, template)`** -- Generate a synthetic myth from archetypes and a template.

---

## Phase 3: Dynamics

### Submodule: `cultural_dynamics`

Macro-scale analysis of cultural trends, oscillations (zeitgeist), and power dynamics.

#### Exported Classes

- **`CulturalState`** -- Snapshot of the cultural landscape at a point in time.
- **`Trajectory`** -- Time-series trajectory of cultural state evolution.
- **`PowerMap`** -- Map of power dynamics between cultural actors.
- **`Signal`** -- A cultural signal or trend indicator.
- **`FrequencyMap`** -- Frequency-domain representation of cultural oscillations.
- **`CulturalDynamicsEngine`** -- Engine for simulating and analyzing cultural dynamics.

#### Exported Functions

- **`detect_oscillation(trajectory)`** -- Detect oscillatory patterns in a cultural trajectory.
- **`backlash_model(signal)`** -- Model the backlash response to a cultural signal.
- **`map_power_dynamics(state)`** -- Generate a power map from a cultural state.

### Submodule: `swarm`

Swarm intelligence, collective behavior modeling, flocking algorithms, and consensus mechanisms.

#### Exported Classes

- **`SwarmAgent`** -- Individual agent in a swarm with position, velocity, and state.
- **`SwarmState`** -- Aggregate state of the entire swarm.
- **`FlockingParams`** -- Parameters for flocking behavior (separation, alignment, cohesion).
- **`EmergentPattern`** -- A detected emergent pattern from swarm behavior.
- **`ConsensusState`** -- State of group consensus formation.
- **`SwarmEngine`** -- Engine for running swarm simulations.

#### Exported Functions

- **`update_flock(agents, params)`** -- Apply one step of flocking behavior to all agents.
- **`reach_consensus(agents)`** -- Simulate consensus formation among agents.
- **`quorum_sensing(agents, threshold)`** -- Detect quorum sensing activation.

### Submodule: `neurolinguistic`

Micro-scale cognitive engineering for framing, linguistic pattern detection, and bias exploitation.

#### Exported Classes

- **`CognitiveFrame`** -- A cognitive frame that shapes perception of information.
- **`LinguisticPattern`** -- A detected linguistic pattern (Milton model, Meta model, etc.).
- **`PersuasionAttempt`** -- Record of a persuasion attempt with technique and target.
- **`BiasInstance`** -- A detected cognitive bias instance.
- **`NeurolinguisticEngine`** -- Engine for cognitive frame analysis and persuasion modeling.

#### Exported Functions

- **`analyze_frames(text)`** -- Analyze cognitive frames present in text.
- **`reframe(text, target_frame)`** -- Reframe text to align with a target cognitive frame.
- **`milton_model_patterns()`** -- Returns the set of Milton model hypnotic language patterns.
- **`meta_model_patterns()`** -- Returns the set of Meta model precision language patterns.
- **`detect_patterns(text)`** -- Detect linguistic patterns in text.

---

## Phase 4: Topology

### Submodule: `hyperreality`

Baudrillardian simulacra, reality tunnel modeling, and simulation level assessment.

#### Exported Classes

- **`Simulacrum`** -- A simulation or copy that has become more real than reality.
- **`SimulationLevel`** -- Enumeration of Baudrillard's four stages of simulation.
- **`RealityTunnel`** -- A reality tunnel representing a subjective worldview.
- **`OntologicalStatus`** -- The ontological status of an information entity.
- **`HyperrealityEngine`** -- Engine for hyperreality analysis and simulacrum generation.

#### Exported Functions

- **`assess_reality_level(entity)`** -- Assess the simulation level of an information entity.
- **`generate_simulacrum(template)`** -- Generate a simulacrum from a template.

### Submodule: `ideoscape`

Information cartography for visualizing the terrain of ideas using 2D/3D mapping.

#### Exported Classes

- **`IdeoscapeLayer`** -- A layer in the ideational landscape.
- **`MapFeature`** -- A feature (mountain, valley, river) in the idea terrain.
- **`CoordinateSystem`** -- Coordinate system for the ideoscape (semantic axes).
- **`ProjectionType`** -- Projection method for mapping high-dimensional ideas to 2D/3D.
- **`TerrainMap`** -- The complete terrain map of an ideational landscape.
- **`IdeoscapeEngine`** -- Engine for generating and analyzing ideational terrain.

#### Exported Functions

- **`generate_terrain(ideas, coordinate_system)`** -- Generate terrain from a set of ideas.
- **`locate_features(terrain)`** -- Locate notable features in the terrain map.

### Submodule: `rhizome`

Rhizomatic network analysis for distributed, non-hierarchical connection modeling.

#### Exported Classes

- **`Node`** -- A node in a rhizomatic network.
- **`Edge`** -- An edge connecting two nodes.
- **`Graph`** -- A complete graph structure.
- **`NetworkTopology`** -- Description of the network's topological properties.
- **`RhizomeEngine`** -- Engine for building and analyzing rhizomatic networks.

#### Exported Functions

- **`build_graph(nodes, edges)`** -- Construct a graph from nodes and edges.
- **`calculate_centrality(graph)`** -- Calculate centrality metrics for all nodes.

---

## Phase 5: Truth & Control

### Submodule: `epistemic`

Epistemic territory mapping, truth verification, and knowledge warfare modeling.

#### Exported Classes

- **`Fact`** -- A verifiable factual claim.
- **`Belief`** -- A held belief with confidence level.
- **`Evidence`** -- A piece of evidence supporting or refuting a claim.
- **`EpistemicState`** -- The epistemic state of an agent (what it knows, believes, and can verify).
- **`EpistemicEngine`** -- Engine for truth verification and epistemic analysis.

#### Exported Functions

- **`verify_claim(claim, evidence)`** -- Verify a claim against available evidence.
- **`calculate_certainty(belief, evidence)`** -- Calculate the certainty level of a belief given evidence.

### Submodule: `cybernetic`

Second-order cybernetics, control systems, and feedback loop engineering.

#### Exported Classes

- **`FeedbackLoop`** -- A feedback loop (positive or negative) in a control system.
- **`ControlSystem`** -- A complete cybernetic control system with inputs, outputs, and loops.
- **`SystemState`** -- The current state of a cybernetic system.
- **`Homeostat`** -- A homeostatic regulator maintaining equilibrium.
- **`CyberneticEngine`** -- Engine for simulating and analyzing cybernetic systems.
- **`PIDController`** -- Proportional-Integral-Derivative controller implementation.

#### Exported Functions

- **`apply_control(system, input_signal)`** -- Apply a control signal to a cybernetic system.

---

## Top-Level Exports Summary

All classes listed below are importable directly from `codomyrmex.meme`:

| Submodule | Exports |
|-----------|---------|
| `memetics` | `Meme`, `Memeplex`, `MemeticCode`, `FitnessMap`, `MemeticEngine` |
| `semiotic` | `Sign`, `SignType`, `DriftReport`, `SemioticAnalyzer` |
| `contagion` | `ContagionModel`, `CascadeDetector`, `PropagationTrace`, `Cascade`, `CascadeType`, `ResonanceMap` |
| `narrative` | `Narrative`, `NarrativeArc`, `Archetype`, `NarrativeEngine` |
| `cultural_dynamics` | `CulturalState`, `CulturalDynamicsEngine`, `PowerMap` |
| `swarm` | `SwarmAgent`, `SwarmEngine`, `EmergentPattern`, `ConsensusState`, `SwarmState` |
| `neurolinguistic` | `CognitiveFrame`, `BiasInstance`, `NeurolinguisticEngine` |
| `hyperreality` | `Simulacrum`, `HyperrealityEngine`, `SimulationLevel`, `RealityTunnel` |
| `ideoscape` | `IdeoscapeLayer`, `IdeoscapeEngine`, `MapFeature`, `TerrainMap` |
| `rhizome` | `RhizomeEngine`, `Graph`, `Node`, `Edge`, `NetworkTopology` |
| `epistemic` | `EpistemicEngine`, `EpistemicState`, `Fact`, `Belief`, `Evidence` |
| `cybernetic` | `CyberneticEngine`, `ControlSystem`, `FeedbackLoop`, `SystemState` |

## Authentication & Authorization

Not applicable for this internal analysis module.

## Rate Limiting

Not applicable for this internal analysis module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. Module version: `0.1.0`. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
