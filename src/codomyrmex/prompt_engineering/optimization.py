"""
Prompt Optimization Utilities

Provides strategies and tools for transforming prompt templates
to improve clarity, token efficiency, and model response quality.
"""

from __future__ import annotations

import re
import textwrap
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .templates import PromptTemplate


class OptimizationStrategy(Enum):
    """Available prompt optimization strategies."""

    CONCISE = "concise"
    DETAILED = "detailed"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"


@dataclass
class OptimizationResult:
    """Result of a prompt optimization operation."""

    original: PromptTemplate
    optimized: PromptTemplate
    strategy: OptimizationStrategy
    changes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_reduction_estimate(self) -> float:
        """
        Estimate the token reduction as a ratio.

        Uses a rough word-based estimate (not tiktoken) to give
        a directional sense of compression.

        Returns:
            Ratio of optimized length to original length (< 1.0 means shorter).
        """
        original_words = len(self.original.template_str.split())
        optimized_words = len(self.optimized.template_str.split())
        if original_words == 0:
            return 1.0
        return optimized_words / original_words

    def to_dict(self) -> dict[str, Any]:
        """Convert optimization result to dictionary."""
        return {
            "original": self.original.to_dict(),
            "optimized": self.optimized.to_dict(),
            "strategy": self.strategy.value,
            "changes": self.changes,
            "token_reduction_estimate": self.token_reduction_estimate,
            "metadata": self.metadata,
        }


