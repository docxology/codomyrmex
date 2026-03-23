"""
Testing Utilities

Property-based testing, fuzzing, fixtures, and test data generation.


Submodules:
    chaos: Consolidated chaos capabilities.
    workflow: Consolidated workflow capabilities."""

# Shared schemas for cross-module interop
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

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
            "help": "list available test frameworks and strategies",
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
            "args": {
                "--path": {"help": "Path to test file or directory", "required": True}
            },
            "handler": lambda path=".", **kwargs: print(f"Running tests at: {path}"),
        },
    }


__all__ = [
    "DictGenerator",
    # Fixtures
    "Fixture",
    "FixtureManager",
    "FloatGenerator",
    "FuzzResult",
    "Fuzzer",
    # Fuzzing
    "FuzzingStrategy",
    # Generators
    "GeneratorStrategy",
    "IntGenerator",
    "ListGenerator",
    "OneOfGenerator",
    # Property testing
    "PropertyTestResult",
    "StringGenerator",
    "TestDataFactory",
    "chaos",
    # CLI integration
    "cli_commands",
    "fixture",
    "property_test",
    "workflow",
]
