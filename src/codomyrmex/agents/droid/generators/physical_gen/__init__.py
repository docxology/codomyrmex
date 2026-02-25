"""Physical generator modules."""

from .api_spec import generate_physical_api_spec
from .docs import generate_physical_docs_content
from .examples import generate_physical_examples
from .init import generate_physical_init_content
from .manager import generate_physical_manager_content
from .readme import generate_physical_readme_content
from .requirements import generate_physical_requirements
from .sensor import generate_sensor_integration_content
from .simulation import generate_physical_simulation_content
from .tests import generate_physical_tests

__all__ = [
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
