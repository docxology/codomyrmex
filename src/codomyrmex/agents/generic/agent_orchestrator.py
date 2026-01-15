from typing import Any, Optional

from dataclasses import dataclass

from codomyrmex.agents.core import AgentCapabilities
from codomyrmex.agents.core import AgentInterface, AgentRequest, AgentResponse
from codomyrmex.agents.core.exceptions import AgentError
from codomyrmex.logging_monitoring import get_logger











































"""Multi-agent orchestration utilities."""

logger = get_logger(__name__)


@dataclass
class OrchestrationStrategy:
    """Strategy for orchestrating multiple agents."""

    name: str
    description: str
    parallel: bool = False
    sequential: bool = True
    fallback: bool = False


class AgentOrchestrator:
    """Orchestrates multiple agents for complex tasks."""

    def __init__(self, agents: list[AgentInterface]):
        """
        Initialize orchestrator with list of agents.

        Args:
            agents: List of agent instances to orchestrate
        """
        self.agents = agents
        self.logger = get_logger(__name__)

    def execute_parallel(
        self,
        request: AgentRequest,
        agents: Optional[list[AgentInterface]] = None,
    ) -> list[AgentResponse]:
        """
        Execute request on multiple agents in parallel.

        Args:
            request: Agent request to execute
            agents: List of agents to use (defaults to all agents)

        Returns:
            List of agent responses
        """
        agents_to_use = agents or self.agents

        if not agents_to_use:
            raise AgentError("No agents available for orchestration")

        self.logger.info(
            f"Executing parallel request on {len(agents_to_use)} agents"
        )

        responses = []
        for agent in agents_to_use:
            try:
                response = agent.execute(request)
                responses.append(response)
            except Exception as e:
                self.logger.error(f"Agent {agent} failed: {e}")
                responses.append(
                    AgentResponse(
                        content="",
                        error=str(e),
                        metadata={"agent": str(agent)},
                    )
                )

        return responses

    def execute_sequential(
        self,
        request: AgentRequest,
        agents: Optional[list[AgentInterface]] = None,
        stop_on_success: bool = False,
    ) -> list[AgentResponse]:
        """
        Execute request on multiple agents sequentially.

        Args:
            request: Agent request to execute
            agents: List of agents to use (defaults to all agents)
            stop_on_success: Stop after first successful response

        Returns:
            List of agent responses
        """
        agents_to_use = agents or self.agents

        if not agents_to_use:
            raise AgentError("No agents available for orchestration")

        self.logger.info(
            f"Executing sequential request on {len(agents_to_use)} agents"
        )

        responses = []
        for agent in agents_to_use:
            try:
                response = agent.execute(request)
                responses.append(response)

                if stop_on_success and response.is_success():
                    self.logger.info(
                        f"Stopping after successful response from {agent}"
                    )
                    break
            except Exception as e:
                self.logger.error(f"Agent {agent} failed: {e}")
                responses.append(
                    AgentResponse(
                        content="",
                        error=str(e),
                        metadata={"agent": str(agent)},
                    )
                )

        return responses

    def execute_with_fallback(
        self,
        request: AgentRequest,
        agents: Optional[list[AgentInterface]] = None,
    ) -> AgentResponse:
        """
        Execute request with fallback to next agent on failure.

        Args:
            request: Agent request to execute
            agents: List of agents to use (defaults to all agents)

        Returns:
            First successful agent response, or last error response
        """
        agents_to_use = agents or self.agents

        if not agents_to_use:
            raise AgentError("No agents available for orchestration")

        self.logger.info(
            f"Executing with fallback on {len(agents_to_use)} agents"
        )

        last_error_response = None

        for agent in agents_to_use:
            try:
                response = agent.execute(request)
                if response.is_success():
                    self.logger.info(f"Success with agent {agent}")
                    return response
                else:
                    last_error_response = response
                    self.logger.warning(
                        f"Agent {agent} failed: {response.error}"
                    )
            except Exception as e:
                self.logger.error(f"Agent {agent} raised exception: {e}")
                last_error_response = AgentResponse(
                    content="",
                    error=str(e),
                    metadata={"agent": str(agent)},
                )

        if last_error_response:
            self.logger.error("All agents failed")
            return last_error_response

        raise AgentError("No agents available and no error response")

    def select_agent_by_capability(
        self, capability: str, agents: Optional[list[AgentInterface]] = None
    ) -> list[AgentInterface]:
        """
        Select agents that support a specific capability.

        Args:
            capability: Capability name to check
            agents: List of agents to check (defaults to all agents)

        Returns:
            List of agents that support the capability
        """

        agents_to_check = agents or self.agents

        try:
            capability_enum = AgentCapabilities(capability)
        except ValueError:
            self.logger.warning(f"Unknown capability: {capability}")
            return []

        supported_agents = [
            agent
            for agent in agents_to_check
            if agent.supports_capability(capability_enum)
        ]

        return supported_agents


