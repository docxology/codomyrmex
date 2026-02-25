"""Physical management generators — modularized subpackage.

This package re-exports all generator functions for backward compatibility.
"""

from .tasks import (
    create_physical_management_module, test_statistics_display, refactor_todo_processing,
    testing_and_docs, prompt_engineering, ollama_module,
)
from .content_generators import (
    generate_physical_init_content, generate_physical_manager_content, generate_physical_simulation_content, generate_sensor_integration_content,
)
from .doc_generators import (
    generate_physical_readme_content, generate_physical_api_spec, generate_physical_examples,
    generate_physical_tests, generate_physical_requirements, generate_physical_docs_content,
)

__all__ = ['create_physical_management_module', 'test_statistics_display', 'refactor_todo_processing', 'testing_and_docs', 'prompt_engineering', 'ollama_module', 'generate_physical_init_content', 'generate_physical_manager_content', 'generate_physical_simulation_content', 'generate_sensor_integration_content', 'generate_physical_readme_content', 'generate_physical_api_spec', 'generate_physical_examples', 'generate_physical_tests', 'generate_physical_requirements', 'generate_physical_docs_content']
