"""
Testing Utilities

Property-based testing, fuzzing, fixtures, and test data generation.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .strategies import (
    GeneratorStrategy,
    IntGenerator,
    FloatGenerator,
    StringGenerator,
    ListGenerator,
    DictGenerator,
    OneOfGenerator,
)

from .property_testing import (
    PropertyTestResult,
    property_test,
)

from .fuzzing import (
    FuzzingStrategy,
    FuzzResult,
    Fuzzer,
)

from .fixture_utils import (
    Fixture,
    FixtureManager,
    fixture,
    TestDataFactory,
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
