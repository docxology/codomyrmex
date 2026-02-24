"""PAI ↔ Codomyrmex MCP Bridge.

Registers every Codomyrmex capability as MCP tools, resources, and prompts
so that PAI agents can access the full module ecosystem via MCP protocol
*or* direct Python calls.

Upstream: https://github.com/danielmiessler/Personal_AI_Infrastructure

Example — MCP server::

    from codomyrmex.agents.pai.mcp_bridge import create_codomyrmex_mcp_server
    server = create_codomyrmex_mcp_server()
    server.run()  # stdio or HTTP

Example — direct call (no MCP overhead)::

    from codomyrmex.agents.pai.mcp_bridge import call_tool
    modules = call_tool("codomyrmex.list_modules")
    status  = call_tool("codomyrmex.pai_status")
    result  = call_tool("codomyrmex.read_file", path="pyproject.toml")
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import json
import pkgutil
import subprocess
import sys
import yaml
import os
import threading
import time
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol import (
    MCPServer,
    MCPServerConfig,
    MCPToolRegistry,
)
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

logger = get_logger(__name__)

# ── Project root (best-effort) ───────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # src/codomyrmex/agents/pai → repo root


def _get_package_version() -> str:
    try:
        from importlib.metadata import version
        return version("codomyrmex")
    except Exception:
        return "unknown"


# =====================================================================
# Tool Definitions
# =====================================================================

def _tool_list_modules(**_kwargs: Any) -> dict[str, Any]:
    """List all available Codomyrmex modules."""
    import codomyrmex
    modules = codomyrmex.list_modules()
    return {"modules": modules, "count": len(modules)}


def _tool_module_info(*, module_name: str) -> dict[str, Any]:
    """Get info about a specific Codomyrmex module (docstring, exports, path)."""
    try:
        mod = importlib.import_module(f"codomyrmex.{module_name}")
    except ImportError as exc:
        return {"error": f"Module not found: {module_name}", "detail": str(exc)}

    exports = getattr(mod, "__all__", [n for n in dir(mod) if not n.startswith("_")])
    doc = (mod.__doc__ or "").strip()
    mod_path = getattr(mod, "__file__", None)

    return {
        "module": module_name,
        "docstring": doc[:500] if doc else None,
        "exports": exports[:50],
        "export_count": len(exports),
        "path": str(mod_path) if mod_path else None,
    }


# ─────────────────────────────────────────────────────────────────────
# Universal Module Proxy Tools
# ─────────────────────────────────────────────────────────────────────

def _tool_list_module_functions(*, module: str = "") -> dict[str, Any]:
    """List all public callable functions in a Codomyrmex module.

    Args:
        module: Module path (e.g. 'encryption', 'cache', 'validation').
                Automatically prefixed with 'codomyrmex.'.

    Returns:
        Dict with function names, signatures, and docstrings.
    """
    full_path = f"codomyrmex.{module}" if not module.startswith("codomyrmex.") else module
    try:
        mod = importlib.import_module(full_path)
    except ImportError as e:
        return {"error": f"Module {full_path} not found: {e}"}

    functions = []
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            sig = str(inspect.signature(obj))
        except (ValueError, TypeError):
            sig = "(...)"
        doc = inspect.getdoc(obj) or ""
        if len(doc) > 200:
            doc = doc[:200] + "..."
        functions.append({"name": name, "signature": sig, "docstring": doc})

    classes = []
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if name.startswith("_"):
            continue
        doc = inspect.getdoc(obj) or ""
        if len(doc) > 200:
            doc = doc[:200] + "..."
        methods = [m for m in dir(obj) if not m.startswith("_") and callable(getattr(obj, m, None))]
        classes.append({"name": name, "docstring": doc, "public_methods": methods[:20]})

    return {
        "module": full_path,
        "functions": functions,
        "classes": classes,
        "total_callables": len(functions) + len(classes),
    }


def _tool_call_module_function(*, function: str = "", kwargs: dict | None = None) -> dict[str, Any]:
    """Call any public function from any Codomyrmex module.

    Args:
        function: Fully qualified function path (e.g. 'encryption.encrypt').
                  Will be auto-prefixed with 'codomyrmex.' if not already.
        kwargs: Keyword arguments to pass to the function.

    Returns:
        Dict with 'result' key (function return value) or 'error' key.
    """
    if kwargs is None:
        kwargs = {}
    if not function.startswith("codomyrmex."):
        function = f"codomyrmex.{function}"

    parts = function.rsplit(".", 1)
    if len(parts) != 2:
        return {"error": f"Invalid function path: {function!r}. Expected 'module.function'."}

    module_path, func_name = parts
    if func_name.startswith("_"):
        return {"error": f"Cannot call private function {func_name!r}."}

    try:
        mod = importlib.import_module(module_path)
    except ImportError as e:
        return {"error": f"Module {module_path} not found: {e}"}

    func = getattr(mod, func_name, None)
    if func is None or not callable(func):
        available = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n, None))]
        return {"error": f"Function {func_name!r} not found in {module_path}.", "available": available[:30]}

    try:
        result = func(**kwargs)
        try:
            import json as _json
            _json.dumps(result)
        except (TypeError, ValueError):
            result = str(result)
        return {"result": result}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _tool_get_module_readme(*, module: str = "") -> dict[str, Any]:
    """Read the README.md for a Codomyrmex module.

    Args:
        module: Module name (e.g. 'encryption', 'cache').

    Returns:
        Dict with README contents or error.
    """
    full_path = f"codomyrmex.{module}" if not module.startswith("codomyrmex.") else module
    try:
        mod = importlib.import_module(full_path)
    except ImportError as e:
        return {"error": f"Module {full_path} not found: {e}"}

    mod_dir = Path(getattr(mod, "__file__", "")).parent
    readme = mod_dir / "README.md"
    if not readme.exists():
        spec = mod_dir / "SPEC.md"
        if spec.exists():
            readme = spec
        else:
            return {"error": f"No README.md or SPEC.md found in {mod_dir}"}

    content = readme.read_text()
    if len(content) > 5000:
        content = content[:5000] + "\n\n... (truncated)"

    return {"module": full_path, "path": str(readme), "content": content}


def _tool_pai_status(**_kwargs: Any) -> dict[str, Any]:
    """Get PAI installation status via PAIBridge."""
    from codomyrmex.agents.pai import PAIBridge
    bridge = PAIBridge()
    return bridge.get_status()


def _tool_pai_awareness(**_kwargs: Any) -> dict[str, Any]:
    """Get full PAI awareness data (missions, projects, tasks, TELOS, memory)."""
    try:
        from codomyrmex.website.data_provider import DataProvider
        dp = DataProvider(root_dir=_PROJECT_ROOT)
        return dp.get_pai_awareness_data()
    except Exception as exc:
        logger.warning("PAI awareness data unavailable: %s", exc)
        return {"error": str(exc)}


def _tool_run_tests(*, module: str | None = None, verbose: bool = False) -> dict[str, Any]:
    """Run pytest for a specific module or the whole project."""
    cmd = [sys.executable, "-m", "pytest"]
    if module:
        # Map module name to test path
        test_path = _PROJECT_ROOT / "src" / "codomyrmex" / "tests" / "unit" / module
        if test_path.is_dir():
            cmd.append(str(test_path))
        else:
            cmd.extend(["-k", module])
    if verbose:
        cmd.append("-v")
    cmd.append("--tb=short")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(_PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "returncode": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"error": "Test execution timed out (120s limit)"}
    except Exception as exc:
        return {"error": str(exc)}


def _tool_list_workflows(**_kwargs: Any) -> dict[str, Any]:
    """List available Claude Code workflows from .agent/workflows.
    
    Parses YAML frontmatter to extract descriptions.
    """
    workflows_dir = _PROJECT_ROOT / ".agent" / "workflows"
    if not workflows_dir.exists():
        return {"workflows": [], "count": 0, "error": "No workflow directory found"}
        
    results = []
    warnings = []
    
    for item in workflows_dir.glob("*.md"):
        try:
            content = item.read_text(encoding="utf-8")
            # Parse YAML frontmatter
            description = "No description"
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if isinstance(frontmatter, dict):
                            description = frontmatter.get("description", description)
                    except yaml.YAMLError:
                        warnings.append(f"Invalid YAML frontmatter in {item.name}")
            
            results.append({
                "name": item.stem, # filename without .md
                "description": description,
                "filepath": str(item),
                "size_bytes": item.stat().st_size,
            })
        except Exception as e:
            warnings.append(f"Failed to read {item.name}: {e}")
            
    return {
        "workflows": sorted(results, key=lambda x: x["name"]), 
        "count": len(results),
        "warnings": warnings
    }


def _tool_invalidate_cache(module: str | None = None) -> dict[str, Any]:
    """Invalidate the dynamic tool discovery cache.
    
    Args:
        module: Optional. If provided, invalidates and rescans only that module.
                If None, clears the entire cache.
    """
    if module:
        # We call scan_module from discovery engine
        if _DISCOVERY_ENGINE is None:
             return {"error": "Discovery engine not initialized"}
             
        report = _DISCOVERY_ENGINE.scan_module(module)
        
        # Force a cache refresh next time get_tool_registry is called
        global _CACHE_TIMESTAMP
        _CACHE_TIMESTAMP = 0.0 
        
        return {
             "cleared": False, # We didn't clear everything
             "rescanned_module": module,
             "tools_found": len(report.tools),
             "failed": bool(report.failed_modules)
        }
    else:
        invalidate_tool_cache()
        return {"cleared": True, "rescan_duration_ms": 0.0, "new_tool_count": 0} # stats avail on next call


# =====================================================================
# Tool Registry
# =====================================================================

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


# =====================================================================
# Resource Definitions
# =====================================================================

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


# =====================================================================
# Prompt Definitions
# =====================================================================

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


# =====================================================================
# Public API
# =====================================================================

# ─────────────────────────────────────────────────────────────────────
# Dynamic Discovery Integration (v0.1.8 Stream 3: TTL cache)
# ─────────────────────────────────────────────────────────────────────

_DYNAMIC_TOOLS_CACHE: list[tuple[str, str, Any, dict[str, Any]]] | None = None
_DYNAMIC_TOOLS_CACHE_LOCK = threading.Lock()
_CACHE_EXPIRY: float | None = None  # monotonic timestamp when cache expires
_DEFAULT_CACHE_TTL: float = float(os.environ.get("CODOMYRMEX_MCP_CACHE_TTL", "300"))
_DISCOVERY_ENGINE: Any | None = None


def invalidate_tool_cache() -> None:
    """Clear the dynamic tool discovery cache and its TTL."""
    global _DYNAMIC_TOOLS_CACHE, _CACHE_EXPIRY
    with _DYNAMIC_TOOLS_CACHE_LOCK:
        _DYNAMIC_TOOLS_CACHE = None
        _CACHE_EXPIRY = None
    logger.info("Dynamic tool cache invalidated")


_FALLBACK_SCAN_TARGETS = [
    "codomyrmex.data_visualization",
    "codomyrmex.llm",
    "codomyrmex.agentic_memory",
    "codomyrmex.security",
    "codomyrmex.git_operations",
    "codomyrmex.coding",
    "codomyrmex.documentation",
    "codomyrmex.email",
]


def _find_mcp_modules() -> list[str]:
    """Auto-discover all codomyrmex sub-packages that contain an ``mcp_tools`` module.

    Uses :func:`pkgutil.walk_packages` to walk the ``codomyrmex`` package tree,
    filtering for modules whose name ends with ``.mcp_tools``.  Returns the
    *parent* package name for each match (e.g. ``codomyrmex.security``).

    Falls back to :data:`_FALLBACK_SCAN_TARGETS` if the walk fails entirely.
    """
    try:
        root = importlib.import_module("codomyrmex")
        root_path = getattr(root, "__path__", None)
        if not root_path:
            return list(_FALLBACK_SCAN_TARGETS)

        parents: set[str] = set()
        for importer, name, ispkg in pkgutil.walk_packages(
            root_path, prefix="codomyrmex."
        ):
            if name.endswith(".mcp_tools"):
                # e.g. "codomyrmex.security.mcp_tools" -> "codomyrmex.security"
                parent = name.rsplit(".", 1)[0]
                parents.add(parent)

        if not parents:
            logger.warning("pkgutil walk found 0 mcp_tools modules; using fallback")
            return list(_FALLBACK_SCAN_TARGETS)

        logger.info("Auto-discovered %d modules with mcp_tools", len(parents))
        return sorted(parents)

    except Exception as exc:
        logger.warning("_find_mcp_modules failed (%s); using fallback targets", exc)
        return list(_FALLBACK_SCAN_TARGETS)


def _discover_dynamic_tools() -> list[tuple[str, str, Any, dict[str, Any]]]:
    """Scan modules for @mcp_tool definitions using MCPDiscovery engine.

    Uses a TTL-based cache.
    """
    global _DYNAMIC_TOOLS_CACHE, _CACHE_EXPIRY, _DISCOVERY_ENGINE
    now = time.monotonic()
    with _DYNAMIC_TOOLS_CACHE_LOCK:
        if _DYNAMIC_TOOLS_CACHE is not None and _CACHE_EXPIRY is not None and now < _CACHE_EXPIRY:
            logger.debug("Discovery cache hit (expires in %.1fs)", _CACHE_EXPIRY - now)
            # Record cache hit if engine available
            if _DISCOVERY_ENGINE:
                 _DISCOVERY_ENGINE.record_cache_hit()
            return _DYNAMIC_TOOLS_CACHE

    if _DISCOVERY_ENGINE is None:
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery
        _DISCOVERY_ENGINE = MCPDiscovery()

    t0 = time.monotonic()

    scan_targets = _find_mcp_modules()
    
    for target in scan_targets:
        try:
             _DISCOVERY_ENGINE.scan_package(target)
        except Exception as e:
             logger.warning(f"Failed to scan package {target}: {e}")
        
    tools: list[tuple[str, str, Any, dict[str, Any]]] = []
    
    for tool in _DISCOVERY_ENGINE.list_tools():
        if tool.handler:
            tools.append((tool.name, tool.description, tool.handler, tool.parameters))
            
    elapsed_ms = (time.monotonic() - t0) * 1000
    logger.info(
        "Dynamic tools discovered: %d in %.0fms",
        len(tools), elapsed_ms,
    )

    with _DYNAMIC_TOOLS_CACHE_LOCK:
        _DYNAMIC_TOOLS_CACHE = tools
        _CACHE_EXPIRY = time.monotonic() + _DEFAULT_CACHE_TTL

    return tools


# =====================================================================
# Public API
# =====================================================================

def get_tool_registry() -> MCPToolRegistry:
    """Create an :class:`MCPToolRegistry` populated with all Codomyrmex tools (static + dynamic).

    Returns:
        A registry with core static tools + dynamically discovered module tools.
    """
    registry = MCPToolRegistry()

    # 1. Register Core Static Tools
    for name, description, handler, input_schema in _TOOL_DEFINITIONS:
        registry.register(
            tool_name=name,
            schema={
                "name": name,
                "description": description,
                "inputSchema": input_schema,
            },
            handler=handler,
        )

    # 2. Register Dynamic Module Tools
    dynamic_tools = _discover_dynamic_tools()
    for name, description, handler, input_schema in dynamic_tools:
        registry.register(
            tool_name=name,
            schema={
                "name": name,
                "description": description,
                "inputSchema": input_schema,
            },
            handler=handler,
        )

    return registry


def create_codomyrmex_mcp_server(
    *,
    name: str = "codomyrmex-mcp-server",
    transport: str = "stdio",
) -> MCPServer:
    """Create a fully-configured MCP server with all Codomyrmex capabilities.

    Args:
        name: Server identity name.
        transport: ``"stdio"`` or ``"http"``.

    Returns:
        An :class:`MCPServer` ready to ``run()``.
    """
    config = MCPServerConfig(name=name, transport=transport)
    server = MCPServer(config=config)

    # ── Warm-up: eagerly populate discovery cache ─────────────────
    if config.warm_up:
        t0 = time.monotonic()
        _discover_dynamic_tools()
        warm_ms = (time.monotonic() - t0) * 1000
        logger.info("Discovery warm-up completed in %.0fms", warm_ms)

    # ── Register tools (Static + Dynamic) ──────────────────────────
    registry = get_tool_registry()
    # The server uses its own internal registry, so we copy over
    # (or ideally server accepts a pre-built registry, but standard pattern confirms manual reg)

    for tool_name in registry.list_tools():
        tool = registry.get_tool(tool_name)
        if tool:
            server.register_tool(
                name=tool_name,
                schema=tool["schema"],
                handler=tool["handler"],
            )

    # ── Register resources ────────────────────────────────────────
    for uri, res_name, res_desc, mime in _RESOURCE_DEFINITIONS:
        if uri == "codomyrmex://modules":
            def _modules_provider() -> str:
                import codomyrmex
                return json.dumps({"modules": codomyrmex.list_modules()})
            provider = _modules_provider
        elif uri == "codomyrmex://status":
            def _status_provider() -> str:
                return json.dumps(_tool_pai_status())
            provider = _status_provider
        else:
            provider = None

        server.register_resource(
            uri=uri,
            name=res_name,
            description=res_desc,
            mime_type=mime,
            content_provider=provider,
        )

    # ── Register prompts ──────────────────────────────────────────
    for prompt_name, prompt_desc, prompt_args, template in _PROMPT_DEFINITIONS:
        server.register_prompt(
            name=prompt_name,
            description=prompt_desc,
            arguments=prompt_args,
            template=template,
        )

    # ── Register discovery metrics resource ────────────────────────
    def _discovery_metrics_provider() -> str:
        from codomyrmex.model_context_protocol.discovery import MCPDiscovery as _Disc
        disc = _Disc()
        m = disc.get_metrics()
        return json.dumps({
            "total_tools": m.total_tools,
            "scan_duration_ms": m.scan_duration_ms,
            "failed_modules": m.failed_modules,
            "modules_scanned": m.modules_scanned,
            "cache_hits": m.cache_hits,
            "last_scan_time": m.last_scan_time.isoformat() if m.last_scan_time else None,
        })

    server.register_resource(
        uri="codomyrmex://discovery/metrics",
        name="Discovery Metrics",
        description="Runtime metrics from MCP tool discovery (scan time, failures, cache hits).",
        mime_type="application/json",
        content_provider=_discovery_metrics_provider,
    )

    logger.info(
        "Codomyrmex MCP server created: %d tools, %d resources, %d prompts",
        len(server._tool_registry.list_tools()),
        len(server._resources),
        len(server._prompts),
    )
    return server


def call_tool(name: str, **kwargs: Any) -> dict[str, Any]:
    """Call a Codomyrmex MCP tool directly (no MCP protocol overhead).

    This is the fastest way to invoke tools from Python code.
    Supports both static core tools and dynamically discovered module tools.
    
    Delegates to ``trust_gateway.trusted_call_tool`` to ensure:
    1. Authorization policies are enforced.
    2. Audit logs are recorded.
    3. Destructive actions are confirmed.

    Args:
        name: Tool name (e.g. ``"codomyrmex.list_modules"``).
        **kwargs: Tool arguments.

    Returns:
        Tool result dictionary.  On error, returns a dict with
        ``"error"`` key containing a structured :class:`MCPToolError` dict.
    
    Raises:
        KeyError: If the tool name is not registered.
    """
    from codomyrmex.agents.pai.trust_gateway import trusted_call_tool, SecurityError
    from codomyrmex.model_context_protocol.errors import (
        MCPToolError,
        MCPErrorCode,
        execution_error,
    )
    from codomyrmex.logging_monitoring.core.correlation import with_correlation
    
    # Check if tool is known first to match original behavior's KeyError
    # (trusted_call_tool will also check, but let's be explicit about "registration" vs "trust")
    # Actually trusted_call_tool handles this via get_tool_registry() lookup.
    
    with with_correlation():
        try:
            return trusted_call_tool(name, **kwargs)
        except KeyError:
            # Re-raise KeyError to maintain contract if tool not found
            all_static = sorted(t[0] for t in _TOOL_DEFINITIONS)
            raise KeyError(f"Unknown tool: {name!r}. Available (static): {all_static}")
        except SecurityError as exc:
            return {"error": MCPToolError(
                code=MCPErrorCode.ACCESS_DENIED,
                message=str(exc),
                tool_name=name
            ).to_dict()}
        except ValueError as exc:
            from codomyrmex.model_context_protocol.errors import validation_error
            return {"error": validation_error(
                tool_name=name,
                message=str(exc)
            ).to_dict()}
        except TimeoutError as exc:
            return {"error": MCPToolError(
                code=MCPErrorCode.TIMEOUT,
                message=str(exc),
                tool_name=name,
            ).to_dict()}
        except Exception as exc:
            # Wrap other execution errors
            module_hint = name.split(".")[1] if "." in name else name
            return {"error": execution_error(
                name, exc, module=module_hint
            ).to_dict()}


def get_skill_manifest() -> dict[str, Any]:
    """Return a PAI-compatible skill manifest for Codomyrmex.

    This can be consumed by PAI's skill routing system to understand
    what capabilities Codomyrmex provides.

    Returns:
        Dictionary with skill metadata, tools, workflows, and knowledge scope.
    """
    # Start with static schema
    static_tools = [
        {
            "name": t[0],
            "description": t[1],
            "category": t[0].split(".")[1] if "." in t[0] else "general",
            "input_schema": t[3],
        }
        for t in _TOOL_DEFINITIONS
    ]

    # Merge dynamic tools
    dynamic_list = _discover_dynamic_tools()
    dynamic_tools = []
    for t in dynamic_list:
        name, description, handler, input_schema = t
        # Extract category from @mcp_tool metadata on the handler
        category = "general"
        if handler and hasattr(handler, "_mcp_tool_meta"):
            category = handler._mcp_tool_meta.get("category", "general")
        if category == "general" and "." in name:
            # Fallback: derive from dotted tool name prefix
            category = name.split(".")[1]
        dynamic_tools.append({
            "name": name,
            "description": description,
            "category": category,
            "input_schema": input_schema,
        })

    # Deduplicate: dynamic tools override static when names collide
    seen: dict[str, dict[str, Any]] = {}
    for t in static_tools:
        seen[t["name"]] = t
    for t in dynamic_tools:
        seen[t["name"]] = t  # dynamic wins
    all_tools = sorted(seen.values(), key=lambda t: t["name"])

    return {
        "name": "Codomyrmex",
        "version": _get_package_version(),
        "description": (
            "Modular coding workspace exposing 100+ modules for AI-assisted "
            "development, code analysis, testing, documentation, and automation."
        ),
        "upstream": "https://github.com/docxology/codomyrmex",
        "mcp_server": "codomyrmex-mcp-server",
        "tools": all_tools,
        "resources": [
            {"uri": r[0], "name": r[1], "description": r[2]}
            for r in _RESOURCE_DEFINITIONS
        ],
        "prompts": [
            {"name": p[0], "description": p[1]}
            for p in _PROMPT_DEFINITIONS
        ],
        "workflows": [
            {
                "name": "codomyrmexVerify",
                "steps": [
                    "codomyrmex.pai_status",
                    "verify_capabilities()",
                ],
                "description": "Verify all Codomyrmex capabilities",
            },
            {
                "name": "codomyrmexTrust",
                "steps": [
                    "trust_all()",
                ],
                "description": "Trust Codomyrmex tools for full execution",
            },
            {
                "name": "analyze_and_test",
                "steps": [
                    "codomyrmex.list_modules",
                    "codomyrmex.module_info",
                    "codomyrmex.analyze_python",
                    "codomyrmex.run_tests",
                ],
                "description": "Discover → Analyze → Test a module",
            },
            {
                "name": "code_review",
                "steps": [
                    "codomyrmex.git_status",
                    "codomyrmex.git_diff",
                    "codomyrmex.search_codebase",
                    "codomyrmex.analyze_python",
                ],
                "description": "Review changes via git status → diff → search → analysis",
            },
            {
                "name": "pai_health_check",
                "steps": [
                    "codomyrmex.pai_status",
                    "codomyrmex.pai_awareness",
                    "codomyrmex.list_modules",
                ],
                "description": "Full PAI + Codomyrmex health assessment",
            },
        ],
        "algorithm_mapping": {
            "OBSERVE": ["codomyrmex.list_modules", "codomyrmex.module_info", "codomyrmex.list_directory"],
            "THINK": ["codomyrmex.analyze_python", "codomyrmex.search_codebase"],
            "PLAN": ["codomyrmex.read_file", "codomyrmex.json_query"],
            "BUILD": ["codomyrmex.write_file"],
            "EXECUTE": ["codomyrmex.run_command", "codomyrmex.run_tests"],
            "VERIFY": ["codomyrmex.git_status", "codomyrmex.git_diff", "codomyrmex.checksum_file"],
            "LEARN": ["codomyrmex.pai_awareness", "codomyrmex.pai_status"],
        },
        "knowledge_scope": {
            "core_infrastructure": [
                "logging_monitoring", "config_management", "environment_setup",
                "events", "exceptions", "utils", "schemas", "concurrency",
                "compression", "serialization", "streaming",
            ],
            "ai_and_agents": [
                "agents", "llm", "model_context_protocol", "orchestrator",
                "prompt_engineering", "cerebrum", "agentic_memory",
                "inference_optimization", "model_ops", "model_registry",
                "model_evaluation", "prompt_testing",
            ],
            "code_and_analysis": [
                "coding", "static_analysis", "tree_sitter", "documentation",
                "git_operations", "build_synthesis", "testing", "validation",
                "pattern_matching", "dependency_injection",
            ],
            "data_and_processing": [
                "database_management", "vector_store", "cache", "data_lineage",
                "data_visualization", "graph_rag", "feature_store",
                "feature_flags", "search", "documents", "fpf", "scrape",
            ],
            "security_and_identity": [
                "security", "auth", "encryption", "privacy", "defense",
                "identity", "wallet", "governance",
            ],
            "infrastructure_and_ops": [
                "cloud", "containerization", "deployment", "ci_cd_automation",
                "networking", "telemetry", "performance", "metrics",
                "edge_computing", "service_mesh", "scheduler", "rate_limiting",
                "cost_management", "chaos_engineering", "migration",
                "observability_dashboard",
            ],
            "ui_and_interface": [
                "cli", "website", "terminal_interface", "ide", "visualization",
                "video", "audio", "multimodal", "accessibility", "i18n",
                "templating", "notification",
            ],
            "domain_and_simulation": [
                "bio_simulation", "finance", "logistics", "spatial", "education",
                "meme", "embodiment", "evolutionary_ai", "quantum",
                "smart_contracts", "market", "dark", "physical_management",
                "relations", "collaboration",
            ],
            "system_and_meta": [
                "system_discovery", "plugin_system", "skills", "tool_use",
                "tools", "module_template", "examples", "tests",
                "workflow_testing", "api",
            ],
        },
    }


# =====================================================================
# Convenience: tool count constant
# =====================================================================

def get_total_tool_count() -> int:
    """Get the total number of registered tools (static + dynamic)."""
    return len(get_tool_registry().list_tools())




__all__ = [
    "create_codomyrmex_mcp_server",
    "get_tool_registry",
    "get_skill_manifest",
    "call_tool",
    "invalidate_tool_cache",
    "TOOL_COUNT",
    "RESOURCE_COUNT",
    "PROMPT_COUNT",
]

# Static counts for the core (non-dynamic) definitions.
# These are consumed by the PAI __init__.py and trust_gateway for reporting.
TOOL_COUNT: int = len(_TOOL_DEFINITIONS)
RESOURCE_COUNT: int = len(_RESOURCE_DEFINITIONS)
PROMPT_COUNT: int = len(_PROMPT_DEFINITIONS)

