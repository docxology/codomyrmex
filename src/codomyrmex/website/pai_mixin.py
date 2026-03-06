"""PAI awareness data mixin for DataProvider.

Extracted from data_provider.py for modularity. This mixin provides:
- get_pai_missions(): Read PAI mission definitions
- get_pai_projects(): Read PAI project definitions
- get_pai_tasks(): Parse TASKS.md for a specific project
- get_pai_telos(): Read TELOS life profile files
- get_pai_memory_overview(): Stat memory subdirectories
- get_pai_awareness_data(): Aggregate all PAI ecosystem data

When the PAI PM Server (scripts/pai/pm/server.ts) is running,
get_pai_awareness_data() delegates to its /api/awareness endpoint
to avoid duplicating the read logic. Falls back to direct YAML reads
when the server is not available.
"""

from __future__ import annotations

import json as _json
import os
import re
import urllib.error
import urllib.request
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# PM Server base URL — configurable via PAI_PM_PORT env var
_PM_SERVER_PORT = os.environ.get("PAI_PM_PORT", "8889")
_PM_SERVER_BASE = f"http://localhost:{_PM_SERVER_PORT}"


class PAIProviderMixin:
    """Mixin providing PAI awareness data methods."""

    def start_websocket_push(self, host: str = "0.0.0.0", port: int = 8890) -> None:
        """Start a background thread that pushes PAI awareness and health data over WebSockets every 15s.

        This replaces frontend HTTP polling with a push model.
        """
        import importlib.util

        if importlib.util.find_spec("websockets") is None:
            logger.warning("websockets library not available. WebSocket push disabled.")
            return

        import asyncio
        import threading

        self._ws_clients = set()

        async def broadcast():
            while True:
                await asyncio.sleep(15)
                if self._ws_clients:
                    try:
                        # Grab fresh data
                        awareness_data = self.get_pai_awareness_data()
                        # Health data if available on the same class
                        health_data = getattr(self, "get_health_status", dict)()

                        message = _json.dumps({
                            "type": "update",
                            "awareness": awareness_data,
                            "health": health_data
                        })

                        # Gather all sends
                        coros = [client.send(message) for client in list(self._ws_clients)]
                        if coros:
                            await asyncio.gather(*coros, return_exceptions=True)
                    except Exception as e:
                        logger.error("WebSocket broadcast error: %s", e)

        async def handler(websocket):
            import websockets
            self._ws_clients.add(websocket)
            try:
                # Send immediate initial state
                awareness_data = self.get_pai_awareness_data()
                health_data = getattr(self, "get_health_status", dict)()
                await websocket.send(_json.dumps({
                    "type": "update",
                    "awareness": awareness_data,
                    "health": health_data
                }))

                # Keep connection alive
                async for msg in websocket:
                    pass
            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                logger.debug("WebSocket client error: %s", e)
            finally:
                self._ws_clients.remove(websocket)

        async def serve():

            import websockets
            try:
                async with websockets.serve(handler, host, port):
                    logger.info("WebSocket push server running on ws://%s:%s", host, port)
                    await broadcast()
            except OSError as e:
                logger.debug("Could not start WebSocket push server on %s:%s (already in use?) - %s", host, port, e)
            except Exception as e:
                logger.error("WebSocket serve error: %s", e)

        def run_loop():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(serve())

        thread = threading.Thread(target=run_loop, daemon=True, name="PAIWebSocketPush")
        thread.start()

    def get_pai_missions(self) -> list[dict[str, Any]]:
        """Read PAI mission definitions from ~/.claude/MEMORY/STATE/missions/."""
        missions_dir = self._PAI_ROOT / "MEMORY" / "STATE" / "missions"
        if not missions_dir.exists():
            return []

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        missions: list[dict[str, Any]] = []

        for mission_dir in missions_dir.iterdir():
            if not mission_dir.is_dir():
                continue
            mission_file = mission_dir / "MISSION.yaml"
            if not mission_file.exists():
                continue
            try:
                data = yaml.safe_load(mission_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
            except Exception as e:
                logger.debug("Failed to parse mission YAML %s: %s", mission_file, e)
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = mission_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.debug(
                        "Failed to parse progress.json for mission %s: %s",
                        mission_dir.name,
                        e,
                    )

            missions.append(
                {
                    "id": mission_dir.name,
                    "title": data.get("title", mission_dir.name),
                    "status": data.get("status", "unknown"),
                    "priority": data.get("priority", "MEDIUM"),
                    "description": data.get("description", ""),
                    "success_criteria": data.get("success_criteria", []),
                    "linked_projects": data.get("linked_projects", []),
                    "completion_percentage": progress.get("completion_percentage", 0),
                    "recent_activity": progress.get("recent_activity", []),
                }
            )

        missions.sort(key=lambda m: priority_order.get(m["priority"], 99))
        return missions

    def get_pai_projects(self) -> list[dict[str, Any]]:
        """Read PAI project definitions from ~/.claude/MEMORY/STATE/projects/."""
        projects_dir = self._PAI_ROOT / "MEMORY" / "STATE" / "projects"
        if not projects_dir.exists():
            return []

        projects: list[dict[str, Any]] = []

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            project_file = project_dir / "PROJECT.yaml"
            if not project_file.exists():
                continue
            try:
                data = yaml.safe_load(project_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
            except Exception as e:
                logger.debug("Failed to parse project YAML %s: %s", project_file, e)
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = project_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception as e:
                    logger.debug(
                        "Failed to parse progress.json for project %s: %s",
                        project_dir.name,
                        e,
                    )

            projects.append(
                {
                    "id": project_dir.name,
                    "title": data.get("title", project_dir.name),
                    "status": data.get("status", "unknown"),
                    "goal": data.get("goal", ""),
                    "priority": data.get("priority", "MEDIUM"),
                    "parent_mission": data.get("parent_mission", ""),
                    "tags": data.get("tags", []),
                    "completion_percentage": progress.get("completion_percentage", 0),
                    "task_counts": progress.get("task_counts", {}),
                    "recent_activity": progress.get("recent_activity", []),
                }
            )

        projects.sort(key=lambda p: (p["parent_mission"], p["title"]))
        return projects

    def get_pai_tasks(self, project_id: str) -> dict[str, Any]:
        """Parse TASKS.md for a specific PAI project.

        Raises ValueError for path traversal attempts.
        """
        if ".." in project_id or "/" in project_id:
            raise ValueError("Invalid project_id")

        tasks_file = (
            self._PAI_ROOT / "MEMORY" / "STATE" / "projects" / project_id / "TASKS.md"
        )
        if not tasks_file.exists():
            return {}

        try:
            content = tasks_file.read_text(encoding="utf-8")
        except Exception:
            return {}

        completed: list[str] = []
        remaining: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith(("- [x]", "- [X]")):
                completed.append(stripped[5:].strip())
            elif stripped.startswith("- [ ]"):
                remaining.append(stripped[5:].strip())

        return {
            "completed": completed,
            "remaining": remaining,
            "total": len(completed) + len(remaining),
            "done": len(completed),
        }

    def get_pai_telos(self) -> list[dict[str, Any]]:
        """Read TELOS life profile files from ~/.claude/skills/PAI/USER/TELOS/."""
        telos_dir = self._PAI_ROOT / "skills" / "PAI" / "USER" / "TELOS"
        if not telos_dir.exists():
            return []

        telos: list[dict[str, Any]] = []
        for md_file in telos_dir.iterdir():
            if not md_file.is_file() or md_file.suffix != ".md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                size = md_file.stat().st_size
            except Exception:
                content = ""
                size = 0
            telos.append(
                {
                    "name": md_file.stem,
                    "filename": md_file.name,
                    "size_bytes": size,
                    "preview": content[:200],
                }
            )

        telos.sort(key=lambda t: t["name"])
        return telos

    def get_pai_memory_overview(self) -> dict[str, Any]:
        """Stat ~/.claude/MEMORY/ subdirectories for counts."""
        memory_dir = self._PAI_ROOT / "MEMORY"
        if not memory_dir.exists():
            return {"directories": [], "total_files": 0, "work_sessions_count": 0}

        directories: list[dict[str, Any]] = []
        total_files = 0

        try:
            items = sorted(memory_dir.iterdir())
        except OSError:
            items = []

        for item in items:
            if not item.is_dir():
                total_files += 1
                continue
            try:
                file_count = sum(1 for f in item.rglob("*") if f.is_file())
                subdir_count = sum(1 for d in item.iterdir() if d.is_dir())
            except OSError:
                file_count = 0
                subdir_count = 0
            total_files += file_count
            directories.append(
                {
                    "name": item.name,
                    "file_count": file_count,
                    "subdir_count": subdir_count,
                }
            )

        # Count work sessions
        work_dir = memory_dir / "WORK"
        work_sessions_count = 0
        if work_dir.exists():
            try:
                work_sessions_count = sum(1 for d in work_dir.iterdir() if d.is_dir())
            except OSError as e:
                logger.debug("Failed to count work sessions in %s: %s", work_dir, e)

        return {
            "directories": directories,
            "total_files": total_files,
            "work_sessions_count": work_sessions_count,
        }

    def _build_pai_mermaid_graph(
        self,
        missions: list[dict[str, Any]],
        projects: list[dict[str, Any]],
    ) -> str:
        """Generate a Mermaid graph TD string from mission→project hierarchy."""

        def _sanitize(text: str) -> str:
            """Sanitize."""
            return re.sub(r"[^a-zA-Z0-9_]", "_", text)

        def _escape_label(text: str) -> str:
            return text.replace('"', "'").replace("<", "").replace(">", "")

        lines = ["graph TD"]

        # classDef for status-based styling
        lines.append("    classDef active fill:#10b981,stroke:#059669,color:#fff")
        lines.append("    classDef paused fill:#f59e0b,stroke:#d97706,color:#fff")
        lines.append("    classDef completed fill:#6b7280,stroke:#4b5563,color:#fff")
        lines.append("    classDef in_progress fill:#3b82f6,stroke:#2563eb,color:#fff")
        lines.append("    classDef blocked fill:#ef4444,stroke:#dc2626,color:#fff")
        lines.append("    classDef unknown fill:#94a3b8,stroke:#64748b,color:#fff")

        linked_project_ids: set[str] = set()

        for mission in missions:
            m_id = "M_" + _sanitize(mission.get("id", "unknown"))
            m_label = _escape_label(mission.get("title", "Untitled"))
            lines.append(f'    {m_id}["{m_label}"]')
            status_class = _sanitize(mission.get("status", "unknown"))
            lines.append(f"    class {m_id} {status_class}")

            for proj_ref in mission.get("linked_projects") or []:
                p_id = "P_" + _sanitize(str(proj_ref))
                linked_project_ids.add(str(proj_ref))
                lines.append(f"    {m_id} --> {p_id}")

        for project in projects:
            p_id = "P_" + _sanitize(project.get("id", "unknown"))
            p_label = _escape_label(project.get("title", "Untitled"))
            lines.append(f'    {p_id}["{p_label}"]')
            status_class = _sanitize(project.get("status", "unknown"))
            lines.append(f"    class {p_id} {status_class}")

            # If it has a parent_mission but wasn't linked from mission side, add edge
            parent = project.get("parent_mission")
            if parent and project["id"] not in linked_project_ids:
                pm_id = "M_" + _sanitize(str(parent))
                lines.append(f"    {pm_id} --> {p_id}")

        return "\n".join(lines)

    def get_pai_awareness_data(self) -> dict[str, Any]:
        """Aggregate all PAI ecosystem data for the awareness dashboard.

        When the PAI PM Server is running (default port 8889), delegates to its
        /api/awareness endpoint for a single source of truth. Falls back to
        direct YAML reads when the server is not available.
        """
        # ── HTTP-first: try PMServer /api/awareness ──
        try:
            req = urllib.request.Request(
                f"{_PM_SERVER_BASE}/api/awareness",
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    server_data = _json.loads(resp.read().decode("utf-8"))
                    # Augment with skills/hooks that only Python-side can discover
                    if "skills" not in server_data:
                        server_data["skills"] = self._discover_skills()
                    if "hooks" not in server_data:
                        server_data["hooks"] = self._discover_hooks()
                    if "metrics" in server_data:
                        server_data["metrics"]["skill_count"] = len(
                            server_data.get("skills", [])
                        )
                        server_data["metrics"]["hook_count"] = len(
                            server_data.get("hooks", [])
                        )
                    logger.debug(
                        "PAI awareness data fetched from PMServer at %s",
                        _PM_SERVER_BASE,
                    )
                    return server_data
        except (
            urllib.error.URLError,
            OSError,
            _json.JSONDecodeError,
            TimeoutError,
        ) as e:
            logger.debug("PMServer not available, falling back to YAML: %s", e)

        # ── Fallback: direct YAML reads (offline mode) ──
        try:
            missions = self.get_pai_missions()
        except Exception:
            missions = []
        try:
            projects = self.get_pai_projects()
        except Exception:
            projects = []
        try:
            telos = self.get_pai_telos()
        except Exception:
            telos = []
        try:
            memory = self.get_pai_memory_overview()
        except Exception:
            memory = {"directories": [], "total_files": 0, "work_sessions_count": 0}

        total_tasks = 0
        completed_tasks = 0
        for project in projects:
            tc = project.get("task_counts", {})
            total_tasks += sum(
                tc.get(k, 0)
                for k in (
                    "completed",
                    "in_progress",
                    "remaining",
                    "blocked",
                    "optional",
                )
            )
            completed_tasks += tc.get("completed", 0)

        overall_completion = (
            round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
        )

        skills = self._discover_skills()
        hooks = self._discover_hooks()

        return {
            "missions": missions,
            "projects": projects,
            "telos": telos,
            "memory": memory,
            "skills": skills,
            "hooks": hooks,
            "metrics": {
                "mission_count": len(missions),
                "project_count": len(projects),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "telos_files": len(telos),
                "overall_completion": overall_completion,
                "skill_count": len(skills),
                "hook_count": len(hooks),
            },
            "mermaid_graph": self._safe_mermaid_graph(missions, projects),
        }

    def _discover_skills(self) -> list[str]:
        """Discover PAI skill directories."""
        try:
            skills_dir = self._PAI_ROOT / "skills"
            if skills_dir.exists():
                return sorted(
                    d.name
                    for d in skills_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                )
        except Exception as e:
            logger.debug("Failed to discover PAI skills: %s", e)
        return []

    def _discover_hooks(self) -> list[str]:
        """Discover PAI hook files."""
        try:
            hooks_dir = self._PAI_ROOT / "hooks"
            if hooks_dir.exists():
                return sorted(
                    f.stem
                    for f in hooks_dir.iterdir()
                    if f.is_file() and not f.name.startswith(".")
                )
        except Exception as e:
            logger.debug("Failed to discover PAI hooks: %s", e)
        return []

    def _safe_mermaid_graph(
        self,
        missions: list[dict[str, Any]],
        projects: list[dict[str, Any]],
    ) -> str:
        """Build mermaid graph with error isolation."""
        try:
            return self._build_pai_mermaid_graph(missions, projects)
        except Exception:
            return 'graph TD\n    ERR["Graph unavailable"]'
