"""
Utility functions for the Data Visualization module.

- All logging is handled via logging_monitoring (get_codomyrmex_logger).
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import logging
import os


def get_codomyrmex_logger(name: str) -> logging.Logger:
    """
    Attempts to get a logger from the Codomyrmex logging_monitoring module.
    Falls back to standard Python logging if the Codomyrmex module is not found.
    """
    try:
        from codomyrmex.logging_monitoring.logger_config import get_logger

        logger_instance = get_logger(name)
    except ImportError:
        logger_instance = logging.getLogger(name)
        if not logger_instance.hasHandlers():
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        logger_instance.info(
            f"Codomyrmex logging_monitoring module not found or not yet configured for {name}. "
            f"Using standard Python logging."
        )
    return logger_instance


# Get a logger for this utility module itself
logger = get_codomyrmex_logger(__name__)

# Recommend: At application startup, call environment_setup.env_checker.ensure_dependencies_installed()
# to check for required dependencies and environment variables.


def save_plot(fig, output_path: str, dpi: int = 300):
    """
    Helper function to save a matplotlib figure.
    Creates the output directory if it doesn't exist.
    """
    if not output_path:
        logger.warning(
            "Output path not provided for saving plot. Plot will not be saved to file."
        )
        return
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
        logger.info(f"Plot successfully saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving plot to {output_path}: {e}", exc_info=True)


# Common aesthetic settings (optional, can be expanded)
DEFAULT_FIGURE_SIZE = (10, 6)  # Standard figure size
DEFAULT_GRID_STYLE = {"visible": True, "linestyle": "--", "alpha": 0.7}
DEFAULT_TITLE_FONTSIZE = 16
DEFAULT_LABEL_FONTSIZE = 12


def apply_common_aesthetics(
    ax, title: str = None, x_label: str = None, y_label: str = None
):
    """
    Applies common aesthetic settings to a matplotlib Axes object.
    """
    if title:
        ax.set_title(title, fontsize=DEFAULT_TITLE_FONTSIZE)
    if x_label:
        ax.set_xlabel(x_label, fontsize=DEFAULT_LABEL_FONTSIZE)
    if y_label:
        ax.set_ylabel(y_label, fontsize=DEFAULT_LABEL_FONTSIZE)
    ax.grid(**DEFAULT_GRID_STYLE)


# Configure this once, perhaps based on an environment variable or a config file
CODOMYRMEX_LOGGING_NAMESPACE_PREFIX = "codomyrmex"
