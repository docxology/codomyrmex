"""Hermes Agent module for Codomyrmex.

Provides seamless integration with the NousResearch Hermes Agent CLI framework.
"""

from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError

__all__ = ["HermesClient", "HermesError"]
