"""Paperclip REST API client for Codomyrmex agents.

HTTP client for the Paperclip server at ``localhost:3100``.
Uses only ``urllib.request`` (stdlib) — no external HTTP dependency.

See: https://github.com/paperclipai/paperclip
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from codomyrmex.agents.core.exceptions import PaperclipError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class PaperclipAPIClient:
    """HTTP client for the Paperclip REST API.

    All methods hit the Paperclip server (default ``http://localhost:3100``)
    and return parsed JSON responses.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3100",
        api_key: str | None = None,
        timeout: int = 30,
    ):
        """Initialize the API client.

        Args:
            base_url: Paperclip server URL (default ``http://localhost:3100``).
            api_key: Optional bearer token for authenticated endpoints.
            timeout: HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # Internal HTTP helpers
    # ------------------------------------------------------------------ #

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an HTTP request and return the parsed JSON response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH).
            path: URL path (e.g. ``/api/companies``).
            data: Optional JSON body for POST/PUT/PATCH.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            PaperclipError: On HTTP or connection errors.
        """
        url = f"{self.base_url}{path}"
        headers: dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body: bytes | None = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                if not raw:
                    return {"status": resp.status}
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            error_body = ""
            try:
                error_body = exc.read().decode("utf-8")
            except Exception:
                pass
            logger.error(
                "Paperclip API HTTP error: %s %s → %d",
                method,
                url,
                exc.code,
                extra={"body": error_body[:500]},
            )
            raise PaperclipError(
                f"Paperclip API error {exc.code}: {error_body[:200]}",
                command=f"{method} {path}",
                exit_code=exc.code,
            ) from exc
        except urllib.error.URLError as exc:
            logger.error(
                "Paperclip API connection error: %s %s → %s",
                method,
                url,
                exc.reason,
            )
            raise PaperclipError(
                f"Paperclip API connection error: {exc.reason}",
                command=f"{method} {path}",
            ) from exc
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Paperclip API error: %s", exc, exc_info=True)
            raise PaperclipError(
                f"Paperclip API error: {exc!s}",
                command=f"{method} {path}",
            ) from exc

    # ------------------------------------------------------------------ #
    # Health
    # ------------------------------------------------------------------ #

    def health_check(self) -> dict[str, Any]:
        """Check server health.

        Returns:
            Health status dict from the server.
        """
        return self._request("GET", "/api/health")

    # ------------------------------------------------------------------ #
    # Companies
    # ------------------------------------------------------------------ #

    def list_companies(self) -> dict[str, Any]:
        """list all companies.

        Returns:
            dict with a ``companies`` list.
        """
        return self._request("GET", "/api/companies")

    def get_company(self, company_id: str) -> dict[str, Any]:
        """Get details of a specific company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}")

    def create_company(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Create a new company.

        Args:
            name: Company name.
            **kwargs: Additional company fields (template, description, etc.).
        """
        payload: dict[str, Any] = {"name": name, **kwargs}
        return self._request("POST", "/api/companies", data=payload)

    # ------------------------------------------------------------------ #
    # Agents
    # ------------------------------------------------------------------ #

    def list_agents(self, company_id: str) -> dict[str, Any]:
        """list agents in a company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/agents")

    def get_agent(self, company_id: str, agent_id: str) -> dict[str, Any]:
        """Get details of a specific agent.

        Args:
            company_id: Company identifier.
            agent_id: Agent identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/agents/{agent_id}")

    def create_agent(
        self,
        company_id: str,
        name: str,
        role: str = "engineer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Register a new agent in a company.

        Args:
            company_id: Company identifier.
            name: Agent display name.
            role: Agent role (e.g. ``engineer``, ``ceo``, ``designer``).
            **kwargs: Additional agent fields (adapter, budget, skills, etc.).
        """
        payload: dict[str, Any] = {"name": name, "role": role, **kwargs}
        return self._request(
            "POST", f"/api/companies/{company_id}/agents", data=payload
        )

    def trigger_heartbeat(self, agent_id: str) -> dict[str, Any]:
        """Trigger a heartbeat run for an agent via the API.

        Args:
            agent_id: Agent identifier.
        """
        return self._request("POST", f"/api/agents/{agent_id}/heartbeat")

    # ------------------------------------------------------------------ #
    # Issues / Tickets
    # ------------------------------------------------------------------ #

    def list_issues(self, company_id: str) -> dict[str, Any]:
        """list issues in a company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/issues")

    def get_issue(self, company_id: str, issue_id: str) -> dict[str, Any]:
        """Get details of a specific issue.

        Args:
            company_id: Company identifier.
            issue_id: Issue identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/issues/{issue_id}")

    def create_issue(
        self,
        company_id: str,
        title: str,
        description: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new issue/ticket in a company.

        Args:
            company_id: Company identifier.
            title: Issue title.
            description: Optional issue description.
            **kwargs: Additional issue fields (assignee_id, priority, etc.).
        """
        payload: dict[str, Any] = {"title": title, **kwargs}
        if description:
            payload["description"] = description
        return self._request(
            "POST", f"/api/companies/{company_id}/issues", data=payload
        )

    # ------------------------------------------------------------------ #
    # Activity / Dashboard
    # ------------------------------------------------------------------ #

    def get_activity(self, company_id: str) -> dict[str, Any]:
        """Get the activity feed for a company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/activity")

    def get_dashboard(self, company_id: str) -> dict[str, Any]:
        """Get the dashboard summary for a company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/dashboard")

    # ------------------------------------------------------------------ #
    # Approvals
    # ------------------------------------------------------------------ #

    def list_approvals(self, company_id: str) -> dict[str, Any]:
        """list pending approvals for a company.

        Args:
            company_id: Company identifier.
        """
        return self._request("GET", f"/api/companies/{company_id}/approvals")

    def approve(self, company_id: str, approval_id: str) -> dict[str, Any]:
        """Approve a pending approval.

        Args:
            company_id: Company identifier.
            approval_id: Approval identifier.
        """
        return self._request(
            "POST",
            f"/api/companies/{company_id}/approvals/{approval_id}/approve",
        )

    def reject(self, company_id: str, approval_id: str) -> dict[str, Any]:
        """Reject a pending approval.

        Args:
            company_id: Company identifier.
            approval_id: Approval identifier.
        """
        return self._request(
            "POST",
            f"/api/companies/{company_id}/approvals/{approval_id}/reject",
        )
