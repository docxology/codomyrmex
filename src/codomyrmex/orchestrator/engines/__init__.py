"""
Workflow engine implementations.

Provides different execution engines for orchestrating workflows.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set
from datetime import datetime
from enum import Enum
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import time


class TaskState(Enum):
    """States a task can be in."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class TaskDefinition:
    """Definition of a task in a workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    action: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    retries: int = 0
    retry_delay: float = 1.0
    condition: Optional[Callable[[Dict], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    state: TaskState
    output: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attempts: int = 0
    
    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tasks: List[TaskDefinition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(
        self,
        name: str,
        action: Callable,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Add a task to the workflow."""
        task = TaskDefinition(
            name=name,
            action=action,
            dependencies=dependencies or [],
            **kwargs
        )
        self.tasks.append(task)
        return task.id
    
    def get_task(self, task_id: str) -> Optional[TaskDefinition]:
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id or task.name == task_id:
                return task
        return None
    
    def get_execution_order(self) -> List[List[TaskDefinition]]:
        """Get tasks in topological order (parallelizable batches)."""
        # Build dependency graph
        task_map = {t.id: t for t in self.tasks}
        task_map.update({t.name: t for t in self.tasks})
        
        in_degree = {t.id: 0 for t in self.tasks}
        dependents = {t.id: [] for t in self.tasks}
        
        for task in self.tasks:
            for dep_id in task.dependencies:
                dep = task_map.get(dep_id)
                if dep:
                    in_degree[task.id] += 1
                    dependents[dep.id].append(task.id)
        
        # Kahn's algorithm with level tracking
        levels: List[List[TaskDefinition]] = []
        current_level = [t for t in self.tasks if in_degree[t.id] == 0]
        
        while current_level:
            levels.append(current_level)
            next_level = []
            
            for task in current_level:
                for dep_id in dependents[task.id]:
                    in_degree[dep_id] -= 1
                    if in_degree[dep_id] == 0:
                        dep_task = task_map[dep_id]
                        if dep_task not in next_level:
                            next_level.append(dep_task)
            
            current_level = next_level
        
        return levels


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    workflow_id: str
    success: bool
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        return self.task_results.get(task_id)


class ExecutionEngine(ABC):
    """Abstract base class for workflow execution engines."""
    
    @abstractmethod
    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        """Execute a workflow synchronously."""
        pass
    
    @abstractmethod
    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        """Execute a workflow asynchronously."""
        pass


