
"""ReAct Agent Implementation.

This module provides a generic ReAct (Reasoning and Acting) agent
that uses registered tools to solve problems via the plan→act→observe
lifecycle.
"""
from __future__ import annotations

import json

from typing import Any, TYPE_CHECKING
from collections.abc import Iterator

if TYPE_CHECKING:
    from codomyrmex.llm import BaseLLMClient

from codomyrmex.logging_monitoring import get_logger

from .base import AgentCapabilities, AgentRequest, AgentResponse, BaseAgent
from .messages import AgentMessage, MessageRole, ToolCall, ToolResult
from .registry import ToolRegistry

logger = get_logger(__name__)


class ReActAgent(BaseAgent):
    """A ReAct agent that interleaves reasoning and acting.

    Implements the ``AgentProtocol`` methods (``plan``, ``act``, ``observe``)
    and composes them inside ``_execute_impl``.
    """

    def __init__(
        self,
        name: str,
        tool_registry: ToolRegistry,
        llm_client: BaseLLMClient | Any = None,
        config: dict[str, Any] | None = None,
        max_steps: int = 10,
    ):
        """Execute   Init   operations natively."""
        capabilities = [
            AgentCapabilities.MULTI_TURN,
            AgentCapabilities.CODE_EXECUTION,
        ]
        super().__init__(name, capabilities, config)
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self.max_steps = max_steps

    # ------------------------------------------------------------------
    # AgentProtocol: plan / act / observe
    # ------------------------------------------------------------------

    def plan(self, request: AgentRequest) -> list[str]:
        """Build a plan: return the system prompt + available tool names.

        For prompts starting with ``call:``, the plan is a single direct
        tool invocation.  Otherwise the plan relies on the LLM to decide.
        """
        tools = self.tool_registry.list_tools()
        tool_names = [t.name for t in tools]

        if request.prompt.startswith("call:"):
            parts = request.prompt.split(" ", 2)
            return [f"call_tool:{parts[1]}"] if len(parts) >= 2 else ["invalid_call"]

        return [f"llm_reason_with_tools:{','.join(tool_names)}"]

    def act(self, action: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Execute a single action from the plan.

        Supported action prefixes:
        - ``call_tool:<name>`` — invoke a tool directly.
        - ``llm_reason_with_tools:<names>`` — run the full LLM ReAct loop.
        """
        context = context or {}

        if action.startswith("call_tool:"):
            return self._act_direct_tool(action, context)

        if action.startswith("llm_reason_with_tools:"):
            return self._act_llm_loop(context)

        return AgentResponse(content=f"Unknown action: {action}", error="unknown_action")

    def observe(self, response: AgentResponse) -> dict[str, Any]:
        """Extract structured observations from an act() result."""
        return {
            "content": response.content,
            "success": response.is_success(),
            "error": response.error,
            "metadata": response.metadata or {},
        }

    # ------------------------------------------------------------------
    # _execute_impl: orchestrates plan → act → observe
    # ------------------------------------------------------------------

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute the ReAct loop via plan→act→observe."""
        self.logger.info(f"Starting ReAct loop for prompt: {request.prompt}")

        actions = self.plan(request)
        context: dict[str, Any] = {
            "prompt": request.prompt,
            "history": [],
        }
        last_response = AgentResponse(content="No actions planned", error="empty_plan")

        for action in actions:
            last_response = self.act(action, context)
            observation = self.observe(last_response)
            context["history"].append({"action": action, "observation": observation})

            if not observation["success"]:
                break

        return last_response

    # ------------------------------------------------------------------
    # Internal act implementations
    # ------------------------------------------------------------------

    def _act_direct_tool(self, action: str, context: dict[str, Any]) -> AgentResponse:
        """Handle ``call_tool:<name>`` actions."""
        tool_name = action.split(":", 1)[1]
        prompt = context.get("prompt", "")

        kwargs: dict[str, Any] = {}
        parts = prompt.split(" ", 2)
        if len(parts) > 2:
            try:
                kwargs = json.loads(parts[2])
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
                pass

        try:
            self.logger.info(f"Executing tool {tool_name} with {kwargs}")
            result = self.tool_registry.execute(tool_name, **kwargs)
            return AgentResponse(
                content=f"Tool {tool_name} returned: {result}",
                metadata={"tool": tool_name, "steps_taken": 1},
            )
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"Tool {tool_name} failed: {e}")
            return AgentResponse(content="", error=str(e))

    def _act_llm_loop(self, context: dict[str, Any]) -> AgentResponse:
        """Run the LLM-driven ReAct reasoning loop."""
        prompt = context.get("prompt", "")
        tools = self.tool_registry.list_tools()
        tool_names = [t.name for t in tools]

        history: list[AgentMessage] = [
            AgentMessage.system(self._get_system_prompt()),
            AgentMessage.user(prompt),
        ]

        if self.llm_client is None:
            return AgentResponse(
                content=f"Processed request: {prompt}. Available tools: {tool_names}",
                metadata={"steps_taken": 0},
            )

        steps = 0
        final_answer: str | None = None

        while steps < self.max_steps:
            steps += 1
            try:
                history_dicts = [m.to_llm_dict() for m in history]

                if hasattr(self.llm_client, "chat"):
                    response = self.llm_client.chat(history_dicts)
                elif hasattr(self.llm_client, "complete"):
                    prompt_text = "\n".join(f"{m.role.value}: {m.content}" for m in history)
                    response = self.llm_client.complete(prompt_text)
                else:
                    self.logger.warning("LLM client has no chat/complete method")
                    break

                response_text = response if isinstance(response, str) else str(response)

                if "Final Answer:" in response_text:
                    final_answer = response_text.split("Final Answer:")[-1].strip()
                    break

                if "Action:" in response_text:
                    action_line = response_text.split("Action:")[-1].split("\n")[0].strip()
                    try:
                        tool_name = action_line.split()[0]
                        kwargs = self._parse_action_args(action_line)
                        result = self.tool_registry.execute(tool_name, **kwargs)
                        history.append(AgentMessage.assistant(response_text))
                        history.append(AgentMessage.user(f"Observation: {result}"))
                    except Exception as tool_error:
                        history.append(AgentMessage.user(f"Observation: Error - {tool_error}"))
                else:
                    history.append(AgentMessage.assistant(response_text))

            except Exception as llm_error:
                self.logger.warning(f"LLM call failed: {llm_error}")
                break

        if final_answer is None:
            final_answer = f"Processed request: {prompt}. Available tools: {tool_names}"

        return AgentResponse(content=final_answer, metadata={"steps_taken": steps})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
        """
        parts = action_line.split(None, 1)
        if len(parts) < 2:
            return {}

        args_str = parts[1].strip()

        if args_str.startswith("{"):
            try:
                return json.loads(args_str)
            except json.JSONDecodeError:
                pass

        result: dict[str, Any] = {}
        for item in args_str.split():
            if "=" in item:
                key, value = item.split("=", 1)
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value

        return result

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """Stream agent response."""
        res = self.execute(request)
        yield res.content

