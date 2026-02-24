"""Built-in droid task handlers used by the TODO runner."""

from __future__ import annotations

from importlib import import_module

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from . import controller as controller_module

logger = get_logger(__name__)


def ensure_documentation_exists(*, prompt: str, description: str) -> str:
    """Validate that the controller module exposes documented interfaces."""
    if "documentation" not in prompt.lower():
        raise ValueError("Shared prompt must mention documentation")
    if not controller_module.DroidController.__doc__:
        raise RuntimeError("DroidController is missing documentation")
    logger.info("documentation verified", extra={"description": description})
    return "documentation verified"


def confirm_logging_integrations(*, prompt: str, description: str) -> str:
    """Ensure logging utilities are wired for droid operations."""
    from .controller import logger as controller_logger

    if controller_logger is None:
        raise RuntimeError("Controller logger not initialised")
    logger.info("logging confirmed", extra={"description": description})
    return "logging confirmed"


def verify_real_methods(*, prompt: str, description: str) -> str:
    """Check that referenced methods exist before marking TODO complete."""
    target_module = import_module('codomyrmex.agents.droid.controller')
    required = ["DroidController", "save_config_to_file", "load_config_from_file"]
    for name in required:
        if not hasattr(target_module, name):
            raise AttributeError(f"Missing required symbol: {name}")
    logger.info("methods verified", extra={"description": description})
    return "methods verified"


def verify_readiness(*, prompt: str, description: str) -> str:
    """Check the ecosystem for autonomous readiness."""
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    required_dirs = ["src/codomyrmex", "scripts", "src/codomyrmex/tests"]

    missing = []
    for d in required_dirs:
        if not (project_root / d).exists():
            missing.append(d)

    if missing:
        raise RuntimeError(f"Missing required directories: {', '.join(missing)}")

    logger.info("Autonomous readiness verified", extra={"description": description})
    return "Autonomous readiness verified"


__all__ = [
    "ensure_documentation_exists",
    "confirm_logging_integrations",
    "verify_real_methods",
    "verify_readiness",
]
