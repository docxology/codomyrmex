"""PAI awareness data mixin for DataProvider.

Extracted from data_provider.py for modularity. This mixin provides:
- get_pai_missions(): Read PAI mission definitions
- get_pai_projects(): Read PAI project definitions
- get_pai_tasks(): Parse TASKS.md for a specific project
- get_pai_telos(): Read TELOS life profile files
- get_pai_memory_overview(): Stat memory subdirectories
- get_pai_awareness_data(): Aggregate all PAI ecosystem data
"""

from __future__ import annotations

import json as _json
import re
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class PAIProviderMixin:
    """Mixin providing PAI awareness data methods."""

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
            except Exception:
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = mission_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            missions.append({
                "id": mission_dir.name,
                "title": data.get("title", mission_dir.name),
                "status": data.get("status", "unknown"),
                "priority": data.get("priority", "MEDIUM"),
                "description": data.get("description", ""),
                "success_criteria": data.get("success_criteria", []),
                "linked_projects": data.get("linked_projects", []),
                "completion_percentage": progress.get("completion_percentage", 0),
                "recent_activity": progress.get("recent_activity", []),
            })

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
            except Exception:
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = project_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            projects.append({
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
            })

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
            if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
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
            telos.append({
                "name": md_file.stem,
                "filename": md_file.name,
                "size_bytes": size,
                "preview": content[:200],
            })

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
            directories.append({
                "name": item.name,
                "file_count": file_count,
                "subdir_count": subdir_count,
            })

        # Count work sessions
        work_dir = memory_dir / "WORK"
        work_sessions_count = 0
        if work_dir.exists():
            try:
                work_sessions_count = sum(1 for d in work_dir.iterdir() if d.is_dir())
            except OSError:
                pass

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
            """Execute  Sanitize operations natively."""
            return re.sub(r"[^a-zA-Z0-9_]", "_", text)

        def _escape_label(text: str) -> str:
            """Execute  Escape Label operations natively."""
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

            for proj_ref in (mission.get("linked_projects") or []):
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
        """Aggregate all PAI ecosystem data for the awareness dashboard."""
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
            # task_counts has: completed, in_progress, remaining, blocked, optional
            # Sum all to get total (there is no 'total' key in progress.json)
            total_tasks += sum(
                tc.get(k, 0)
                for k in ("completed", "in_progress", "remaining", "blocked", "optional")
            )
            completed_tasks += tc.get("completed", 0)

        overall_completion = (
            round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
        )

        # Discover PAI skills and hooks
        skills: list[str] = []
        hooks: list[str] = []
        try:
            skills_dir = self._PAI_ROOT / "skills"
            if skills_dir.exists():
                skills = sorted(
                    d.name for d in skills_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                )
        except Exception:
            pass
        try:
            hooks_dir = self._PAI_ROOT / "hooks"
            if hooks_dir.exists():
                hooks = sorted(
                    f.stem for f in hooks_dir.iterdir()
                    if f.is_file() and not f.name.startswith(".")
                )
        except Exception:
            pass

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

    def _safe_mermaid_graph(
        self,
        missions: list[dict[str, Any]],
        projects: list[dict[str, Any]],
    ) -> str:
        """Build mermaid graph with error isolation."""
        try:
            return self._build_pai_mermaid_graph(missions, projects)
        except Exception:
            return "graph TD\n    ERR[\"Graph unavailable\"]"

