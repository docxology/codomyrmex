"""Model Operations module for Codomyrmex."""

from .datasets.datasets import Dataset, DatasetSanitizer
from .fine_tuning.fine_tuning import FineTuningJob
from .evaluation.evaluators import Evaluator

# Submodule exports
from . import datasets
from . import evaluation
from . import fine_tuning
from . import training

__all__ = [
    "Dataset",
    "DatasetSanitizer",
    "FineTuningJob",
    "Evaluator",
    "datasets",
    "evaluation",
    "fine_tuning",
    "training",
]

__version__ = "0.1.0"

