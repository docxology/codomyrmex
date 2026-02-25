"""
Tool Use Module

Registry, composition, and validation for tool-based workflows.
Provides a central registry for managing tools, a chain abstraction
for sequential tool pipelines, and input/output validation utilities.
"""

__version__ = "0.1.0"

from .chains import ChainResult, ChainStep, ToolChain
from .registry import ToolEntry, ToolRegistry, tool
from .validation import ValidationResult, validate_input, validate_output

__all__ = [
    # Validation
    "ValidationResult",
    "validate_input",
    "validate_output",
    # Registry
    "ToolEntry",
    "ToolRegistry",
    "tool",
    # Chains
    "ChainStep",
    "ChainResult",
    "ToolChain",
]
