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
- ant_colony subpackage: Ant movement, pheromone trails, food pickup/drop
- Environment grid, food sources, obstacles, pheromone decay, neighbors
- Genome mutation, crossover, fitness calculation
- Population evolution, selection, elitism
"""

import pytest

from codomyrmex.bio_simulation.ant_colony.ant import (
    Ant as DetailedAnt,
)
from codomyrmex.bio_simulation.ant_colony.ant import (
    AntState as DetailedAntState,
)
from codomyrmex.bio_simulation.ant_colony.colony import Colony as DetailedColony
from codomyrmex.bio_simulation.ant_colony.environment import Environment
from codomyrmex.bio_simulation.colony import Ant, AntState, Colony
from codomyrmex.bio_simulation.genomics.genome import Genome, Population

# ======================================================================
# Original tests (colony.py simple Ant/Colony)
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
    Ant(id=2, state=AntState.FORAGING)
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


# ======================================================================
# ant_colony subpackage: Detailed Ant tests
# ======================================================================

@pytest.mark.unit
def test_detailed_ant_creation_defaults():
    """DetailedAnt is created with default position, IDLE state, full energy."""
    ant = DetailedAnt()
    assert ant.position == (0.0, 0.0)
    assert ant.state == DetailedAntState.IDLE
    assert ant.energy == 100.0
    assert ant.carrying == 0.0
    assert ant.pheromone_trail == []


@pytest.mark.unit
def test_detailed_ant_move_updates_position():
    """Moving an ant changes its position based on direction."""
    ant = DetailedAnt(position=(5.0, 5.0))
    ant.move((1.0, 0.0))
    assert ant.position[0] == pytest.approx(6.0)
    assert ant.position[1] == pytest.approx(5.0)


@pytest.mark.unit
def test_detailed_ant_move_normalizes_direction():
    """Moving with a non-unit direction normalizes to speed length."""
    ant = DetailedAnt(position=(0.0, 0.0), _speed=1.0)
    ant.move((3.0, 4.0))  # magnitude=5, normalized to (0.6, 0.8)
    assert ant.position[0] == pytest.approx(0.6)
    assert ant.position[1] == pytest.approx(0.8)


@pytest.mark.unit
def test_detailed_ant_move_zero_direction_no_change():
    """Moving with zero direction does not change position or energy."""
    ant = DetailedAnt(position=(3.0, 4.0), energy=50.0)
    ant.move((0.0, 0.0))
    assert ant.position == (3.0, 4.0)
    assert ant.energy == 50.0


@pytest.mark.unit
def test_detailed_ant_move_depletes_energy():
    """Moving costs energy proportional to speed."""
    ant = DetailedAnt(energy=100.0, _speed=2.0)
    ant.move((1.0, 0.0))
    # energy -= speed * 0.5 = 2.0 * 0.5 = 1.0
    assert ant.energy == pytest.approx(99.0)


@pytest.mark.unit
def test_detailed_ant_move_records_trail():
    """Moving appends position to pheromone trail."""
    ant = DetailedAnt()
    ant.move((1.0, 0.0))
    ant.move((0.0, 1.0))
    assert len(ant.pheromone_trail) == 2


@pytest.mark.unit
def test_detailed_ant_deposit_pheromone_empty_trail():
    """Deposit pheromone returns empty list when trail is empty."""
    ant = DetailedAnt()
    deposits = ant.deposit_pheromone(strength=1.0)
    assert deposits == []


@pytest.mark.unit
def test_detailed_ant_deposit_pheromone_with_trail():
    """Deposit pheromone returns decaying deposits along trail."""
    ant = DetailedAnt()
    ant.move((1.0, 0.0))
    ant.move((1.0, 0.0))
    deposits = ant.deposit_pheromone(strength=1.0)
    assert len(deposits) == 2
    # Most recent deposit should have highest strength
    assert deposits[0][1] >= deposits[1][1]


@pytest.mark.unit
def test_detailed_ant_pick_up_food_within_capacity():
    """Ant picks up food up to available amount when under capacity."""
    ant = DetailedAnt()
    picked = ant.pick_up_food(5.0)
    assert picked == pytest.approx(5.0)
    assert ant.carrying == pytest.approx(5.0)
    assert ant.state == DetailedAntState.RETURNING


@pytest.mark.unit
def test_detailed_ant_pick_up_food_exceeds_capacity():
    """Ant carries at most 10 units; excess is left behind."""
    ant = DetailedAnt()
    picked = ant.pick_up_food(15.0)
    assert picked == pytest.approx(10.0)
    assert ant.carrying == pytest.approx(10.0)


@pytest.mark.unit
def test_detailed_ant_pick_up_food_partial_carry():
    """Ant already carrying some food picks up only remaining capacity."""
    ant = DetailedAnt(carrying=7.0)
    picked = ant.pick_up_food(5.0)
    assert picked == pytest.approx(3.0)
    assert ant.carrying == pytest.approx(10.0)


@pytest.mark.unit
def test_detailed_ant_drop_food_returns_carried_amount():
    """Dropping food returns all carried food and switches to FORAGING."""
    ant = DetailedAnt(carrying=8.0, state=DetailedAntState.RETURNING)
    dropped = ant.drop_food()
    assert dropped == pytest.approx(8.0)
    assert ant.carrying == 0.0
    assert ant.state == DetailedAntState.FORAGING


@pytest.mark.unit
def test_detailed_ant_is_alive_positive_energy():
    """Ant with positive energy is alive."""
    ant = DetailedAnt(energy=0.1)
    assert ant.is_alive() is True


@pytest.mark.unit
def test_detailed_ant_is_alive_zero_energy():
    """Ant with zero energy is dead."""
    ant = DetailedAnt(energy=0.0)
    assert ant.is_alive() is False


@pytest.mark.unit
def test_detailed_ant_distance_to():
    """Distance calculation uses Euclidean metric."""
    ant = DetailedAnt(position=(0.0, 0.0))
    assert ant.distance_to((3.0, 4.0)) == pytest.approx(5.0)


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
def test_environment_custom_nest_position():
    """Environment respects custom nest position."""
    env = Environment(10, 10, nest_position=(2, 3))
    assert env.nest_position == (2, 3)


@pytest.mark.unit
def test_environment_add_food_source():
    """Adding food sources registers them properly."""
    env = Environment(10, 10)
    env.add_food_source((3, 3), 50.0)
    assert len(env.food_sources) == 1
    assert env.food_sources[0].amount == pytest.approx(50.0)


@pytest.mark.unit
def test_environment_add_food_source_merges_same_position():
    """Adding food at same position merges amounts."""
    env = Environment(10, 10)
    env.add_food_source((3, 3), 50.0)
    env.add_food_source((3, 3), 30.0)
    assert len(env.food_sources) == 1
    assert env.food_sources[0].amount == pytest.approx(80.0)


@pytest.mark.unit
def test_environment_remove_food():
    """Removing food reduces the source amount."""
    env = Environment(10, 10)
    env.add_food_source((5, 5), 100.0)
    taken = env.remove_food((5, 5), 40.0)
    assert taken == pytest.approx(40.0)
    assert env.food_sources[0].amount == pytest.approx(60.0)


@pytest.mark.unit
def test_environment_remove_food_depletes_source():
    """Removing all food from a source removes the source entirely."""
    env = Environment(10, 10)
    env.add_food_source((5, 5), 20.0)
    taken = env.remove_food((5, 5), 25.0)
    assert taken == pytest.approx(20.0)
    assert len(env.food_sources) == 0


@pytest.mark.unit
def test_environment_remove_food_nonexistent():
    """Removing food from nonexistent position returns 0."""
    env = Environment(10, 10)
    taken = env.remove_food((1, 1), 10.0)
    assert taken == 0.0


@pytest.mark.unit
def test_environment_obstacle_blocks_passability():
    """Adding an obstacle makes a cell impassable."""
    env = Environment(10, 10)
    env.add_obstacle((5, 5))
    assert env.is_passable((5, 5)) is False
    assert env.is_passable((5, 4)) is True


@pytest.mark.unit
def test_environment_out_of_bounds_not_passable():
    """Out-of-bounds positions are not passable."""
    env = Environment(10, 10)
    assert env.is_passable((-1, 0)) is False
    assert env.is_passable((0, -1)) is False
    assert env.is_passable((10, 0)) is False
    assert env.is_passable((0, 10)) is False


@pytest.mark.unit
def test_environment_pheromone_set_and_get():
    """Setting pheromones accumulates at a cell."""
    env = Environment(10, 10)
    env.set_pheromone((3, 3), 1.0)
    env.set_pheromone((3, 3), 0.5)
    pmap = env.get_pheromone_map()
    assert pmap[(3, 3)] == pytest.approx(1.5)


@pytest.mark.unit
def test_environment_decay_pheromones():
    """Pheromone decay reduces intensity; below threshold removes entry."""
    env = Environment(10, 10)
    env.set_pheromone((1, 1), 1.0)
    env.set_pheromone((2, 2), 0.005)
    env.decay_pheromones(rate=0.95)
    pmap = env.get_pheromone_map()
    assert (1, 1) in pmap
    assert pmap[(1, 1)] == pytest.approx(0.95)
    # 0.005 * 0.95 = 0.00475 < 0.01 threshold, should be removed
    assert (2, 2) not in pmap


@pytest.mark.unit
def test_environment_get_neighbors_center():
    """Neighbors of a center cell include all 8 adjacent cells."""
    env = Environment(10, 10)
    neighbors = env.get_neighbors((5, 5))
    assert len(neighbors) == 8


@pytest.mark.unit
def test_environment_get_neighbors_corner():
    """Neighbors of corner cell (0,0) are limited by boundaries."""
    env = Environment(10, 10)
    neighbors = env.get_neighbors((0, 0))
    # Only (1,0), (0,1), (1,1) are valid
    assert len(neighbors) == 3


@pytest.mark.unit
def test_environment_get_neighbors_excludes_obstacles():
    """Neighbors list excludes obstacle cells."""
    env = Environment(10, 10)
    env.add_obstacle((6, 5))
    neighbors = env.get_neighbors((5, 5))
    assert (6, 5) not in neighbors
    assert len(neighbors) == 7


@pytest.mark.unit
def test_environment_food_at_within_radius():
    """food_at finds a food source within the radius."""
    env = Environment(20, 20)
    env.add_food_source((10, 10), 50.0)
    result = env.food_at((10, 11), radius=1.5)
    assert result is not None
    assert result.amount == pytest.approx(50.0)


@pytest.mark.unit
def test_environment_food_at_outside_radius():
    """food_at returns None when food is beyond the radius."""
    env = Environment(20, 20)
    env.add_food_source((10, 10), 50.0)
    result = env.food_at((10, 15), radius=1.5)
    assert result is None


# ======================================================================
# Genome tests
# ======================================================================

@pytest.mark.unit
def test_genome_creation_and_length():
    """Genome stores genes and computes length."""
    g = Genome(genes=[0.1, 0.5, 0.9])
    assert g.length == 3
    assert g.genes == [0.1, 0.5, 0.9]


@pytest.mark.unit
def test_genome_random_creation():
    """Genome.random creates a genome with correct length and valid values."""
    g = Genome.random(10)
    assert g.length == 10
    for gene in g.genes:
        assert 0.0 <= gene <= 1.0


@pytest.mark.unit
def test_genome_fitness_score():
    """Fitness score is the mean of gene values."""
    g = Genome(genes=[0.2, 0.4, 0.6])
    assert g.fitness_score() == pytest.approx(0.4)


@pytest.mark.unit
def test_genome_fitness_score_empty():
    """Empty genome has fitness 0."""
    g = Genome(genes=[])
    assert g.fitness_score() == 0.0


@pytest.mark.unit
def test_genome_mutate_preserves_length():
    """Mutation produces a new genome of the same length."""
    g = Genome(genes=[0.5] * 20)
    mutated = g.mutate(rate=0.5)
    assert mutated.length == g.length


@pytest.mark.unit
def test_genome_mutate_values_stay_clamped():
    """Mutated gene values remain in [0, 1]."""
    g = Genome(genes=[0.0, 1.0, 0.5, 0.0, 1.0])
    for _ in range(50):
        mutated = g.mutate(rate=1.0)
        for gene in mutated.genes:
            assert 0.0 <= gene <= 1.0


@pytest.mark.unit
def test_genome_mutate_zero_rate_no_change():
    """Mutation rate of 0 produces an identical copy."""
    g = Genome(genes=[0.1, 0.2, 0.3])
    mutated = g.mutate(rate=0.0)
    assert mutated.genes == g.genes


@pytest.mark.unit
def test_genome_crossover_produces_two_children():
    """Crossover produces exactly two offspring."""
    p1 = Genome(genes=[0.0, 0.0, 0.0, 0.0])
    p2 = Genome(genes=[1.0, 1.0, 1.0, 1.0])
    c1, c2 = p1.crossover(p2)
    assert c1.length == 4
    assert c2.length == 4


@pytest.mark.unit
def test_genome_crossover_mismatched_length_raises():
    """Crossover between genomes of different lengths raises ValueError."""
    p1 = Genome(genes=[0.0, 0.0])
    p2 = Genome(genes=[1.0, 1.0, 1.0])
    with pytest.raises(ValueError, match="different lengths"):
        p1.crossover(p2)


@pytest.mark.unit
def test_genome_crossover_genes_come_from_parents():
    """Offspring genes are subsets of parent genes (no new values)."""
    p1 = Genome(genes=[0.1, 0.2, 0.3, 0.4])
    p2 = Genome(genes=[0.5, 0.6, 0.7, 0.8])
    c1, c2 = p1.crossover(p2)
    for gene in c1.genes:
        assert gene in p1.genes or gene in p2.genes
    for gene in c2.genes:
        assert gene in p1.genes or gene in p2.genes


@pytest.mark.unit
def test_genome_repr_contains_info():
    """Genome repr includes length and fitness."""
    g = Genome(genes=[0.5, 0.5])
    r = repr(g)
    assert "length=2" in r
    assert "fitness=" in r


# ======================================================================
# Population tests
# ======================================================================

@pytest.mark.unit
def test_population_creation():
    """Population is initialized with correct size and generation 0."""
    pop = Population(size=20, genome_length=5)
    assert pop.size == 20
    assert pop.genome_length == 5
    assert pop.generation == 0
    assert len(pop.individuals) == 20


@pytest.mark.unit
def test_population_evolve_advances_generations():
    """Evolving increments the generation counter."""
    pop = Population(size=10, genome_length=5)
    pop.evolve(generations=5)
    assert pop.generation == 5


@pytest.mark.unit
def test_population_evolve_returns_sorted():
    """Evolve returns individuals sorted by fitness descending."""
    pop = Population(size=10, genome_length=5)
    result = pop.evolve(generations=3)
    for i in range(len(result) - 1):
        assert result[i].fitness_score() >= result[i + 1].fitness_score()


@pytest.mark.unit
def test_population_get_best():
    """get_best returns the individual with highest fitness."""
    pop = Population(size=10, genome_length=5)
    best = pop.get_best()
    for individual in pop.individuals:
        assert individual.fitness_score() <= best.fitness_score()


@pytest.mark.unit
def test_population_average_fitness():
    """average_fitness returns the mean of all fitness scores."""
    pop = Population(size=10, genome_length=5)
    avg = pop.average_fitness()
    expected = sum(g.fitness_score() for g in pop.individuals) / 10
    assert avg == pytest.approx(expected)


@pytest.mark.unit
def test_population_select_parents_returns_correct_count():
    """select_parents returns the requested number of parents."""
    pop = Population(size=20, genome_length=5, tournament_size=3)
    parents = pop.select_parents(10)
    assert len(parents) == 10


@pytest.mark.unit
def test_population_history_records_generations():
    """Evolution history records stats for each generation."""
    pop = Population(size=10, genome_length=5)
    pop.evolve(generations=4)
    assert len(pop.history) == 4
    for entry in pop.history:
        assert "generation" in entry
        assert "best_fitness" in entry
        assert "avg_fitness" in entry


@pytest.mark.unit
def test_population_elitism_preserves_best():
    """The best individual survives across generations (elitism)."""
    pop = Population(size=10, genome_length=5, mutation_rate=0.0)
    best_before = pop.get_best().fitness_score()
    pop.evolve(generations=1)
    best_after = pop.get_best().fitness_score()
    # With elitism and no mutation, best should not decrease
    assert best_after >= best_before


# ======================================================================
# Detailed Colony (ant_colony.colony) tests
# ======================================================================

@pytest.mark.unit
def test_detailed_colony_construction():
    """DetailedColony spawns ants at nest in FORAGING state."""
    env = Environment(20, 20)
    colony = DetailedColony(size=5, environment=env)
    assert colony.size == 5
    assert len(colony.ants) == 5
    assert colony.tick == 0
    assert colony.food_collected == 0.0
    for ant in colony.ants:
        assert ant.state == DetailedAntState.FORAGING


@pytest.mark.unit
def test_detailed_colony_simulate_step_advances_tick():
    """simulate_step increments the tick counter."""
    env = Environment(20, 20)
    colony = DetailedColony(size=3, environment=env)
    result = colony.simulate_step()
    assert result["tick"] == 1
    assert colony.tick == 1


@pytest.mark.unit
def test_detailed_colony_simulate_step_returns_stats():
    """simulate_step returns dict with expected keys."""
    env = Environment(20, 20)
    colony = DetailedColony(size=3, environment=env)
    result = colony.simulate_step()
    assert "tick" in result
    assert "alive" in result
    assert "food_collected" in result
    assert "food_remaining" in result


@pytest.mark.unit
def test_detailed_colony_get_stats_keys():
    """get_stats returns comprehensive statistics."""
    env = Environment(20, 20)
    colony = DetailedColony(size=5, environment=env)
    stats = colony.get_stats()
    expected_keys = {"tick", "population", "dead", "states", "average_energy",
                     "food_collected", "food_remaining", "pheromone_cells"}
    assert expected_keys.issubset(stats.keys())


@pytest.mark.unit
def test_detailed_colony_add_food_source():
    """add_food_source delegates to environment."""
    env = Environment(20, 20)
    colony = DetailedColony(size=3, environment=env)
    colony.add_food_source((5, 5), 100.0)
    assert len(env.food_sources) == 1
    assert env.food_sources[0].amount == pytest.approx(100.0)


@pytest.mark.unit
def test_detailed_colony_dead_ants_not_counted_alive():
    """Dead ants are excluded from alive count in stats."""
    env = Environment(20, 20)
    colony = DetailedColony(size=3, environment=env)
    colony.ants[0].energy = 0.0
    stats = colony.get_stats()
    assert stats["population"] == 2
    assert stats["dead"] == 1
