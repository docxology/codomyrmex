"""MCP static tool definitions."""

from typing import Any

from codomyrmex.model_context_protocol.tools import (
    analyze_python_file,
    checksum_file,
    git_diff,
    git_status,
    json_query,
    list_directory,
    read_file,
    run_shell_command,
    search_codebase,
    write_file,
)

from .discovery import _tool_invalidate_cache
from .proxy_tools import (
    _tool_call_module_function,
    _tool_get_module_readme,
    _tool_list_module_functions,
    _tool_list_modules,
    _tool_list_workflows,
    _tool_module_info,
    _tool_pai_awareness,
    _tool_pai_status,
    _tool_run_tests,
)

# Each entry: (name, description, handler, input_schema)
_TOOL_DEFINITIONS: list[tuple[str, str, Any, dict[str, Any]]] = [
    # File Operations
    (
        "codomyrmex.read_file",
        "Read file contents with metadata",
        read_file,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"},
                "encoding": {"type": "string", "default": "utf-8"},
                "max_size": {"type": "integer", "default": 1000000},
            },
            "required": ["path"],
        },
    ),
    (
        "codomyrmex.write_file",
        "Write content to a file",
        write_file,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"},
                "create_dirs": {"type": "boolean", "default": True},
            },
            "required": ["path", "content"],
        },
    ),
    (
        "codomyrmex.list_directory",
        "List directory contents with filtering",
        list_directory,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "pattern": {"type": "string", "default": "*"},
                "recursive": {"type": "boolean", "default": False},
                "max_items": {"type": "integer", "default": 200},
            },
        },
    ),
    # Code Analysis
    (
        "codomyrmex.analyze_python",
        "Analyze a Python file for structure and metrics",
        analyze_python_file,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Python file path"},
            },
            "required": ["path"],
        },
    ),
    (
        "codomyrmex.search_codebase",
        "Search for patterns in code files (regex supported)",
        search_codebase,
        {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Search pattern"},
                "path": {"type": "string", "default": "."},
                "file_types": {"type": "array", "items": {"type": "string"}},
                "case_sensitive": {"type": "boolean", "default": False},
                "max_results": {"type": "integer", "default": 100},
            },
            "required": ["pattern"],
        },
    ),
    # Git Operations
    (
        "codomyrmex.git_status",
        "Get git repository status",
        git_status,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
            },
        },
    ),
    (
        "codomyrmex.git_diff",
        "Get git diff for changes",
        git_diff,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "staged": {"type": "boolean", "default": False},
            },
        },
    ),
    # Shell
    (
        "codomyrmex.run_command",
        "Execute a shell command safely",
        run_shell_command,
        {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to execute"},
                "cwd": {"type": "string", "default": "."},
                "timeout": {"type": "integer", "default": 30},
            },
            "required": ["command"],
        },
    ),
    # Data Utilities
    (
        "codomyrmex.json_query",
        "Read and optionally query a JSON file via dot-notation",
        json_query,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "JSON file path"},
                "query": {"type": "string", "description": "Dot-notation path"},
            },
            "required": ["path"],
        },
    ),
    (
        "codomyrmex.checksum_file",
        "Calculate file checksum (md5, sha1, sha256)",
        checksum_file,
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "algorithm": {"type": "string", "default": "sha256"},
            },
            "required": ["path"],
        },
    ),
    # Discovery
    (
        "codomyrmex.list_modules",
        "List all available Codomyrmex modules",
        _tool_list_modules,
        {"type": "object", "properties": {}},
    ),
    (
        "codomyrmex.module_info",
        "Get info about a specific module (docstring, exports, path)",
        _tool_module_info,
        {
            "type": "object",
            "properties": {
                "module_name": {"type": "string", "description": "Module name (e.g. 'llm', 'security')"},
            },
            "required": ["module_name"],
        },
    ),
    # PAI
    (
        "codomyrmex.pai_status",
        "Get PAI installation status and component inventory",
        _tool_pai_status,
        {"type": "object", "properties": {}},
    ),
    (
        "codomyrmex.pai_awareness",
        "Get full PAI awareness data (missions, projects, tasks, memory)",
        _tool_pai_awareness,
        {"type": "object", "properties": {}},
    ),
    # Testing
    (
        "codomyrmex.run_tests",
        "Run pytest for a specific module or the whole project",
        _tool_run_tests,
        {
            "type": "object",
            "properties": {
                "module": {"type": "string", "description": "Module name to test (optional)"},
                "verbose": {"type": "boolean", "default": False},
            },
        },
    ),
    # ── Universal Module Proxy ────────────────────────────────────
    (
        "codomyrmex.list_module_functions",
        "List all public callable functions and classes in any Codomyrmex module. "
        "Use this to discover what's available before calling call_module_function.",
        _tool_list_module_functions,
        {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Module path (e.g. 'encryption', 'cache', 'auth.authenticator')",
                },
            },
            "required": ["module"],
        },
    ),
    (
        "codomyrmex.call_module_function",
        "Call any public function from any Codomyrmex module by path. "
        "Use list_module_functions first to discover available functions.",
        _tool_call_module_function,
        {
            "type": "object",
            "properties": {
                "function": {
                    "type": "string",
                    "description": "Fully qualified function path (e.g. 'encryption.encrypt', 'cache.get_cache')",
                },
                "kwargs": {
                    "type": "object",
                    "description": "Keyword arguments to pass to the function",
                    "default": {},
                },
            },
            "required": ["function"],
        },
    ),
    (
        "codomyrmex.get_module_readme",
        "Read the README.md or SPEC.md documentation for any Codomyrmex module",
        _tool_get_module_readme,
        {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Module name (e.g. 'encryption', 'cache', 'auth')",
                },
            },
            "required": ["module"],
        },
    ),
    (
        "codomyrmex.list_workflows",
        "List available Claude Code workflows",
        _tool_list_workflows,
        {"type": "object", "properties": {}},
    ),
    (
        "codomyrmex.invalidate_cache",
        "Invalidate dynamic tool discovery cache",
        _tool_invalidate_cache,
        {
            "type": "object",
            "properties": {
                "module": {"type": "string", "description": "Specific module to rescan (optional)"},
            },
        },
    ),
]

