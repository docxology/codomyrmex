#!/usr/bin/env python3
"""
Agents - Real Usage Examples

Demonstrates actual agent capabilities:
- Agent client interfaces
- Orchestrator stubs
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError as exc:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

# The agents package's dependencies (e.g. aiohttp) are core project
# dependencies, so an ImportError here means a broken environment and must surface.
from codomyrmex.agents import (
    AgentCapabilities,
    AgentOrchestrator,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


# 1. Define a Mock Agent for demonstration (to avoid requiring real API keys in example)
class DemoAgent(BaseAgent):
    def __init__(self, name="demo_agent"):
        super().__init__(name=name, capabilities=[AgentCapabilities.TEXT_COMPLETION])

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        self.logger.info(
            f"Agent {self.name} processing prompt: {request.prompt[:20]}..."
        )
        return AgentResponse(
            content=f"Response from {self.name} for: {request.prompt}",
            metadata={"agent": self.name},
        )


def main():
    setup_logging()
    print_info("Running Agents Examples...")

    # 1. Orchestrator and Client Usage
    print_info("Initializing real AgentOrchestrator with demo agents...")
    agent_a = DemoAgent(name="Agent_A")
    agent_b = DemoAgent(name="Agent_B")

    orchestrator = AgentOrchestrator(agents=[agent_a, agent_b])

    request = AgentRequest(prompt="What is the capital of France?")

    # 2. Parallel Execution
    print_info("Executing request in parallel across orchestrated agents...")
    responses = orchestrator.execute_parallel(request)

    for resp in responses:
        if resp.is_success():
            print_success(
                f"  {resp.metadata.get('agent', 'Unknown agent')}: {resp.content}"
            )
        else:
            print_error(f"  Agent failed: {resp.error}")

    # 3. Fallback Execution
    print_info("Executing with fallback strategy...")
    fallback_response = orchestrator.execute_with_fallback(request)
    print_success(f"  Fallback Result: {fallback_response.content}")

    print_success("Agents examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
