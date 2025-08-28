"""
Contains the create_line_plot function for generating line plots.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""
import matplotlib.pyplot as plt
import os
from .plot_utils import get_codomyrmex_logger, save_plot, apply_common_aesthetics, DEFAULT_FIGURE_SIZE

logger = get_codomyrmex_logger(__name__)

def create_line_plot(
    x_data: list,
    y_data: list,
    title: str = "Line Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str = None,
    show_plot: bool = False,
    line_labels: list = None, # For multiple lines
    markers: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE
):
    """
    Generates a line plot.
    Uses logging_monitoring for logging.
    If y_data is a list of lists, and x_data is a single list, multiple lines are plotted.
    If line_labels are provided, they will be used for the legend.
    """
    logger.debug(f"Generating line plot titled '{title}'")
    if len(x_data) == 0 or len(y_data) == 0:
        logger.warning("Empty data provided for line plot. No plot generated.")
        return None

    fig, ax = plt.subplots(figsize=figure_size)
    
    if isinstance(y_data[0], list): # Multiple lines
        if not line_labels or len(line_labels) != len(y_data):
            line_labels = [f'Line {i+1}' for i in range(len(y_data))]
            logger.debug("Line labels not provided or mismatch length; auto-generating labels.")
        for i, y_series in enumerate(y_data):
            if len(x_data) != len(y_series):
                logger.warning(f"Length mismatch for line {line_labels[i]}: x_data ({len(x_data)}) and y_series ({len(y_series)}). Skipping this line.")
                continue
            ax.plot(x_data, y_series, label=line_labels[i], marker='o' if markers else None)
        ax.legend()
    else: # Single line
        if len(x_data) != len(y_data):
            logger.warning(f"Length mismatch: x_data ({len(x_data)}) and y_data ({len(y_data)}). Line plot not generated.")
            return None
        ax.plot(x_data, y_data, marker='o' if markers else None)

    apply_common_aesthetics(ax, title, x_label, y_label)
    plt.tight_layout()

    if output_path:
        save_plot(fig, output_path)
    
    if show_plot:
        logger.debug(f"Displaying plot: {title}")
        plt.show()
    else:
        plt.close(fig) # Close the figure to free memory if not shown
    
    logger.info(f"Line plot '{title}' generated successfully.")
    return fig # Return the figure object for potential further manipulation

if __name__ == '__main__':
    # This section is for direct testing of line_plot.py
    # Assumes plot_utils.py is in the same directory or Python path is set correctly.
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_dir = os.path.join(current_dir, "test_outputs_data_visualization")
    os.makedirs(test_output_dir, exist_ok=True)
    logger.info(f"Test outputs will be saved in {test_output_dir}")

    x_simple = [1, 2, 3, 4, 5]
    y_simple = [2, 3, 5, 7, 6]
    y_multiple = [[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [2, 2, 2, 2, 2]]
    line_labels_multiple = ['Ascending', 'Descending', 'Constant']

    create_line_plot(x_simple, y_simple, 
                     title="Test Simple Line Plot (from line_plot.py)", 
                     output_path=os.path.join(test_output_dir, "line_plot_simple_standalone.png"), 
                     markers=True)
    
    create_line_plot(x_simple, y_multiple, 
                     title="Test Multiple Lines Plot (from line_plot.py)", 
                     line_labels=line_labels_multiple,
                     output_path=os.path.join(test_output_dir, "line_plot_multiple_standalone.png"))
    
    # Example with show_plot (might require GUI environment)
    # create_line_plot(x_simple, y_simple, title="Test Show Line Plot", show_plot=True)

    logger.info(f"Completed direct testing of line_plot.py. Check the '{test_output_dir}' directory.") 