
"""
Agent Orchestration Demo
========================

Demonstrates advanced multi-agent orchestration patterns using codomyrmex.

Features showcased:
1. Parallel execution (newly upgraded with ThreadPoolExecutor)
2. Sequential execution
3. Fallback strategies (Circuit Breaker pattern)

Run with:
    uv run python src/codomyrmex/examples/agent_orchestration_demo.py
"""

import random
import time
from collections.abc import Iterator

from codomyrmex.agents import (
    AgentCapabilities,
    AgentInterface,
    AgentOrchestrator,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.logging_monitoring import get_logger, setup_logging

logger = get_logger(__name__)

class SimulatedAgent(AgentInterface):
    """A simulated agent with configurable delay and failure rate."""

    def __init__(self, name: str, delay: float = 0.5, failure_rate: float = 0.0):
        super().__init__()
        self.name = name
        self.delay = delay
        self.failure_rate = failure_rate
        self.capabilities = [AgentCapabilities.TEXT_COMPLETION]

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the operation."""
        logger.info(f"[{self.name}] Received request: {request.prompt[:20]}...")

        # Simulate work
        time.sleep(self.delay)

        # Simulate failure
        if random.random() < self.failure_rate:
            error_msg = f"[{self.name}] Simulated failure!"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        response_content = f"[{self.name}] Processed: {request.prompt}"
        logger.info(f"[{self.name}] Finished processing")

        return AgentResponse(
            content=response_content,
            metadata={"agent": self.name, "latency": self.delay}
        )

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """stream ."""
        yield f"[{self.name}] Stream chunk 1"
        yield f"[{self.name}] Stream chunk 2"

    def setup(self) -> None:
        """Configure and prepare this instance for use."""
        return None  # Demo agent — no setup needed

    def test_connection(self) -> bool:
        return True

    def get_capabilities(self):
        """Return a dictionary of supported capabilities."""
        return self.capabilities

    def supports_capability(self, capability):
        return capability in self.capabilities


def main():
    """main ."""
    setup_logging()

    logger.info("Initializing agents...")

    # 1. Fast agents (for parallel demo)
    agent_a = SimulatedAgent("Agent A (Fast)", delay=1.0)
    agent_b = SimulatedAgent("Agent B (Fast)", delay=1.0)
    agent_c = SimulatedAgent("Agent C (Fast)", delay=1.0)

    # 2. Slow/Failing agents (for fallback demo)
    agent_unreliable = SimulatedAgent("Agent D (Unreliable)", delay=0.5, failure_rate=1.0)
    agent_reliable = SimulatedAgent("Agent E (Reliable)", delay=0.5, failure_rate=0.0)

    orchestrator = AgentOrchestrator([agent_a, agent_b, agent_c])

    req = AgentRequest(prompt="Analyze this code block.")

    # --- Parallel Execution Demo ---
    print("\n" + "="*50)
    print("DEMO 1: Parallel Execution")
    print("Expected: All 3 agents finish in ~1.0s (not 3.0s)")
    print("="*50)

    start_time = time.perf_counter()
    responses = orchestrator.execute_parallel(req, agents=[agent_a, agent_b, agent_c])
    duration = time.perf_counter() - start_time

    print(f"\nParallel execution took: {duration:.2f}s")
    for r in responses:
        if r:
            print(f"Result: {r.content}")

    # --- Sequential Execution Demo ---
    print("\n" + "="*50)
    print("DEMO 2: Sequential Execution")
    print("Expected: Agents finish one by one ~2.0s total")
    print("="*50)

    start_time = time.perf_counter()
    responses = orchestrator.execute_sequential(req, agents=[agent_a, agent_b])
    duration = time.perf_counter() - start_time

    print(f"\nSequential execution took: {duration:.2f}s")

    # --- Fallback Demo ---
    print("\n" + "="*50)
    print("DEMO 3: Fallback Strategy")
    print("Expected: First agent fails, second agent succeeds")
    print("="*50)

    orchestrator_fallback = AgentOrchestrator([agent_unreliable, agent_reliable])

    response = orchestrator_fallback.execute_with_fallback(req)

    if response.is_success():
        print(f"\nFallback success! Result from: {response.content}")
    else:
        print("\nFallback failed!")

if __name__ == "__main__":
    main()
