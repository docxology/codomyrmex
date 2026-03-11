"""Tests for the bio_simulation module.

Tests cover:
- Module import
- AntState enum values
- Ant creation and default state
- Ant energy depletion on move
- Ant movement during foraging
- Colony construction with population
- Colony step advances tick
- Colony stats returns expected keys
- Colony ignores dead ants
- ant_colony subpackage: Ant movement, pheromone trails, food pickup/drop
- Environment grid, food sources, obstacles, pheromone decay, neighbors
- Genome mutation, crossover, fitness calculation
- Population evolution, selection, elitism
"""

import pytest

from codomyrmex.bio_simulation import (
    Ant,
    AntState,
    Colony,
    Environment,
    Genome,
    Population,
)

# ======================================================================
# Basic tests (Colony, Ant, Environment)
# ======================================================================


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
    assert AntState.RESTING.name == "RESTING"
    assert AntState.IDLE.name == "IDLE"


@pytest.mark.unit
def test_ant_creation_defaults():
    """Ant is created with IDLE state and full energy."""
    ant = Ant(id=0)
    assert ant.id == 0
    assert ant.state == AntState.IDLE
    assert ant.energy == 1.0
    assert ant.position == (0.0, 0.0)


@pytest.mark.unit
def test_ant_move_depletes_energy():
    """Ant.move reduces energy."""
    ant = Ant(id=1, energy=1.0)
    ant.move((1.0, 0.0))
    assert ant.energy < 1.0


@pytest.mark.unit
def test_colony_construction():
    """Colony creates correct number of ants."""
    colony = Colony(population=10)
    assert len(colony.ants) == 10
    assert colony.tick == 0
    for ant in colony.ants:
        assert isinstance(ant, Ant)


@pytest.mark.unit
def test_colony_construction_negative_population():
    """Colony cannot be created with negative population."""
    with pytest.raises(ValueError, match="Population must be non-negative"):
        Colony(population=-1)


@pytest.mark.unit
def test_colony_step_advances_tick():
    """Colony.step increments the tick counter."""
    colony = Colony(population=5)
    # 1 hour = 60 ticks
    colony.step(hours=1)
    assert colony.tick == 60


@pytest.mark.unit
def test_colony_step_negative_hours():
    """Colony.step cannot run for negative hours."""
    colony = Colony(population=5)
    with pytest.raises(ValueError, match="Hours must be non-negative"):
        colony.step(hours=-1)


@pytest.mark.unit
def test_colony_stats():
    """Colony.stats returns expected keys."""
    colony = Colony(population=3)
    stats = colony.stats()
    assert "tick" in stats
    assert "alive" in stats
    assert "dead" in stats
    assert "food_collected" in stats
    assert "state_distribution" in stats


@pytest.mark.unit
def test_colony_resting_recovery():
    """Ants in RESTING state recover energy."""
    # Create colony with no random genome traits to avoid interference
    colony = Colony(population=1)
    ant = colony.ants[0]
    ant.genome.traits = {"endurance": 0.5}  # recovery = 0.01 * (0.5 + 0.5) = 0.01
    ant.state = AntState.RESTING
    ant.energy = 0.5
    # 1 tick = 1/60 hour
    # recovery = 0.01 per tick. After 10 ticks energy should be 0.6
    for _ in range(10):
        colony._step_tick()
    assert ant.energy == pytest.approx(0.6)
    assert ant.state == AntState.RESTING


@pytest.mark.unit
def test_colony_resting_to_foraging():
    """Ants in RESTING state switch to FORAGING when energy is high."""
    colony = Colony(population=1)
    ant = colony.ants[0]
    ant.genome.traits = {"endurance": 0.5}
    ant.state = AntState.RESTING
    ant.energy = 0.895
    colony._step_tick()
    assert ant.energy >= 0.9
    assert ant.state == AntState.FORAGING


@pytest.mark.unit
def test_colony_idle_to_foraging():
    """Ants in IDLE state sometimes switch to FORAGING."""
    colony = Colony(population=100)
    for ant in colony.ants:
        ant.state = AntState.IDLE

    # Run a few ticks, some should switch
    for _ in range(10):
        colony._step_tick()

    states = [ant.state for ant in colony.ants]
    assert AntState.FORAGING in states


# ======================================================================
# Detailed Ant tests
# ======================================================================


@pytest.mark.unit
def test_ant_move_updates_position():
    """Moving an ant changes its position based on direction."""
    ant = Ant(id=10, position=(5.0, 5.0))
    ant.move((1.0, 0.0))
    assert ant.position[0] > 5.0
    assert ant.position[1] == pytest.approx(5.0)