class PromptOptimizer:
    """
    Applies optimization strategies to prompt templates.

    Each strategy transforms the template content in a specific way
    to optimize for different goals (brevity, reasoning depth, etc.).
    """

    def __init__(self) -> None:
        self._strategy_handlers = {
            OptimizationStrategy.CONCISE: self._optimize_concise,
            OptimizationStrategy.DETAILED: self._optimize_detailed,
            OptimizationStrategy.CHAIN_OF_THOUGHT: self._optimize_chain_of_thought,
            OptimizationStrategy.FEW_SHOT: self._optimize_few_shot,
        }
        self._few_shot_examples: list[dict[str, str]] = []

    def set_few_shot_examples(self, examples: list[dict[str, str]]) -> None:
        """
        Set examples for the few-shot optimization strategy.

        Args:
            examples: List of dicts with "input" and "output" keys.
        """
        self._few_shot_examples = examples

    def optimize(
        self,
        template: PromptTemplate,
        strategy: OptimizationStrategy,
        **kwargs: Any,
    ) -> OptimizationResult:
        """
        Optimize a prompt template using the specified strategy.

        Args:
            template: The template to optimize.
            strategy: The optimization strategy to apply.
            **kwargs: Strategy-specific options.

        Returns:
            OptimizationResult with original and optimized templates.

        Raises:
            ValueError: If the strategy is not recognized.
        """
        handler = self._strategy_handlers.get(strategy)
        if handler is None:
            raise ValueError(f"Unknown optimization strategy: {strategy}")

        optimized_str, changes = handler(template.template_str, **kwargs)

        optimized_template = PromptTemplate(
            name=f"{template.name}_optimized_{strategy.value}",
            template_str=optimized_str,
            variables=list(template.variables),
            version=template.version,
            metadata={
                **template.metadata,
                "optimization_strategy": strategy.value,
                "source_template": template.name,
            },
        )

        return OptimizationResult(
            original=template,
            optimized=optimized_template,
            strategy=strategy,
            changes=changes,
        )

    def _optimize_concise(self, text: str, **kwargs: Any) -> tuple[str, list[str]]:
        """
        Apply concise optimization: reduce verbosity while preserving meaning.

        Removes filler phrases, collapses whitespace, and strips redundant
        instruction preambles.
        """
        changes: list[str] = []
        result = text

        # Remove common filler phrases
        filler_patterns = [
            (r"\bplease\s+", ""),
            (r"\bkindly\s+", ""),
            (r"\bI would like you to\s+", ""),
            (r"\bCould you please\s+", ""),
            (r"\bI want you to\s+", ""),
            (r"\bI need you to\s+", ""),
            (r"\bMake sure to\s+", ""),
            (r"\bBe sure to\s+", ""),
        ]

        for pattern, replacement in filler_patterns:
            new_result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            if new_result != result:
                changes.append(f"Removed filler matching '{pattern}'")
                result = new_result

        # Collapse multiple blank lines into one
        collapsed = re.sub(r"\n{3,}", "\n\n", result)
        if collapsed != result:
            changes.append("Collapsed multiple blank lines")
            result = collapsed

        # Strip trailing whitespace on each line
        stripped = "\n".join(line.rstrip() for line in result.split("\n"))
        if stripped != result:
            changes.append("Stripped trailing whitespace")
            result = stripped

        result = result.strip()

        if not changes:
            changes.append("No concise optimizations applicable")

        return result, changes

    def _optimize_detailed(self, text: str, **kwargs: Any) -> tuple[str, list[str]]:
        """
        Apply detailed optimization: add structure and explicit instructions.

        Wraps the prompt with clear section headers and output format guidance.
        """
        changes: list[str] = []

        sections = []

        # Add role context if not present
        if not re.search(r"(?i)(you are|role:|act as)", text):
            sections.append("## Role\nYou are a helpful assistant.")
            changes.append("Added role context section")

        # Add the original task section
        sections.append(f"## Task\n{text.strip()}")
        changes.append("Wrapped original prompt in Task section")

        # Add constraints section if not present
        if not re.search(r"(?i)(constraint|requirement|rule|must|should)", text):
            sections.append(
                "## Constraints\n"
                "- Be accurate and factual\n"
                "- If unsure, state your uncertainty\n"
                "- Provide actionable output"
            )
            changes.append("Added constraints section")

        # Add output format section if not present
        if not re.search(r"(?i)(format|output|respond)", text):
            sections.append(
                "## Output Format\n"
                "Provide a clear, structured response."
            )
            changes.append("Added output format section")

        result = "\n\n".join(sections)
        return result, changes

    def _optimize_chain_of_thought(
        self, text: str, **kwargs: Any
    ) -> tuple[str, list[str]]:
        """
        Apply chain-of-thought optimization: add step-by-step reasoning scaffold.

        Prepends a thinking instruction and appends a step-by-step framework
        to encourage systematic reasoning.
        """
        changes: list[str] = []

        parts = [text.strip()]

        # Add thinking preamble if not already present
        if not re.search(r"(?i)(step[- ]by[- ]step|think|reason)", text):
            parts.insert(
                0,
                "Think through this step-by-step before providing your final answer.",
            )
            changes.append("Added step-by-step thinking preamble")

        # Add reasoning scaffold
        scaffold = textwrap.dedent("""\

            Follow this reasoning process:
            1. Identify the key elements of the problem
            2. Break down the problem into sub-parts
            3. Analyze each sub-part systematically
            4. Synthesize findings into a coherent answer
            5. Verify your reasoning for consistency""").strip()

        if "reasoning process" not in text.lower():
            parts.append(scaffold)
            changes.append("Added reasoning scaffold with 5-step framework")

        # Add answer delimiter
        parts.append(
            "After your reasoning, provide your final answer prefixed with "
            "'ANSWER:' on its own line."
        )
        changes.append("Added explicit answer delimiter instruction")

        result = "\n\n".join(parts)
        return result, changes

    def _optimize_few_shot(self, text: str, **kwargs: Any) -> tuple[str, list[str]]:
        """
        Apply few-shot optimization: inject examples before the actual prompt.

        Uses examples set via set_few_shot_examples(), or accepts them
        through the 'examples' kwarg.
        """
        changes: list[str] = []

        examples = kwargs.get("examples", self._few_shot_examples)

        parts = []

        if examples:
            parts.append("Here are some examples:\n")
            for i, ex in enumerate(examples, 1):
                input_text = ex.get("input", "")
                output_text = ex.get("output", "")
                parts.append(
                    f"Example {i}:\n"
                    f"Input: {input_text}\n"
                    f"Output: {output_text}"
                )
            changes.append(f"Added {len(examples)} few-shot example(s)")
        else:
            parts.append(
                "# Note: No examples provided.\n"
                "# Use set_few_shot_examples() or pass 'examples' kwarg "
                "to add few-shot examples."
            )
            changes.append("No examples available; added placeholder note")

        parts.append(f"Now complete the following:\n\n{text.strip()}")
        changes.append("Appended original prompt after examples")

        result = "\n\n".join(parts)
        return result, changes

    def bulk_optimize(
        self,
        templates: list[PromptTemplate],
        strategy: OptimizationStrategy,
        **kwargs: Any,
    ) -> list[OptimizationResult]:
        """
        Optimize multiple templates with the same strategy.

        Args:
            templates: List of templates to optimize.
            strategy: The optimization strategy to apply to all.
            **kwargs: Strategy-specific options passed to each optimization.

        Returns:
            List of OptimizationResult objects.
        """
        return [self.optimize(t, strategy, **kwargs) for t in templates]

    def available_strategies(self) -> list[str]:
        """
        List available optimization strategy names.

        Returns:
            Sorted list of strategy value strings.
        """
        return sorted(s.value for s in OptimizationStrategy)


__all__ = [
    "OptimizationStrategy",
    "OptimizationResult",
    "PromptOptimizer",
]
