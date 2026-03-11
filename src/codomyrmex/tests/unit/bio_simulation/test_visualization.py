"""Tests for bio_simulation visualization."""

import pytest
from codomyrmex.bio_simulation import Colony as AntColony
from codomyrmex.bio_simulation.colony import Colony as BasicColony
from codomyrmex.bio_simulation.visualization import render_colony_state
from codomyrmex.data_visualization import ScatterPlot


@pytest.mark.unit
def test_render_colony_state_ant_colony():
    """Verify render_colony_state works with AntColony (uses .position)."""
    colony = AntColony(population=5)
    plot = render_colony_state(colony)
    assert isinstance(plot, ScatterPlot)
    assert len(plot.x_data) == 5
    assert len(plot.y_data) == 5


@pytest.mark.unit
def test_render_colony_state_basic_colony():
    """Verify render_colony_state works with BasicColony (uses .x, .y)."""
    colony = BasicColony(population_size=3)
    plot = render_colony_state(colony)
    assert isinstance(plot, ScatterPlot)
    assert len(plot.x_data) == 3
    assert len(plot.y_data) == 3


@pytest.mark.unit
def test_render_colony_state_empty():
    """Verify render_colony_state works with no ants."""
    colony = BasicColony(population_size=0)
    plot = render_colony_state(colony)
    assert isinstance(plot, ScatterPlot)
    assert len(plot.x_data) == 0
