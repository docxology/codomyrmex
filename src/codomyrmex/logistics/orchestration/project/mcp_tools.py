"""
MCP (Model Context Protocol) Tools for Codomyrmex Orchestration

This module provides MCP tools that allow AI models to interact with the
orchestration system, enabling AI-driven project management and task execution.
"""

from datetime import datetime, timezone
from typing import Any

# Import Codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

try:
    from codomyrmex.model_context_protocol import MCPErrorDetail, MCPToolResult

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.error("CRITICAL: MCP core modules are not installed. Cannot instantiate MCP tools. Zero mock policy enforces crashing instead of mocking.")

    def __raise_mcp_error(*args, **kwargs):
        """raise Mcp Error ."""
        raise RuntimeError("MCP tools cannot be utilized without the codomyrmex.model_context_protocol package installed.")

    MCPToolResult = __raise_mcp_error
    MCPErrorDetail = __raise_mcp_error


from .orchestration_engine import get_orchestration_engine
from .project_manager import get_project_manager
from .resource_manager import get_resource_manager
from .task_orchestrator import (
    Task,
    TaskPriority,
    get_task_orchestrator,
)
from .workflow_manager import WorkflowStep, get_workflow_manager


class OrchestrationMCPTools:
    """MCP tools for orchestration operations."""

    def __init__(self):
        """Initialize MCP tools."""
        self.engine = get_orchestration_engine()
        self.wf_manager = get_workflow_manager()
        self.task_orchestrator = get_task_orchestrator()
        self.project_manager = get_project_manager()
        self.resource_manager = get_resource_manager()

        if not MCP_AVAILABLE:
            raise RuntimeError("Cannot initialize OrchestrationMCPTools: MCP not available (Zero-Mock strict mode)")

    def get_tool_definitions(self) -> dict[str, dict[str, Any]]:
        """Get MCP tool definitions."""
        return {
            "execute_workflow": {
                "name": "execute_workflow",
                "description": "Execute a workflow with the orchestration engine",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {
                            "type": "string",
                            "description": "Name of workflow to execute",
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Workflow parameters",
                            "default": {},
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID for tracking",
                        },
                    },
                    "required": ["workflow_name"],
                },
            },
            "create_workflow": {
                "name": "create_workflow",
                "description": "Create a new workflow with specified steps",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the workflow",
                        },
                        "steps": {
                            "type": "array",
                            "description": "List of workflow steps",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "module": {"type": "string"},
                                    "action": {"type": "string"},
                                    "parameters": {"type": "object", "default": {}},
                                    "dependencies": {"type": "array", "default": []},
                                    "timeout": {"type": "integer", "default": None},
                                },
                                "required": ["name", "module", "action"],
                            },
                        },
                        "description": {
                            "type": "string",
                            "description": "Workflow description",
                        },
                    },
                    "required": ["name", "steps"],
                },
            },
            "list_workflows": {
                "name": "list_workflows",
                "description": "List all available workflows",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            "create_project": {
                "name": "create_project",
                "description": "Create a new project with optional template",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the project",
                        },
                        "template": {
                            "type": "string",
                            "description": "Project template to use",
                            "default": "ai_analysis",
                        },
                        "description": {
                            "type": "string",
                            "description": "Project description",
                        },
                        "path": {
                            "type": "string",
                            "description": "Project directory path",
                        },
                    },
                    "required": ["name"],
                },
            },
            "list_projects": {
                "name": "list_projects",
                "description": "List all available projects",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            "execute_task": {
                "name": "execute_task",
                "description": "Execute a single task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Task name"},
                        "module": {
                            "type": "string",
                            "description": "Module to execute",
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to execute",
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Task parameters",
                            "default": {},
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high", "critical"],
                            "default": "normal",
                        },
                        "dependencies": {
                            "type": "array",
                            "description": "Task dependencies",
                            "default": [],
                        },
                    },
                    "required": ["name", "module", "action"],
                },
            },
            "get_system_status": {
                "name": "get_system_status",
                "description": "Get comprehensive system status",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            "get_health_status": {
                "name": "get_health_status",
                "description": "Get system health status",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            "allocate_resources": {
                "name": "allocate_resources",
                "description": "Allocate system resources",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User identifier"},
                        "requirements": {
                            "type": "object",
                            "description": "Resource requirements",
                            "properties": {
                                "cpu": {"type": "object"},
                                "memory": {"type": "object"},
                                "disk": {"type": "object"},
                                "network": {"type": "object"},
                            },
                        },
                    },
                    "required": ["user_id", "requirements"],
                },
            },
            "create_complex_workflow": {
                "name": "create_complex_workflow",
                "description": "Create and execute a complex workflow with multiple steps",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Workflow name"},
                        "workflow_definition": {
                            "type": "object",
                            "description": "Workflow definition with steps and dependencies",
                            "properties": {
                                "steps": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "module": {"type": "string"},
                                            "action": {"type": "string"},
                                            "parameters": {"type": "object"},
                                        },
                                        "required": ["name", "module", "action"],
                                    },
                                },
                                "dependencies": {
                                    "type": "object",
                                    "description": "Step dependencies",
                                },
                            },
                            "required": ["steps"],
                        },
                    },
                    "required": ["name", "workflow_definition"],
                },
            },
        }

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> MCPToolResult:
        """Execute an MCP tool."""
        if not MCP_AVAILABLE:
            return MCPToolResult(
                success=False,
                error="MCP not available",
                error_details=[
                    MCPErrorDetail(
                        type="ImportError", message="MCP module not available"
                    )
                ],
            )

        try:
            if tool_name == "execute_workflow":
                return self._execute_workflow_tool(arguments)
            elif tool_name == "create_workflow":
                return self._create_workflow_tool(arguments)
            elif tool_name == "list_workflows":
                return self._list_workflows_tool(arguments)
            elif tool_name == "create_project":
                return self._create_project_tool(arguments)
            elif tool_name == "list_projects":
                return self._list_projects_tool(arguments)
            elif tool_name == "execute_task":
                return self._execute_task_tool(arguments)
            elif tool_name == "get_system_status":
                return self._get_system_status_tool(arguments)
            elif tool_name == "get_health_status":
                return self._get_health_status_tool(arguments)
            elif tool_name == "allocate_resources":
                return self._allocate_resources_tool(arguments)
            elif tool_name == "create_complex_workflow":
                return self._create_complex_workflow_tool(arguments)
            else:
                return MCPToolResult(
                    success=False,
                    error=f"Unknown tool: {tool_name}",
                    error_details=[
                        MCPErrorDetail(
                            type="ValueError", message=f"Tool '{tool_name}' not found"
                        )
                    ],
                )
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPToolResult(
                success=False,
                error=str(e),
                error_details=[MCPErrorDetail(type=type(e).__name__, message=str(e))],
            )

    def _execute_workflow_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Execute workflow tool."""
        workflow_name = arguments["workflow_name"]
        parameters = arguments.get("parameters", {})
        session_id = arguments.get("session_id")

        result = self.engine.execute_workflow(workflow_name, session_id, **parameters)

        return MCPToolResult(
            success=result.get("success", False),
            data=result,
            metadata={
                "workflow_name": workflow_name,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _create_workflow_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Create workflow tool."""
        name = arguments["name"]
        steps_data = arguments["steps"]
        description = arguments.get("description", "")

        # Convert step data to WorkflowStep objects
        steps = []
        for step_data in steps_data:
            step = WorkflowStep(
                name=step_data["name"],
                module=step_data["module"],
                action=step_data["action"],
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", []),
                timeout=step_data.get("timeout"),
            )
            steps.append(step)

        success = self.wf_manager.create_workflow(name, steps)

        return MCPToolResult(
            success=success,
            data={
                "workflow_name": name,
                "steps_count": len(steps),
                "description": description,
            },
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _list_workflows_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """List workflows tool."""
        workflows = self.wf_manager.list_workflows()

        return MCPToolResult(
            success=True,
            data={"workflows": workflows, "count": len(workflows)},
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _create_project_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Create project tool."""
        name = arguments["name"]
        template = arguments.get("template", "ai_analysis")
        description = arguments.get("description", "")
        path = arguments.get("path")

        try:
            project = self.project_manager.create_project(
                name=name, template_name=template, description=description, path=path
            )

            return MCPToolResult(
                success=True,
                data={
                    "project_name": project.name,
                    "project_type": project.type.value,
                    "project_path": project.path,
                    "template_used": template,
                    "workflows": project.workflows,
                },
                metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=str(e),
                error_details=[MCPErrorDetail(type=type(e).__name__, message=str(e))],
            )

    def _list_projects_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """List projects tool."""
        projects = self.project_manager.list_projects()
        project_details = []

        for project_name in projects:
            project = self.project_manager.get_project(project_name)
            if project:
                project_details.append(
                    {
                        "name": project.name,
                        "type": project.type.value,
                        "status": project.status.value,
                        "path": project.path,
                        "created_at": project.created_at.isoformat(),
                    }
                )

        return MCPToolResult(
            success=True,
            data={"projects": project_details, "count": len(project_details)},
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _execute_task_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Execute task tool."""
        name = arguments["name"]
        module = arguments["module"]
        action = arguments["action"]
        parameters = arguments.get("parameters", {})
        priority = arguments.get("priority", "normal")
        dependencies = arguments.get("dependencies", [])

        # Convert priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }

        task = Task(
            name=name,
            module=module,
            action=action,
            parameters=parameters,
            priority=priority_map.get(priority, TaskPriority.NORMAL),
            dependencies=dependencies,
        )

        result = self.engine.execute_task(task)

        return MCPToolResult(
            success=result.get("success", False),
            data=result,
            metadata={
                "task_name": name,
                "module": module,
                "action": action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _get_system_status_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Get system status tool."""
        status = self.engine.get_system_status()

        return MCPToolResult(
            success=True,
            data=status,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _get_health_status_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Get health status tool."""
        health = self.engine.health_check()

        return MCPToolResult(
            success=True,
            data=health,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _allocate_resources_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Allocate resources tool."""
        user_id = arguments["user_id"]
        requirements = arguments["requirements"]

        allocated = self.resource_manager.allocate_resources(user_id, requirements)

        return MCPToolResult(
            success=allocated is not None,
            data={
                "allocated": allocated,
                "user_id": user_id,
                "requirements": requirements,
            },
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )

    def _create_complex_workflow_tool(self, arguments: dict[str, Any]) -> MCPToolResult:
        """Create complex workflow tool."""
        name = arguments["name"]
        workflow_definition = arguments["workflow_definition"]

        result = self.engine.execute_complex_workflow(workflow_definition)

        return MCPToolResult(
            success=result.get("success", False),
            data={"workflow_name": name, "execution_result": result},
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
        )


# Global MCP tools instance
_mcp_tools = None


def get_mcp_tools() -> OrchestrationMCPTools:
    """Get the global MCP tools instance."""
    global _mcp_tools
    if _mcp_tools is None:
        _mcp_tools = OrchestrationMCPTools()
    return _mcp_tools


def get_mcp_tool_definitions() -> dict[str, dict[str, Any]]:
    """Get MCP tool definitions."""
    tools = get_mcp_tools()
    return tools.get_tool_definitions()


def execute_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> MCPToolResult:
    """Execute an MCP tool."""
    tools = get_mcp_tools()
    return tools.execute_tool(tool_name, arguments)


# Example usage and testing
if __name__ == "__main__":
    # Test MCP tools
    tools = get_mcp_tools()

    # Test tool definitions
    definitions = tools.get_tool_definitions()
    print(f"Available tools: {list(definitions.keys())}")

    # Test workflow listing
    result = tools.execute_tool("list_workflows", {})
    print(f"List workflows result: {result.success}")

    # Test system status
    result = tools.execute_tool("get_system_status", {})
    print(f"System status result: {result.success}")

    print("MCP tools test completed")
