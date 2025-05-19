"""
Generates scatter plots.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""
import matplotlib.pyplot as plt
from .plot_utils import save_plot, get_codomyrmex_logger

logger = get_codomyrmex_logger(__name__)

def create_scatter_plot(
    x_data: list,
    y_data: list,
    title: str = "Scatter Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    output_path: str = None,
    show_plot: bool = False,
    dot_size: int = 20,
    dot_color: str = 'blue',
    alpha: float = 0.7
):
    """
    Generates a scatter plot.
    Uses logging_monitoring for logging.
    """
    logger.debug(f"Generating scatter plot titled '{title}'")
    if not x_data or not y_data:
        logger.warning("Empty data provided for scatter plot. No plot generated.")
        return
    if len(x_data) != len(y_data):
        logger.warning(f"Length mismatch for scatter plot: x_data ({len(x_data)}) vs y_data ({len(y_data)}). Plot not generated.")
        return

    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data, s=dot_size, c=dot_color, alpha=alpha)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)
    
    if output_path:
        save_plot(fig, output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
    logger.info(f"Scatter plot '{title}' generated successfully.")

if __name__ == '__main__':
    # Example Usage
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / "output" / "data_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"--- Example: Basic Scatter Plot ---")
    sample_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_y = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29] # Prime numbers
    create_scatter_plot(
        x_data=sample_x,
        y_data=sample_y,
        title="Sample Scatter Plot: Prime Numbers",
        x_label="Index",
        y_label="Prime Number",
        output_path=str(output_dir / "basic_scatter_plot.png"),
        show_plot=False,
        dot_color='green',
        alpha=0.6
    )
    logger.info(f"Scatter plot example saved to {output_dir / 'basic_scatter_plot.png'}")

    logger.info(f"--- Example: Scatter Plot with Different Dot Size ---")
    sample_x_2 = [i*0.5 for i in range(20)]
    sample_y_2 = [x**2 for x in sample_x_2]
    create_scatter_plot(
        x_data=sample_x_2,
        y_data=sample_y_2,
        title="Scatter Plot: Quadratic Relationship",
        x_label="X Value",
        y_label="X Squared",
        output_path=str(output_dir / "quadratic_scatter_plot.png"),
        show_plot=False,
        dot_size=50,
        dot_color='purple'
    )
    logger.info(f"Scatter plot example saved to {output_dir / 'quadratic_scatter_plot.png'}")
    
    # Setup a root logger for the example script if this is run directly
    # (assuming logging_monitoring.setup_logging would handle this in a full app context)
    import logging
    if not get_codomyrmex_logger('').hasHandlers(): # Check if root logger is already configured
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.info("Basic logging configured for direct script execution of scatter_plot.py.") 