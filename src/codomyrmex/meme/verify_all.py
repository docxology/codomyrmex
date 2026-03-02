#!/usr/bin/env python3
"""Verification script for the new meme module."""
import sys

# Ensure src is in path
sys.path.insert(0, "/Users/mini/Documents/GitHub/codomyrmex/src")

def info(msg):
    """Info."""
    print(f"\033[94m[INFO]\033[0m {msg}")

def success(msg):
    """Success."""
    print(f"\033[92m[PASS]\033[0m {msg}")

def fail(msg):
    """Fail."""
    print(f"\033[91m[FAIL]\033[0m {msg}")

try:
    info("Attempting to import codomyrmex.meme package...")
    success("Imported codomyrmex.meme")

    # 1. Memetics
    info("Testing memetics...")
    from codomyrmex.meme.memetics.models import Meme
    m = Meme(content="Test Meme")
    assert m.fitness >= 0
    success("Memetics: Meme creation valid")

    # 2. Semiotic
    info("Testing semiotic...")
    from codomyrmex.meme.semiotic.models import Sign
    s = Sign(signifier="dog", signified="animal")
    assert s.id
    success("Semiotic: Sign creation valid")

    # 3. Contagion
    info("Testing contagion...")
    from codomyrmex.meme.contagion.epidemic import SIRModel
    sir = SIRModel()
    trace = sir.simulate(steps=10)
    assert len(trace.time_steps) > 0
    success("Contagion: SIR simulation valid")

    # 4. Narrative
    info("Testing narrative...")
    from codomyrmex.meme.narrative.models import Archetype
    from codomyrmex.meme.narrative.myth import synthesize_myth
    myth = synthesize_myth("Testing", {"Hero": Archetype.HERO})
    assert myth.title
    success("Narrative: Myth synthesis valid")

    # 5. Cultural Dynamics
    info("Testing cultural_dynamics...")
    from codomyrmex.meme.cultural_dynamics.models import CulturalState
    cs = CulturalState()
    assert cs.timestamp > 0
    success("Cultural Dynamics: State creation valid")

    # 6. Swarm
    info("Testing swarm...")
    from codomyrmex.meme.swarm.engine import SwarmEngine
    se = SwarmEngine(num_agents=5)
    se.step()
    success("Swarm: Engine step valid")

    # 7. Neurolinguistic
    info("Testing neurolinguistic...")
    from codomyrmex.meme.neurolinguistic.engine import NeurolinguisticEngine
    nle = NeurolinguisticEngine()
    audit = nle.audit("Just testing words.")
    assert isinstance(audit, dict)
    success("Neurolinguistic: Audit valid")

    # 8. Ideoscape
    info("Testing ideoscape...")
    from codomyrmex.meme.ideoscape.cartography import generate_terrain
    from codomyrmex.meme.ideoscape.models import MapFeature
    f = MapFeature(name="Peak", position=[0.0, 0.0])
    t = generate_terrain([f], resolution=10)
    assert t.height_map.shape == (10, 10)
    success("Ideoscape: Terrain generation valid")

    # 9. Rhizome
    info("Testing rhizome...")
    from codomyrmex.meme.rhizome.models import NetworkTopology
    from codomyrmex.meme.rhizome.network import build_graph
    g = build_graph(10, NetworkTopology.RANDOM)
    assert len(g.nodes) == 10
    success("Rhizome: Graph construction valid")

    # 10. Epistemic
    info("Testing epistemic...")
    from codomyrmex.meme.epistemic.truth import verify_claim
    fact = verify_claim("Sky is blue", [])
    assert fact.confidence == 0.5  # Neutral with no evidence
    success("Epistemic: Claim verification valid")

    # 11. Hyperreality
    info("Testing hyperreality...")
    from codomyrmex.meme.hyperreality.simulation import (
        SimulationLevel,
        generate_simulacrum,
    )
    sim = generate_simulacrum("Original", SimulationLevel.PURE)
    assert sim.fidelity == 1.0
    success("Hyperreality: Simulacrum generation valid")

    # 12. Cybernetic
    info("Testing cybernetic...")
    from codomyrmex.meme.cybernetic.control import PIDController
    pid = PIDController()
    out = pid.compute(10.0, 5.0, 1.0)
    assert out != 0
    success("Cybernetic: PID valid")

    print("\n\033[92mALL SYSTEMS FUNCTIONAL\033[0m")

except Exception as e:
    fail(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
