"""Stigmergy — indirect coordination via persistent environmental traces.

Quantitative markers (strength, evaporation, reinforcement) complement
:class:`~codomyrmex.agentic_memory.core.memory.AgentMemory` retention; see
``docs/bio/stigmergy.md`` for the conceptual mapping.
"""

from codomyrmex.agentic_memory.stigmergy.field import TraceField
from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig, TraceMarker
from codomyrmex.agentic_memory.stigmergy.policy import (
    boost_importance_value,
    importance_boost_from_trace,
)
from codomyrmex.agentic_memory.stigmergy.sqlite_ledger import SqliteTraceLedger

__all__ = [
    "StigmergyConfig",
    "TraceField",
    "TraceMarker",
    "SqliteTraceLedger",
    "boost_importance_value",
    "importance_boost_from_trace",
]
