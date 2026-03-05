"""Configuration for the Google Workspace CLI module."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class GWSConfig:
    """Configuration read from environment variables."""

    token: str
    credentials_file: str
    account: str
    timeout: int
    page_all: bool

    @property
    def has_token(self) -> bool:
        """Return True if a bearer token is configured."""
        return bool(self.token)

    @property
    def has_credentials(self) -> bool:
        """Return True if a credentials file path is configured."""
        return bool(self.credentials_file)

    @property
    def has_auth(self) -> bool:
        """Return True if any authentication method is configured."""
        return self.has_token or self.has_credentials


def get_config() -> GWSConfig:
    """Return a GWSConfig populated from environment variables."""
    return GWSConfig(
        token=os.getenv("GOOGLE_WORKSPACE_CLI_TOKEN", ""),
        credentials_file=os.getenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", ""),
        account=os.getenv("GOOGLE_WORKSPACE_CLI_ACCOUNT", ""),
        timeout=int(os.getenv("GWS_TIMEOUT", "60")),
        page_all=os.getenv("GWS_PAGE_ALL", "").lower() in ("1", "true"),
    )
