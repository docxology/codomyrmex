"""
Task management and scheduling for multi-agent workflows.

Provides TaskManager for task scheduling, dependency resolution,
and load balancing across agents.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import heapq
import logging

from ..models import Task, TaskResult, TaskStatus, TaskPriority
from ..exceptions import (
    TaskNotFoundError,
    TaskDependencyError,
    TaskExecutionError,
    CapabilityMismatchError,
)
from ..agents.base import CollaborativeAgent
from ..protocols import AgentState

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Task scheduling strategies."""
    FIFO = "fifo"              # First-in, first-out
    PRIORITY = "priority"       # By task priority
    SHORTEST_FIRST = "shortest" # Estimate shortest tasks first
    ROUND_ROBIN = "round_robin" # Distribute evenly


@dataclass(order=True)
class PriorityTask:
    """Wrapper for priority queue ordering."""
    priority: int
    timestamp: float = field(compare=True)
    task: Task = field(compare=False)


class TaskQueue:
    """
    Priority-based task queue.
    
    Manages pending tasks with priority ordering and dependency tracking.
    """
    
    def __init__(self):
        self._heap: List[PriorityTask] = []
        self._tasks: Dict[str, Task] = {}
        self._counter = 0
    
    def push(self, task: Task) -> None:
        """Add a task to the queue."""
        # Higher priority = lower number (so negate for max-heap behavior)
        priority = -task.priority
        self._counter += 1
        item = PriorityTask(priority, self._counter, task)
        heapq.heappush(self._heap, item)
        self._tasks[task.id] = task
    
    def pop(self) -> Optional[Task]:
        """Remove and return the highest priority task."""
        while self._heap:
            item = heapq.heappop(self._heap)
            if item.task.id in self._tasks:
                del self._tasks[item.task.id]
                return item.task
        return None
    
    def peek(self) -> Optional[Task]:
        """Return the highest priority task without removing it."""
        while self._heap:
            if self._heap[0].task.id in self._tasks:
                return self._heap[0].task
            heapq.heappop(self._heap)
        return None
    
    def remove(self, task_id: str) -> bool:
        """Remove a task by ID (lazy removal)."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID without removing it."""
        return self._tasks.get(task_id)
    
    def __len__(self) -> int:
        return len(self._tasks)
    
    def __bool__(self) -> bool:
        return bool(self._tasks)


