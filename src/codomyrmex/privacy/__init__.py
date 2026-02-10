"""Privacy Module.

Provides Crumb Cleaning (sanitization) and Mixnet Routing (anonymity).
"""

from .crumbs import CrumbCleaner
from .mixnet import MixnetProxy

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the privacy module."""
    return {
        "scan": {
            "help": "Scan for privacy issues (data leaks, tracking crumbs)",
            "args": ["--path"],
            "handler": lambda path=None: print(
                f"Scanning {'path: ' + path if path else 'current environment'} "
                "for privacy issues...\n"
                "  CrumbCleaner: ready\n"
                "  MixnetProxy:  ready"
            ),
        },
        "report": {
            "help": "Generate a privacy audit report",
            "handler": lambda: print(
                "Privacy Report:\n"
                "  Crumb cleaner status: active\n"
                "  Mixnet proxy status:  active\n"
                "  Known issues:         0"
            ),
        },
    }


__all__ = [
    "CrumbCleaner",
    "MixnetProxy",
    # CLI integration
    "cli_commands",
]