@pytest.mark.unit
def test_ant_deposit_pheromone_with_trail():
    """Deposit pheromone returns decaying deposits along trail."""
    ant = Ant(id=11)
    ant.move((1.0, 0.0))
    ant.move((1.0, 0.0))
    deposits = ant.deposit_pheromone(strength=1.0)
    assert len(deposits) == 2
    # Most recent deposit should have highest strength
    assert deposits[0][1] >= deposits[1][1]


@pytest.mark.unit
def test_ant_pick_up_food():
    """Ant picks up food and switches to RETURNING."""
    ant = Ant(id=12, genome=Genome(traits={"strength": 0.5}))
    # Default max_carry is 10.0. strength=0.5 -> max_carry=10.0
    picked = ant.pick_up_food(5.0)
    assert picked == pytest.approx(5.0)
    assert ant.carrying is True
    assert ant.state == AntState.RETURNING


@pytest.mark.unit
def test_ant_pick_up_food_already_carrying():
    """Ant cannot pick up food if already carrying some."""
    ant = Ant(id=12, carrying=True)
    picked = ant.pick_up_food(5.0)
    assert picked == 0.0


@pytest.mark.unit
def test_ant_drop_food():
    """Dropping food returns carried amount and switches to RESTING."""
    ant = Ant(id=13)
    ant.pick_up_food(8.0)
    dropped = ant.drop_food()
    assert dropped == pytest.approx(8.0)
    assert ant.carrying is False
    assert ant.state == AntState.RESTING


@pytest.mark.unit
def test_ant_drop_food_dead():
    """Dead ant cannot drop food."""
    ant = Ant(id=14, energy=0.0, carrying=True)
    dropped = ant.drop_food()
    assert dropped == 0.0


@pytest.mark.unit
def test_ant_move_dead():
    """Dead ant cannot move."""
    ant = Ant(id=15, energy=0.0, position=(0.0, 0.0))
    ant.move((1.0, 1.0))
    assert ant.position == (0.0, 0.0)


@pytest.mark.unit
def test_ant_move_zero_magnitude():
    """Moving in zero direction does nothing."""
    ant = Ant(id=16, position=(0.0, 0.0))
    ant.move((0.0, 0.0))
    assert ant.position == (0.0, 0.0)


@pytest.mark.unit
def test_ant_valid_transitions():
    """Verify valid state transitions."""
    ant = Ant(id=17, state=AntState.FORAGING)
    assert AntState.RETURNING in ant.valid_transitions


# ======================================================================
# Environment tests
# ======================================================================


@pytest.mark.unit
def test_environment_construction():
    """Environment is created with correct dimensions and default nest."""
    env = Environment(20, 15)
    assert env.width == 20
    assert env.height == 15
    assert env.nest_position == (10, 7)


@pytest.mark.unit
def test_environment_add_food_source():
    """Adding food sources registers them properly."""
    env = Environment(10, 10)
    env.add_food_source((3, 3), 50.0)
    assert len(env.food_sources) == 1
    assert env.food_sources[0].amount == pytest.approx(50.0)


@pytest.mark.unit
def test_environment_add_food_source_merge():
    """Adding food to existing location merges sources."""
    env = Environment(10, 10)
    env.add_food_source((3, 3), 50.0)
    env.add_food_source((3, 3), 50.0)
    assert len(env.food_sources) == 1
    assert env.food_sources[0].amount == pytest.approx(100.0)


@pytest.mark.unit
def test_environment_remove_food():
    """Removing food reduces the source amount."""
    env = Environment(10, 10)
    env.add_food_source((5, 5), 100.0)
    taken = env.remove_food((5, 5), 40.0)
    assert taken == pytest.approx(40.0)
    assert env.food_sources[0].amount == pytest.approx(60.0)


@pytest.mark.unit
def test_environment_remove_food_missing():
    """Removing food from non-existent source returns 0."""
    env = Environment(10, 10)
    taken = env.remove_food((5, 5), 40.0)
    assert taken == 0.0


@pytest.mark.unit
def test_environment_remove_food_depletes_source():
    """Removing all food from a source removes the source entirely."""
    env = Environment(10, 10)
    env.add_food_source((5, 5), 20.0)
    taken = env.remove_food((5, 5), 25.0)
    assert taken == pytest.approx(20.0)
    assert len(env.food_sources) == 0


@pytest.mark.unit
def test_environment_obstacle_blocks_passability():
    """Adding an obstacle makes a cell impassable."""
    env = Environment(10, 10)
    env.add_obstacle((5, 5))
    assert env.is_passable((5, 5)) is False
    assert env.is_passable((5, 4)) is True


@pytest.mark.unit
def test_environment_is_passable_out_of_bounds():
    """Cells out of bounds are not passable."""
    env = Environment(10, 10)
    assert env.is_passable((-1, 0)) is False
    assert env.is_passable((10, 10)) is False


