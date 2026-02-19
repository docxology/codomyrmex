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
from .main import main, run_server

# MCP Decorators
from .decorators import mcp_tool

# MCP Client
from .client import MCPClient, MCPClientConfig, MCPClientError

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


# MCP Errors and Validation (v0.1.8 Stream 1)
from .errors import MCPErrorCode, MCPToolError, FieldError
from .validation import ValidationResult, validate_tool_arguments

# MCP Transport Robustness (v0.1.8 Stream 2)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    get_circuit_breaker,
    get_all_circuit_metrics,
    reset_all_circuits,
)
from .rate_limiter import RateLimiter, RateLimiterConfig
from .discovery import (
    FailedModule,
    DiscoveryReport,
    DiscoveryMetrics,
    MCPDiscoveryEngine,
)

# MCP Tool Taxonomy (v0.2.0 Stream 1)
from .taxonomy import (
    ToolCategory,
    categorize_tool,
    categorize_all_tools,
    generate_taxonomy_report,
    TaxonomyReport,
)


__all__ = [
    "MCPErrorDetail",
    "MCPMessage",
    "MCPToolCall",
    "MCPToolRegistry",
    "MCPToolResult",
    "MCPServer",
    "MCPServerConfig",
    "mcp_tool",
    "MCPClient",
    "MCPClientConfig",
    "MCPClientError",
    # Stream 1
    "MCPErrorCode",
    "MCPToolError",
    "FieldError",
    "ValidationResult",
    "validate_tool_arguments",
    # Stream 2
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "CircuitState",
    "get_circuit_breaker",
    "get_all_circuit_metrics",
    "reset_all_circuits",
    "RateLimiter",
    "RateLimiterConfig",
    # Stream 3
    "FailedModule",
    "DiscoveryReport",
    "DiscoveryMetrics",
    "MCPDiscoveryEngine",
    # v0.2.0 taxonomy
    "ToolCategory",
    "categorize_tool",
    "categorize_all_tools",
    "generate_taxonomy_report",
    "TaxonomyReport",
    "schemas",
    "adapters",
    "validators",
    "discovery",
    "cli_commands",
    "main",
    "run_server",
]


