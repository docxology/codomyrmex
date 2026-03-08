"""openfang exception hierarchy."""


class OpenFangError(Exception):
    """Base exception for all openfang integration errors."""


class OpenFangNotInstalledError(OpenFangError):
    """openfang binary not found on PATH."""


class OpenFangTimeoutError(OpenFangError):
    """openfang subprocess exceeded the configured timeout."""


class OpenFangBuildError(OpenFangError):
    """cargo build failed when building openfang from source."""


class OpenFangConfigError(OpenFangError):
    """Invalid or missing openfang configuration."""
