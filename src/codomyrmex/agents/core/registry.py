
"""Tool Registry for Agents.

This module provides a registry for tools that can be used by agents.
Tools are functions or methods that are exposed to the LLM.
"""

import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

@dataclass
class Tool:
    """Represents a tool available to an agent."""
    name: str
    func: Callable
    description: str
    args_schema: Dict[str, Any]
    return_schema: Optional[Dict[str, Any]] = None
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON schema format (e.g. for OpenAI functions)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema
        }

class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self.logger = get_logger(self.__class__.__name__)

    def register(self, tool: Tool):
        """Register a tool instance."""
        if tool.name in self._tools:
            self.logger.warning(f"Overwriting tool '{tool.name}'")
        self._tools[tool.name] = tool
        self.logger.debug(f"Registered tool: {tool.name}")

    def register_function(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        """Register a python function as a tool."""
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or "No description provided."
        
        # Simple schema extraction (can be enhanced with Pydantic)
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            param_type = "string" # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        tool = Tool(
            name=tool_name,
            func=func,
            description=tool_desc,
            args_schema=parameters
        )
        self.register(tool)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas."""
        return [tool.to_schema() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        return tool.func(**kwargs)
