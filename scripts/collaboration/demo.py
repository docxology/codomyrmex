#!/usr/bin/env python3
"""Thin orchestrator demo for the collaboration module.

This script demonstrates a complete multi-agent workflow using the
consolidated SwarmManager, including task decomposition, role-based
assignment, and async result reporting.

Usage:
    python demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.collaboration import (
    AgentRole,
    SwarmAgent,
    SwarmManager,
    SwarmMessage,
    SwarmMessageType,
    Vote,
)


class SimulatedAgent:
    """A helper to simulate a real agent reacting to messages."""

    def __init__(self, manager: SwarmManager, agent_id: str, role: AgentRole):
        self.manager = manager
        self.agent_id = agent_id
        self.role = role
        # Subscribe to tasks for this role
        self.manager.bus.subscribe(
            self.agent_id, f"tasks.role.{self.role.value}", self.on_task
        )

    async def on_task(self, message: SwarmMessage):
        if (
            message.message_type == SwarmMessageType.TASK_ASSIGNMENT
            and message.recipient == self.agent_id
        ):
            task_id = message.payload["task_id"]
            desc = message.payload["description"]
            print(f"  [Agent {self.agent_id}] Processing: {desc}")

            # Simulate work
            await asyncio.sleep(0.1)

            # Send result back
            await self.manager.bus.publish(
                f"results.agent.{self.agent_id}",
                SwarmMessage(
                    message_type=SwarmMessageType.RESULT,
                    sender=self.agent_id,
                    payload={
                        "task_id": task_id,
                        "result": {
                            "status": "success",
                            "output": f"Completed by {self.role.value}",
                        },
                    },
                ),
            )


async def run_demo():
    print("=== Codomyrmex Collaboration Demo ===")

    # 1. Initialize Swarm Manager
    manager = SwarmManager()
    print("[1] Swarm Manager initialized.")

    # 2. Register specialized agents and start their simulation
    agents = [
        ("architect-01", AgentRole.ARCHITECT),
        ("coder-01", AgentRole.CODER),
        ("tester-01", AgentRole.TESTER),
    ]

    sim_agents = []
    for aid, role in agents:
        manager.register_agent(SwarmAgent(aid, role))
        sim_agents.append(SimulatedAgent(manager, aid, role))

    print(f"[2] Registered {manager.pool.size} agents with different roles.")

    # 3. Execute a complex mission
    mission = "Design and implement a secure login system with unit tests"
    print(f"\n[3] Starting mission: '{mission}'")

    # Short timeout for demo
    results = await manager.execute_mission(mission)

    print("\n--- Mission Results ---")
    for i, res in enumerate(results, 1):
        print(f"  Step {i}: {res['description']}")
        print(
            f"  Result: {res['result'].get('status')} - {res['result'].get('output')}"
        )

    # 4. Request consensus on the final output
    print("\n[4] Requesting consensus on deployment...")
    votes = [
        Vote("architect-01", True, reason="Architecture is sound"),
        Vote("coder-01", True, reason="Implementation matches spec"),
        Vote("tester-01", False, reason="Security audit still pending"),
    ]

    consensus = await manager.request_consensus(
        "Deploy to production", votes, strategy="majority"
    )
    print("  Proposal: Deploy to production")
    print(f"  Decision: {consensus.decision.value}")
    print(f"  Approval Score: {consensus.approval_score:.2f}")

    # 5. Check final status
    print("\n[5] Swarm Status:")
    status = manager.get_status()
    print(
        f"  Agents: {status['pool']['total']} total, {status['pool']['available']} available"
    )
    print(f"  Message Bus: {status['bus']['history_size']} messages in history")

    print("\n=== Demo Complete ===")

    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "collaboration"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/collaboration/config.yaml")


if __name__ == "__main__":
    asyncio.run(run_demo())
