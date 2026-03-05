"""
codomyrmex.meme — Unified Memetic Warfare & Information Dynamics Module.

A comprehensive framework for modeling, analyzing, and engineering the
propagation, mutation, and evolution of information units (memes) through
cultural, cognitive, and network substrates.

Submodules
----------
memetics        Core memetic engine — Meme, Memeplex, fitness, mutation.
semiotic        Computational semiotics — signs, encoding, drift.
contagion       Information cascade & epidemic propagation models.
narrative       Computational narratology — arcs, myths, insurgency.
cultural_dynamics  Cultural oscillation, zeitgeist, power dynamics.
hyperreality    Baudrillardian simulacra & consensus engineering.
swarm           Swarm intelligence — ACO, PSO, stigmergy, emergence.
neurolinguistic Cognitive framing, bias exploitation, metacognition.
ideoscape       Ideational ecosystem ecology — Lotka-Volterra for ideas.
rhizome         Rhizomatic network analysis — plateaus, lines of flight.
epistemic       Epistemic territory mapping & knowledge warfare.
cybernetic      Cybernetic control theory & feedback engineering.
"""

__version__ = "0.1.0"

# Phase 1 — Core Engine
# Phase 2 — Propagation
from codomyrmex.meme.contagion import (
    Cascade,
    CascadeDetector,
    CascadeType,
    ContagionModel,
    PropagationTrace,
    ResonanceMap,
)

# Phase 3 — Dynamics
from codomyrmex.meme.cultural_dynamics import (
    CulturalDynamicsEngine,
    CulturalState,
    PowerMap,
)

# Phase 5 — Control
from codomyrmex.meme.cybernetic import (
    ControlSystem,
    CyberneticEngine,
    FeedbackLoop,
    SystemState,
)
from codomyrmex.meme.epistemic import (
    Belief,
    EpistemicEngine,
    EpistemicState,
    Evidence,
    Fact,
)

# Phase 4 — Higher-Order
from codomyrmex.meme.hyperreality import (
    HyperrealityEngine,
    RealityTunnel,
    Simulacrum,
    SimulationLevel,
)
from codomyrmex.meme.ideoscape import (
    IdeoscapeEngine,
    IdeoscapeLayer,
    MapFeature,
    TerrainMap,
)
from codomyrmex.meme.memetics import (
    FitnessMap,
    Meme,
    Memeplex,
    MemeticCode,
    MemeticEngine,
)
from codomyrmex.meme.narrative import (
    Archetype,
    Narrative,
    NarrativeArc,
    NarrativeEngine,
)
from codomyrmex.meme.neurolinguistic import (
    BiasInstance,
    CognitiveFrame,
    NeurolinguisticEngine,
)
from codomyrmex.meme.rhizome import (
    Edge,
    Graph,
    NetworkTopology,
    Node,
    RhizomeEngine,
)
from codomyrmex.meme.semiotic import (
    DriftReport,
    SemioticAnalyzer,
    Sign,
    SignType,
)
from codomyrmex.meme.swarm import (
    ConsensusState,
    EmergentPattern,
    SwarmAgent,
    SwarmEngine,
    SwarmState,
)

__all__ = [
    "Archetype",
    "Belief",
    "BiasInstance",
    "Cascade",
    "CascadeDetector",
    "CascadeType",
    # neurolinguistic
    "CognitiveFrame",
    "ConsensusState",
    # contagion
    "ContagionModel",
    "ControlSystem",
    "CulturalDynamicsEngine",
    # cultural_dynamics
    "CulturalState",
    # cybernetic
    "CyberneticEngine",
    "DriftReport",
    "Edge",
    "EmergentPattern",
    # epistemic
    "EpistemicEngine",
    "EpistemicState",
    "Evidence",
    "Fact",
    "FeedbackLoop",
    "FitnessMap",
    "Graph",
    "HyperrealityEngine",
    "IdeoscapeEngine",
    # ideoscape
    "IdeoscapeLayer",
    "MapFeature",
    # memetics
    "Meme",
    "Memeplex",
    "MemeticCode",
    "MemeticEngine",
    # narrative
    "Narrative",
    "NarrativeArc",
    "NarrativeEngine",
    "NetworkTopology",
    "NeurolinguisticEngine",
    "Node",
    "PowerMap",
    "PropagationTrace",
    "RealityTunnel",
    "ResonanceMap",
    # rhizome
    "RhizomeEngine",
    "SemioticAnalyzer",
    # semiotic
    "Sign",
    "SignType",
    # hyperreality
    "Simulacrum",
    "SimulationLevel",
    # swarm
    "SwarmAgent",
    "SwarmEngine",
    "SwarmState",
    "SystemState",
    "TerrainMap",
]
