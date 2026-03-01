"""agenticSeek integration sub-module for Codomyrmex.

Provides a comprehensive wrapper around the
`agenticSeek <https://github.com/Fosowl/agenticSeek>`_ framework—a
fully-local, privacy-first autonomous agent system with multi-agent
routing, web browsing, multi-language code execution, and task
planning.

Exports:
    AgenticSeekClient: Main CLI-based agent client.
    AgenticSeekConfig: Typed config.ini representation.
    AgenticSeekAgentType: Agent specialisation enum.
    AgenticSeekRouter: Heuristic query-to-agent classifier.
    AgenticSeekTaskPlanner: JSON plan parsing and ordering.
    AgenticSeekCodeExecutor: Code block extraction and command building.
    AgenticSeekBrowserConfig: Browser automation settings.
"""

__version__ = "0.1.0"

from .agent_router import AgenticSeekRouter
from .agent_types import (
    SUPPORTED_LANGUAGES,
    AgenticSeekAgentType,
    AgenticSeekConfig,
    AgenticSeekExecutionResult,
    AgenticSeekMemoryEntry,
    AgenticSeekProvider,
    AgenticSeekTaskStatus,
    AgenticSeekTaskStep,
    resolve_language,
)
from .agentic_seek_client import AgenticSeekClient
from .browser_automation import (
    AgenticSeekBrowserConfig,
    build_navigation_prompt,
    build_search_prompt,
    clean_links,
    extract_form_fields,
    extract_links,
    get_today_date,
)
from .code_execution import (
    AgenticSeekCodeExecutor,
    CodeBlock,
    build_execution_command,
    classify_language,
    extract_code_blocks,
    parse_execution_output,
)
from .task_planner import (
    AgenticSeekTaskPlanner,
    extract_task_names,
    get_execution_order,
    parse_plan_json,
    validate_plan,
)

__all__ = [
    # Client
    "AgenticSeekClient",
    # Data models
    "AgenticSeekAgentType",
    "AgenticSeekConfig",
    "AgenticSeekProvider",
    "AgenticSeekMemoryEntry",
    "AgenticSeekTaskStatus",
    "AgenticSeekTaskStep",
    "AgenticSeekExecutionResult",
    "SUPPORTED_LANGUAGES",
    "resolve_language",
    # Router
    "AgenticSeekRouter",
    # Code execution
    "AgenticSeekCodeExecutor",
    "CodeBlock",
    "extract_code_blocks",
    "classify_language",
    "build_execution_command",
    "parse_execution_output",
    # Task planning
    "AgenticSeekTaskPlanner",
    "parse_plan_json",
    "validate_plan",
    "get_execution_order",
    "extract_task_names",
    # Browser automation
    "AgenticSeekBrowserConfig",
    "extract_links",
    "clean_links",
    "extract_form_fields",
    "build_search_prompt",
    "build_navigation_prompt",
    "get_today_date",
]
