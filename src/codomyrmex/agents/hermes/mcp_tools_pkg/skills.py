"""Hermes MCP tools — skills category."""

from __future__ import annotations

from typing import Any

from codomyrmex.agents.hermes.mcp_tools_pkg._client import _get_client
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="hermes",
    tags=["hermes", "skills", "registry", "interop"],
    description="list all skills available to the Hermes agent (CLI backend only).",
)
def hermes_skills_list() -> dict[str, Any]:
    """list available Hermes skills.

    Returns:
        dict with keys: status, output, or error info

    """
    try:
        client = _get_client(timeout=10)
        result = client.list_skills()
        if result.get("success"):
            return {"status": "success", "output": result.get("output", "")}
        return {
            "status": "error",
            "message": result.get("error", "Skills require CLI backend"),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    tags=["hermes", "skills", "registry", "interop"],
    description=(
        "Resolve registry skill_ids to Hermes CLI -s names and metadata. "
        "Uses bundled registry plus optional CODOMYRMEX_SKILLS_REGISTRY overlay."
    ),
)
def hermes_skills_resolve(skill_ids: list[str] | str) -> dict[str, Any]:
    """Map stable registry ids to Hermes preload names for MCP / PAI routing."""
    try:
        from codomyrmex.agents.hermes import skill_registry

        resolved = skill_registry.resolve_skill_ids(skill_ids)
        return {"status": "success", **resolved}
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "skill_ids_requested": [],
            "unknown_skill_ids": [],
            "hermes_preload": [],
            "resolved_entries": [],
        }


@mcp_tool(
    category="hermes",
    tags=["hermes", "skills", "registry", "interop"],
    description=(
        "Validate registry hermes_preload names against Hermes CLI skills list when available."
    ),
)
def hermes_skills_validate_registry() -> dict[str, Any]:
    """Structural + optional live check against ``hermes skills list``."""
    try:
        from codomyrmex.agents.hermes import skill_registry

        idx = skill_registry.load_skill_index()
        base: dict[str, Any] = {
            "registry_skill_count": len(idx),
            "skill_ids": sorted(idx.keys()),
        }
        client = _get_client(timeout=30)
        if client.active_backend != "cli":
            return {
                **base,
                "status": "skipped",
                "reason": "Hermes CLI backend required for live list comparison",
            }
        res = client.list_skills()
        if not res.get("success"):
            return {
                **base,
                "status": "error",
                "message": res.get("error", "list_skills failed"),
            }
        out = res.get("output") or ""
        val = skill_registry.validate_registry_against_cli_lines(out, index=idx)
        return {"status": val.get("status", "ok"), **base, **val}
    except Exception as exc:
        return {"status": "error", "message": str(exc), "registry_skill_count": 0}


@mcp_tool(
    category="hermes",
    description="list all available Hermes prompt template names.",
)
def hermes_template_list() -> dict[str, Any]:
    """list available Hermes prompt templates.

    Returns:
        dict with keys: status, templates (list of names), count

    """
    try:
        from codomyrmex.agents.hermes.templates import TemplateLibrary

        lib = TemplateLibrary()
        names = lib.list_templates()
        return {"status": "success", "templates": names, "count": len(names)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Render a named Hermes prompt template with variable substitution. "
        "Returns the rendered user prompt and system prompt."
    ),
)
def hermes_template_render(
    template_name: str,
    variables: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Render a Hermes prompt template.

    Args:
        template_name: Name of the built-in template (e.g. ``"code_review"``).
        variables: Optional dict of variable substitutions.  Missing variables
            are left as ``{placeholder}`` in the output (safe rendering).

    Returns:
        dict with keys: status, template_name, rendered_prompt, system_prompt, variables_used

    """
    try:
        from codomyrmex.agents.hermes.templates import TemplateLibrary

        lib = TemplateLibrary()
        template = lib.get(template_name)
        rendered = template.render_safe(**(variables or {}))
        return {
            "status": "success",
            "template_name": template_name,
            "rendered_prompt": rendered,
            "system_prompt": template.system_prompt,
            "variables_used": list((variables or {}).keys()),
        }
    except KeyError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Install a Hermes skill from a git repository URL. "
        "Runs hermes skills install <repo_url>. "
        "Restart the gateway after installation for the skill to be available."
    ),
)
def hermes_skill_install(repo_url: str) -> dict[str, Any]:
    """Install a Hermes skill from a git URL.

    Args:
        repo_url: Git URL of the skill repository, e.g.
            ``"https://github.com/nativ3ai/hermes-geopolitical-market-sim.git"``.

    Returns:
        dict with keys: status, output, error
    """
    try:
        client = _get_client()
        result = client.install_skill(repo_url)
        return {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "tip": "Run hermes gateway restart to activate the new skill.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    tags=["hermes", "mcp", "fastmcp", "interop"],
    description=(
        "Generate a FastMCP server scaffold for Codomyrmex↔Hermes integration. "
        "Wraps optional-skills/mcp/fastmcp/scaffold_fastmcp.py."
    ),
)
def hermes_fastmcp_scaffold(
    output_dir: str,
    server_name: str,
    force: bool = False,
) -> dict[str, Any]:
    """Scaffold a FastMCP server package via Hermes optional-skills."""
    try:
        import json

        client = _get_client()
        result = client.scaffold_fastmcp(
            output_dir=output_dir,
            server_name=server_name,
            force=force,
        )
        response: dict[str, Any] = {
            "status": "success" if result.get("success") else "error",
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "script_path": result.get("script_path", ""),
        }
        output = result.get("output", "").strip()
        if output.startswith("{") and output.endswith("}"):
            try:
                payload = json.loads(output)
                if isinstance(payload, dict):
                    response["scaffold"] = payload
            except json.JSONDecodeError:
                pass
        return response
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="hermes",
    description=(
        "Initiate an autonomous red/green/refactor coverage loop on a target filepath. "
        "The system will repeatedly run pytest and repair the codebase until the tests pass."
    ),
)
def hermes_run_coverage_loop(target_filepath: str) -> dict[str, Any]:
    """Autonomous pytest healing loop.

    Args:
        target_filepath: The path to the test file or directory to verify.

    Returns:
        dict containing status, number of turns taken, and output trace.

    """
    try:
        # Load the client explicitly configured for the current repository
        client = _get_client()
        result = client._run_coverage_loop(target_filepath)
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
