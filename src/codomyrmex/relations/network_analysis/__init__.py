"""Network analysis subpackage for the relations module.

Provides social graph construction, community detection,
centrality metrics, and path-finding algorithms.
"""

from .graph import GraphMetrics, SocialGraph

__all__ = ["SocialGraph", "GraphMetrics"]
