"""Full Hermes orchestration pipeline.

Chains: status check → template render → chat execution → session
persistence → summary report.  This is the showcase entry point
demonstrating all subsystems working together.

Usage::

    python -m codomyrmex.agents.hermes.scripts.run_pipeline
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from codomyrmex.agents.hermes.scripts.run_chat import run_chat
from codomyrmex.agents.hermes.scripts.run_session import run_session
from codomyrmex.agents.hermes.scripts.run_status import run_status
from codomyrmex.agents.hermes.scripts.run_template import (
    list_available_templates,
    render_template,
)


def run_pipeline(
    *,
    task: str = "code_review",
    prompt: str = "Explain the observer pattern in one paragraph.",
    session_prompts: list[str] | None = None,
    db_path: str = ":memory:",
    backend: str = "auto",
    model: str = "hermes3",
) -> dict[str, Any]:
    """Run the full Hermes orchestration pipeline.

    Steps:
        1. **Status** — probe backend availability
        2. **Templates** — list available templates, render one
        3. **Chat** — single-turn execution
        4. **Session** — multi-turn persistence round-trip
        5. **Summary** — aggregate results

    Args:
        task: Template name to render.
        prompt: Prompt for single-turn chat.
        session_prompts: Prompts for multi-turn session.
        db_path: SQLite path for session persistence.
        backend: Backend preference.
        model: Ollama model name.

    Returns:
        Pipeline summary dict with results from each stage.
    """
    start = time.time()
    results: dict[str, Any] = {"stages": {}}

    # ── Stage 1: Status ──────────────────────────────────────────────
    status_result = run_status(backend=backend, model=model)
    results["stages"]["status"] = {
        "active_backend": status_result["active_backend"],
        "cli_available": status_result["cli_available"],
        "ollama_available": status_result["ollama_available"],
        "success": status_result["success"],
    }

    # ── Stage 2: Templates ───────────────────────────────────────────
    available = list_available_templates()
    rendered = render_template(task)
    results["stages"]["templates"] = {
        "available_count": len(available),
        "available": available,
        "rendered_template": task,
        "rendered_prompt_length": len(rendered["rendered_prompt"]),
    }

    # ── Stage 3: Chat ────────────────────────────────────────────────
    chat_result = run_chat(prompt, backend=backend, model=model)
    results["stages"]["chat"] = {
        "status": chat_result["status"],
        "content_length": len(chat_result.get("content", "")),
        "elapsed_s": chat_result.get("elapsed_s", 0),
        "backend": chat_result.get("backend", "unknown"),
    }

    # ── Stage 4: Session ─────────────────────────────────────────────
    if session_prompts is None:
        session_prompts = [
            "What is the observer pattern?",
            "Give a Python example.",
        ]
    session_result = run_session(
        session_prompts, db_path=db_path, backend=backend, model=model,
    )
    results["stages"]["session"] = {
        "status": session_result["status"],
        "session_id": session_result["session_id"],
        "message_count": session_result["message_count"],
        "persisted": session_result["persisted"],
        "reloaded": session_result["reloaded"],
    }

    # ── Stage 5: Summary ─────────────────────────────────────────────
    elapsed = time.time() - start
    all_ok = all(
        stage.get("success", stage.get("status")) in (True, "success")
        for stage in results["stages"].values()
    )
    results["pipeline_status"] = "success" if all_ok else "partial"
    results["total_elapsed_s"] = round(elapsed, 3)
    results["backend"] = status_result["active_backend"]

    return results


def main() -> None:
    """CLI entry point."""
    result = run_pipeline()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["pipeline_status"] == "success" else 1)


if __name__ == "__main__":
    main()
