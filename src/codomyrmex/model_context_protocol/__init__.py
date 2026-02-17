"""
Model Context Protocol Module for Codomyrmex.

The Model Context Protocol (MCP) is a foundational specification within the Codomyrmex
ecosystem, designed to standardize communication and interactions between different
components and external models.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available classes:
- MCPErrorDetail
- MCPToolCall
- MCPToolResult
"""

from codomyrmex.exceptions import CodomyrmexError

# Submodule exports
from . import adapters, discovery, schemas, validators
from .schemas.mcp_schemas import (
    MCPErrorDetail,
    MCPMessage,
    MCPToolCall,
    MCPToolRegistry,
    MCPToolResult,
)

# MCP Server
from .server import MCPServer, MCPServerConfig

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the model_context_protocol module."""
    return {
        "tools": {
            "help": "List registered MCP tools",
            "handler": lambda **kwargs: print(
                "MCP Tool Registry:\n"
                f"  Registry class: {MCPToolRegistry.__name__}\n"
                f"  Message class: {MCPMessage.__name__}\n"
                f"  Tool call class: {MCPToolCall.__name__}\n"
                f"  Tool result class: {MCPToolResult.__name__}\n"
                f"  Error detail class: {MCPErrorDetail.__name__}\n"
                "  Submodules: adapters, discovery, schemas, validators"
            ),
        },
        "status": {
            "help": "Show MCP server status and configuration",
            "handler": lambda **kwargs: print(
                f"MCP Server: {MCPServer.__name__}\n"
                f"MCP Config: {MCPServerConfig.__name__}\n"
                "Adapters module loaded: True\n"
                "Discovery module loaded: True\n"
                "Validators module loaded: True"
            ),
        },
    }


__all__ = [
    "MCPErrorDetail",
    "MCPMessage",
    "MCPToolCall",
    "MCPToolRegistry",
    "MCPToolResult",
    "MCPServer",
    "MCPServerConfig",
    "schemas",
    "adapters",
    "validators",
    "discovery",
    "cli_commands",
]


