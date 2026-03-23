"""Codomyrmex cloud/google_workspace module -- Google Workspace SDK clients.

Install SDK: uv sync --extra google_workspace
Configure:   set GWS_SERVICE_ACCOUNT_FILE or GOOGLE_APPLICATION_CREDENTIALS env var.
"""

from __future__ import annotations

from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.cloud.google_workspace.calendar import GoogleCalendarClient
from codomyrmex.cloud.google_workspace.chat import GoogleChatClient
from codomyrmex.cloud.google_workspace.docs import GoogleDocsClient
from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient
from codomyrmex.cloud.google_workspace.exceptions import (
    GoogleWorkspaceAPIError,
    GoogleWorkspaceAuthError,
    GoogleWorkspaceError,
    GoogleWorkspaceNotFoundError,
    GoogleWorkspaceQuotaError,
)
from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient
from codomyrmex.cloud.google_workspace.sheets import GoogleSheetsClient

__all__ = [
    "GoogleCalendarClient",
    "GoogleChatClient",
    "GoogleCredentials",
    "GoogleDocsClient",
    "GoogleDriveClient",
    "GoogleGmailClient",
    "GoogleSheetsClient",
    "GoogleWorkspaceAPIError",
    "GoogleWorkspaceAuthError",
    "GoogleWorkspaceBase",
    "GoogleWorkspaceError",
    "GoogleWorkspaceNotFoundError",
    "GoogleWorkspaceQuotaError",
]
