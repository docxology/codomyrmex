"""
Alerting Submodule

Alert rule configuration and notification routing
"""

__version__ = "0.1.0"
__all__ = []

# Lazy imports for performance
# from .core import *

from .alert_evaluator import *  # noqa: F401, F403
from .alerts import *  # noqa: F401, F403
