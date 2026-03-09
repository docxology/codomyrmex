"""Hermes orchestration scripts.

Runnable scripts that exercise real HermesClient, session persistence,
prompt templates, MCP tools, and evolution-submodule data models.
"""

from codomyrmex.agents.hermes.scripts.run_status import run_status
from codomyrmex.agents.hermes.scripts.run_chat import run_chat
from codomyrmex.agents.hermes.scripts.run_stream import run_stream
from codomyrmex.agents.hermes.scripts.run_session import run_session
from codomyrmex.agents.hermes.scripts.run_template import run_template
from codomyrmex.agents.hermes.scripts.run_pipeline import run_pipeline
from codomyrmex.agents.hermes.scripts.run_evolution_bridge import run_evolution_bridge
from codomyrmex.agents.hermes.scripts.run_mcp_tools import run_mcp_tools

__all__ = [
    "run_status",
    "run_chat",
    "run_stream",
    "run_session",
    "run_template",
    "run_pipeline",
    "run_evolution_bridge",
    "run_mcp_tools",
]
