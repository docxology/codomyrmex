"""
Codomyrmex Ollama Integration Module

This module provides comprehensive integration with Ollama local LLMs,
enabling flexible model management, execution, and output handling within
the Codomyrmex ecosystem.
"""

from .config_manager import ConfigManager
from .model_runner import ModelRunner
from .ollama_manager import OllamaManager
from .output_manager import OutputManager

__all__ = [
    'OllamaManager',
    'ModelRunner',
    'OutputManager',
    'ConfigManager'
]

__version__ = '1.0.0'
