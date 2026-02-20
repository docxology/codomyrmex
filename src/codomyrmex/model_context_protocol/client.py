# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.transport.client instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.transport.client"""
from .transport.client import *  # noqa: F401,F403
from .transport.client import (
    MCPClient,
    MCPClientConfig,
    MCPClientError,
    _HTTPTransport,
    _StdioTransport,
    _Transport,
)
