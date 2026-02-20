# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.transport.main instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.transport.main"""
from .transport.main import *  # noqa: F401,F403
from .transport.main import (
    main,
    run_server,
)
