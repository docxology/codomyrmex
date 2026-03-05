"""stdlib HTTP client for the PAI Project Manager REST API."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from codomyrmex.pai_pm.exceptions import PaiPmConnectionError, PaiPmTimeoutError


class PaiPmClient:
    """Thin HTTP client for PAI PM /api/* endpoints (stdlib only, no deps)."""

    def __init__(self, base_url: str = "", timeout: int = 30) -> None:
        if not base_url:
            from codomyrmex.pai_pm.config import get_config

            cfg = get_config()
            base_url = f"http://{cfg.host}:{cfg.port}"
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # ── Internal helpers ──────────────────────────────────────────────────

    def _get(self, path: str) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise PaiPmConnectionError(
                f"PAI PM server unreachable at {url}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise PaiPmTimeoutError(f"Request to {url} timed out") from exc

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise PaiPmConnectionError(
                f"PAI PM server unreachable at {url}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise PaiPmTimeoutError(f"Request to {url} timed out") from exc

    # ── Public API ────────────────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """GET /api/health — server status and uptime."""
        return self._get("/api/health")

    def get_state(self) -> dict[str, Any]:
        """GET /api/state — full dashboard data (missions, projects, tasks)."""
        return self._get("/api/state")

    def get_awareness(self) -> dict[str, Any]:
        """GET /api/awareness — agent awareness context."""
        return self._get("/api/awareness")

    def dispatch_execute(
        self,
        action: str,
        backend: str = "",
        model: str = "",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST /api/dispatch/execute — run a dispatch action."""
        body: dict[str, Any] = {"action": action}
        if backend:
            body["backend"] = backend
        if model:
            body["model"] = model
        if context:
            body["context"] = context
        return self._post("/api/dispatch/execute", body)

    def dispatch_status(self, job_id: str) -> dict[str, Any]:
        """GET /api/dispatch/status/:job_id — check dispatch job status."""
        return self._get(f"/api/dispatch/status/{job_id}")

    def list_missions(self) -> list[dict[str, Any]]:
        """GET /api/missions — list all missions."""
        result = self._get("/api/missions")
        if isinstance(result, list):
            return result
        return result.get("missions", [])

    def list_projects(self) -> list[dict[str, Any]]:
        """GET /api/projects — list all projects."""
        result = self._get("/api/projects")
        if isinstance(result, list):
            return result
        return result.get("projects", [])

    def list_tasks(self, project_slug: str) -> list[dict[str, Any]]:
        """GET /api/projects/:slug/tasks — list tasks for a project."""
        result = self._get(f"/api/projects/{project_slug}/tasks")
        if isinstance(result, list):
            return result
        return result.get("tasks", [])
