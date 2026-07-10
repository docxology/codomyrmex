"""Agent orchestration with optional capability-profile routing.

Provides :class:`AgentOrchestrator` — register agents, filter visible
tools by capability profile, spawn capability-scoped tasks, and build
agent-task workflows.

These were extracted from ``integration.py`` to keep each module focused.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .workflows.workflow import Workflow

logger = get_logger(__name__)

__all__ = ["AgentOrchestrator"]


class AgentOrchestrator:
    """Orchestrator for agent tasks with optional capability-profile routing.

    Args:
        capability_profile: Optional dict mapping capability names to lists of
            tool/module names that agent variants must support.  When provided,
            :meth:`spawn_agent` uses this to select only tools matching the
            requested role.
    """

    def __init__(
        self,
        capability_profile: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize agent orchestrator."""
        self._agents: dict[str, Any] = {}
        self.capability_profile = capability_profile or {}

    def register_agent(self, name: str, agent: Any):
        """Register an agent.

        Args:
            name: Agent name
            agent: Agent instance
        """
        self._agents[name] = agent

    def get_agent(self, name: str) -> Any | None:
        """Get registered agent.

        Args:
            name: Agent name

        Returns:
            Agent instance if found
        """
        return self._agents.get(name)

    @staticmethod
    def filter_tools(
        all_tools: list[str],
        profile: dict[str, list[str]],
        role: str,
    ) -> list[str]:
        """Return the subset of *all_tools* matching a capability role.

        Args:
            all_tools: Complete list of available tool names.
            profile: Capability profile mapping role → allowed tool patterns.
            role: Role key to look up in *profile*.

        Returns:
            Filtered list — or *all_tools* unchanged if *role* not in *profile*.
        """
        allowed = profile.get(role)
        if allowed is None:
            return all_tools
        return [t for t in all_tools if any(t.startswith(p) for p in allowed)]

    def spawn_agent(
        self,
        role: str,
        task: str,
        *,
        extra_kwargs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Synchronously run a capabity-scoped task using the given role.

        Resolves the allowed tool list from :attr:`capability_profile` for
        *role*, then dispatches to the first registered agent that matches, or
        falls back to a direct ``run_agent_task`` call.

        Args:
            role: Capability role (key in :attr:`capability_profile`).
            task: Task description string to pass to the agent.
            extra_kwargs: Optional additional kwargs forwarded to the agent.

        Returns:
            dict with status, role, task, and either result or error.
        """
        allowed_tools = self.filter_tools(
            list(self._agents.keys()), self.capability_profile, role
        )
        agent_name = next(
            (name for name in allowed_tools if name in self._agents),
            next(iter(self._agents), None),
        )

        if agent_name is None:
            return {
                "status": "error",
                "role": role,
                "task": task,
                "error": f"No agents registered for role '{role}'.",
            }

        agent = self._agents[agent_name]
        try:
            # Prefer synchronous callables to avoid imposing async in a
            # synchronous orchestration context.
            if callable(agent):
                result = agent(task, **(extra_kwargs or {}))
            else:
                result = {"raw": str(agent)}
            return {
                "status": "success",
                "role": role,
                "agent": agent_name,
                "result": result,
            }
        except Exception as exc:
            logger.warning("spawn_agent error for role '%s': %s", role, exc)
            return {
                "status": "error",
                "role": role,
                "agent": agent_name,
                "error": str(exc),
            }

    async def run_agent_task(
        self, agent_name: str, task: str, **kwargs
    ) -> dict[str, Any]:
        """Run a task using an agent.

        Args:
            agent_name: Name of agent to use
            task: Task to execute
            **kwargs: Task parameters

        Returns:
            Task result
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return {"success": False, "error": f"Agent '{agent_name}' not found"}

        try:
            # Try different agent interfaces
            if hasattr(agent, "execute"):
                result = await agent.execute(task, **kwargs)
            elif hasattr(agent, "run"):
                result = await agent.run(task, **kwargs)
            elif callable(agent):
                result = await agent(task, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' has no execute method",
                }

            return {"success": True, "agent": agent_name, "result": result}

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            return {"success": False, "agent": agent_name, "error": str(e)}

    def create_agent_workflow(
        self, tasks: list[dict[str, Any]], name: str = "agent_workflow"
    ) -> Workflow:
        """Create a workflow from agent tasks.

        Args:
            tasks: list of task definitions
            name: Workflow name

        Returns:
            Workflow instance
        """
        wf = Workflow(name=name)

        for task_def in tasks:
            task_name = task_def.get("name", f"task_{len(wf.tasks)}")
            agent_name = task_def.get("agent")
            task_content = task_def.get("task", "")
            dependencies = task_def.get("depends_on", [])
            task_timeout = task_def.get("timeout", 300)

            async def agent_action(
                _task_results: dict | None = None,
                _agent=agent_name,
                _task=task_content,
                _kwargs=task_def.get("kwargs", {}),
            ) -> dict[str, Any]:
                return await self.run_agent_task(_agent, _task, **_kwargs)

            wf.add_task(
                name=task_name,
                action=agent_action,
                dependencies=dependencies,
                timeout=task_timeout,
            )

        return wf
