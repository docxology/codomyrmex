"""Evolutionary AI module for Codomyrmex."""

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .genome.genome import Genome
except ImportError:
    Genome = None

try:
    from .population.population import Population
except ImportError:
    Population = None

# Submodule exports
from . import operators
from . import selection
from . import fitness

# Try optional submodules
try:
    from . import genome
except ImportError:
    pass

try:
    from . import population
except ImportError:
    pass

__all__ = [
    "operators",
    "selection",
    "fitness",
]

if Genome:
    __all__.append("Genome")
if Population:
    __all__.append("Population")

__version__ = "0.1.0"
