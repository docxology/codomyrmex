"""Relations Module for Codomyrmex.

Provides CRM contact management, social network analysis,
and graph metrics.
"""

from .crm import Contact, ContactManager, Interaction
from .network_analysis import SocialGraph, GraphMetrics

__all__ = [
    "Contact",
    "ContactManager",
    "GraphMetrics",
    "Interaction",
    "SocialGraph",
]
