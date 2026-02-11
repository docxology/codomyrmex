"""Agent Setup — Registry, configuration, and interactive setup wizard.

Provides:
- ``AgentRegistry``: Declarative catalog of all agents with live health probes.
- ``load_config`` / ``save_config``: YAML config file persistence.
- ``run_setup_wizard``: Interactive terminal walk-through.

Quick start::

    python -m codomyrmex.agents.agent_setup
"""

from .registry import AgentDescriptor, AgentRegistry, ProbeResult
from .config_file import load_config, save_config, merge_with_env

__all__ = [
    "AgentDescriptor",
    "AgentRegistry",
    "ProbeResult",
    "load_config",
    "save_config",
    "merge_with_env",
]
