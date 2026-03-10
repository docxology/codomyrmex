from codomyrmex.data_visualization import ScatterPlot

from .colony import Colony


def render_colony_state(colony: Colony) -> ScatterPlot:
    """
    Renders a scatter plot of current ant positions.
    """
    x_coords = []
    y_coords = []

    if hasattr(colony, "ants"):
        for ant in colony.ants:
            if hasattr(ant, "position"):
                x_coords.append(ant.position[0])
                y_coords.append(ant.position[1])
            elif hasattr(ant, "x") and hasattr(ant, "y"):
                x_coords.append(ant.x)
                y_coords.append(ant.y)

    return ScatterPlot(
        title="Real-time Colony State",
        x_label="X Coordinate",
        y_label="Y Coordinate",
        x_data=x_coords,
        y_data=y_coords,
    )
