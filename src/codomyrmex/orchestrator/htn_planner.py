"""Hierarchical Task Network (HTN) Planner.

Provides multi-scale temporal abstraction by decomposing high-level
compound objectives into primitive actionable operators that can
be executed by agents. Supports recursive exploration and state
backtracking for complex non-deterministic domains.
"""

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class State:
    """Represents the current state of the world."""

    facts: dict[str, Any]

    def copy(self) -> "State":
        """Return a deep copy of the state for isolating search paths."""
        return State(facts=copy.deepcopy(self.facts))


class Operator:
    """A primitive action that directly mutates the state."""

    def __init__(self, name: str, action: Callable[[State, Any], bool]):
        """Initialize the operator.

        Args:
            name: Identifier for the operator.
            action: A callable function taking (State, *args) and modifying state in-place.
                    It should return True if successful, False if preconditions aren't met.
        """
        self.name = name
        self.action = action

    def apply(self, state: State, *args: Any) -> bool:
        """Apply the conditional operator to the given state."""
        return self.action(state, *args)


class Method:
    """Decomposes a compound task into a subtask network."""

    def __init__(
        self,
        name: str,
        preconditions: Callable[[State, Any], bool],
        subtasks_generator: Callable[[State, Any], list[tuple[str, ...]]],
    ):
        """Initialize the decomposition method.

        Args:
            name: Method identifier.
            preconditions: Function checking if method is applicable to current state.
            subtasks_generator: Function returning a list of task tuples to replace the wrapper task.
        """
        self.name = name
        self.preconditions = preconditions
        self.subtasks_generator = subtasks_generator

    def is_applicable(self, state: State, *args: Any) -> bool:
        """Check if method preconditions are met."""
        return self.preconditions(state, *args)

    def decompose(self, state: State, *args: Any) -> list[tuple[str, ...]]:
        """Generate the sequential list of subtasks."""
        return self.subtasks_generator(state, *args)


class HTNPlanner:
    """Hierarchical Task Network Planner engine."""

    def __init__(self) -> None:
        """Initialize empty memory mappings of operators and methods."""
        self.operators: dict[str, Operator] = {}
        # Allows multiple non-deterministic methods mapping to the same compound task name
        self.methods: dict[str, list[Method]] = {}

    def add_operator(self, operator: Operator) -> None:
        """Register a primitive state modification operator."""
        self.operators[operator.name] = operator

    def add_method(self, task_name: str, method: Method) -> None:
        """Register an abstraction method for a compound task."""
        if task_name not in self.methods:
            self.methods[task_name] = []
        self.methods[task_name].append(method)

    def plan(
        self, initial_state: State, tasks: list[tuple[str, ...]]
    ) -> Optional[list[tuple[str, ...]]]:
        """Generate a sequential primitive operator chain to achieve abstract tasks.

        Args:
            initial_state: The starting world knowledge tree state.
            tasks: A list of tasks to accomplish (each is a tuple `(name, *args)`).

        Returns:
            A list of primitive task tuples representing the executable plan,
            or None if planning pathfinding evaluates all trees as insoluble.
        """
        return self._search(initial_state.copy(), tasks, [])

    def _search(
        self,
        state: State,
        tasks: list[tuple[str, ...]],
        current_plan: list[tuple[str, ...]],
    ) -> Optional[list[tuple[str, ...]]]:
        """Recursive graph pathfinding core loop."""
        if not tasks:
            return current_plan

        task = tasks[0]
        task_name = task[0]
        args = task[1:]

        # If it's a primitive operator (base case of tree)
        if task_name in self.operators:
            op = self.operators[task_name]
            # Since operators mutate state in-place natively, we branch off a copy
            # to allow sibling backtracking if subsequent chain operations fail.
            new_state = state.copy()
            if op.apply(new_state, *args):
                result_plan = self._search(new_state, tasks[1:], [*current_plan, task])
                if result_plan is not None:
                    return result_plan
            return None

        # If it's a structural compound mapping target
        if task_name in self.methods:
            for method in self.methods[task_name]:
                if method.is_applicable(state, *args):
                    subtasks = method.decompose(state, *args)
                    # Unspooling Depth-First Replacement replacing the unreduced parent task
                    new_tasks = subtasks + tasks[1:]
                    result_plan = self._search(state, new_tasks, current_plan)
                    if result_plan is not None:
                        return result_plan

        # Total resolution failure
        return None
