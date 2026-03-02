"""
Property-Based Testing

Property testing decorator and result types.
"""

import functools
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .strategies import GeneratorStrategy


@dataclass
class PropertyTestResult:
    """Result of a property-based test."""
    passed: bool
    iterations: int
    failures: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0
    shrunk_example: dict[str, Any] | None = None


def property_test(
    iterations: int = 100,
    **generators: GeneratorStrategy,
):
    """Decorator for property-based tests."""
    def decorator(func: Callable) -> Callable:
        """Decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper."""
            failures = []
            start = datetime.now()

            for _i in range(iterations):
                test_kwargs = {
                    name: gen.generate()
                    for name, gen in generators.items()
                }
                test_kwargs.update(kwargs)

                try:
                    result = func(*args, **test_kwargs)
                    if result is False:
                        failures.append(test_kwargs.copy())
                except Exception as e:
                    failures.append({
                        **test_kwargs,
                        "__error__": str(e),
                    })

            duration = (datetime.now() - start).total_seconds()

            return PropertyTestResult(
                passed=len(failures) == 0,
                iterations=iterations,
                failures=failures[:10],  # Limit stored failures
                duration_seconds=duration,
            )

        return wrapper
    return decorator
