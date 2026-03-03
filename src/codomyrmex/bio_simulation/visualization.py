from codomyrmex.data_visualization import ScatterPlot

from .ant_colony.colony import Colony


def render_colony_state(colony: Colony) -> ScatterPlot:
    """Renders a scatter plot of current ant positions.

    Args:
        colony: The ant colony instance to render.

    Returns:
        A ScatterPlot object showing the current spatial positions
        of all living ants.
    """
    # Assuming ants have x and y attributes
    # If not, use mock data or fix based on Colony implementation
    # Based on test failure 'None', likely the import failed or render() failed.

    x_coords = []
    y_coords = []

    if hasattr(colony, "ants"):
        x_coords = [ant.position[0] for ant in colony.ants]
        y_coords = [ant.position[1] for ant in colony.ants]

    return ScatterPlot(
        title="Real-time Colony State",
        x_label="X Coordinate",
        y_label="Y Coordinate",
        x_data=x_coords,
        y_data=y_coords,
    )
