"""
Mermaid submodule for data_visualization.

Provides Mermaid diagram generation capabilities.
"""

from .mermaid_generator import MermaidGenerator, generate_mermaid_diagram

__all__ = [
    "MermaidGenerator",
    "generate_mermaid_diagram",
]
