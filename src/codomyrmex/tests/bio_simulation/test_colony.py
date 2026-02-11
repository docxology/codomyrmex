from codomyrmex.bio_simulation.colony import Colony, AntState

def test_colony_simulation():
    colony = Colony(population_size=10)
    assert len(colony.ants) == 10
    assert colony.tick == 0
    
    colony.step()
    assert colony.tick == 1
    
    # Check energy drain
    assert colony.ants[0].energy < 100.0

def test_census():
    colony = Colony(10)
    census = colony.get_census()
    assert census[AntState.IDLE] == 10
