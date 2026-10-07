"""Package-level validation API documented in validation/API_SPECIFICATION.md."""

from __future__ import annotations

import subprocess
import sys

import pytest

from codomyrmex import validation
from codomyrmex.validation import (
    ValidationResult,
    Validator,
    get_errors,
    is_valid,
    validate,
)

SCHEMA = {"type": "integer"}


@pytest.mark.unit
def test_is_valid() -> None:
    assert is_valid(42, SCHEMA) is True
    assert is_valid("forty-two", SCHEMA) is False


@pytest.mark.unit
def test_validate_and_get_errors_agree_with_validator() -> None:
    result = validate("forty-two", SCHEMA)
    assert isinstance(result, ValidationResult)
    assert result.is_valid is False
    assert len(get_errors("forty-two", SCHEMA)) == len(result.errors) >= 1
    assert get_errors(42, SCHEMA) == []
    assert Validator().is_valid(42, SCHEMA) is is_valid(42, SCHEMA)


@pytest.mark.unit
def test_unknown_attribute_raises() -> None:
    with pytest.raises(AttributeError):
        _ = validation.not_a_real_export


@pytest.mark.unit
def test_package_import_does_not_load_the_engine() -> None:
    code = (
        "import sys, codomyrmex.validation; "
        "print('codomyrmex.validation.validator' in sys.modules)"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert out.stdout.strip() == "False"
