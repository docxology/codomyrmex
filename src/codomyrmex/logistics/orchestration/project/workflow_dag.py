from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional, Any
import logging

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger







"""
Workflow DAG (Directed Acyclic Graph) Implementation for Codomyrmex

This module provides comprehensive DAG functionality for complex workflow management,
including dependency resolution, cycle detection, topological sorting, and visualization.
"""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class DAGValidationError(Exception):
    """Exception raised when DAG validation fails."""
    pass

class CycleDetectedError(DAGValidationError):
    """Exception raised when a cycle is detected in the DAG."""
    pass

class TaskStatus(Enum):
    """Status of a task in the workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class DAGTask:
    """Represents a task in the DAG."""
    name: str
    module: str
    action: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    execution_order: int = -1
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "name": self.name,
            "module": self.module,
            "action": self.action,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "status": self.status.value,
            "execution_order": self.execution_order,
            "result": self.result,
            "error": self.error
        }

class WorkflowDAG:
    """
    Directed Acyclic Graph implementation for workflow management.

    Provides functionality for:
    - Task dependency management
    - Cycle detection
    - Topological sorting
    - Execution order determination
    - Visualization generation
    """

    def __init__(self, tasks: Optional[List[Dict]] = None):
        """
        Initialize the DAG with optional tasks.

        Args:
            tasks: List of task dictionaries to initialize the DAG with
        """
        self.tasks: Dict[str, DAGTask] = {}
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependents

        if tasks:
            for task_dict in tasks:
                self.add_task(task_dict)

    def add_task(self, task_dict: Dict[str, Any]) -> None:
        """
        Add a task to the DAG.

        Args:
            task_dict: Dictionary containing task information
        """
        task = DAGTask(
            name=task_dict["name"],
            module=task_dict.get("module", ""),
            action=task_dict.get("action", ""),
            dependencies=task_dict.get("dependencies", []),
            parameters=task_dict.get("parameters", {})
        )

        self.tasks[task.name] = task

        # Add dependencies to graph
        for dep in task.dependencies:
            self.graph[task.name].add(dep)
            self.reverse_graph[dep].add(task.name)

    def add_dependency(self, task_name: str, depends_on: str) -> None:
        """
        Add a dependency between two tasks.

        Args:
            task_name: Name of the task that depends on another
            depends_on: Name of the task being depended on
        """
        if task_name not in self.tasks:
            raise ValueError(f"Task '{task_name}' not found in DAG")
        if depends_on not in self.tasks:
            raise ValueError(f"Dependency task '{depends_on}' not found in DAG")

        self.tasks[task_name].dependencies.append(depends_on)
        self.graph[task_name].add(depends_on)
        self.reverse_graph[depends_on].add(task_name)

    def validate_dag(self) -> Tuple[bool, List[str]]:
        """
        Validate the DAG for cycles and other issues.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for cycles
        try:
            self._detect_cycles()
        except CycleDetectedError as e:
            errors.append(str(e))

        # Check for missing dependencies
        for task_name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task '{task_name}' depends on missing task '{dep}'")

        # Check for self-dependencies
        for task_name, task in self.tasks.items():
            if task_name in task.dependencies:
                errors.append(f"Task '{task_name}' cannot depend on itself")

        return len(errors) == 0, errors

    def _detect_cycles(self) -> None:
        """
        Detect cycles in the DAG using DFS.

        Raises:
            CycleDetectedError: If a cycle is detected
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> None:
            """
            Depth-First Search to detect cycles.
            
            Args:
                node: The starting node identifier.
            """
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle = self._find_cycle(node, neighbor)
                    raise CycleDetectedError(f"Cycle detected in DAG: {' -> '.join(cycle)}")

            rec_stack.remove(node)

        for node in self.tasks:
            if node not in visited:
                dfs(node)

    def _find_cycle(self, start: str, end: str) -> List[str]:
        """Find the cycle path from start to end."""
        # Simple cycle reconstruction
        path = [start]
        current = start

        while current != end:
            # Find next node in path to end
            for neighbor in self.graph[current]:
                if neighbor == end or neighbor in path:
                    if neighbor not in path:
                        path.append(neighbor)
                    current = neighbor
                    break
            else:
                # Should not happen if cycle exists
                break

        path.append(end)
        return path

    def get_execution_order(self) -> List[List[str]]:
        """
        Get the topological execution order of tasks.

        Returns:
            List of lists, where each inner list contains tasks that can be
            executed in parallel at that level
        """
        # Validate DAG first
        is_valid, errors = self.validate_dag()
        if not is_valid:
            raise DAGValidationError(f"DAG validation failed: {errors}")

        # Kahn's algorithm for topological sorting
        in_degree = {task: len(deps) for task, deps in self.graph.items()}
        queue = deque([task for task in self.tasks if in_degree[task] == 0])
        result = []
        processed = 0

        while queue:
            level = []
            level_size = len(queue)

            for _ in range(level_size):
                task = queue.popleft()
                level.append(task)
                processed += 1

                # Update in-degrees of dependents
                for dependent in self.reverse_graph[task]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            result.append(level)

        if processed != len(self.tasks):
            raise DAGValidationError("DAG contains cycles or unreachable tasks")

        return result

    def get_task_dependencies(self, task_name: str) -> List[str]:
        """
        Get all dependencies of a task (recursive).

        Args:
            task_name: Name of the task

        Returns:
            List of all dependency task names
        """
        if task_name not in self.tasks:
            return []

        dependencies = set()
        stack = list(self.tasks[task_name].dependencies)

        while stack:
            dep = stack.pop()
            if dep not in dependencies:
                dependencies.add(dep)
                # Add transitive dependencies
                if dep in self.tasks:
                    stack.extend(self.tasks[dep].dependencies)

        return list(dependencies)

    def get_dependent_tasks(self, task_name: str) -> List[str]:
        """
        Get all tasks that depend on the given task (recursive).

        Args:
            task_name: Name of the task

        Returns:
            List of all dependent task names
        """
        if task_name not in self.tasks:
            return []

        dependents = set()
        stack = list(self.reverse_graph[task_name])

        while stack:
            dep = stack.pop()
            if dep not in dependents:
                dependents.add(dep)
                # Add transitive dependents
                stack.extend(self.reverse_graph[dep])

        return list(dependents)

    def visualize(self) -> str:
        """
        Generate a Mermaid diagram for the DAG.

        Returns:
            Mermaid diagram as a string
        """
        lines = ["graph TD"]

        # Add nodes
        for task_name, task in self.tasks.items():
            label = f"{task_name}\\n{task.module}:{task.action}"
            lines.append(f"    {task_name}[\"{label}\"]")

        # Add edges
        added_edges = set()
        for task_name, deps in self.graph.items():
            for dep in deps:
                edge_key = (dep, task_name)
                if edge_key not in added_edges:
                    lines.append(f"    {dep} --> {task_name}")
                    added_edges.add(edge_key)

        return "\\n".join(lines)

    def get_task(self, task_name: str) -> Optional[DAGTask]:
        """Get a task by name."""
        return self.tasks.get(task_name)

    def get_all_tasks(self) -> Dict[str, DAGTask]:
        """Get all tasks in the DAG."""
        return self.tasks.copy()

    def reset_task_statuses(self) -> None:
        """Reset all task statuses to PENDING."""
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.error = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire DAG to a dictionary."""
        return {
            "tasks": {name: task.to_dict() for name, task in self.tasks.items()},
            "graph": {task: list(deps) for task, deps in self.graph.items()},
            "reverse_graph": {task: list(deps) for task, deps in self.reverse_graph.items()}
        }
