"""Tests for the bio_simulation module.

Tests cover:
- Module import
- AntState enum values
- Ant creation and default state
- Ant energy depletion on step
- Ant movement during foraging
- Colony construction with population_size
- Colony step advances tick
- Colony census counts by state
- Colony ignores dead ants (zero energy)
- Multiple simulation steps
"""

import pytest

from codomyrmex.bio_simulation.colony import Ant, AntState, Colony


@pytest.mark.unit
def test_module_import():
    """bio_simulation module is importable."""
    from codomyrmex import bio_simulation
    assert bio_simulation is not None


@pytest.mark.unit
def test_ant_state_enum_values():
    """AntState enum has expected members."""
    assert AntState.FORAGING.name == "FORAGING"
    assert AntState.RETURNING.name == "RETURNING"
    assert AntState.DEFENDING.name == "DEFENDING"
    assert AntState.IDLE.name == "IDLE"


@pytest.mark.unit
def test_ant_creation_defaults():
    """Ant is created with IDLE state and full energy."""
    ant = Ant(id=0)
    assert ant.id == 0
    assert ant.state == AntState.IDLE
    assert ant.energy == 100.0
    assert ant.x == 0
    assert ant.y == 0


@pytest.mark.unit
def test_ant_step_depletes_energy():
    """Ant.step reduces energy by 0.1."""
    ant = Ant(id=1)
    initial_energy = ant.energy
    ant.step()
    assert ant.energy == pytest.approx(initial_energy - 0.1)


@pytest.mark.unit
def test_ant_foraging_movement():
    """Foraging ant changes position on step."""
    ant = Ant(id=2, state=AntState.FORAGING)
    positions = set()
    # Run enough steps to observe movement (random, so collect multiple)
    for _ in range(50):
        ant_copy = Ant(id=2, state=AntState.FORAGING, x=0, y=0)
        ant_copy.step()
        positions.add((ant_copy.x, ant_copy.y))
    # With 50 tries, at least some should differ from (0,0)
    assert len(positions) > 1


@pytest.mark.unit
def test_idle_ant_does_not_move():
    """Idle ant stays at the same position."""
    ant = Ant(id=3, state=AntState.IDLE, x=5, y=5)
    ant.step()
    assert ant.x == 5
    assert ant.y == 5


@pytest.mark.unit
def test_colony_construction():
    """Colony creates correct number of ants."""
    colony = Colony(population_size=10)
    assert len(colony.ants) == 10
    assert colony.tick == 0
    for ant in colony.ants:
        assert isinstance(ant, Ant)


@pytest.mark.unit
def test_colony_step_advances_tick():
    """Colony.step increments the tick counter."""
    colony = Colony(population_size=5)
    colony.step()
    assert colony.tick == 1
    colony.step()
    assert colony.tick == 2


@pytest.mark.unit
def test_colony_census():
    """Colony.get_census returns counts by AntState."""
    colony = Colony(population_size=3)
    census = colony.get_census()
    # All ants start IDLE
    assert census[AntState.IDLE] == 3
    assert census[AntState.FORAGING] == 0
    assert census[AntState.RETURNING] == 0
    assert census[AntState.DEFENDING] == 0


@pytest.mark.unit
def test_colony_dead_ants_stop_acting():
    """Ants with zero energy do not step."""
    colony = Colony(population_size=2)
    colony.ants[0].energy = 0.0
    colony.ants[1].energy = 100.0
    colony.ants[1].state = AntState.FORAGING

    colony.step()
    # Dead ant energy unchanged (step not called on it)
    assert colony.ants[0].energy == 0.0
    # Live ant lost energy
    assert colony.ants[1].energy < 100.0


@pytest.mark.unit
def test_colony_multiple_steps():
    """Colony can run multiple simulation steps."""
    colony = Colony(population_size=5)
    for _ in range(100):
        colony.step()
    assert colony.tick == 100
    # All ants should have lost energy
    for ant in colony.ants:
        assert ant.energy < 100.0
