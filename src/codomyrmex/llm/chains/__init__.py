"""
Chain implementations for LLM reasoning.

Provides chain-of-thought, reasoning, and multi-step processing patterns.
"""

import json
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')


class ChainType(Enum):
    """Types of chains."""
    SIMPLE = "simple"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    MAP_REDUCE = "map_reduce"
    ROUTER = "router"


@dataclass
class ChainStep:
    """A single step in a chain."""
    name: str
    prompt_template: str
    output_key: str = "output"
    input_keys: list[str] = field(default_factory=list)
    parser: Callable[[str], Any] | None = None

    def format_prompt(self, context: dict[str, Any]) -> str:
        """Format the prompt template with context values."""
        prompt = self.prompt_template
        for key, value in context.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt

    def parse_output(self, output: str) -> Any:
        """Parse the output using the configured parser."""
        if self.parser:
            return self.parser(output)
        return output


@dataclass
class ChainResult:
    """Result of running a chain."""
    success: bool
    output: Any
    steps: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def get_step_output(self, step_name: str) -> Any | None:
        """Get output from a specific step."""
        for step in self.steps:
            if step.get("name") == step_name:
                return step.get("output")
        return None


class Chain(ABC):
    """Abstract base class for chains."""

    chain_type: ChainType

    def __init__(self, name: str = "chain"):
        self.name = name
        self.steps: list[ChainStep] = []

    @abstractmethod
    def run(self, input_data: dict[str, Any], llm_func: Callable[[str], str]) -> ChainResult:
        """Run the chain with input data."""
        pass

    def add_step(self, step: ChainStep) -> 'Chain':
        """Add a step to the chain."""
        self.steps.append(step)
        return self


class SimpleChain(Chain):
    """A simple single-step chain."""

    chain_type = ChainType.SIMPLE

    def __init__(self, prompt_template: str, name: str = "simple_chain"):
        super().__init__(name)
        self.prompt_template = prompt_template

    def run(self, input_data: dict[str, Any], llm_func: Callable[[str], str]) -> ChainResult:
        """Run the operation."""
        try:
            prompt = self.prompt_template
            for key, value in input_data.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))

            output = llm_func(prompt)

            return ChainResult(
                success=True,
                output=output,
                context=input_data,
                steps=[{"name": self.name, "prompt": prompt, "output": output}],
            )
        except Exception as e:
            return ChainResult(success=False, output=None, error=str(e))


class SequentialChain(Chain):
    """A chain that runs steps sequentially, passing context between them."""

    chain_type = ChainType.SEQUENTIAL

    def run(self, input_data: dict[str, Any], llm_func: Callable[[str], str]) -> ChainResult:
        """Run the operation."""
        context = dict(input_data)
        step_results = []

        try:
            for step in self.steps:
                prompt = step.format_prompt(context)
                output = llm_func(prompt)
                parsed_output = step.parse_output(output)

                context[step.output_key] = parsed_output
                step_results.append({
                    "name": step.name,
                    "prompt": prompt,
                    "output": parsed_output,
                })

            return ChainResult(
                success=True,
                output=context.get(self.steps[-1].output_key if self.steps else "output"),
                steps=step_results,
                context=context,
            )
        except Exception as e:
            return ChainResult(
                success=False,
                output=None,
                steps=step_results,
                context=context,
                error=str(e),
            )


class ChainOfThought(SequentialChain):
    """A chain that implements chain-of-thought reasoning."""

    def __init__(self, name: str = "cot_chain"):
        super().__init__(name)

        # Add reasoning step
        self.add_step(ChainStep(
            name="reasoning",
            prompt_template="""Think through this step-by-step:

Question: {question}

Let's approach this systematically:
1. First, let me understand what's being asked...
2. Then, I'll consider the relevant information...
3. Finally, I'll work through to the answer...

Reasoning:""",
            output_key="reasoning",
        ))

        # Add answer extraction step
        self.add_step(ChainStep(
            name="answer",
            prompt_template="""Based on this reasoning:
{reasoning}

Now provide a clear, concise answer to: {question}

Answer:""",
            output_key="answer",
        ))


