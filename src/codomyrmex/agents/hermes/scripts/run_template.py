"""Template-driven Hermes execution.

Renders a ``PromptTemplate`` from the template library, then sends
it through ``HermesClient``.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_template code_review
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.hermes_client import HermesClient, HermesError
from codomyrmex.agents.hermes.templates import TemplateLibrary


def render_template(
    template_name: str,
    variables: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Render a template without executing it.

    Args:
        template_name: Name of a built-in or registered template.
        variables: Variable values to substitute.

    Returns:
        Dict with ``template_name``, ``system_prompt``, ``rendered_prompt``,
        ``variables_used``.
    """
    lib = TemplateLibrary()
    template = lib.get(template_name)

    # Provide sensible defaults for demo
    defaults = _demo_variables(template_name)
    merged = {**defaults, **(variables or {})}
    rendered = template.render_safe(**merged)

    return {
        "template_name": template_name,
        "system_prompt": template.system_prompt,
        "rendered_prompt": rendered,
        "variables_used": list(merged.keys()),
    }


def run_template(
    template_name: str,
    variables: dict[str, str] | None = None,
    *,
    backend: str = "auto",
    model: str = "hermes3",
) -> dict[str, Any]:
    """Render a template and execute it through Hermes.

    Args:
        template_name: Template name from the library.
        variables: Variable overrides.
        backend: Backend preference.
        model: Ollama model name.

    Returns:
        Dict with keys: ``status``, ``template``, ``content``,
        ``error``, ``elapsed_s``.
    """
    rendered = render_template(template_name, variables)

    client = HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_model": model,
        }
    )

    start = time.time()
    try:
        request = AgentRequest(
            prompt=rendered["rendered_prompt"],
            context={"system_prompt": rendered["system_prompt"]},
        )
        response = client.execute(request)
        elapsed = time.time() - start
        return {
            "status": "success" if response.is_success() else "error",
            "template": rendered,
            "content": response.content,
            "error": response.error,
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }
    except HermesError as exc:
        elapsed = time.time() - start
        return {
            "status": "error",
            "template": rendered,
            "content": "",
            "error": str(exc),
            "elapsed_s": round(elapsed, 3),
            "backend": client.active_backend,
        }


def list_available_templates() -> list[str]:
    """Return sorted list of all available template names."""
    return TemplateLibrary().list_templates()


def _demo_variables(template_name: str) -> dict[str, str]:
    """Provide sensible demo variables for each built-in template."""
    demos: dict[str, dict[str, str]] = {
        "code_review": {
            "language": "python",
            "code": "def add(a, b):\n    return a + b",
            "focus_areas": "correctness, style",
        },
        "task_decomposition": {
            "task_description": "Build a REST API for user management",
            "context": "Python FastAPI project, PostgreSQL backend",
            "constraints": "Must be done in 2 sprints",
        },
        "documentation": {
            "doc_type": "API reference",
            "component_name": "HermesClient",
            "description": "Chat completion client with dual backend support",
            "audience": "developers",
        },
        "debugging": {
            "error_message": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "context": "Data processing pipeline",
            "language": "python",
            "code": "total = count + label",
            "expected": "Concatenated string",
            "actual": "TypeError exception",
        },
    }
    return demos.get(template_name, {})


def main() -> None:
    """CLI entry point — pass template name as first argument."""
    name = sys.argv[1] if len(sys.argv) > 1 else "code_review"
    if name == "--list":
        for t in list_available_templates():
            print(f"  • {t}")
        return
    result = run_template(name)
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
