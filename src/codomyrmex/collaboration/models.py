"""
Core data models for the collaboration module.

Provides Task, TaskResult, SwarmStatus, and AgentStatus dataclasses
for multi-agent collaboration workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class TaskStatus(Enum):
    """Status of a task in the system."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    A task to be executed by agents in the swarm.
    
    Attributes:
        id: Unique task identifier.
        name: Human-readable task name.
        description: Detailed task description.
        required_capabilities: List of capabilities an agent needs to execute this task.
        priority: Task priority (1-10, higher is more urgent).
        dependencies: IDs of tasks that must complete before this one.
        metadata: Additional task-specific metadata.
        created_at: When the task was created.
        status: Current task status.
        assigned_agent_id: ID of the agent assigned to this task.
    """
    name: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    required_capabilities: List[str] = field(default_factory=list)
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "assigned_agent_id": self.assigned_agent_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize task from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            description=data.get("description", ""),
            required_capabilities=data.get("required_capabilities", []),
            priority=data.get("priority", 5),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            status=TaskStatus(data.get("status", "pending")),
            assigned_agent_id=data.get("assigned_agent_id"),
        )
    
    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)


@dataclass
class TaskResult:
    """
    Result of a task execution.
    
    Attributes:
        task_id: ID of the executed task.
        success: Whether the task completed successfully.
        output: Task output data.
        error: Error message if task failed.
        duration: Execution duration in seconds.
        agent_id: ID of the agent that executed the task.
        completed_at: When the task completed.
    """
    task_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    agent_id: str = ""
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "duration": self.duration,
            "agent_id": self.agent_id,
            "completed_at": self.completed_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """Deserialize result from dictionary."""
        return cls(
            task_id=data["task_id"],
            success=data["success"],
            output=data.get("output"),
            error=data.get("error"),
            duration=data.get("duration", 0.0),
            agent_id=data.get("agent_id", ""),
            completed_at=datetime.fromisoformat(data["completed_at"]) if "completed_at" in data else datetime.now(),
        )


@dataclass
class SwarmStatus:
    """
    Status of the entire swarm.
    
    Attributes:
        total_agents: Total number of agents in the swarm.
        active_agents: Number of currently active agents.
        idle_agents: Number of idle agents.
        pending_tasks: Number of tasks waiting for execution.
        running_tasks: Number of currently executing tasks.
        completed_tasks: Number of completed tasks.
        failed_tasks: Number of failed tasks.
        uptime_seconds: How long the swarm has been running.
    """
    total_agents: int = 0
    active_agents: int = 0
    idle_agents: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize status to dictionary."""
        return {
            "total_agents": self.total_agents,
            "active_agents": self.active_agents,
            "idle_agents": self.idle_agents,
            "pending_tasks": self.pending_tasks,
            "running_tasks": self.running_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "uptime_seconds": self.uptime_seconds,
        }


@dataclass
class AgentStatus:
    """
    Status of an individual agent.
    
    Attributes:
        agent_id: Unique agent identifier.
        name: Agent name.
        status: Current status (idle, busy, offline, error).
        current_task_id: ID of the task currently being executed.
        capabilities: List of agent capabilities.
        tasks_completed: Number of tasks completed by this agent.
        tasks_failed: Number of tasks failed by this agent.
        last_heartbeat: Last time agent sent a heartbeat.
    """
    agent_id: str
    name: str = ""
    status: str = "idle"
    current_task_id: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize status to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "current_task_id": self.current_task_id,
            "capabilities": self.capabilities,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentStatus":
        """Deserialize status from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            name=data.get("name", ""),
            status=data.get("status", "idle"),
            current_task_id=data.get("current_task_id"),
            capabilities=data.get("capabilities", []),
            tasks_completed=data.get("tasks_completed", 0),
            tasks_failed=data.get("tasks_failed", 0),
            last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]) if "last_heartbeat" in data else datetime.now(),
        )


__all__ = [
    "TaskPriority",
    "TaskStatus",
    "Task",
    "TaskResult",
    "SwarmStatus",
    "AgentStatus",
]
