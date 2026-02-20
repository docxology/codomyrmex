# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.quality.taxonomy instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.quality.taxonomy"""
from .quality.taxonomy import *  # noqa: F401,F403
from .quality.taxonomy import (
    ToolCategory,
    categorize_tool,
    categorize_all_tools,
    generate_taxonomy_report,
    TaxonomyReport,
)
