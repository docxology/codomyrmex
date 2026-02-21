# DEPRECATED(v0.2.0): Shim module. Import from documentation.quality.audit instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: documentation.quality.audit"""
from .quality.audit import *  # noqa: F401,F403
from .quality.audit import (
    ModuleAudit,
    audit_documentation,
    audit_rasp,
)
