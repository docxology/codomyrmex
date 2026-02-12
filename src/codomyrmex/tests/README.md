# Tests Module

**Version**: v0.1.0 | **Status**: Active

Test suites with real data analysis (no mock methods).


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Quick Start

```bash
# Run all tests
pytest src/codomyrmex/tests/

# Run unit tests only
pytest src/codomyrmex/tests/unit/

# Run integration tests
pytest src/codomyrmex/tests/integration/

# Run with coverage
pytest src/codomyrmex/tests/ --cov=codomyrmex --cov-report=html

# Run specific module tests
pytest src/codomyrmex/tests/unit/test_llm.py -v
```

## Directory Structure

| Directory | Description |
|-----------|-------------|
| `unit/` | Unit tests for individual functions/classes |
| `integration/` | Integration tests for module interactions |
| `performance/` | Performance benchmarks and load tests |
| `fixtures/` | Shared test fixtures and factories |
| `examples/` | Example test patterns |

## Key Files

| File | Description |
|------|-------------|
| `conftest.py` | Shared pytest fixtures |
| `RUNNING_TESTS.md` | Detailed test running guide |

## Writing Tests

```python
# tests/unit/test_mymodule.py
import pytest
from codomyrmex.mymodule import MyClass

@pytest.fixture
def my_instance():
    return MyClass()

def test_feature(my_instance):
    result = my_instance.feature()
    assert result is not None
```


## Documentation

- [Module Documentation](../../../docs/modules/tests/README.md)
- [Agent Guide](../../../docs/modules/tests/AGENTS.md)
- [Specification](../../../docs/modules/tests/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
