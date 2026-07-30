"""Minimal ML pipeline-definition MCP surface.

The current functions return structured, stateless receipts. They do not
persist or execute machine-learning workloads.
"""

from .mcp_tools import ml_pipeline_create, ml_pipeline_execute

__all__ = ["ml_pipeline_create", "ml_pipeline_execute"]
