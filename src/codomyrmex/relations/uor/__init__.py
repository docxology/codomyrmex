"""UOR subpackage — Universal Object Reference for the relations module.

Integrates concepts from the UOR Foundation:
- PRISM triadic coordinates for structural identity
- Content-addressed hashing for entity/relationship identity
- Derivation tracking for provenance certificates

References:
    - https://github.com/UOR-Foundation
    - https://github.com/UOR-Foundation/prism
    - https://github.com/UOR-Foundation/UOR-Framework
"""

from .derivation import DerivationRecord, DerivationTracker
from .engine import PrismEngine, TriadicCoordinate
from .entities import UOREntity, UORRelationship
from .graph import UORGraph
from .manager import EntityManager

__all__ = [
    "DerivationRecord",
    "DerivationTracker",
    "EntityManager",
    "PrismEngine",
    "TriadicCoordinate",
    "UOREntity",
    "UORGraph",
    "UORRelationship",
]