class ReActChain(Chain):
    """A chain implementing the ReAct (Reason + Act) pattern."""

    chain_type = ChainType.SEQUENTIAL

    def __init__(
        self,
        tools: dict[str, Callable[[str], str]],
        max_iterations: int = 5,
        name: str = "react_chain"
    ):
        super().__init__(name)
        self.tools = tools
        self.max_iterations = max_iterations

    def run(self, input_data: dict[str, Any], llm_func: Callable[[str], str]) -> ChainResult:
        """Run the operation."""
        context = dict(input_data)
        step_results = []
        scratchpad = ""

        tool_descriptions = "\n".join(
            f"- {name}: Use this tool by writing 'Action: {name}[input]'"
            for name in self.tools.keys()
        )

        base_prompt = f"""Answer the following question using the available tools.

Available Tools:
{tool_descriptions}
- Finish: Use 'Action: Finish[answer]' when you have the final answer.

Question: {{question}}

Use this format:
Thought: [your reasoning about what to do next]
Action: [ToolName][input to the tool]

{{scratchpad}}

Thought:"""

        try:
            for i in range(self.max_iterations):
                prompt = base_prompt.format(
                    question=context.get("question", ""),
                    scratchpad=scratchpad
                )

                response = llm_func(prompt)

                # Parse action
                action_match = re.search(r'Action:\s*(\w+)\[(.*?)\]', response, re.DOTALL)
                if action_match:
                    tool_name = action_match.group(1)
                    tool_input = action_match.group(2).strip()

                    if tool_name == "Finish":
                        return ChainResult(
                            success=True,
                            output=tool_input,
                            steps=step_results,
                            context=context,
                        )

                    if tool_name in self.tools:
                        observation = self.tools[tool_name](tool_input)
                        scratchpad += f"\nThought: {response}\nObservation: {observation}"
                        step_results.append({
                            "name": f"step_{i}",
                            "thought": response,
                            "action": tool_name,
                            "action_input": tool_input,
                            "observation": observation,
                        })
                    else:
                        scratchpad += f"\nThought: {response}\nObservation: Tool '{tool_name}' not found."
                else:
                    scratchpad += f"\nThought: {response}"

            return ChainResult(
                success=False,
                output=None,
                steps=step_results,
                context=context,
                error="Max iterations reached",
            )
        except Exception as e:
            return ChainResult(
                success=False,
                output=None,
                steps=step_results,
                error=str(e),
            )


def create_chain(chain_type: ChainType, **kwargs) -> Chain:
    """Factory function to create chains."""
    chains = {
        ChainType.SIMPLE: SimpleChain,
        ChainType.SEQUENTIAL: SequentialChain,
    }

    chain_class = chains.get(chain_type)
    if not chain_class:
        raise ValueError(f"Unsupported chain type: {chain_type}")

    return chain_class(**kwargs)


# Output parsers
def json_parser(output: str) -> dict:
    """Parse JSON from output."""
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', output)
    if json_match:
        return json.loads(json_match.group(1))
    return json.loads(output)


def list_parser(output: str) -> list[str]:
    """Parse a numbered or bulleted list."""
    lines = output.strip().split('\n')
    items = []
    for line in lines:
        # Remove numbering and bullets
        cleaned = re.sub(r'^[\d\.\-\*\•]+\s*', '', line.strip())
        if cleaned:
            items.append(cleaned)
    return items


__all__ = [
    "ChainType",
    "ChainStep",
    "ChainResult",
    "Chain",
    "SimpleChain",
    "SequentialChain",
    "ChainOfThought",
    "ReActChain",
    "create_chain",
    "json_parser",
    "list_parser",
]
