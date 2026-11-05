"""Operator authorization for MCP tools that delegate URL handling.

The external downloader/delivery service cannot be constrained by this process's
HTTP adapter. These tools therefore require explicit per-tool host configuration
before delegating any URL. Direct Python backend APIs retain their own contracts.
"""

from __future__ import annotations

import os
from typing import Final, Literal

POLICY_ENV: Final = "CODOMYRMEX_MCP_DELEGATED_URL_TOOLS"
DELEGATED_URL_TOOLS: Final = frozenset(
    {
        "codomyrmex.video_transcribe_url",
        "codomyrmex.agentmail_create_webhook",
    }
)

PolicyErrorCode = Literal["DELEGATED_URL_DISABLED", "DELEGATED_URL_POLICY_INVALID"]


class DelegatedURLPolicyError(PermissionError):
    """A delegated URL tool lacks valid operator authorization."""

    def __init__(self, code: PolicyErrorCode) -> None:
        self.code = code
        messages = {
            "DELEGATED_URL_DISABLED": (
                "Delegated URL tool is disabled; configure "
                f"{POLICY_ENV} only for a separately contained backend"
            ),
            "DELEGATED_URL_POLICY_INVALID": (
                f"Invalid {POLICY_ENV} configuration; use unique, exact supported "
                "tool names"
            ),
        }
        super().__init__(messages[code])


def require_delegated_url_tool(tool_name: str) -> None:
    """Require an explicit per-tool operator grant, read on every invocation.

    Missing/empty configuration denies access. A nonempty list must contain only
    unique canonical names from DELEGATED_URL_TOOLS. Any malformed entry invalidates
    the complete configuration. No URL, caller argument, or tool trust hint grants
    permission, and the grant does not attest to external network containment.
    """
    if tool_name not in DELEGATED_URL_TOOLS:
        raise DelegatedURLPolicyError("DELEGATED_URL_POLICY_INVALID")
    configured = os.environ.get(POLICY_ENV, "")
    if len(configured) > 1024:
        raise DelegatedURLPolicyError("DELEGATED_URL_POLICY_INVALID")
    if not configured.strip():
        raise DelegatedURLPolicyError("DELEGATED_URL_DISABLED")
    entries = [entry.strip() for entry in configured.split(",")]
    grants = frozenset(entries)
    if len(entries) != len(grants) or not grants.issubset(DELEGATED_URL_TOOLS):
        raise DelegatedURLPolicyError("DELEGATED_URL_POLICY_INVALID")
    if tool_name not in grants:
        raise DelegatedURLPolicyError("DELEGATED_URL_DISABLED")
