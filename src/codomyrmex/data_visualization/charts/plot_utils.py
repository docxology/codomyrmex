"""
Plot Utilities for Codomyrmex Data Visualization.

Provides shared utility functions for chart generation including:
- Logging configuration
- Plot saving with format detection
- Common styling helpers
"""

import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Try to import from codomyrmex logging, fallback to standard logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    
    def get_codomyrmex_logger(name: str):
        """Get a configured logger for the given name."""
        return get_logger(name)
except ImportError:
    def get_codomyrmex_logger(name: str):
        """Get a standard Python logger."""
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        return logger


logger = get_codomyrmex_logger(__name__)


def save_plot(
    fig,
    output_path: str,
    dpi: int = 150,
    transparent: bool = False,
    bbox_inches: str = 'tight'
) -> bool:
    """
    Save a matplotlib figure to a file.
    
    Args:
        fig: The matplotlib figure to save.
        output_path: The path where to save the plot.
        dpi: Dots per inch resolution.
        transparent: Whether to make the background transparent.
        bbox_inches: Bounding box control ('tight' recommended).
    
    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Detect format from extension
        suffix = output_path.suffix.lower()
        fmt = suffix[1:] if suffix else 'png'
        
        # Save the figure
        fig.savefig(
            output_path,
            format=fmt,
            dpi=dpi,
            transparent=transparent,
            bbox_inches=bbox_inches
        )
        
        logger.info(f"Plot saved successfully to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save plot to {output_path}: {e}")
        return False


def apply_codomyrmex_style(ax, title: str = None):
    """
    Apply Codomyrmex styling to a matplotlib axes.
    
    Args:
        ax: The matplotlib axes to style.
        title: Optional title to set.
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    
    return ax


def get_color_palette(n_colors: int = 10) -> list:
    """
    Get a list of colors for visualizations.
    
    Args:
        n_colors: Number of colors needed.
    
    Returns:
        List of color hex codes.
    """
    base_palette = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange  
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
    ]
    
    # Repeat palette if more colors needed
    if n_colors <= len(base_palette):
        return base_palette[:n_colors]
    else:
        repeats = (n_colors // len(base_palette)) + 1
        return (base_palette * repeats)[:n_colors]
