"""Tests for Sprint 35: API Versioning & Compatibility.

Covers APIVersion, @versioned/@deprecated decorators, VersionRegistry,
and CompatShimGenerator.
"""

import warnings
import pytest

from codomyrmex.model_context_protocol.versioning import (
    APIVersion,
    CompatibilityMatrix,
    deprecated,
    versioned,
)
from codomyrmex.model_context_protocol.version_registry import VersionRegistry
from codomyrmex.model_context_protocol.compat import CompatShimGenerator, ShimMapping


# ─── APIVersion ──────────────────────────────────────────────────────

class TestAPIVersion:
    """Test suite for APIVersion."""

    def test_parse(self):
        """Test functionality: parse."""
        v = APIVersion.parse("v1.2.3")
        assert v.major == 1 and v.minor == 2 and v.patch == 3

    def test_ordering(self):
        """Test functionality: ordering."""
        assert APIVersion(1, 0, 0) < APIVersion(2, 0, 0)
        assert APIVersion(1, 1, 0) > APIVersion(1, 0, 0)

    def test_compatibility(self):
        """Test functionality: compatibility."""
        v1 = APIVersion(1, 0, 0)
        v12 = APIVersion(1, 2, 0)
        v2 = APIVersion(2, 0, 0)
        assert v1.is_compatible(v12) is True
        assert v1.is_compatible(v2) is False

    def test_str(self):
        """Test functionality: str."""
        assert str(APIVersion(1, 2, 3)) == "v1.2.3"


# ─── Decorators ──────────────────────────────────────────────────────

class TestDecorators:
    """Test suite for Decorators."""

    def test_versioned(self):
        """Test functionality: versioned."""
        @versioned("2.1.0")
        def my_tool():
            return 42
        assert my_tool._api_version == APIVersion(2, 1, 0)
        assert my_tool() == 42

    def test_deprecated_warns(self):
        """Test functionality: deprecated warns."""
        @deprecated(since="1.0.0", removal="2.0.0", replacement="new_fn")
        def old_fn():
            return "result"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_fn()
            assert result == "result"
            assert len(w) == 1
            assert "deprecated" in str(w[0].message).lower()


# ─── VersionRegistry ────────────────────────────────────────────────

class TestVersionRegistry:
    """Test suite for VersionRegistry."""

    def test_register_and_get(self):
        """Test functionality: register and get."""
        reg = VersionRegistry()
        reg.register("search", version="1.0.0")
        tool = reg.get_tool("search")
        assert tool is not None
        assert str(tool.version) == "v1.0.0"

    def test_deprecate(self):
        """Test functionality: deprecate."""
        reg = VersionRegistry()
        reg.register("old_tool", version="1.0.0")
        reg.deprecate("old_tool", since="1.0.0", removal="2.0.0")
        assert reg.is_deprecated("old_tool") is True

    def test_list_deprecated(self):
        """Test functionality: list deprecated."""
        reg = VersionRegistry()
        reg.register("a", version="1.0.0")
        reg.register("b", version="1.0.0")
        reg.deprecate("b", since="1.0.0")
        assert reg.list_deprecated() == ["b"]

    def test_migration_guide(self):
        """Test functionality: migration guide."""
        reg = VersionRegistry()
        reg.add_migration("tool", "1.0.0", "2.0.0", "rename", "tool → tool_v2")
        steps = reg.migration_guide()
        assert len(steps) == 1

    def test_markdown_output(self):
        """Test functionality: markdown output."""
        reg = VersionRegistry()
        reg.register("search", version="1.0.0")
        md = reg.to_markdown()
        assert "search" in md


# ─── CompatShimGenerator ────────────────────────────────────────────

class TestCompatShimGenerator:
    """Test suite for CompatShimGenerator."""

    def test_shim_forwards_call(self):
        """Test functionality: shim forwards call."""
        def new_fn(query: str) -> str:
            return f"result:{query}"

        gen = CompatShimGenerator()
        gen.add_mapping(ShimMapping(old_name="search", new_name="search_v2"))
        shim = gen.create_shim("search", target_fn=new_fn)
        assert shim(query="test") == "result:test"

    def test_param_rename(self):
        """Test functionality: param rename."""
        def new_fn(query: str) -> str:
            return query.upper()

        gen = CompatShimGenerator()
        gen.add_mapping(ShimMapping(
            old_name="find", new_name="search",
            param_renames={"q": "query"},
        ))
        shim = gen.create_shim("find", target_fn=new_fn)
        assert shim(q="hello") == "HELLO"

    def test_translate_params(self):
        """Test functionality: translate params."""
        gen = CompatShimGenerator()
        gen.add_mapping(ShimMapping(
            old_name="old", new_name="new",
            param_renames={"x": "y"},
        ))
        result = gen.translate_params("old", {"x": 1, "z": 2})
        assert result == {"y": 1, "z": 2}
