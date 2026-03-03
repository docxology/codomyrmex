"""MCP tool definitions for the aider module.

Exposes aider AI pair programming as MCP tools for agent consumption.
All tools use subprocess execution with safe defaults (--yes --no-pretty --no-auto-commits).
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_runner(model: str = "", timeout: int = 300):
    """Lazy import of AiderRunner to avoid circular deps."""
    from codomyrmex.aider.core import AiderRunner

    return AiderRunner(model=model, timeout=timeout)


def _get_version():
    """Lazy import of get_aider_version."""
    from codomyrmex.aider.core import get_aider_version

    return get_aider_version


def _get_config():
    """Lazy import of get_config."""
    from codomyrmex.aider.config import get_config

    return get_config


@mcp_tool(
    category="aider",
    description="Check if aider is installed and return version + configured model.",
)
def aider_check() -> dict[str, Any]:
    """Check aider installation status and current configuration.

    Returns:
        dict with keys: status, installed, version, model, install_hint
    """
    try:
        get_ver = _get_version()
        version = get_ver()
        cfg_fn = _get_config()
        cfg = cfg_fn()
        if version:
            return {
                "status": "success",
                "installed": True,
                "version": version,
                "model": cfg.model,
            }
        return {
            "status": "success",
            "installed": False,
            "version": "",
            "model": cfg.model,
            "install_hint": "uv tool install aider-chat",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="aider",
    description=(
        "Edit files using aider AI pair programming. "
        "Applies code changes based on a natural-language instruction."
    ),
)
def aider_edit(
    file_paths: list[str],
    instruction: str,
    model: str = "claude-sonnet-4-6",
    timeout: int = 300,
) -> dict[str, Any]:
    """Edit one or more files using aider with a code-mode instruction.

    Args:
        file_paths: List of file paths to include in aider context for editing.
        instruction: Natural-language instruction describing the change to make.
        model: LLM model to use (default: claude-sonnet-4-6).
        timeout: Subprocess timeout in seconds (default: 300).

    Returns:
        dict with keys: status, output, stderr, returncode
    """
    if not file_paths:
        return {"status": "error", "message": "file_paths must not be empty"}
    try:
        runner = _get_runner(model=model, timeout=timeout)
        result = runner.run_message(file_paths, instruction)
        return {
            "status": "success",
            "output": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="aider",
    description=(
        "Ask aider a question about code without making any file changes. "
        "Returns analysis or explanation."
    ),
)
def aider_ask(
    file_paths: list[str],
    question: str,
    model: str = "claude-sonnet-4-6",
    timeout: int = 120,
) -> dict[str, Any]:
    """Ask aider about code in ask mode (no file changes made).

    Args:
        file_paths: List of file paths to include as context.
        question: Question to ask about the code.
        model: LLM model to use (default: claude-sonnet-4-6).
        timeout: Subprocess timeout in seconds (default: 120).

    Returns:
        dict with keys: status, answer, stderr
    """
    try:
        runner = _get_runner(model=model, timeout=timeout)
        result = runner.run_ask(file_paths, question)
        return {
            "status": "success",
            "answer": result["stdout"],
            "stderr": result["stderr"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="aider",
    description=(
        "Use aider's architect mode for complex multi-step refactoring. "
        "Uses two-model workflow: one plans, one edits."
    ),
)
def aider_architect(
    file_paths: list[str],
    task: str,
    model: str = "claude-sonnet-4-6",
    editor_model: str = "",
    timeout: int = 600,
) -> dict[str, Any]:
    """Run aider in architect mode for complex tasks requiring planning.

    Args:
        file_paths: List of file paths to include.
        task: Complex task description for the architect to plan and execute.
        model: Architect model (planner). Default: claude-sonnet-4-6.
        editor_model: Editor model (applies changes). Defaults to same as model.
        timeout: Subprocess timeout in seconds (default: 600).

    Returns:
        dict with keys: status, output, stderr, returncode
    """
    if not file_paths:
        return {"status": "error", "message": "file_paths must not be empty"}
    try:
        runner = _get_runner(model=model, timeout=timeout)
        result = runner.run_architect(file_paths, task, editor_model=editor_model)
        return {
            "status": "success",
            "output": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="aider",
    description=(
        "Return current aider configuration: model, API key presence, "
        "and timeout settings."
    ),
)
def aider_config() -> dict[str, Any]:
    """Return current aider configuration from environment.

    Returns:
        dict with keys: status, model, has_anthropic_key, has_openai_key,
        has_any_key, timeout
    """
    try:
        cfg_fn = _get_config()
        cfg = cfg_fn()
        return {
            "status": "success",
            "model": cfg.model,
            "has_anthropic_key": cfg.has_anthropic_key,
            "has_openai_key": cfg.has_openai_key,
            "has_any_key": cfg.has_any_key,
            "timeout": cfg.timeout,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
