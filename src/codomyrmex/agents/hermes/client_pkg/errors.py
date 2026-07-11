"""Hermes client exceptions and auto-heal allowlist."""

from __future__ import annotations

from codomyrmex.agents.core.exceptions import AgentError

AUTO_HEAL_ALLOWLIST: set[str] = {
    "requests",
    "numpy",
    "pandas",
    "httpx",
    "pydantic",
    "rich",
    "click",
    "psutil",
    "pillow",
    "cryptography",
    "pyyaml",
    "toml",
    "jinja2",
    "sqlalchemy",
    "redis",
    "celery",
    "fastapi",
    "uvicorn",
    "gunicorn",
    "flask",
    "boto3",
    "paramiko",
    "websockets",
    "aiohttp",
    "beautifulsoup4",
    "lxml",
}


class HermesError(AgentError):
    """Exception raised when Hermes execution fails."""

    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class AutoRetryException(Exception):
    """Exception raised internally to trigger the autonomous error-correction loop."""


__all__ = ["AUTO_HEAL_ALLOWLIST", "AutoRetryException", "HermesError"]