_RESOURCE_DEFINITIONS: list[tuple[str, str, str, str]] = [
    # (uri, name, description, mime_type)
    (
        "codomyrmex://modules",
        "Module Inventory",
        "Complete list of all Codomyrmex modules with descriptions",
        "application/json",
    ),
    (
        "codomyrmex://status",
        "System Status",
        "Current Codomyrmex system status including PAI integration",
        "application/json",
    ),
]

_PROMPT_DEFINITIONS: list[tuple[str, str, list[dict[str, Any]], str]] = [
    (
        "codomyrmex.analyze_module",
        "Analyze a Codomyrmex module — structure, exports, tests, documentation",
        [{"name": "module_name", "description": "Module to analyze", "required": True}],
        (
            "Analyze the Codomyrmex module '{module_name}'. "
            "Use codomyrmex.module_info to get its exports, then "
            "codomyrmex.search_codebase to find its tests, and "
            "codomyrmex.read_file to review its README.md. "
            "Provide: 1) Purpose, 2) Key exports, 3) Test coverage, 4) Recommendations."
        ),
    ),
    (
        "codomyrmex.debug_issue",
        "Debug an issue using Codomyrmex tools",
        [{"name": "description", "description": "Issue description", "required": True}],
        (
            "Debug this issue: '{description}'. "
            "Use codomyrmex.search_codebase to find relevant code, "
            "codomyrmex.analyze_python to understand file structure, "
            "codomyrmex.git_diff to check recent changes, and "
            "codomyrmex.run_tests to verify. "
            "Provide: 1) Root cause, 2) Fix, 3) Verification steps."
        ),
    ),
    (
        "codomyrmex.create_test",
        "Generate tests for a Codomyrmex module",
        [{"name": "module_name", "description": "Module to create tests for", "required": True}],
        (
            "Create zero-mock tests for the Codomyrmex module '{module_name}'. "
            "Use codomyrmex.module_info to get exports, then "
            "codomyrmex.read_file to review the source. "
            "Generate pytest tests using real objects — no mocks. "
            "Follow the project's Zero-Mock testing policy."
        ),
    ),
    (
        "codomyrmexAnalyze",
        "Perform deep analysis of a Codomyrmex project or specific file",
        [{"name": "path", "description": "Path to analyze (default: '.')", "required": False}],
        "Run the /codomyrmexAnalyze workflow for deep structural and quality analysis of '{path}'.",
    ),
    (
        "codomyrmexMemory",
        "Add a new entry to the Codomyrmex agentic long-term memory",
        [
            {"name": "content", "description": "Content to remember", "required": True},
            {"name": "importance", "description": "Importance score 1-10", "required": False},
        ],
        "Run the /codomyrmexMemory workflow to persist: '{content}' (Importance: {importance}).",
    ),
    (
        "codomyrmexSearch",
        "Search for patterns in the codebase using regex",
        [
            {"name": "pattern", "description": "Regex search pattern", "required": True},
            {"name": "path", "description": "Search root path", "required": False},
        ],
        "Run the /codomyrmexSearch workflow for pattern '{pattern}' in '{path}'.",
    ),
    (
        "codomyrmexDocs",
        "Retrieve README or SPEC documentation for any Codomyrmex module",
        [{"name": "module", "description": "Module name", "required": True}],
        "Run the /codomyrmexDocs workflow to get documentation for module '{module}'.",
    ),
    (
        "codomyrmexStatus",
        "Get detailed system health and PAI awareness status",
        [],
        "Run the /codomyrmexStatus workflow for a full system health and PAI integration report.",
    ),
    (
        "codomyrmexVerify",
        "Verify all Codomyrmex capabilities available to Claude Code via MCP",
        [],
        "Run the /codomyrmexVerify workflow to audit modules, tools, and PAI status.",
    ),
    (
        "codomyrmexTrust",
        "Trust Codomyrmex tools for full execution in Claude Code",
        [],
        "Run the /codomyrmexTrust workflow to promote destructive tools to TRUSTED status.",
    ),
]

