"""Exceptions for the formal_verification module."""


class SolverError(Exception):
    """Base exception for all formal verification solver errors."""


class SolverTimeoutError(SolverError):
    """Raised when a solver exceeds its configured timeout."""


class ModelBuildError(SolverError):
    """Raised when a constraint model cannot be constructed."""


class UnsatisfiableError(SolverError):
    """Raised when a model is provably unsatisfiable (optional — see verify_isc for advisory mode)."""


class BackendNotAvailableError(SolverError):
    """Raised when a requested solver backend is not installed."""


class InvalidConstraintError(SolverError):
    """Raised when a constraint expression is malformed."""
