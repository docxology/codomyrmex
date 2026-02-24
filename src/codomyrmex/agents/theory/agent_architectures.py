from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

"""Agent architecture patterns and implementations."""

logger = get_logger(__name__)


class ArchitectureType(Enum):
    """Types of agent architectures."""

    REACTIVE = "reactive"
    DELIBERATIVE = "deliberative"
    HYBRID = "hybrid"


class AgentArchitecture(ABC):
    """Abstract base class for agent architectures."""

    def __init__(self, name: str, architecture_type: ArchitectureType):
        """
        Initialize agent architecture.

        Args:
            name: Architecture name
            architecture_type: Type of architecture
        """
        self.name = name
        self.architecture_type = architecture_type
        self.logger = get_logger(f"{__name__}.{name}")

    @abstractmethod
    def perceive(self, environment: dict[str, Any]) -> dict[str, Any]:
        """
        Perceive the environment.

        Args:
            environment: Environment state

        Returns:
            Perceived information
        """
        pass

    @abstractmethod
    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """
        Make a decision based on perception.

        Args:
            perception: Perceived information

        Returns:
            Decision/action
        """
        pass

    @abstractmethod
    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Execute an action.

        Args:
            decision: Decision/action to execute

        Returns:
            Action result
        """
        pass


class ReactiveArchitecture(AgentArchitecture):
    """Reactive agent architecture (stimulus-response)."""

    def __init__(self, name: str = "reactive"):
        """Initialize reactive architecture."""
        super().__init__(name, ArchitectureType.REACTIVE)
        self.rules: list[tuple[callable, callable]] = []

    def add_rule(
        self, condition: callable, action: callable
    ) -> None:
        """
        Add a condition-action rule.

        Args:
            condition: Condition function
            action: Action function
        """
        self.rules.append((condition, action))
        self.logger.debug(f"Added rule: {condition.__name__} -> {action.__name__}")

    def perceive(self, environment: dict[str, Any]) -> dict[str, Any]:
        """Perceive the environment (pass-through for reactive agents)."""
        return environment

    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """
        Make decision based on reactive rules.

        Args:
            perception: Perceived information

        Returns:
            Decision/action
        """
        for condition, action in self.rules:
            if condition(perception):
                self.logger.debug(f"Rule matched: {condition.__name__}")
                return {"action": action, "args": perception}

        return {"action": None, "args": perception}

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Execute action.

        Args:
            decision: Decision/action to execute

        Returns:
            Action result
        """
        action = decision.get("action")
        if action:
            return action(decision.get("args", {}))
        return {"result": "no_action"}


class KnowledgeBase:
    """Simple Knowledge Base for deliberative agents."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.facts: dict[str, Any] = {}
        self.rules: list[callable] = []

    def add_fact(self, key: str, value: Any) -> None:
        """Add or update a fact in the knowledge base."""
        self.facts[key] = value

    def get_fact(self, key: str) -> Any | None:
        """Get a fact by key."""
        return self.facts.get(key)

    def remove_fact(self, key: str) -> bool:
        """Remove a fact from the knowledge base.

        Returns:
            True if fact was removed, False if not found
        """
        if key in self.facts:
            del self.facts[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all facts from the knowledge base."""
        self.facts.clear()

    def has_fact(self, key: str) -> bool:
        """Check if a fact exists."""
        return key in self.facts

    def list_facts(self) -> list[str]:
        """List all fact keys."""
        return list(self.facts.keys())

    def query(self, query_func: callable) -> Any:
        """Query facts using a custom function."""
        return query_func(self.facts)


