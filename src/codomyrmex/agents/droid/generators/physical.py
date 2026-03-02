"""Physical management generators for droid tasks.

This module re-exports all generators from the `physical_generators` subpackage
for backward compatibility.
"""

from .physical_generators import (  # noqa: F401
    create_physical_management_module,
    generate_physical_api_spec,
    generate_physical_docs_content,
    generate_physical_examples,
    generate_physical_init_content,
    generate_physical_manager_content,
    generate_physical_readme_content,
    generate_physical_requirements,
    generate_physical_simulation_content,
    generate_physical_tests,
    generate_sensor_integration_content,
    ollama_module,
    prompt_engineering,
    refactor_todo_processing,
    test_statistics_display,
    testing_and_docs,
)

__all__ = [
    "create_physical_management_module",
    "test_statistics_display",
    "refactor_todo_processing",
    "testing_and_docs",
    "prompt_engineering",
    "ollama_module",
    "generate_physical_init_content",
    "generate_physical_manager_content",
    "generate_physical_simulation_content",
    "generate_sensor_integration_content",
    "generate_physical_readme_content",
    "generate_physical_api_spec",
    "generate_physical_examples",
    "generate_physical_tests",
    "generate_physical_requirements",
    "generate_physical_docs_content",
]
