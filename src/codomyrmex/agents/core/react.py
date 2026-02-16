
"""ReAct Agent Implementation.

This module provides a generic ReAct (Reasoning and Acting) agent
that can use registered tools to solve problems.
"""

import json
from typing import Any
from collections.abc import Iterator

from codomyrmex.logging_monitoring import get_logger

from .base import AgentCapabilities, AgentRequest, AgentResponse, BaseAgent
from .registry import ToolRegistry

logger = get_logger(__name__)

class ReActAgent(BaseAgent):
    """
    A generic ReAct agent that interleaves reasoning and acting.

    It uses a ToolRegistry to discover and execute tools.
    """

    def __init__(
        self,
        name: str,
        tool_registry: ToolRegistry,
        llm_client: Any = None, # Placeholder for LLM interface
        config: dict[str, Any] | None = None,
        max_steps: int = 10
    ):
        capabilities = [
            AgentCapabilities.MULTI_TURN,
            AgentCapabilities.CODE_EXECUTION # If tools allow it
        ]
        super().__init__(name, capabilities, config)
        self.tool_registry = tool_registry
        self.llm_client = llm_client # In a real implementation, this would be a standardized LLM client
        self.max_steps = max_steps

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute the ReAct loop."""

        history = []
        history.append({"role": "system", "content": self._get_system_prompt()})
        history.append({"role": "user", "content": request.prompt})

        steps = 0
        final_answer = None

        # Simulating the loop for now as we don't have a real LLM connected in this env
        # In a real scenario, this would loop calling the LLM, parsing Thought/Action, executing, and feeding back Observation.

        self.logger.info(f"Starting ReAct loop for prompt: {request.prompt}")

        # Simplified Logic for demonstration/testing without live LLM:
        # If the prompt matches a tool call pattern exactly, execute it.
        # Otherwise return a placeholder.

        # NOTE: This is where we would plug in the `codomyrmex.llm` module.
        # For Phase 17, we establish the STRUCTURE.

        try:
            # Get available tools for the system prompt
            tools = self.tool_registry.list_tools()
            tool_names = [t.name for t in tools]

            # LLM client integration for the ReAct loop
            if self.llm_client is not None:
                # Use the LLM client to process the ReAct loop
                while steps < self.max_steps:
                    steps += 1
                    try:
                        # Call LLM with current history
                        if hasattr(self.llm_client, 'chat'):
                            response = self.llm_client.chat(history)
                        elif hasattr(self.llm_client, 'complete'):
                            # Alternative interface for completion-style clients
                            prompt_text = "\n".join(
                                f"{m['role']}: {m['content']}" for m in history
                            )
                            response = self.llm_client.complete(prompt_text)
                        else:
                            self.logger.warning("LLM client has no chat/complete method, falling back")
                            break

                        # Parse response for Thought/Action/Final Answer pattern
                        response_text = response if isinstance(response, str) else str(response)

                        # Check for final answer
                        if "Final Answer:" in response_text:
                            final_answer = response_text.split("Final Answer:")[-1].strip()
                            break

                        # Parse action if present
                        if "Action:" in response_text:
                            action_line = response_text.split("Action:")[-1].split("\n")[0].strip()
                            # Execute tool and add observation
                            try:
                                result = self.tool_registry.execute(action_line.split()[0],
                                    **self._parse_action_args(action_line))
                                history.append({"role": "assistant", "content": response_text})
                                history.append({"role": "user", "content": f"Observation: {result}"})
                            except Exception as tool_error:
                                history.append({"role": "user", "content": f"Observation: Error - {tool_error}"})
                        else:
                            # No action parsed, treat as thinking/reasoning step
                            history.append({"role": "assistant", "content": response_text})

                    except Exception as llm_error:
                        self.logger.warning(f"LLM call failed: {llm_error}, falling back to direct execution")
                        break

            # Fallback behavior: Check if prompt asks to run a tool directly
            # This allows unit testing the harness without an LLM.

            if final_answer is None and request.prompt.startswith("call:"):
                # Format: call: tool_name args={"k": "v"}
                parts = request.prompt.split(" ", 2)
                if len(parts) >= 2:
                    tool_name = parts[1]
                    kwargs = {}
                    if len(parts) > 2:
                        try:
                            kwargs = json.loads(parts[2])
                        except Exception:
                            pass

                    self.logger.info(f"Executing tool {tool_name} with {kwargs}")
                    result = self.tool_registry.execute(tool_name, **kwargs)
                    final_answer = f"Tool {tool_name} returned: {result}"
                else:
                    final_answer = "Invalid call format."
            elif final_answer is None:
                final_answer = f"Processed request: {request.prompt}. Available tools: {tool_names}"

            return AgentResponse(
                content=final_answer,
                metadata={"steps_taken": steps}
            )

        except Exception as e:
            self.logger.error(f"ReAct loop failed: {e}")
            return AgentResponse(content="", error=str(e))

    def _get_system_prompt(self) -> str:
        """Construct the system prompt with tool definitions."""
        schemas = self.tool_registry.get_schemas()
        return f"""You are an intelligent agent.
You have access to the following tools:
{json.dumps(schemas, indent=2)}

Use the following format:
Thought: ...
Action: ...
Observation: ...
... (repeat)
Final Answer: ...
"""

    def _parse_action_args(self, action_line: str) -> dict[str, Any]:
        """Parse action arguments from an action line.

        Supports formats like:
        - tool_name {"key": "value"}
        - tool_name key=value key2=value2

        Args:
            action_line: The action line to parse

        Returns:
            Dictionary of parsed arguments
        """
        parts = action_line.split(None, 1)
        if len(parts) < 2:
            return {}

        args_str = parts[1].strip()

        # Try JSON format first
        if args_str.startswith("{"):
            try:
                return json.loads(args_str)
            except json.JSONDecodeError:
                pass

        # Try key=value format
        result = {}
        for item in args_str.split():
            if "=" in item:
                key, value = item.split("=", 1)
                # Try to parse value as JSON for complex types
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value

        return result

    def stream(self, request: AgentRequest) -> Iterator[str]:
        # Simple implementation
        res = self.execute(request)
        yield res.content
