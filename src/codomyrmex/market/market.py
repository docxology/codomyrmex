"""
Market Module

Reverse Auction and Demand Aggregation
"""

from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class Market:
    """
    Multi-agent marketplace coordinator.

    Orchestrates task allocation between agents using reverse auctions
    and demand aggregation. Agents can post tasks, bid on work, and
    the market finds optimal allocations.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Market.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._tasks: dict[str, dict[str, Any]] = {}
        self._agents: dict[str, dict[str, Any]] = {}
        self._allocations: list[dict[str, Any]] = []
        logger.info("Market initialized")

    def register_agent(self, agent_id: str, capabilities: list[str], max_concurrent: int = 3) -> None:
        """Register an agent with its capabilities."""
        self._agents[agent_id] = {
            "id": agent_id,
            "capabilities": set(capabilities),
            "max_concurrent": max_concurrent,
            "active_tasks": 0,
        }
        logger.info(f"Agent {agent_id} registered with {len(capabilities)} capabilities")

    def post_task(self, task_id: str, required_capabilities: list[str],
                  priority: int = 0, metadata: dict[str, Any] | None = None) -> None:
        """Post a task to the marketplace for agent allocation."""
        self._tasks[task_id] = {
            "id": task_id,
            "required": set(required_capabilities),
            "priority": priority,
            "metadata": metadata or {},
            "status": "open",
            "assigned_to": None,
        }
        logger.debug(f"Task {task_id} posted with priority {priority}")

    def process(self, data: Any = None) -> dict[str, Any]:
        """
        Run allocation matching: assign open tasks to capable agents.

        Uses greedy allocation by priority: highest-priority tasks get
        first pick of capable agents with available capacity.

        Args:
            data: Optional additional context (unused, kept for interface compatibility)

        Returns:
            Allocation results with matched task-agent pairs.
        """
        open_tasks = sorted(
            [t for t in self._tasks.values() if t["status"] == "open"],
            key=lambda t: t["priority"],
            reverse=True,
        )

        new_allocations = []
        for task in open_tasks:
            best_agent = None
            best_score = -1

            for agent in self._agents.values():
                if agent["active_tasks"] >= agent["max_concurrent"]:
                    continue
                overlap = len(task["required"] & agent["capabilities"])
                if overlap == 0:
                    continue
                score = overlap / len(task["required"]) if task["required"] else 0
                if score > best_score:
                    best_score = score
                    best_agent = agent

            if best_agent:
                allocation = {
                    "task_id": task["id"],
                    "agent_id": best_agent["id"],
                    "match_score": best_score,
                }
                new_allocations.append(allocation)
                task["status"] = "assigned"
                task["assigned_to"] = best_agent["id"]
                best_agent["active_tasks"] += 1

        self._allocations.extend(new_allocations)
        logger.info(f"Allocated {len(new_allocations)} tasks to agents")

        return {
            "allocated": len(new_allocations),
            "unallocated": len([t for t in self._tasks.values() if t["status"] == "open"]),
            "allocations": new_allocations,
        }

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed, freeing the agent's capacity."""
        task = self._tasks.get(task_id)
        if not task or task["status"] != "assigned":
            return False
        agent = self._agents.get(task["assigned_to"], {})
        if agent:
            agent["active_tasks"] = max(0, agent.get("active_tasks", 1) - 1)
        task["status"] = "completed"
        return True

    def get_stats(self) -> dict[str, Any]:
        """Get marketplace statistics."""
        return {
            "total_agents": len(self._agents),
            "total_tasks": len(self._tasks),
            "open_tasks": len([t for t in self._tasks.values() if t["status"] == "open"]),
            "assigned_tasks": len([t for t in self._tasks.values() if t["status"] == "assigned"]),
            "completed_tasks": len([t for t in self._tasks.values() if t["status"] == "completed"]),
            "total_allocations": len(self._allocations),
        }


# Convenience function
def create_market(config: dict[str, Any] | None = None) -> Market:
    """
    Create a new Market instance.

    Args:
        config: Optional configuration

    Returns:
        Market instance
    """
    return Market(config)
