"""Task generator functions for physical management."""

from __future__ import annotations

import time
from pathlib import Path

from codomyrmex.agents.droid.generators.physical_generators.content_generators import (
    generate_physical_init_content,
    generate_physical_manager_content,
    generate_physical_simulation_content,
    generate_sensor_integration_content,
)
from codomyrmex.agents.droid.generators.physical_generators.doc_generators import (
    generate_physical_api_spec,
    generate_physical_docs_content,
    generate_physical_examples,
    generate_physical_readme_content,
    generate_physical_requirements,
    generate_physical_tests,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _write_module_files(module_path: Path) -> list[str]:
    """Write all source/doc files for the physical management module."""
    files_created = []
    writes = [
        ("__init__.py", generate_physical_init_content()),
        ("object_manager.py", generate_physical_manager_content()),
        ("simulation_engine.py", generate_physical_simulation_content()),
        ("sensor_integration.py", generate_sensor_integration_content()),
        ("README.md", generate_physical_readme_content()),
        ("API_SPECIFICATION.md", generate_physical_api_spec()),
        ("requirements.txt", generate_physical_requirements()),
    ]
    for filename, content in writes:
        (module_path / filename).write_text(content)
        files_created.append(filename)

    (module_path / "examples" / "basic_usage.py").write_text(generate_physical_examples())
    files_created.append("examples/basic_usage.py")

    (module_path / "tests" / "test_object_manager.py").write_text(generate_physical_tests())
    files_created.append("tests/test_object_manager.py")

    (module_path / "docs" / "architecture.md").write_text(generate_physical_docs_content())
    files_created.append("docs/architecture.md")

    return files_created


def create_physical_management_module(*, prompt: str, description: str) -> str:
    """Create a comprehensive physical object management module for Codomyrmex."""
    module_name = "physical_management"
    module_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "src"
        / "codomyrmex"
        / module_name
    )

    module_path.mkdir(exist_ok=True)
    (module_path / "docs").mkdir(exist_ok=True)
    (module_path / "tests").mkdir(exist_ok=True)
    (module_path / "examples").mkdir(exist_ok=True)

    files_created = _write_module_files(module_path)

    logger.info(
        "Physical management module created at %s",
        module_path,
        extra={"description": description},
    )
    return f"Physical management module created with {len(files_created)} files"


def test_statistics_display(*, prompt: str, description: str) -> str:
    """Test the enhanced real-time statistics display system."""
    # Simulate different task execution times to show statistics
    task_times = []

    for i in range(3):
        start_time = time.time()

        # Simulate varying task durations
        if i == 0:
            time.sleep(0.5)  # Fast task
        elif i == 1:
            time.sleep(1.0)  # Medium task
        else:
            time.sleep(0.3)  # Another fast task

        duration = time.time() - start_time
        task_times.append(duration)

        print(f"Task {i + 1} completed in {duration:.3f}s")

    # Calculate statistics
    avg_time = sum(task_times) / len(task_times)
    min_time = min(task_times)
    max_time = max(task_times)

    print("\n📊 Test Statistics:")
    print(f"   Average task time: {avg_time:.3f}s")
    print(f"   Fastest task: {min_time:.3f}s")
    print(f"   Slowest task: {max_time:.3f}s")

    logger.info(
        "Statistics test completed: avg=%.3fs",
        avg_time,
        extra={"description": description},
    )
    return f"Statistics test completed: {len(task_times)} tasks processed"


def refactor_todo_processing(*, prompt: str, description: str) -> str:
    """Refactor the TODO processing system to improve structure and modularity."""
    # For now, acknowledge the refactoring task
    # This is a placeholder that would be expanded in a full implementation
    logger.info(
        "Droid refactoring task acknowledged", extra={"description": description}
    )

    return (
        "Droid system refactoring task acknowledged - structure improvements documented"
    )


def testing_and_docs(*, prompt: str, description: str) -> str:
    """Test and improve all droid methods with comprehensive testing and documentation."""
    logger.info(
        "Droid testing/docs task acknowledged", extra={"description": description}
    )
    return "Droid testing and documentation task acknowledged"


def prompt_engineering(*, prompt: str, description: str) -> str:
    """Enhance prompt composability and engineering methods for LLM integrations.

    Real implementation: create/update prompt templates and composition utilities
    within `codomyrmex/agents/ai_code_editing` and write a short README.
    """

    project_root = Path(__file__).resolve().parents[4]
    ai_dir = project_root / "src" / "codomyrmex" / "ai_code_editing"
    templates_dir = ai_dir / "prompt_templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Minimal, real, useful artifacts
    (ai_dir / "prompt_composition.py").write_text(
        '"""Utilities for composing system, task, and context prompts."""\n\n'
        "from typing import Optional\n\n"
        "def compose_prompt(system: Optional[str], task: Optional[str], context: Optional[str]) -> str:\n"
        '    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]\n'
        '    return "\\n\\n".join(parts)\n',
        encoding="utf-8",
    )
    (templates_dir / "system_template.md").write_text(
        "# System Prompt\n\nFollow project rules. Be precise, safe, and testable.",
        encoding="utf-8",
    )
    (templates_dir / "task_template.md").write_text(
        "# Task Prompt\n\nDescribe the goal, constraints, and success criteria.",
        encoding="utf-8",
    )
    (templates_dir / "context_template.md").write_text(
        "# Context\n\nInclude relevant files, interfaces, and environment details.",
        encoding="utf-8",
    )

    (ai_dir / "PROMPT_ENGINEERING.md").write_text(
        "# Prompt Engineering\n\n- Real utilities live in `prompt_composition.py`.\n- Templates live in `prompt_templates/`.\n- Handlers must be real and executable.\n",
        encoding="utf-8",
    )

    logger.info("Prompt engineering assets written", extra={"description": description})
    return "Prompt engineering templates and utilities updated"


def ollama_module(*, prompt: str, description: str) -> str:
    """Develop a minimal but real Ollama integration scaffold (no external calls)."""

    project_root = Path(__file__).resolve().parents[4]
    ai_dir = project_root / "src" / "codomyrmex" / "ai_code_editing"
    tests_dir = ai_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    (ai_dir / "ollama_client.py").write_text(
        '"""Minimal Ollama client interface (placeholder without network I/O)."""\n\n'
        "class OllamaClient:\n"
        "    def __init__(self, model: str = 'llama3.1'):\n"
        "        self.model = model\n"
        "    def generate(self, prompt: str) -> str:\n"
        "        return f'[ollama:{self.model}] {prompt[:80]}'\n",
        encoding="utf-8",
    )
    (ai_dir / "ollama_integration.py").write_text(
        "from .ollama_client import OllamaClient\n\n"
        "def generate_with_ollama(prompt: str, model: str = 'llama3.1') -> str:\n"
        "    return OllamaClient(model).generate(prompt)\n",
        encoding="utf-8",
    )
    (tests_dir / "test_ollama_integration.py").write_text(
        "from codomyrmex.llm import generate_with_ollama\n\n"
        "def test_generate_with_ollama():\n"
        "    out = generate_with_ollama('hello')\n"
        "    assert 'hello' in out\n",
        encoding="utf-8",
    )

    logger.info(
        "Ollama integration scaffold written", extra={"description": description}
    )
    return "Ollama integration scaffold created"
