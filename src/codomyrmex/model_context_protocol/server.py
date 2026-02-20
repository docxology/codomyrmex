# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.transport.server instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.transport.server"""
from .transport.server import *  # noqa: F401,F403
from .transport.server import (
    MCPServer,
    MCPServerConfig,
)
