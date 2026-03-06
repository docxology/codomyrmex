"""
Languages Module for Codomyrmex.

Provides utilities for interacting with various programming languages,
including checking if they are installed, providing installation instructions,
setting up projects, and running scripts.
"""

from .mcp_tools import register_mcp_tools

__all__ = ["register_mcp_tools"]