class DeliberativeArchitecture(AgentArchitecture):
    """Deliberative agent architecture (planning-based)."""

    def __init__(self, name: str = "deliberative"):
        """Initialize deliberative architecture."""
        super().__init__(name, ArchitectureType.DELIBERATIVE)
        self.goals: list[dict[str, Any]] = []
        self.plans: list[dict[str, Any]] = []
        self.kb = KnowledgeBase()

    def set_goal(self, goal: dict[str, Any]) -> None:
        """
        Set a goal for the agent.

        Args:
            goal: Goal description
        """
        self.goals.append(goal)
        self.logger.debug(f"Set goal: {goal}")

    def plan(self, goal: dict[str, Any], current_state: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Create a plan to achieve a goal using knowledge base.

        Args:
            goal: Goal to achieve
            current_state: Current state

        Returns:
            List of actions (plan)
        """
        # Store current state in KB
        for k, v in current_state.items():
            self.kb.add_fact(f"state_{k}", v)

        # Simple planning logic (enhanced from placeholder)
        # If goal is "reach_location", and we are at "A", plan is "move_to_B", "move_to_Goal"
        plan = []
        if goal.get("type") == "complex":
             plan.append({"action": "decompose_goal", "goal": goal})
             plan.append({"action": "execute_subgoals"})
        else:
             plan.append({"action": "achieve_goal", "goal": goal, "context": self.kb.facts})

        self.plans.append(plan)
        self.logger.debug(f"Created plan for goal: {goal}")
        return plan

    def perceive(self, environment: dict[str, Any]) -> dict[str, Any]:
        """
        Perceive and interpret the environment.

        Args:
            environment: Environment state

        Returns:
            Interpreted perception
        """
        # Update KB with new perceptions
        for k, v in environment.items():
            self.kb.add_fact(k, v)

        return {
            "raw": environment,
            "interpreted": self._interpret(environment),
        }

    def _interpret(self, environment: dict[str, Any]) -> dict[str, Any]:
        """Interpret environment state."""
        return environment

    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """
        Make decision through planning.

        Args:
            perception: Perceived information

        Returns:
            Decision/action
        """
        if not self.goals:
            return {"action": None, "plan": []}

        goal = self.goals[0]
        # Plan based on interpreted state
        plan = self.plan(goal, perception.get("interpreted", {}))

        if plan:
            next_action = plan[0]
            return {"action": next_action, "plan": plan}
        return {"action": None, "plan": []}

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Execute planned action.

        Args:
            decision: Decision/action to execute

        Returns:
            Action result
        """
        action = decision.get("action")
        if action:
            self.logger.info(f"Executing deliberative action: {action}")
            return {"result": "executed", "action": action}
        return {"result": "no_action"}


class HybridArchitecture(AgentArchitecture):
    """Hybrid agent architecture (combines reactive and deliberative)."""

    def __init__(self, name: str = "hybrid"):
        """Initialize hybrid architecture."""
        super().__init__(name, ArchitectureType.HYBRID)
        self.reactive = ReactiveArchitecture("reactive_layer")
        self.deliberative = DeliberativeArchitecture("deliberative_layer")
        self.mode: str = "reactive"  # or "deliberative"

    def perceive(self, environment: dict[str, Any]) -> dict[str, Any]:
        """Perceive using both layers."""
        reactive_perception = self.reactive.perceive(environment)
        deliberative_perception = self.deliberative.perceive(environment)
        return {
            "reactive": reactive_perception,
            "deliberative": deliberative_perception,
        }

    def decide(self, perception: dict[str, Any]) -> dict[str, Any]:
        """
        Make decision using appropriate layer.

        Args:
            perception: Perceived information

        Returns:
            Decision/action
        """
        # Try reactive first
        reactive_decision = self.reactive.decide(perception.get("reactive", {}))
        if reactive_decision.get("action"):
            self.mode = "reactive"
            return reactive_decision

        # Fall back to deliberative
        deliberative_decision = self.deliberative.decide(
            perception.get("deliberative", {})
        )
        self.mode = "deliberative"
        return deliberative_decision

    def act(self, decision: dict[str, Any]) -> dict[str, Any]:
        """
        Execute action using appropriate layer.

        Args:
            decision: Decision/action to execute

        Returns:
            Action result
        """
        if self.mode == "reactive":
            return self.reactive.act(decision)
        else:
            return self.deliberative.act(decision)


