"""Model Operations module for Codomyrmex."""

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .datasets.datasets import Dataset, DatasetSanitizer
except ImportError:
    Dataset = None
    DatasetSanitizer = None

try:
    from .fine_tuning.fine_tuning import FineTuningJob
except ImportError:
    FineTuningJob = None

try:
    from .evaluation.evaluators import Evaluator
except ImportError:
    Evaluator = None

# Submodule exports
from . import evaluation
from . import training

# Try optional submodules
try:
    from . import datasets
except ImportError:
    pass

try:
    from . import fine_tuning
except ImportError:
    pass

__all__ = [
    "evaluation",
    "training",
]

if Dataset:
    __all__.extend(["Dataset", "DatasetSanitizer"])
if FineTuningJob:
    __all__.append("FineTuningJob")
if Evaluator:
    __all__.append("Evaluator")

__version__ = "0.1.0"
