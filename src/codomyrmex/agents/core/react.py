
"""ReAct Agent Implementation.

This module provides a generic ReAct (Reasoning and Acting) agent
that can use registered tools to solve problems.
"""

from typing import Any, Dict, Iterator, List, Optional
import json

from codomyrmex.logging_monitoring import get_logger
from .base import BaseAgent, AgentCapabilities, AgentRequest, AgentResponse
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
        config: Optional[Dict[str, Any]] = None,
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
            # Mock reasoning step
            tools = self.tool_registry.list_tools()
            tool_names = [t.name for t in tools]
            
            # TODO: Implement actual LLM call loop
            # response = self.llm_client.chat(history)
            # ... parse ... 
            
            # Fallback for now: Check if prompt asks to run a tool directly (e.g. "Run tool X")
            # This allows unit testing the harness without an LLM.
            
            if request.prompt.startswith("call:"):
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
            else:
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

    def stream(self, request: AgentRequest) -> Iterator[str]:
        # Simple implementation
        res = self.execute(request)
        yield res.content