class SequentialEngine(ExecutionEngine):
    """Executes tasks sequentially in dependency order."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        context = initial_context or {}
        task_results: Dict[str, TaskResult] = {}
        start_time = datetime.now()
        
        try:
            levels = workflow.get_execution_order()
            
            for level in levels:
                for task in level:
                    result = self._execute_task(task, context, task_results)
                    task_results[task.id] = result
                    
                    if result.state == TaskState.FAILED:
                        return WorkflowResult(
                            workflow_id=workflow.id,
                            success=False,
                            task_results=task_results,
                            start_time=start_time,
                            end_time=datetime.now(),
                            error=f"Task {task.name} failed: {result.error}",
                        )
                    
                    context[task.id] = result.output
                    context[task.name] = result.output
            
            return WorkflowResult(
                workflow_id=workflow.id,
                success=True,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
            )
            
        except Exception as e:
            return WorkflowResult(
                workflow_id=workflow.id,
                success=False,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )
    
    def _execute_task(
        self,
        task: TaskDefinition,
        context: Dict[str, Any],
        previous_results: Dict[str, TaskResult],
    ) -> TaskResult:
        # Check condition
        if task.condition and not task.condition(context):
            return TaskResult(
                task_id=task.id,
                state=TaskState.SKIPPED,
            )
        
        attempts = 0
        max_attempts = task.retries + 1
        last_error = None
        
        while attempts < max_attempts:
            attempts += 1
            start_time = datetime.now()
            
            try:
                if task.action:
                    output = task.action(context)
                else:
                    output = None
                
                return TaskResult(
                    task_id=task.id,
                    state=TaskState.COMPLETED,
                    output=output,
                    start_time=start_time,
                    end_time=datetime.now(),
                    attempts=attempts,
                )
                
            except Exception as e:
                last_error = str(e)
                if attempts < max_attempts:
                    time.sleep(task.retry_delay)
        
        return TaskResult(
            task_id=task.id,
            state=TaskState.FAILED,
            error=last_error,
            start_time=start_time,
            end_time=datetime.now(),
            attempts=attempts,
        )
    
    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.execute,
            workflow,
            initial_context,
        )


class ParallelEngine(ExecutionEngine):
    """Executes independent tasks in parallel."""
    
    def __init__(
        self,
        max_workers: int = 4,
        max_retries: int = 3,
    ):
        self.max_workers = max_workers
        self.max_retries = max_retries
    
    def execute(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        context = initial_context or {}
        task_results: Dict[str, TaskResult] = {}
        start_time = datetime.now()
        context_lock = threading.Lock()
        
        try:
            levels = workflow.get_execution_order()
            
            for level in levels:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {
                        executor.submit(
                            self._execute_task,
                            task,
                            dict(context),
                            task_results,
                        ): task
                        for task in level
                    }
                    
                    for future in as_completed(futures):
                        task = futures[future]
                        try:
                            result = future.result()
                            
                            with context_lock:
                                task_results[task.id] = result
                                if result.state == TaskState.COMPLETED:
                                    context[task.id] = result.output
                                    context[task.name] = result.output
                            
                            if result.state == TaskState.FAILED:
                                # Cancel remaining tasks
                                for f in futures:
                                    f.cancel()
                                
                                return WorkflowResult(
                                    workflow_id=workflow.id,
                                    success=False,
                                    task_results=task_results,
                                    start_time=start_time,
                                    end_time=datetime.now(),
                                    error=f"Task {task.name} failed",
                                )
                                
                        except Exception as e:
                            task_results[task.id] = TaskResult(
                                task_id=task.id,
                                state=TaskState.FAILED,
                                error=str(e),
                            )
            
            return WorkflowResult(
                workflow_id=workflow.id,
                success=True,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
            )
            
        except Exception as e:
            return WorkflowResult(
                workflow_id=workflow.id,
                success=False,
                task_results=task_results,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )
    
    def _execute_task(
        self,
        task: TaskDefinition,
        context: Dict[str, Any],
        previous_results: Dict[str, TaskResult],
    ) -> TaskResult:
        if task.condition and not task.condition(context):
            return TaskResult(task_id=task.id, state=TaskState.SKIPPED)
        
        attempts = 0
        max_attempts = task.retries + 1
        
        while attempts < max_attempts:
            attempts += 1
            start_time = datetime.now()
            
            try:
                output = task.action(context) if task.action else None
                return TaskResult(
                    task_id=task.id,
                    state=TaskState.COMPLETED,
                    output=output,
                    start_time=start_time,
                    end_time=datetime.now(),
                    attempts=attempts,
                )
            except Exception as e:
                if attempts < max_attempts:
                    time.sleep(task.retry_delay)
                else:
                    return TaskResult(
                        task_id=task.id,
                        state=TaskState.FAILED,
                        error=str(e),
                        start_time=start_time,
                        end_time=datetime.now(),
                        attempts=attempts,
                    )
        
        return TaskResult(task_id=task.id, state=TaskState.FAILED)
    
    async def execute_async(
        self,
        workflow: WorkflowDefinition,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, workflow, initial_context)


def create_engine(engine_type: str = "parallel", **kwargs) -> ExecutionEngine:
    """Factory function for execution engines."""
    engines = {
        "sequential": SequentialEngine,
        "parallel": ParallelEngine,
    }
    
    engine_class = engines.get(engine_type)
    if not engine_class:
        raise ValueError(f"Unknown engine type: {engine_type}")
    
    return engine_class(**kwargs)


__all__ = [
    "TaskState",
    "TaskDefinition",
    "TaskResult",
    "WorkflowDefinition",
    "WorkflowResult",
    "ExecutionEngine",
    "SequentialEngine",
    "ParallelEngine",
    "create_engine",
]
