"""
Testing Utilities

Property-based testing, fuzzing, fixtures, and test data generation.


Submodules:
    chaos: Consolidated chaos capabilities.
    workflow: Consolidated workflow capabilities."""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from . import chaos, workflow
from .fixture_utils import (
    Fixture,
    FixtureManager,
    TestDataFactory,
    fixture,
)
from .fuzzing import (
    Fuzzer,
    FuzzingStrategy,
    FuzzResult,
)
from .property_testing import (
    PropertyTestResult,
    property_test,
)
from .strategies import (
    DictGenerator,
    FloatGenerator,
    GeneratorStrategy,
    IntGenerator,
    ListGenerator,
    OneOfGenerator,
    StringGenerator,
)


def cli_commands():
    """Return CLI commands for the testing module."""
    return {
        "frameworks": {
            "help": "List available test frameworks and strategies",
            "handler": lambda **kwargs: print(
                "Test Frameworks:\n"
                "  - property_test  (property-based testing)\n"
                "  - fuzzer         (fuzz testing)\n"
                "  - fixtures       (fixture management)\n"
                "  - generators     (test data generation)"
            ),
        },
        "run": {
            "help": "Run tests at a given path",
            "args": {"--path": {"help": "Path to test file or directory", "required": True}},
            "handler": lambda path=".", **kwargs: print(
                f"Running tests at: {path}"
            ),
        },
    }


__all__ = [
    "chaos",
    "workflow",
    # CLI integration
    "cli_commands",
    # Generators
    "GeneratorStrategy",
    "IntGenerator",
    "FloatGenerator",
    "StringGenerator",
    "ListGenerator",
    "DictGenerator",
    "OneOfGenerator",
    # Property testing
    "PropertyTestResult",
    "property_test",
    # Fuzzing
    "FuzzingStrategy",
    "FuzzResult",
    "Fuzzer",
    # Fixtures
    "Fixture",
    "FixtureManager",
    "fixture",
    "TestDataFactory",
]
