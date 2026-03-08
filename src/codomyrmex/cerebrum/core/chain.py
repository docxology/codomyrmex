from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from codomyrmex.cerebrum.core.memory import WorkingMemory
from codomyrmex.logging_monitoring import get_logger

"""Chain-of-thought reasoning implementation."""

logger = get_logger(__name__)


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain."""

    description: str
    action: Callable[[WorkingMemory], Any] | None = None
    result: Any = None
    status: str = "pending"  # pending, completed, failed


class ReasoningChain:
    """Orchestrates a sequence of reasoning steps."""

    def __init__(self):
        """Initialize reasoning chain."""
        self.steps: list[ReasoningStep] = []
        self.logger = get_logger(__name__)

    def add_step(
        self, description: str, action: Callable[[WorkingMemory], Any] | None = None
    ) -> None:
        """Add a step to the reasoning chain.

        Args:
            description: Description of the step
            action: Optional callable to execute for this step
        """
        self.steps.append(ReasoningStep(description=description, action=action))
        self.logger.debug("Added reasoning step: %s", description)

    def execute(self, memory: WorkingMemory) -> "ChainExecutionResult":
        """Execute all steps in the chain.

        Args:
            memory: Working memory to use and update

        Returns:
            Execution result
        """
        self.logger.info("Executing reasoning chain with %s steps", len(self.steps))
        completed_steps = 0
        for step in self.steps:
            try:
                if step.action:
                    step.result = step.action(memory)
                step.status = "completed"
                completed_steps += 1
                self.logger.debug("Completed step: %s", step.description)
            except Exception as e:
                step.status = "failed"
                step.result = str(e)
                self.logger.error("Failed step: %s - %s", step.description, e)
                break

        return ChainExecutionResult(
            steps_completed=completed_steps,
            total_steps=len(self.steps),
            steps=self.steps,
        )


@dataclass
class ChainExecutionResult:
    """Result of executing a reasoning chain."""

    steps_completed: int
    total_steps: int
    steps: list[ReasoningStep]

    @property
    def success(self) -> bool:
        """Check if all steps were completed."""
        return self.steps_completed == self.total_steps
