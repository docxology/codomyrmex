"""Unit tests for the metabolic and cellular bio-simulation systems."""

from codomyrmex.bio_simulation.cellular import CellularAutomaton
from codomyrmex.bio_simulation.reactor import BioReactor, Reaction


def test_cellular_automaton_glider():
    """Verify that a Conway glider translates across the torus over 4 steps natively."""
    ca = CellularAutomaton.glider(offset_x=2, offset_y=2, width=15, height=15)

    # Assert initial glider bounding box
    assert ca.get_cell(3, 2) == 1
    assert ca.get_cell(4, 3) == 1
    assert ca.get_cell(2, 4) == 1
    assert ca.get_cell(3, 4) == 1
    assert ca.get_cell(4, 4) == 1

    # Advance exactly 4 steps (1 full glider cycle representing diagonal translation)
    for _ in range(4):
        ca.step()

    # The glider should have moved exactly +1, +1 natively
    assert ca.get_cell(4, 3) == 1
    assert ca.get_cell(5, 4) == 1
    assert ca.get_cell(3, 5) == 1
    assert ca.get_cell(4, 5) == 1
    assert ca.get_cell(5, 5) == 1

    # Original top-left point shifted
    assert ca.get_cell(2, 4) == 0


def test_bio_reactor_metabolic_decay():
    """Verify that the bioreactor accurately computes degradation natively without mocks."""
    reactor = BioReactor()
    reactor.add_metabolite("ATP", initial_concentration=100.0, degradation_rate=0.1)

    # Run 10 seconds of simulation
    # Decay dt = 0.1 * 100 = 10% per second approximation under Euler
    res = reactor.run(steps=100, dt=0.1)

    # Formula: C(t) = C0 * exp(-k*t) roughly ~ 100 * exp(-0.1 * 10) = 100 * exp(-1) = 36.78
    # Using simple Euler, it's (1 - 0.1*0.1)^100 * 100 ~ 36.60
    final_conc = reactor.metabolites["ATP"].concentration
    assert 36.0 < final_conc < 37.0

    # Verify exact timestep history sizing
    assert len(res["ATP"]) == 101


def test_bio_reactor_synthetic_pathway():
    """Verify that A -> B deterministic conversion obeys max constraints."""
    reactor = BioReactor()
    reactor.add_metabolite("SubstrateA", 50.0)
    reactor.add_metabolite("ProductB", 0.0)

    # Add a reaction moving A to B at fixed velocity 10 units/sec
    def conversion_velocity(concs: dict[str, float]) -> float:
        return 10.0 if concs["SubstrateA"] > 0 else 0.0

    reactor.add_reaction(
        Reaction(
            substrates=["SubstrateA"],
            products=["ProductB"],
            velocity_fn=conversion_velocity,
        )
    )

    # Run 10 seconds steps = 100 dt = 0.1 (total consumed = 10.0 * 10 = 100)
    # But A only has 50, so process truncates exactly at 50 B created
    reactor.run(steps=100, dt=0.1)

    assert reactor.metabolites["SubstrateA"].concentration == 0.0
    assert reactor.metabolites["ProductB"].concentration == 50.0
