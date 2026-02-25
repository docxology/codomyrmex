"""Arscontexta exceptions — re-export from canonical models module."""

from .models import (
    ArsContextaError,
    PipelineError,
    PrimitiveValidationError,
    VaultNotFoundError,
)

__all__ = [
    "ArsContextaError",
    "PipelineError",
    "PrimitiveValidationError",
    "VaultNotFoundError",
]
