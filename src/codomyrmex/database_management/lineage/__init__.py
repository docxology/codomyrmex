"""
Data Lineage Module (Legacy)

This module is now deprecated in favor of codomyrmex.data_lineage.
It is maintained for backward compatibility.
"""

from codomyrmex.data_lineage.graph import LineageGraph
from codomyrmex.data_lineage.models import (
    DataAsset,
    EdgeType,
    LineageEdge,
    LineageNode,
    NodeType,
)
from codomyrmex.data_lineage.tracker import ImpactAnalyzer, LineageTracker

__all__ = [
    "NodeType",
    "EdgeType",
    "LineageNode",
    "LineageEdge",
    "DataAsset",
    "LineageGraph",
    "LineageTracker",
    "ImpactAnalyzer",
]
