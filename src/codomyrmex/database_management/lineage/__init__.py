"""
Data Lineage Module

Track data lineage through transformations with graph-based analysis.
"""

from .models import (
    DataAsset,
    EdgeType,
    LineageEdge,
    LineageNode,
    NodeType,
)
from .graph import LineageGraph
from .tracker import ImpactAnalyzer, LineageTracker

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the data_lineage module."""
    return {
        "trace": lambda: print(
            "Data Lineage Tracing\n"
            "  Node types: " + ", ".join(nt.value for nt in NodeType) + "\n"
            "  Edge types: " + ", ".join(et.value for et in EdgeType) + "\n"
            "  Use LineageTracker to record data transformations and trace lineage."
        ),
        "graph": lambda: print(
            "Lineage Graph\n"
            "  Use LineageGraph to build and query the lineage DAG.\n"
            "  Use ImpactAnalyzer to assess downstream impact of data changes."
        ),
    }


__all__ = [
    "NodeType",
    "EdgeType",
    "LineageNode",
    "LineageEdge",
    "DataAsset",
    "LineageGraph",
    "LineageTracker",
    "ImpactAnalyzer",
    # CLI
    "cli_commands",
]
