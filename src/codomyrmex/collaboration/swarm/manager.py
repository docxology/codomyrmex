"""Swarm orchestration implementation.

Integrates pool, message bus, consensus, and decomposer into a unified
high-level swarm management interface.
"""

from __future__ import annotations

import asyncio
from typing import Any

from codomyrmex.collaboration.swarm.consensus import (
    ConsensusEngine,
    ConsensusResult,
    SwarmVote,
)
from codomyrmex.collaboration.swarm.decomposer import TaskDecomposer
from codomyrmex.collaboration.swarm.message_bus import MessageBus
from codomyrmex.collaboration.swarm.pool import AgentPool
from codomyrmex.collaboration.swarm.protocol import (
    AgentRole,
    SwarmAgent,
    SwarmMessage,
    SwarmMessageType,
    TaskAssignment,
    TaskStatus,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SwarmManager:
    """Orchestrates multi-agent swarm operations.

    The SwarmManager is the high-level entry point for the collaboration module.
    It manages the agent pool, routes messages via the bus, decomposes complex
    missions into tasks, and resolves consensus.

    Usage::

        manager = SwarmManager()
        manager.register_agent(SwarmAgent("agent-1", AgentRole.CODER))

        # Complex mission
        results = await manager.execute_mission("Add auth and tests")
    """

    def __init__(self) -> None:
        """Initialize swarm manager."""
        self.pool = AgentPool()
        self.bus = MessageBus()
        self.decomposer = TaskDecomposer()
        self.consensus_engine = ConsensusEngine()
        self._pending_results: dict[str, asyncio.Future[dict[str, Any]]] = {}

    def register_agent(self, agent: SwarmAgent) -> None:
        """Register an agent with the swarm."""
        self.pool.register(agent)

        # Subscribe manager to results from this agent
        self.bus.subscribe(
            "manager", f"results.agent.{agent.agent_id}", self._handle_result
        )

        logger.info(
            "Agent %s registered and results subscription established.", agent.agent_id
        )

    def _handle_result(self, message: SwarmMessage) -> None:
        """Handle incoming results from agents."""
        task_id = message.payload.get("task_id")
        if task_id and task_id in self._pending_results:
            future = self._pending_results.pop(task_id)
            if not future.done():
                future.set_result(message.payload.get("result", {}))
                logger.debug("Received result for task %s", task_id)

    async def execute_task(
        self, description: str, role: AgentRole = AgentRole.CODER, timeout: float = 30.0
    ) -> dict[str, Any]:
        """Execute a single task using the agent pool.

        Args:
            description: Task description.
            role: Required agent role.
            timeout: Maximum time to wait for result.

        Returns:
            The task result.

        """
        assignment = TaskAssignment(
            description=description,
            required_role=role,
        )

        try:
            agent = self.pool.assign(assignment)
            logger.info("Assigned task %s to %s", assignment.task_id, agent.agent_id)

            # Prepare for result
            future = asyncio.get_running_loop().create_future()
            self._pending_results[assignment.task_id] = future

            # Publish assignment message
            await self.bus.publish(
                f"tasks.role.{role.value}",
                SwarmMessage(
                    message_type=SwarmMessageType.TASK_ASSIGNMENT,
                    sender="manager",
                    recipient=agent.agent_id,
                    payload=assignment.to_dict(),
                ),
            )

            # Wait for result
            try:
                result = await asyncio.wait_for(future, timeout=timeout)
                assignment.status = TaskStatus.COMPLETED
                assignment.result = result
                return result
            except TimeoutError:
                logger.error("Task %s timed out after %ss", assignment.task_id, timeout)
                self._pending_results.pop(assignment.task_id, None)
                return {"status": "error", "message": "timeout"}
            finally:
                self.pool.release(agent.agent_id)

        except Exception as exc:
            logger.error("Task execution failed: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def execute_mission(self, mission: str) -> list[dict[str, Any]]:
        """Decompose and execute a complex mission.

        Args:
            mission: High-level mission description.

        Returns:
            List of results for each sub-task.

        """
        logger.info("Starting mission: %s", mission)
        subtasks = self.decomposer.decompose(mission)
        order = self.decomposer.execution_order(subtasks)

        results = []
        for st in order:
            res = await self.execute_task(st.description, st.role)
            results.append(
                {"task_id": st.task_id, "description": st.description, "result": res}
            )

        return results

    async def request_consensus(
        self, proposal: str, votes: list[SwarmVote], strategy: str = "majority"
    ) -> ConsensusResult:
        """Request a consensus decision from the swarm.

        Args:
            proposal: The proposal to vote on.
            votes: List of votes from agents.
            strategy: Voting strategy.

        Returns:
            Consensus decision.

        """
        logger.info("Requesting consensus for: %s", proposal)
        result = self.consensus_engine.resolve(votes, strategy=strategy)

        # Publish result to the swarm
        await self.bus.publish(
            "broadcast.consensus",
            SwarmMessage(
                message_type=SwarmMessageType.RESULT,
                sender="manager",
                payload={"proposal": proposal, "result": result.to_dict()},
            ),
        )

        return result

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the swarm."""
        return {
            "pool": self.pool.status(),
            "bus": {
                "subscriptions": self.bus.subscription_count,
                "history_size": self.bus.history_size,
            },
        }


__all__ = ["SwarmManager"]
