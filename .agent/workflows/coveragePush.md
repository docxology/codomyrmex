---
description: Push Codomyrmex test coverage above the 60% gate. Zero-mock policy applies.
---

# Coverage Push Workflow

Current gate: **60%** (`[tool.coverage.report] fail_under` in `pyproject.toml`, enforced by CI's coverage gate). (Historical note: Sprint 22 baseline was ~32%.)

## 1. Find High-ROI Targets

```bash
uv run pytest --cov=src/codomyrmex --cov-fail-under=60 --cov-report=term-missing -q 2>&1 | grep " 0%" | head -30
```

Focus on 0%-covered files with the most statements.

## 2. Test File Template

```python
"""Tests for <module>.<file> -- zero-mock, zero-stub."""
import pytest
from codomyrmex.<module>.<file> import <ClassName>

class Test<ClassName>Basics:
    def test_<behavior>(self):
        result = <ClassName>().<method>(<real_input>)
        assert result == <expected>

    def test_<error_path>(self):
        with pytest.raises(<ExceptionType>):
            <ClassName>().<method>(<bad_input>)
```

Skip guard for external deps:

```python
import os
HAS_KEY = bool(os.getenv('API_KEY'))

@pytest.mark.skipif(not HAS_KEY, reason='API_KEY not set')
class TestWithExternalAPI: ...
```

## 3. Zero-Mock Policy

NEVER: `from unittest.mock import MagicMock, patch` | `monkeypatch.setattr` | `assert True` | `pass` in test body

## 4. Verify and Commit

```bash
uv run pytest src/codomyrmex/tests/unit/<module>/ -v --tb=short
git add src/codomyrmex/tests/unit/<module>/test_<file>.py
git commit --no-verify -m "test(<module>): add coverage for <file>"
```
