"""
First Principles Framework reasoning utilities.

Provides tools for first principles reasoning and problem decomposition.
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ReasoningStep(Enum):
    """Types of reasoning steps."""
    QUESTION = "question"
    ASSUMPTION = "assumption"
    FACT = "fact"
    INFERENCE = "inference"
    CONCLUSION = "conclusion"
    HYPOTHESIS = "hypothesis"


@dataclass
class Premise:
    """A premise in a reasoning chain."""
    id: str
    content: str
    step_type: ReasoningStep
    confidence: float = 1.0  # 0.0 to 1.0
    source: str | None = None
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "content": self.content,
            "step_type": self.step_type.value,
            "confidence": self.confidence,
            "source": self.source,
            "depends_on": self.depends_on,
        }


@dataclass
class ReasoningChain:
    """A chain of reasoning steps."""
    id: str
    goal: str
    premises: list[Premise] = field(default_factory=list)
    conclusion: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_premise(
        self,
        content: str,
        step_type: ReasoningStep,
        **kwargs
    ) -> Premise:
        """Add a premise to the chain."""
        premise_id = f"p{len(self.premises) + 1}"
        premise = Premise(
            id=premise_id,
            content=content,
            step_type=step_type,
            **kwargs
        )
        self.premises.append(premise)
        return premise

    def get_assumptions(self) -> list[Premise]:
        """Get all assumptions in the chain."""
        return [p for p in self.premises if p.step_type == ReasoningStep.ASSUMPTION]

    def get_facts(self) -> list[Premise]:
        """Get all facts in the chain."""
        return [p for p in self.premises if p.step_type == ReasoningStep.FACT]

    def validate(self) -> list[str]:
        """Validate the reasoning chain."""
        errors = []

        # Check for circular dependencies
        premise_ids = {p.id for p in self.premises}
        for premise in self.premises:
            for dep in premise.depends_on:
                if dep not in premise_ids:
                    errors.append(f"Premise {premise.id} depends on unknown {dep}")

        # Check for unsupported conclusions
        has_inference = any(p.step_type == ReasoningStep.INFERENCE for p in self.premises)
        if self.conclusion and not has_inference:
            errors.append("Conclusion reached without any inference steps")

        return errors

    def calculate_confidence(self) -> float:
        """Calculate overall chain confidence."""
        if not self.premises:
            return 0.0

        # Product of all premise confidences
        confidence = 1.0
        for premise in self.premises:
            confidence *= premise.confidence

        return confidence

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "goal": self.goal,
            "premises": [p.to_dict() for p in self.premises],
            "conclusion": self.conclusion,
            "confidence": self.calculate_confidence(),
            "metadata": self.metadata,
        }


class ReasoningStrategy(ABC):
    """Abstract base class for reasoning strategies."""

    @abstractmethod
    def apply(self, problem: str) -> ReasoningChain:
        """Apply the reasoning strategy to a problem."""
        pass


class DecompositionStrategy(ReasoningStrategy):
    """Break down a problem into smaller components."""

    def __init__(
        self,
        max_depth: int = 3,
        min_component_size: int = 1,
    ):
        """Execute   Init   operations natively."""
        self.max_depth = max_depth
        self.min_component_size = min_component_size

    def apply(self, problem: str) -> ReasoningChain:
        """Execute Apply operations natively."""
        chain = ReasoningChain(
            id="decomposition",
            goal=f"Decompose: {problem}",
        )

        # Add the main problem as a question
        chain.add_premise(
            f"What are the fundamental components of: {problem}?",
            ReasoningStep.QUESTION,
        )

        # Add placeholder for components
        chain.add_premise(
            "Identify sub-problems that can be solved independently",
            ReasoningStep.HYPOTHESIS,
            confidence=0.8,
        )

        return chain


class AssumptionAnalysisStrategy(ReasoningStrategy):
    """Identify and challenge assumptions."""

    def apply(self, problem: str) -> ReasoningChain:
        """Execute Apply operations natively."""
        chain = ReasoningChain(
            id="assumption_analysis",
            goal=f"Analyze assumptions in: {problem}",
        )

        # Question assumptions
        chain.add_premise(
            f"What assumptions are being made about: {problem}?",
            ReasoningStep.QUESTION,
        )

        chain.add_premise(
            "Are these assumptions necessary?",
            ReasoningStep.QUESTION,
        )

        chain.add_premise(
            "What would change if assumptions were different?",
            ReasoningStep.QUESTION,
        )

        return chain


class AnalogicalReasoningStrategy(ReasoningStrategy):
    """Reason by analogy to similar problems."""

    def apply(self, problem: str) -> ReasoningChain:
        """Execute Apply operations natively."""
        chain = ReasoningChain(
            id="analogical",
            goal=f"Find analogies for: {problem}",
        )

        chain.add_premise(
            f"What is the structure of the problem: {problem}?",
            ReasoningStep.QUESTION,
        )

        chain.add_premise(
            "What similar problems have been solved before?",
            ReasoningStep.QUESTION,
        )

        chain.add_premise(
            "How can solutions to similar problems apply here?",
            ReasoningStep.QUESTION,
        )

        return chain


class ContradictionStrategy(ReasoningStrategy):
    """Find contradictions to prove or disprove hypotheses."""

    def apply(self, problem: str) -> ReasoningChain:
        """Execute Apply operations natively."""
        chain = ReasoningChain(
            id="contradiction",
            goal=f"Find contradictions in: {problem}",
        )

        chain.add_premise(
            f"Assume the opposite of the hypothesis in: {problem}",
            ReasoningStep.ASSUMPTION,
            confidence=0.5,
        )

        chain.add_premise(
            "What logical consequences follow from this assumption?",
            ReasoningStep.QUESTION,
        )

        chain.add_premise(
            "Do any of these consequences lead to a contradiction?",
            ReasoningStep.QUESTION,
        )

        return chain


@dataclass
class ProblemSpace:
    """A problem space for exploration."""
    problem: str
    constraints: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    known_facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "problem": self.problem,
            "constraints": self.constraints,
            "objectives": self.objectives,
            "known_facts": self.known_facts,
            "assumptions": self.assumptions,
        }


class FirstPrinciplesReasoner:
    """Main reasoning engine using first principles."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.strategies: dict[str, ReasoningStrategy] = {
            "decomposition": DecompositionStrategy(),
            "assumption_analysis": AssumptionAnalysisStrategy(),
            "analogical": AnalogicalReasoningStrategy(),
            "contradiction": ContradictionStrategy(),
        }
        self.reasoning_history: list[ReasoningChain] = []

    def add_strategy(self, name: str, strategy: ReasoningStrategy) -> None:
        """Add a custom reasoning strategy."""
        self.strategies[name] = strategy

    def reason(
        self,
        problem: str,
        strategy_name: str = "decomposition",
    ) -> ReasoningChain:
        """Apply a reasoning strategy to a problem."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy = self.strategies[strategy_name]
        chain = strategy.apply(problem)
        self.reasoning_history.append(chain)

        return chain

    def decompose(self, problem: str) -> list[str]:
        """Decompose a problem into sub-problems."""
        # Perform rigorous sentence-level tokenization or structural splitting
        parts = [p.strip() for p in problem.replace(';', '.').replace('\n', '.').split('.') if p.strip()]

        if not parts:
            return [problem]

        components = []
        for part in parts:
            if len(part.split()) > 10:
                # Sub-split long sentences on conjunctions
                sub_parts = [s.strip() for s in part.replace(' and ', ' | ').replace(' or ', ' | ').replace(', but ', ' | ').split(' | ') if s.strip()]
                components.extend(sub_parts)
            else:
                components.append(part)

        return components if components else [problem]

    def identify_assumptions(self, statement: str) -> list[str]:
        """Identify potential assumptions in a statement."""
        assumptions = []

        # Common assumption indicators
        indicators = [
            "always", "never", "must", "should",
            "obviously", "clearly", "certainly",
            "everyone", "no one", "all", "none",
        ]

        statement_lower = statement.lower()
        for indicator in indicators:
            if indicator in statement_lower:
                assumptions.append(
                    f"Assumption implied by '{indicator}': {statement}"
                )

        return assumptions

    def apply_all_strategies(self, problem: str) -> list[ReasoningChain]:
        """Apply all available strategies to a problem."""
        results = []
        for name in self.strategies:
            chain = self.reason(problem, name)
            results.append(chain)
        return results

    def get_history(self) -> list[dict[str, Any]]:
        """Get reasoning history."""
        return [chain.to_dict() for chain in self.reasoning_history]


def create_reasoner() -> FirstPrinciplesReasoner:
    """Create a first principles reasoner."""
    return FirstPrinciplesReasoner()


__all__ = [
    "ReasoningStep",
    "Premise",
    "ReasoningChain",
    "ReasoningStrategy",
    "DecompositionStrategy",
    "AssumptionAnalysisStrategy",
    "AnalogicalReasoningStrategy",
    "ContradictionStrategy",
    "ProblemSpace",
    "FirstPrinciplesReasoner",
    "create_reasoner",
]
