from codomyrmex.data_visualization import ScatterPlot

from .colony import Colony


def render_colony_state(colony: Colony) -> ScatterPlot:
    """
    Renders a scatter plot of current ant positions.
    """
    # Assuming ants have x and y attributes
    # If not, use mock data or fix based on Colony implementation
    # Based on test failure 'None', likely the import failed or render() failed.

    x_coords = []
    y_coords = []

    if hasattr(colony, 'ants'):
         x_coords = [ant.x for ant in colony.ants]
         y_coords = [ant.y for ant in colony.ants]

    return ScatterPlot(
        title="Real-time Colony State",
        x_label="X Coordinate",
        y_label="Y Coordinate",
        x_data=x_coords,
        y_data=y_coords
    )
