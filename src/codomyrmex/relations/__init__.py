"""Relations Module for Codomyrmex.

Provides CRM contact management, social network analysis,
graph metrics, and UOR (Universal Object Reference) integration.
"""

from .crm import Contact, ContactManager, Interaction
from .network_analysis import SocialGraph, GraphMetrics
from .uor import (
    DerivationRecord,
    DerivationTracker,
    EntityManager,
    PrismEngine,
    TriadicCoordinate,
    UOREntity,
    UORGraph,
    UORRelationship,
)

__all__ = [
    "Contact",
    "ContactManager",
    "DerivationRecord",
    "DerivationTracker",
    "EntityManager",
    "GraphMetrics",
    "Interaction",
    "PrismEngine",
    "SocialGraph",
    "TriadicCoordinate",
    "UOREntity",
    "UORGraph",
    "UORRelationship",
]
