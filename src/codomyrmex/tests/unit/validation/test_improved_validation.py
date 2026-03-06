"""Zero-mock tests for the improved validation logic."""

import pytest
from pydantic import BaseModel

from codomyrmex.validation.contextual import ValidationIssue
from codomyrmex.validation.parser import TypeSafeParser
from codomyrmex.validation.rules import is_alphanumeric, is_email, is_in_range, is_url
from codomyrmex.validation.sanitizers import (
    remove_special_chars,
    sanitize_numeric,
    strip_whitespace,
    to_lowercase,
    to_uppercase,
)
from codomyrmex.validation.summary import ValidationSummary
from codomyrmex.validation.validator import Validator


@pytest.mark.unit
class TestRules:
    def test_is_email(self):
        assert is_email("test@example.com") is True
        assert is_email("invalid-email") is False
        assert is_email(None) is False

    def test_is_url(self):
        assert is_url("https://example.com") is True
        assert is_url("not-a-url") is False
        assert is_url(123) is False

    def test_is_alphanumeric(self):
        assert is_alphanumeric("abc123") is True
        assert is_alphanumeric("abc 123") is False
        assert is_alphanumeric("abc-123") is False

    def test_is_in_range(self):
        assert is_in_range(5, min_val=0, max_val=10) is True
        assert is_in_range(-1, min_val=0) is False
        assert is_in_range(11, max_val=10) is False

@pytest.mark.unit
class TestSanitizers:
    def test_strip_whitespace(self):
        assert strip_whitespace("  hello  ") == "hello"
        assert strip_whitespace(123) == 123

    def test_to_lowercase(self):
        assert to_lowercase("HELLO") == "hello"
        assert to_lowercase(None) is None

    def test_to_uppercase(self):
        assert to_uppercase("hello") == "HELLO"

    def test_remove_special_chars(self):
        assert remove_special_chars("hello!@# world") == "hello world"

    def test_sanitize_numeric(self):
        assert sanitize_numeric("123") == 123
        assert sanitize_numeric("123.45") == 123.45
        assert sanitize_numeric("abc") is None

@pytest.mark.unit
class TestValidatorImprovements:
    def test_basic_validation_email_format(self):
        v = Validator()
        schema = {"type": "string", "format": "email"}
        # Test _basic_validation directly to verify our improvements
        assert v._basic_validation("test@example.com", schema).is_valid is True
        assert v._basic_validation("invalid", schema).is_valid is False

    def test_basic_validation_url_format(self):
        v = Validator()
        schema = {"type": "string", "format": "url"}
        assert v._basic_validation("https://google.com", schema).is_valid is True
        assert v._basic_validation("google.com", schema).is_valid is False

    def test_basic_validation_range(self):
        v = Validator()
        schema = {"type": "number", "minimum": 0, "maximum": 100}
        assert v._basic_validation(50, schema).is_valid is True
        assert v._basic_validation(150, schema).is_valid is False

@pytest.mark.unit
class TestTypeCoercion:
    def test_coerce_int(self):
        assert TypeSafeParser.coerce("123", int) == 123
        assert TypeSafeParser.coerce("abc", int) is None

    def test_coerce_bool(self):
        assert TypeSafeParser.coerce("true", bool) is True
        assert TypeSafeParser.coerce("false", bool) is False

    def test_coerce_model(self):
        class MyModel(BaseModel):
            name: str
            age: int

        data = {"name": "John", "age": "30"}
        result = TypeSafeParser.coerce(data, MyModel)
        assert result is not None
        assert result.age == 30

@pytest.mark.unit
class TestErrorMessageFormatting:
    def test_validation_summary_text(self):
        issues = [
            ValidationIssue(field="email", message="Invalid email", severity="error"),
            ValidationIssue(field="age", message="Out of range", severity="warning"),
        ]
        summary = ValidationSummary(issues)
        text = summary.text()
        assert "FAILED" in text
        assert "[ERROR] email: Invalid email" in text
        assert "[WARNING] age: Out of range" in text

    def test_validation_summary_markdown(self):
        issues = [
            ValidationIssue(field="email", message="Invalid email", severity="error"),
        ]
        summary = ValidationSummary(issues)
        markdown = summary.markdown()
        assert "## Validation: ❌ **FAILED**" in markdown
        assert "| `email` | error | Invalid email |" in markdown