@pytest.mark.unit
def test_environment_pheromone_decay():
    """Pheromone decay reduces intensity."""
    env = Environment(10, 10, pheromone_decay=0.1)
    env.set_pheromone((3, 3), 1.0)
    env.decay_pheromones()
    pmap = env.get_pheromone_map()
    assert pmap[(3, 3)] == pytest.approx(0.9)


@pytest.mark.unit
def test_environment_pheromone_decay_custom_rate():
    """Pheromone decay with custom rate."""
    env = Environment(10, 10)
    env.set_pheromone((3, 3), 1.0)
    env.decay_pheromones(rate=0.5)
    pmap = env.get_pheromone_map()
    assert pmap[(3, 3)] == pytest.approx(0.5)


@pytest.mark.unit
def test_environment_get_neighbors_center():
    """Neighbors of a center cell include all 8 adjacent cells."""
    env = Environment(10, 10)
    neighbors = env.get_neighbors((5, 5))
    assert len(neighbors) == 8


@pytest.mark.unit
def test_environment_get_neighbors_excludes_obstacles():
    """Neighbors list excludes obstacle cells."""
    env = Environment(10, 10)
    env.add_obstacle((6, 5))
    neighbors = env.get_neighbors((5, 5))
    assert (6, 5) not in neighbors
    assert len(neighbors) == 7


@pytest.mark.unit
def test_environment_food_at_empty():
    """food_at returns None if no food sources."""
    env = Environment(10, 10)
    assert env.food_at((5, 5)) is None


@pytest.mark.unit
def test_environment_obstacles_property():
    """Verify obstacles property."""
    env = Environment(10, 10)
    env.add_obstacle((1, 1))
    assert (1, 1) in env.obstacles


# ======================================================================
# Genome tests
# ======================================================================


@pytest.mark.unit
def test_genome_random():
    """Genome.random creates a genome with traits."""
    g = Genome.random()
    assert "speed" in g.traits
    assert "strength" in g.traits
    for val in g.traits.values():
        assert 0.0 <= val <= 1.0


@pytest.mark.unit
def test_genome_fitness():
    """Fitness score is the mean of trait values."""
    g = Genome(traits={"a": 0.2, "b": 0.4})
    assert g.fitness_score() == pytest.approx(0.3)


@pytest.mark.unit
def test_genome_fitness_empty():
    """Fitness of empty genome is 0.0."""
    g = Genome(traits={})
    assert g.fitness_score() == 0.0


@pytest.mark.unit
def test_genome_mutate():
    """Mutation produces a new genome."""
    g = Genome.random()
    mutated = g.mutate(rate=1.0)
    assert isinstance(mutated, Genome)


@pytest.mark.unit
def test_genome_crossover_empty():
    """Crossover of empty genomes returns empty offspring."""
    g1 = Genome(traits={})
    g2 = Genome(traits={})
    c1, c2 = g1.crossover(g2)
    assert not c1.traits
    assert not c2.traits


@pytest.mark.unit
def test_genome_repr():
    """Genome repr contains fitness and traits."""
    g = Genome(traits={"speed": 0.5})
    r = repr(g)
    assert "Genome" in r
    assert "fitness=0.5000" in r
    assert "speed=0.500" in r


# ======================================================================
# Population tests
# ======================================================================


@pytest.mark.unit
def test_population_creation():
    """Population is initialized with size."""
    pop = Population(genomes=[Genome.random() for _ in range(20)])
    assert pop.size == 20
    assert pop.generation == 0
    assert len(pop.individuals) == 20


@pytest.mark.unit
def test_population_evolve():
    """Evolving increments the generation counter."""
    pop = Population()
    pop.evolve(generations=5)
    assert pop.generation == 5


@pytest.mark.unit
def test_population_average_fitness_empty():
    """Average fitness of empty population is 0.0."""
    pop = Population(genomes=[])
    assert pop.average_fitness() == 0.0


@pytest.mark.unit
def test_population_trait_distribution():
    """trait_distribution returns stats for each trait."""
    pop = Population()
    dist = pop.trait_distribution()
    assert "speed" in dist
    assert "mean" in dist["speed"]


# ======================================================================
# Death Tracking Fix Tests
# ======================================================================


@pytest.mark.unit
def test_colony_death_tracking():
    """Test that deaths are tracked correctly (only once per ant)."""
    colony = Colony(population=10)
    # Kill an ant
    colony.ants[0].energy = 0
    # Run a step (60 ticks)
    colony.step(hours=1)

    stats = colony.stats()
    assert stats["dead"] == 1
    assert stats["alive"] == 9
    assert len(colony.ants) == 9

    # Run another step
    colony.step(hours=1)
    stats = colony.stats()
    # Should still be 1 if no more died
    assert stats["dead"] >= 1
