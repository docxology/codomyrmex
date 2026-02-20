# DEPRECATED(v0.2.0): Shim module. Import from orchestrator.resilience.self_healing instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: orchestrator.resilience.self_healing"""
from .resilience.self_healing import *  # noqa: F401,F403
from .resilience.self_healing import (
    Diagnoser,
    Diagnosis,
    RecoveryStep,
)
