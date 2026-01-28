"""
Evaluators module - alias for backward compatibility.

Provides metric functions for model evaluation.
"""

# Re-export metric functions from main module
from . import exact_match_metric, length_ratio_metric

# Also export the Evaluator class
from . import Evaluator

__all__ = [
    "exact_match_metric",
    "length_ratio_metric",
    "Evaluator",
]
