"""
Prompt Engineering Module

Provides tools for prompt template management, version tracking,
optimization strategies, and evaluation scoring. Part of the
Codomyrmex modular development platform.


Submodules:
    testing: Consolidated testing capabilities."""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"

from . import testing

# Core template management
# Evaluation
from .evaluation import (
    EvaluationCriteria,
    EvaluationResult,
    PromptEvaluator,
    get_default_criteria,
    score_completeness,
    score_relevance,
    score_response_length,
    score_structure,
)

# Optimization
from .optimization import (
    OptimizationResult,
    OptimizationStrategy,
    PromptOptimizer,
)
from .templates import (
    PromptTemplate,
    TemplateRegistry,
    get_default_registry,
)

# Version tracking
from .versioning import (
    PromptVersion,
    VersionManager,
)

# Try to import shared types for interop
try:
    from codomyrmex.validation.schemas import Config, Result, ResultStatus
except ImportError:
    Result = Any  # type: ignore
    ResultStatus = Any  # type: ignore
    Config = Any  # type: ignore

# Try to import base exception for module error class
try:
    from codomyrmex.exceptions import CodomyrmexError
except ImportError:
    CodomyrmexError = Exception  # type: ignore


class PromptEngineeringError(CodomyrmexError):
    """Raised when prompt engineering operations fail."""


def list_templates() -> list[str]:
    """
    list all templates in the default registry.

    Returns:
        Sorted list of template names.
    """
    return get_default_registry().list()


def list_strategies() -> list[str]:
    """
    list available optimization strategies.

    Returns:
        Sorted list of strategy value strings.
    """
    return PromptOptimizer().available_strategies()


def quick_evaluate(prompt: str, response: str) -> dict[str, Any]:
    """
    Run a quick evaluation of a prompt-response pair using default criteria.

    Args:
        prompt: The prompt string.
        response: The model response string.

    Returns:
        Dictionary with per-criterion scores and weighted total.
    """
    evaluator = PromptEvaluator()
    result = evaluator.evaluate(prompt, response)
    return result.to_dict()


def cli_commands() -> dict[str, Any]:
    """
    Return CLI command definitions for the prompt_engineering module.

    Follows the codomyrmex cli_commands() discovery convention so that
    the CLI core can auto-register these commands.
    """
    return {
        "templates": {
            "help": "list prompt templates in the default registry",
            "handler": lambda args: print(
                "\n".join(list_templates())
                if list_templates()
                else "(no templates registered)"
            ),
            "arguments": [],
        },
        "strategies": {
            "help": "list available prompt optimization strategies",
            "handler": lambda args: print("\n".join(list_strategies())),
            "arguments": [],
        },
        "evaluate": {
            "help": "Evaluate a prompt-response pair (JSON input via stdin)",
            "handler": _cli_evaluate,
            "arguments": [
                {"name": "--prompt", "help": "The prompt text", "required": False},
                {"name": "--response", "help": "The response text", "required": False},
            ],
        },
    }


def _cli_evaluate(args: Any) -> None:
    """CLI handler for the evaluate command."""
    import json
    import sys

    prompt_text = getattr(args, "prompt", None)
    response_text = getattr(args, "response", None)

    if not prompt_text or not response_text:
        # Try reading JSON from stdin
        try:
            data = json.load(sys.stdin)
            prompt_text = data.get("prompt", "")
            response_text = data.get("response", "")
        except (json.JSONDecodeError, EOFError):
            print("Error: Provide --prompt and --response, or pipe JSON to stdin.")
            print('Expected JSON: {"prompt": "...", "response": "..."}')
            return

    result = quick_evaluate(prompt_text, response_text)
    print(json.dumps(result, indent=2))


__all__ = [
    # Evaluation
    "EvaluationCriteria",
    "EvaluationResult",
    "OptimizationResult",
    # Optimization
    "OptimizationStrategy",
    # Error
    "PromptEngineeringError",
    "PromptEvaluator",
    "PromptOptimizer",
    # Templates
    "PromptTemplate",
    # Versioning
    "PromptVersion",
    "TemplateRegistry",
    "VersionManager",
    "cli_commands",
    "get_default_criteria",
    "get_default_registry",
    "list_strategies",
    # Convenience functions
    "list_templates",
    "quick_evaluate",
    "score_completeness",
    "score_relevance",
    "score_response_length",
    "score_structure",
    "testing",
]
