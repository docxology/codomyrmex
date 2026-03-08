"""Tests for agents.hermes.templates — PromptTemplate and TemplateLibrary.

Zero-Mock: All tests use real template objects and string rendering.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.hermes.templates import (
    CODE_REVIEW,
    DEBUGGING,
    DOCUMENTATION,
    TASK_DECOMPOSITION,
    TemplateLibrary,
)
from codomyrmex.agents.hermes.templates.models import PromptTemplate

# ── PromptTemplate ────────────────────────────────────────────────────


class TestPromptTemplate:
    """Verify template rendering."""

    def test_render_all_variables(self) -> None:
        t = PromptTemplate(
            name="test",
            user_template="Hello {name}, you are {role}",
            variables=["name", "role"],
        )
        result = t.render(name="Alice", role="admin")
        assert result == "Hello Alice, you are admin"

    def test_render_missing_variable_raises(self) -> None:
        t = PromptTemplate(
            name="test",
            user_template="Hello {name}",
            variables=["name"],
        )
        with pytest.raises(KeyError, match="name"):
            t.render()

    def test_render_safe_fills_placeholders(self) -> None:
        t = PromptTemplate(
            name="test",
            user_template="Hello {name}, you are {role}",
            variables=["name", "role"],
        )
        result = t.render_safe(name="Bob")
        assert "Bob" in result
        assert "{role}" in result

    def test_extra_kwargs_ignored(self) -> None:
        t = PromptTemplate(
            name="test",
            user_template="Hello {name}",
            variables=["name"],
        )
        result = t.render(name="X", extra="ignored")
        assert result == "Hello X"


# ── Built-in templates ────────────────────────────────────────────────


class TestBuiltinTemplates:
    """Verify built-in template definitions."""

    def test_code_review_template(self) -> None:
        assert CODE_REVIEW.name == "code_review"
        assert "language" in CODE_REVIEW.variables
        assert "code" in CODE_REVIEW.variables
        result = CODE_REVIEW.render(language="python", code="x = 1", focus_areas="style")
        assert "python" in result

    def test_task_decomposition_template(self) -> None:
        assert TASK_DECOMPOSITION.name == "task_decomposition"
        result = TASK_DECOMPOSITION.render(
            task_description="Build API",
            context="Microservice",
            constraints="Budget: $0",
        )
        assert "Build API" in result

    def test_documentation_template(self) -> None:
        assert DOCUMENTATION.name == "documentation"
        assert "doc_type" in DOCUMENTATION.variables

    def test_debugging_template(self) -> None:
        assert DEBUGGING.name == "debugging"
        assert "error_message" in DEBUGGING.variables


# ── TemplateLibrary ───────────────────────────────────────────────────


class TestTemplateLibrary:
    """Verify template library operations."""

    def test_list_templates(self) -> None:
        lib = TemplateLibrary()
        names = lib.list_templates()
        assert "code_review" in names
        assert "task_decomposition" in names
        assert "documentation" in names
        assert "debugging" in names

    def test_get_existing(self) -> None:
        lib = TemplateLibrary()
        t = lib.get("code_review")
        assert t.name == "code_review"

    def test_get_nonexistent_raises(self) -> None:
        lib = TemplateLibrary()
        with pytest.raises(KeyError, match="not found"):
            lib.get("nonexistent_template")

    def test_has(self) -> None:
        lib = TemplateLibrary()
        assert lib.has("code_review") is True
        assert lib.has("nonexistent") is False

    def test_register_custom(self) -> None:
        lib = TemplateLibrary()
        custom = PromptTemplate(
            name="custom",
            user_template="Custom: {msg}",
            variables=["msg"],
        )
        lib.register(custom)
        assert lib.has("custom") is True
        assert lib.get("custom").render(msg="hello") == "Custom: hello"
