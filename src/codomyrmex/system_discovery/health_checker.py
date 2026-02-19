# DEPRECATED(v0.2.0): Shim module. Import from system_discovery.health.health_checker instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from system_discovery.health.health_checker."""
from .health.health_checker import *  # noqa: F401,F403
from .health.health_checker import (
    HealthCheckResult,
    HealthChecker,
    HealthStatus,
    check_module_availability,
)
