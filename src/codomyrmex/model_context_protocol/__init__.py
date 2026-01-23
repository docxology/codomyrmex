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

from .schemas.mcp_schemas import (
    MCPErrorDetail,
    MCPMessage,
    MCPToolCall,
    MCPToolRegistry,
    MCPToolResult,
)

# Submodule exports
from . import schemas
from . import adapters
from . import validators
from . import discovery

__all__ = [
    "MCPErrorDetail",
    "MCPMessage",
    "MCPToolCall",
    "MCPToolRegistry",
    "MCPToolResult",
    "schemas",
    "adapters",
    "validators",
    "discovery",
]

