"""Python client for the Mission Control agent orchestration dashboard.

Communicates with the builderz-labs/mission-control REST API using
stdlib ``urllib.request`` — zero external dependencies.

See: https://github.com/builderz-labs/mission-control
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class MissionControlError(Exception):
    """Raised when a Mission Control operation fails."""


@dataclass
class MissionControlConfig:
    """Configuration for the Mission Control client.

    Attributes:
        base_url: Dashboard base URL (default ``http://localhost:3000``).
        api_key: API key for ``x-api-key`` header authentication.
        auth_user: Login username for session authentication.
        auth_pass: Login password for session authentication.
        app_path: Absolute path to the mission-control git submodule.
        timeout: HTTP request timeout in seconds.
    """

    base_url: str = "http://localhost:3000"
    api_key: str = ""
    auth_user: str = "admin"
    auth_pass: str = ""
    app_path: str = ""
    timeout: int = 30

    def __post_init__(self) -> None:
        """Resolve defaults from environment variables and paths."""
        if not self.api_key:
            self.api_key = os.environ.get("MC_API_KEY", "")
        if not self.auth_pass:
            self.auth_pass = os.environ.get("MC_AUTH_PASS", "")
        if not self.app_path:
            self.app_path = str(
                Path(__file__).parent / "app"
            )
        # Strip trailing slash from base_url
        self.base_url = self.base_url.rstrip("/")


class MissionControlClient:
    """HTTP client for the Mission Control REST API.

    Provides methods for agent management, task orchestration, and
    server lifecycle control.

    Example::

        client = MissionControlClient()
        if client.is_running():
            agents = client.list_agents()
            print(f"Registered agents: {len(agents)}")
    """

    def __init__(
        self,
        config: MissionControlConfig | dict[str, Any] | None = None,
    ) -> None:
        """Initialize the Mission Control client.

        Args:
            config: Configuration object, dict of overrides, or None
                for defaults.
        """
        if config is None:
            self._config = MissionControlConfig()
        elif isinstance(config, dict):
            self._config = MissionControlConfig(**config)
        else:
            self._config = config

        self._session_cookie: str | None = None
        self._server_process: subprocess.Popen[bytes] | None = None

    @property
    def base_url(self) -> str:
        """Dashboard base URL."""
        return self._config.base_url

    @property
    def app_path(self) -> str:
        """Path to the mission-control app directory."""
        return self._config.app_path

    # ── HTTP helpers ─────────────────────────────────────────────

    def _build_headers(self) -> dict[str, str]:
        """Build authentication headers for API requests."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._config.api_key:
            headers["x-api-key"] = self._config.api_key
        if self._session_cookie:
            headers["Cookie"] = self._session_cookie
        return headers

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Mission Control API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path (e.g. ``/api/agents``).
            data: Optional JSON body.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            MissionControlError: On HTTP errors or connectivity issues.
        """
        url = f"{self._config.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data else None

        req = urllib.request.Request(
            url,
            data=body,
            headers=self._build_headers(),
            method=method,
        )

        try:
            with urllib.request.urlopen(
                req, timeout=self._config.timeout
            ) as resp:
                # Capture session cookie if present
                set_cookie = resp.headers.get("Set-Cookie", "")
                if "mc-session" in set_cookie:
                    self._session_cookie = set_cookie.split(";")[0]

                raw = resp.read().decode("utf-8")
                if not raw:
                    return {"status": "success"}
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise MissionControlError(
                f"HTTP {exc.code} {exc.reason} on {method} {path}: {body_text}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MissionControlError(
                f"Connection failed for {method} {path}: {exc.reason}"
            ) from exc
        except Exception as exc:
            raise MissionControlError(
                f"Request failed for {method} {path}: {exc}"
            ) from exc

    # ── Authentication ───────────────────────────────────────────

    def login(self) -> dict[str, Any]:
        """Authenticate with the dashboard and store the session cookie.

        Returns:
            Login response dict.

        Raises:
            MissionControlError: On auth failure.
        """
        return self._request("POST", "/api/auth/login", {
            "username": self._config.auth_user,
            "password": self._config.auth_pass,
        })

    # ── Status ───────────────────────────────────────────────────

    def is_running(self) -> bool:
        """Check if the Mission Control dashboard is reachable.

        Returns:
            True if the dashboard responds, False otherwise.
        """
        try:
            self._request("GET", "/api/auth/me")
            return True
        except MissionControlError:
            return False

    def status(self) -> dict[str, Any]:
        """Get dashboard status and current user info.

        Returns:
            Status dict with ``running`` flag and user info.
        """
        try:
            user_info = self._request("GET", "/api/auth/me")
            return {"running": True, "user": user_info}
        except MissionControlError as exc:
            return {"running": False, "error": str(exc)}

    # ── Agent Management ─────────────────────────────────────────

    def list_agents(self) -> list[dict[str, Any]]:
        """List all registered agents.

        Returns:
            List of agent dicts.
        """
        result = self._request("GET", "/api/agents")
        if isinstance(result, list):
            return result
        return result.get("agents", [])

    def register_agent(
        self,
        name: str,
        model: str = "claude-sonnet-4-20250514",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Register a new agent with Mission Control.

        Args:
            name: Agent display name.
            model: Model identifier.
            **kwargs: Additional agent properties.

        Returns:
            Created agent dict.
        """
        payload = {"name": name, "model": model, **kwargs}
        return self._request("POST", "/api/agents/register", payload)

    # ── Task Management ──────────────────────────────────────────

    def list_tasks(
        self,
        status: str | None = None,
        assigned_to: str | None = None,
        priority: str | None = None,
    ) -> list[dict[str, Any]]:
        """List tasks with optional filters.

        Args:
            status: Filter by task status (inbox, assigned, in_progress,
                review, quality_review, done).
            assigned_to: Filter by assignee.
            priority: Filter by priority level.

        Returns:
            List of task dicts.
        """
        params: list[str] = []
        if status:
            params.append(f"status={status}")
        if assigned_to:
            params.append(f"assigned_to={assigned_to}")
        if priority:
            params.append(f"priority={priority}")

        path = "/api/tasks"
        if params:
            path += "?" + "&".join(params)

        result = self._request("GET", path)
        if isinstance(result, list):
            return result
        return result.get("tasks", [])

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Get task details by ID.

        Args:
            task_id: Task identifier.

        Returns:
            Task detail dict.
        """
        return self._request("GET", f"/api/tasks/{task_id}")

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        assigned_to: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new task on the Kanban board.

        Args:
            title: Task title.
            description: Task description.
            priority: Priority level (low, medium, high, critical).
            assigned_to: Agent ID to assign the task to.
            **kwargs: Additional task properties.

        Returns:
            Created task dict.
        """
        payload: dict[str, Any] = {
            "title": title,
            "description": description,
            "priority": priority,
            **kwargs,
        }
        if assigned_to:
            payload["assigned_to"] = assigned_to
        return self._request("POST", "/api/tasks", payload)

    def update_task(
        self,
        task_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update an existing task.

        Args:
            task_id: Task identifier.
            **kwargs: Fields to update (title, description, status,
                priority, assigned_to, etc.).

        Returns:
            Updated task dict.
        """
        return self._request("PUT", f"/api/tasks/{task_id}", kwargs)

    def delete_task(self, task_id: str) -> dict[str, Any]:
        """Delete a task by ID.

        Args:
            task_id: Task identifier.

        Returns:
            Deletion confirmation dict.
        """
        return self._request("DELETE", f"/api/tasks/{task_id}")

    # ── Task Comments ────────────────────────────────────────────

    def list_comments(self, task_id: str) -> list[dict[str, Any]]:
        """List comments on a task.

        Args:
            task_id: Task identifier.

        Returns:
            List of comment dicts.
        """
        result = self._request("GET", f"/api/tasks/{task_id}/comments")
        if isinstance(result, list):
            return result
        return result.get("comments", [])

    def add_comment(
        self,
        task_id: str,
        content: str,
        author: str = "codomyrmex",
    ) -> dict[str, Any]:
        """Add a comment to a task.

        Args:
            task_id: Task identifier.
            content: Comment text.
            author: Comment author name.

        Returns:
            Created comment dict.
        """
        return self._request(
            "POST",
            f"/api/tasks/{task_id}/comments",
            {"content": content, "author": author},
        )

    # ── Server Lifecycle ─────────────────────────────────────────

    def start_server(self) -> dict[str, Any]:
        """Start the Mission Control dev server.

        Runs ``pnpm dev`` in the app directory as a background process.

        Returns:
            Dict with ``pid`` and ``status``.

        Raises:
            MissionControlError: If the app path doesn't exist or
                pnpm is not available.
        """
        app_dir = Path(self._config.app_path)
        if not app_dir.exists():
            raise MissionControlError(
                f"Mission Control app directory not found: {app_dir}"
            )

        package_json = app_dir / "package.json"
        if not package_json.exists():
            raise MissionControlError(
                f"No package.json found in {app_dir}. "
                "Run 'git submodule update --init' first."
            )

        if self._server_process and self._server_process.poll() is None:
            return {
                "status": "already_running",
                "pid": self._server_process.pid,
            }

        try:
            self._server_process = subprocess.Popen(
                ["pnpm", "dev"],
                cwd=str(app_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            return {
                "status": "started",
                "pid": self._server_process.pid,
            }
        except FileNotFoundError:
            raise MissionControlError(
                "pnpm not found. Install it: npm install -g pnpm"
            )
        except Exception as exc:
            raise MissionControlError(
                f"Failed to start server: {exc}"
            ) from exc

    def stop_server(self) -> dict[str, Any]:
        """Stop the running Mission Control dev server.

        Returns:
            Dict with ``status`` and ``pid``.
        """
        if not self._server_process:
            return {"status": "not_running"}

        if self._server_process.poll() is not None:
            self._server_process = None
            return {"status": "already_stopped"}

        try:
            # Send SIGTERM to the process group
            os.killpg(
                os.getpgid(self._server_process.pid), signal.SIGTERM
            )
            self._server_process.wait(timeout=10)
            pid = self._server_process.pid
            self._server_process = None
            return {"status": "stopped", "pid": pid}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
