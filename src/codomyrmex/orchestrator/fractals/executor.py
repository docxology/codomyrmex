"""Executor for atomic tasks inside git worktrees."""

import os
import shutil
import subprocess
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

from .models import TaskNode
from .planner import format_lineage
from .workspace import WorkspaceManager

logger = get_logger(__name__)


def resolve_bin(name: str) -> str:
    """Resolve a binary in the system PATH."""
    bin_path = shutil.which(name)
    return bin_path or name


CLAUDE_BIN = resolve_bin("claude")


def build_prompt(task: TaskNode) -> str:
    """Build the context prompt for the agent to execute."""
    hierarchy = format_lineage(task.lineage, task.description)
    sibling_context = (
        "\nYou are one of several agents working in parallel on sibling tasks under the same parent. "
        "Do not duplicate work that sibling tasks would handle -- focus only on your specific task."
        if task.lineage
        else ""
    )

    return f"""You are a coding agent executing one task in a larger project.

PROJECT CONTEXT:
{hierarchy}
{sibling_context}

YOUR TASK: {task.description}

INSTRUCTIONS:
- Implement this task fully -- write real, working code.
- Create any files and directories needed. Use sensible project structure.
- Keep your changes focused. Do not implement functionality that belongs to other tasks in the hierarchy.
- Commit your work with a clear commit message describing what you built.
"""


def execute_leaf_task(
    task: TaskNode, workspace_manager: WorkspaceManager, provider: str = "claude"
) -> str:
    """Execute a single atomic task using the specified provider in a git worktree."""
    logger.info("[execute] [%s] '%s' (%s)", task.id, task.description, provider)

    worktree_path = workspace_manager.create_worktree(task.id)
    logger.info("[execute] [%s] worktree: %s", task.id, worktree_path)

    prompt = build_prompt(task)

    if provider == "claude":
        return _invoke_claude(prompt, worktree_path)
    if provider == "codomyrmex":
        return _invoke_internal_agent(prompt, worktree_path)
    raise ValueError(f"Unknown executor provider: {provider}")


def _invoke_claude(prompt: str, cwd: Path) -> str:
    """Invoke the Anthropic Claude CLI tool."""
    env = os.environ.copy()
    if "CLAUDECODE" in env:
        del env["CLAUDECODE"]

    cmd = [CLAUDE_BIN, "--dangerously-skip-permissions", "-p", prompt]
    logger.debug("[executor] spawning: %s", " ".join(cmd))

    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = result.stderr.strip() or f"Exited with code {result.returncode}"
        raise RuntimeError(f"Claude CLI execution failed: {error_msg}")

    return result.stdout


def _invoke_internal_agent(prompt: str, cwd: Path) -> str:
    """Invoke the internal Codomyrmex agent system (Zero-Mock Fallback/Alternative)."""
    from codomyrmex.agents.core.base import AgentRequest
    from codomyrmex.agents.llm_client import get_llm_client

    client = get_llm_client("fractals_executor")
    sys_prompt = "You are an autonomous engineering agent executing tasks in a git worktree. Produce raw code outputs as requested."

    req = AgentRequest(prompt=prompt, metadata={"system": sys_prompt})
    resp = client.execute(req)

    if resp.error:
        raise RuntimeError(f"Internal Agent Error: {resp.error}")

    # Commit the changes as the task requires (simulated logic for the agent)
    # Since simple LLM client just returns text, an actual agent framework loop is needed
    # for full autonomy, but this suffices for the integration layer base.
    return resp.content
