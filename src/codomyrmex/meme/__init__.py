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
from codomyrmex.meme.memetics import (
    Meme,
    Memeplex,
    MemeticCode,
    FitnessMap,
    MemeticEngine,
)
from codomyrmex.meme.semiotic import (
    Sign,
    SignType,
    DriftReport,
    SemioticAnalyzer,
)

# Phase 2 — Propagation
from codomyrmex.meme.contagion import (
    ContagionModel,
    CascadeDetector,
    PropagationTrace,
    Cascade,
    CascadeType,
    ResonanceMap,
)
from codomyrmex.meme.narrative import (
    Narrative,
    NarrativeArc,
    Archetype,
    NarrativeEngine,
)

# Phase 3 — Dynamics
from codomyrmex.meme.cultural_dynamics import (
    CulturalState,
    CulturalDynamicsEngine,
    PowerMap,
)
from codomyrmex.meme.swarm import (
    SwarmAgent,
    SwarmEngine,
    EmergentPattern,
    ConsensusState,
    SwarmState,
)
from codomyrmex.meme.neurolinguistic import (
    CognitiveFrame,
    BiasInstance,
    NeurolinguisticEngine,
)

# Phase 4 — Higher-Order
from codomyrmex.meme.hyperreality import (
    Simulacrum,
    HyperrealityEngine,
    SimulationLevel,
    RealityTunnel,
)
from codomyrmex.meme.ideoscape import (
    IdeoscapeLayer,
    IdeoscapeEngine,
    MapFeature,
    TerrainMap,
)
from codomyrmex.meme.rhizome import (
    RhizomeEngine,
    Graph,
    Node,
    Edge,
    NetworkTopology,
)
from codomyrmex.meme.epistemic import (
    EpistemicEngine,
    EpistemicState,
    Fact,
    Belief,
    Evidence,
)

# Phase 5 — Control
from codomyrmex.meme.cybernetic import (
    CyberneticEngine,
    ControlSystem,
    FeedbackLoop,
    SystemState,
)

__all__ = [
    # memetics
    "Meme", "Memeplex", "MemeticCode", "FitnessMap", "MemeticEngine",
    # semiotic
    "Sign", "SignType", "DriftReport", "SemioticAnalyzer",
    # contagion
    "ContagionModel", "CascadeDetector", "PropagationTrace",
    "Cascade", "CascadeType", "ResonanceMap",
    # narrative
    "Narrative", "NarrativeArc", "Archetype", "NarrativeEngine",
    # cultural_dynamics
    "CulturalState", "CulturalDynamicsEngine", "PowerMap",
    # swarm
    "SwarmAgent", "SwarmEngine", "EmergentPattern", "ConsensusState", "SwarmState",
    # neurolinguistic
    "CognitiveFrame", "BiasInstance", "NeurolinguisticEngine",
    # hyperreality
    "Simulacrum", "HyperrealityEngine", "SimulationLevel", "RealityTunnel",
    # ideoscape
    "IdeoscapeLayer", "IdeoscapeEngine", "MapFeature", "TerrainMap",
    # rhizome
    "RhizomeEngine", "Graph", "Node", "Edge", "NetworkTopology",
    # epistemic
    "EpistemicEngine", "EpistemicState", "Fact", "Belief", "Evidence",
    # cybernetic
    "CyberneticEngine", "ControlSystem", "FeedbackLoop", "SystemState",
]
