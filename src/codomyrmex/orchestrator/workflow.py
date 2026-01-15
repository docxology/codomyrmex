
"""Workflow Orchestration Module.

This module provides support for defining and executing Directed Acyclic Graphs (DAGs)
of tasks. It allows for complex dependency management between tasks.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union
from enum import Enum
import logging

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    """Represents a single unit of work in a workflow."""
    name: str
    action: Callable[..., Any]
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    timeout: Optional[float] = None
    
    # State
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None

    def __hash__(self):
        return hash(self.name)

class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass

class CycleError(WorkflowError):
    """Raised when a circular dependency is detected."""
    pass

class Workflow:
    """Manages a collection of tasks and their dependencies."""

    def __init__(self, name: str):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.logger = get_logger(f"Workflow.{name}")

    def add_task(
        self,
        name: str,
        action: Callable[..., Any],
        dependencies: Optional[List[str]] = None,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> 'Workflow':
        """Add a task to the workflow."""
        if name in self.tasks:
            raise WorkflowError(f"Task '{name}' already exists in workflow.")

        deps = set(dependencies) if dependencies else set()
        
        # Validate dependencies exist
        # Note: We allow adding dependencies that don't exist yet, but validate before run?
        # Or should we enforce existence? Let's verify existence at add time for simplicity,
        # or allow forward references? 
        # Better: Allow forward refs, validate at run time.
        
        task = Task(
            name=name,
            action=action,
            dependencies=deps,
            args=args or [],
            kwargs=kwargs or {},
            timeout=timeout
        )
        self.tasks[name] = task
        return self

    def validate(self):
        """Validate workflow structure (check dependencies exist, check for cycles)."""
        # 1. Check dependencies exist
        for name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise WorkflowError(f"Task '{name}' depends on unknown task '{dep}'")

        # 2. Check for cycles
        visited = set()
        path = set()

        def check_cycle(task_name):
            visited.add(task_name)
            path.add(task_name)
            
            for dep in self.tasks[task_name].dependencies:
                if dep in path:
                    raise CycleError(f"Circular dependency detected: {task_name} -> {dep}")
                if dep not in visited:
                    check_cycle(dep)
            
            path.remove(task_name)

        for name in self.tasks:
            if name not in visited:
                check_cycle(name)

    async def run(self) -> Dict[str, Any]:
        """Execute the workflow."""
        self.validate()
        self.logger.info(f"Starting workflow '{self.name}' with {len(self.tasks)} tasks.")
        
        # Reset task states
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None

        # Topological execution
        # We can run compatible tasks in parallel using asyncio
        
        completed_tasks = set()
        failed_tasks = set()
        
        while len(completed_tasks) + len(failed_tasks) < len(self.tasks):
            # Find runnable tasks
            runnable = []
            for name, task in self.tasks.items():
                if task.status == TaskStatus.PENDING:
                    if task.dependencies.issubset(completed_tasks):
                        runnable.append(task)
            
            if not runnable and (len(completed_tasks) + len(failed_tasks) < len(self.tasks)):
                # This explicitly shouldn't happen if validation passed unless logic error
                # or if skipped tasks blocked others?
                # If dependencies failed, we should handle that.
                
                # Check for tasks blocked by failed dependencies
                blocked = False
                for name, task in self.tasks.items():
                    if task.status == TaskStatus.PENDING:
                        if not task.dependencies.isdisjoint(failed_tasks):
                            self.logger.warning(f"Task '{name}' skipped due to failed dependencies.")
                            task.status = TaskStatus.SKIPPED
                            failed_tasks.add(name) # Treat skipped as failed for dependency resolution purposes? 
                                                   # No, logic needs update.
                            blocked = True
                
                if blocked:
                    continue
                    
                raise WorkflowError("Deadlock detected during execution.")

            # Run tasks concurrently
            if not runnable:
                break

            self.logger.info(f"Running batch: {[t.name for t in runnable]}")
            
            coroutines = []
            for task in runnable:
                task.status = TaskStatus.RUNNING
                coroutines.append(self._execute_task(task))
            
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for task, result in zip(runnable, results):
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error = result
                    failed_tasks.add(task.name)
                    self.logger.error(f"Task '{task.name}' failed: {result}")
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    completed_tasks.add(task.name)
                    self.logger.info(f"Task '{task.name}' completed.")

        results = {name: task.result for name, task in self.tasks.items()}
        return results

    async def _execute_task(self, task: Task) -> Any:
        try:
            if asyncio.iscoroutinefunction(task.action):
                if task.timeout:
                    return await asyncio.wait_for(task.action(*task.args, **task.kwargs), timeout=task.timeout)
                else:
                    return await task.action(*task.args, **task.kwargs)
            else:
                # Run sync functions in thread pool to avoid blocking
                loop = asyncio.get_running_loop()
                func = lambda: task.action(*task.args, **task.kwargs)
                return await loop.run_in_executor(None, func)
        except Exception as e:
            raise e

