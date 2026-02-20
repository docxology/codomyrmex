# DEPRECATED(v0.2.0): Shim module. Import from orchestrator.resilience.failure_taxonomy instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: orchestrator.resilience.failure_taxonomy"""
from .resilience.failure_taxonomy import *  # noqa: F401,F403
from .resilience.failure_taxonomy import (  # explicit re-exports for type checkers
    ClassifiedError,
    FailureCategory,
    RECOVERY_MAP,
    RecoveryStrategy,
    classify_error,
)
