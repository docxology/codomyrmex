"""
Common utilities for Codomyrmex examples.

This package provides shared utilities used across all example scripts including
configuration loading, example execution framework, and common helper functions.
"""

__version__ = "0.1.0"

from .config_loader import load_config, merge_configs
from .example_runner import ExampleRunner
from .utils import setup_example_paths, format_output, ensure_output_dir

__all__ = [
    'load_config',
    'merge_configs',
    'ExampleRunner',
    'setup_example_paths',
    'format_output',
    'ensure_output_dir',
]