class DependencyGraph:
    """
    Tracks task dependencies for workflow execution.
    
    Enables topological sorting and dependency resolution.
    """
    
    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {}  # task_id -> set of dependency task_ids
        self._dependents: Dict[str, Set[str]] = {}    # task_id -> set of tasks depending on it
    
    def add_task(self, task: Task) -> None:
        """Add a task and its dependencies to the graph."""
        task_id = task.id
        self._dependencies[task_id] = set(task.dependencies)
        
        for dep_id in task.dependencies:
            if dep_id not in self._dependents:
                self._dependents[dep_id] = set()
            self._dependents[dep_id].add(task_id)
    
    def remove_task(self, task_id: str) -> None:
        """Remove a task from the graph."""
        # Remove from dependencies of other tasks
        for dep_id in self._dependencies.get(task_id, set()):
            if dep_id in self._dependents:
                self._dependents[dep_id].discard(task_id)
        
        # Remove from dependents
        for dependent_id in self._dependents.get(task_id, set()):
            if dependent_id in self._dependencies:
                self._dependencies[dependent_id].discard(task_id)
        
        self._dependencies.pop(task_id, None)
        self._dependents.pop(task_id, None)
    
    def get_ready_tasks(self, completed: Set[str]) -> List[str]:
        """Get task IDs whose dependencies are all satisfied."""
        ready = []
        for task_id, deps in self._dependencies.items():
            if deps.issubset(completed):
                ready.append(task_id)
        return ready
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """Get dependencies of a task."""
        return self._dependencies.get(task_id, set())
    
    def get_dependents(self, task_id: str) -> Set[str]:
        """Get tasks that depend on a task."""
        return self._dependents.get(task_id, set())
    
    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""
        visited = set()
        rec_stack = set()
        
        def dfs(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep_id in self._dependents.get(task_id, set()):
                if dep_id not in visited:
                    if dfs(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self._dependencies:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        return False


class TaskManager:
    """
    Manages task scheduling and distribution to agents.
    
    Provides task queuing, dependency resolution, load balancing,
    and result tracking for multi-agent workflows.
    
    Attributes:
        strategy: Scheduling strategy to use.
        max_concurrent: Maximum concurrent tasks per agent.
    """
    
    def __init__(
        self,
        strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY,
        max_concurrent: int = 1,
    ):
        self._strategy = strategy
        self._max_concurrent = max_concurrent
        self._queue = TaskQueue()
        self._graph = DependencyGraph()
        self._running: Dict[str, Task] = {}  # task_id -> Task
        self._completed: Dict[str, TaskResult] = {}
        self._failed: Dict[str, TaskResult] = {}
        self._agent_tasks: Dict[str, Set[str]] = {}  # agent_id -> task_ids
        self._callbacks: List[Callable[[Task, TaskResult], None]] = []
    
    def submit(self, task: Task) -> str:
        """
        Submit a task for execution.
        
        Returns:
            The task ID.
        """
        task.status = TaskStatus.QUEUED
        self._queue.push(task)
        self._graph.add_task(task)
        logger.info(f"Task submitted: {task.name} ({task.id})")
        return task.id
    
    def submit_batch(self, tasks: List[Task]) -> List[str]:
        """Submit multiple tasks."""
        return [self.submit(task) for task in tasks]
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a pending task.
        
        Running tasks cannot be cancelled through this method.
        """
        if task_id in self._running:
            logger.warning(f"Cannot cancel running task: {task_id}")
            return False
        
        task = self._queue.get(task_id)
        if task:
            self._queue.remove(task_id)
            self._graph.remove_task(task_id)
            task.status = TaskStatus.CANCELLED
            logger.info(f"Task cancelled: {task_id}")
            return True
        return False
    
    def get_next_task(
        self,
        agent: CollaborativeAgent,
    ) -> Optional[Task]:
        """
        Get the next task for an agent to execute.
        
        Considers agent capabilities, current load, and dependencies.
        """
        # Check agent load
        agent_task_count = len(self._agent_tasks.get(agent.agent_id, set()))
        if agent_task_count >= self._max_concurrent:
            return None
        
        # Get completed task IDs for dependency checking
        completed_ids = set(self._completed.keys())
        
        # Find ready tasks that match agent capabilities
        for _ in range(len(self._queue)):
            task = self._queue.pop()
            if task is None:
                break
            
            # Check dependencies
            if not task.is_ready(list(completed_ids)):
                self._queue.push(task)  # Re-queue
                continue
            
            # Check capabilities
            if task.required_capabilities:
                agent_caps = set(agent.get_capabilities())
                if not set(task.required_capabilities).issubset(agent_caps):
                    self._queue.push(task)
                    continue
            
            # Assign task
            task.status = TaskStatus.RUNNING
            task.assigned_agent_id = agent.agent_id
            self._running[task.id] = task
            
            if agent.agent_id not in self._agent_tasks:
                self._agent_tasks[agent.agent_id] = set()
            self._agent_tasks[agent.agent_id].add(task.id)
            
            logger.info(f"Task {task.name} assigned to {agent.name}")
            return task
        
        return None
    
    def complete_task(self, result: TaskResult) -> None:
        """Mark a task as completed."""
        task_id = result.task_id
        
        if task_id not in self._running:
            raise TaskNotFoundError(task_id)
        
        task = self._running.pop(task_id)
        
        # Update agent task tracking
        if task.assigned_agent_id and task.assigned_agent_id in self._agent_tasks:
            self._agent_tasks[task.assigned_agent_id].discard(task_id)
        
        if result.success:
            task.status = TaskStatus.COMPLETED
            self._completed[task_id] = result
            logger.info(f"Task completed: {task.name}")
        else:
            task.status = TaskStatus.FAILED
            self._failed[task_id] = result
            logger.warning(f"Task failed: {task.name} - {result.error}")
        
        self._graph.remove_task(task_id)
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(task, result)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self._completed:
            return TaskStatus.COMPLETED
        if task_id in self._failed:
            return TaskStatus.FAILED
        if task_id in self._running:
            return TaskStatus.RUNNING
        if self._queue.get(task_id):
            return TaskStatus.QUEUED
        return None
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed or failed task."""
        return self._completed.get(task_id) or self._failed.get(task_id)
    
    def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        return len(self._queue)
    
    def get_running_count(self) -> int:
        """Get count of running tasks."""
        return len(self._running)
    
    def get_completed_count(self) -> int:
        """Get count of completed tasks."""
        return len(self._completed)
    
    def get_failed_count(self) -> int:
        """Get count of failed tasks."""
        return len(self._failed)
    
    def add_callback(self, callback: Callable[[Task, TaskResult], None]) -> None:
        """Add a completion callback."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Task, TaskResult], None]) -> None:
        """Remove a completion callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def run_workflow(
        self,
        agents: List[CollaborativeAgent],
        on_progress: Optional[Callable[[Task, TaskResult], None]] = None,
    ) -> Dict[str, TaskResult]:
        """
        Run all queued tasks as a workflow.
        
        Automatically assigns tasks to agents and waits for completion.
        
        Args:
            agents: List of agents to use.
            on_progress: Optional progress callback.
            
        Returns:
            Dictionary mapping task IDs to results.
        """
        if on_progress:
            self.add_callback(on_progress)
        
        try:
            while self._queue or self._running:
                # Assign tasks to idle agents
                for agent in agents:
                    if agent.state == AgentState.IDLE:
                        task = self.get_next_task(agent)
                        if task:
                            # Execute task in background
                            asyncio.create_task(self._execute_and_complete(agent, task))
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting
            
            # Return all results
            results = {}
            results.update(self._completed)
            results.update(self._failed)
            return results
            
        finally:
            if on_progress:
                self.remove_callback(on_progress)
    
    async def _execute_and_complete(
        self,
        agent: CollaborativeAgent,
        task: Task,
    ) -> None:
        """Execute a task and mark it complete."""
        try:
            result = await agent.process_task(task)
            self.complete_task(result)
        except Exception as e:
            result = TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                agent_id=agent.agent_id,
            )
            self.complete_task(result)


__all__ = [
    "SchedulingStrategy",
    "TaskQueue",
    "DependencyGraph",
    "TaskManager",
]
