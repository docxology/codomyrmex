from codomyrmex.bio_simulation import AntState, Colony


def test_colony_simulation():
    """Test functionality: colony simulation."""
    colony = Colony(population=10)
    assert len(colony.ants) == 10
    assert colony.tick == 0

    colony.step(hours=1)
    assert colony.tick == 60

    # Check energy drain
    assert colony.ants[0].energy < 1.0

def test_census():
    """Test functionality: state distribution."""
    colony = Colony(population=10)
    stats = colony.stats()
    assert stats["state_distribution"]["FORAGING"] == 10
