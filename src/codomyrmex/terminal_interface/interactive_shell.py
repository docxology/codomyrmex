"""Backward-compatible import surface for the interactive shell."""

from .shells.interactive_shell import InteractiveShell, SessionData

__all__ = ["InteractiveShell", "SessionData"]
