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
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error

try:
    from codomyrmex.agents import AgentOrchestrator, AgentRequest, AgentResponse, BaseAgent, AgentCapabilities
except ImportError as e:
    # Handle missing optional dependencies (e.g., aiohttp)
    def main():
        setup_logging()
        print_info(f"Agents module dependencies not available: {e}")
        print_info("Install with: pip install aiohttp")
        print_info("Skipping agents examples - success.")
        return 0
    
    if __name__ == "__main__":
        import sys
        sys.exit(main())
    else:
        # Let the import error propagate if not running as main
        raise

# 1. Define a Mock Agent for demonstration (to avoid requiring real API keys in example)
class DemoAgent(BaseAgent):
    def __init__(self, name="demo_agent"):
        super().__init__(name=name, capabilities=[AgentCapabilities.TEXT_COMPLETION])
    
    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        self.logger.info(f"Agent {self.name} processing prompt: {request.prompt[:20]}...")
        return AgentResponse(
            content=f"Response from {self.name} for: {request.prompt}",
            metadata={"agent": self.name}
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
            print_success(f"  {resp.metadata.get('agent', 'Unknown agent')}: {resp.content}")
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
