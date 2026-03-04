"""Tests for model_context_protocol.decorators — the @mcp_tool decorator.

Tests the decorator metadata attachment, schema generation, callable
preservation, deprecation warnings, and edge cases.
All tests use real function decoration — no mocks.
"""

import warnings

import pytest

from codomyrmex.model_context_protocol.decorators import (
    _generate_schema_from_signature,
    _map_python_type_to_json,
    _safe_default,
    mcp_tool,
)


@pytest.mark.unit
class TestMCPToolDecoratorMetadata:
    """Tests that @mcp_tool attaches correct metadata to decorated functions."""

    def test_decorator_attaches_mcp_tool_attribute(self):
        """Verify decorated function gains _mcp_tool attribute behavior."""
        @mcp_tool(category="testing", description="A unit test tool")
        def sample(x: int) -> int:
            """Sample doc."""
            return x

        assert hasattr(sample, "_mcp_tool")
        assert isinstance(sample._mcp_tool, dict)

    def test_decorator_attaches_mcp_tool_meta_alias(self):
        """Verify decorated function also has _mcp_tool_meta alias behavior."""
        @mcp_tool()
        def another():
            """Another."""
            pass

        assert hasattr(another, "_mcp_tool_meta")
        assert another._mcp_tool is another._mcp_tool_meta

    def test_category_stored_correctly(self):
        """Verify category parameter persists in metadata behavior."""
        @mcp_tool(category="math")
        def add(a: int, b: int) -> int:
            """Add numbers."""
            return a + b

        assert add._mcp_tool["category"] == "math"

    def test_description_from_explicit_param(self):
        """Verify explicit description overrides docstring behavior."""
        @mcp_tool(description="Explicit description")
        def func():
            """Docstring description."""
            pass

        assert func._mcp_tool["description"] == "Explicit description"

    def test_description_falls_back_to_docstring(self):
        """Verify omitted description uses docstring behavior."""
        @mcp_tool()
        def documented():
            """Docstring used as description."""
            pass

        assert documented._mcp_tool["description"] == "Docstring used as description."

    def test_description_empty_when_no_docstring(self):
        """Verify no docstring and no explicit description yields empty string behavior."""
        @mcp_tool()
        def undocumented():
            pass

        assert undocumented._mcp_tool["description"] == ""

    def test_name_auto_prefixed_with_codomyrmex(self):
        """Verify auto-generated name is prefixed with codomyrmex behavior."""
        @mcp_tool()
        def my_tool():
            """Tool."""
            pass

        assert my_tool._mcp_tool["name"].startswith("codomyrmex.")
        assert "my_tool" in my_tool._mcp_tool["name"]

    def test_explicit_name_used_when_provided(self):
        """Verify explicit name parameter is respected behavior."""
        @mcp_tool(name="codomyrmex.custom_name")
        def irrelevant_name():
            """Tool."""
            pass

        assert irrelevant_name._mcp_tool["name"] == "codomyrmex.custom_name"

    def test_name_without_prefix_gets_prefixed(self):
        """Verify a bare name gets codomyrmex prefix behavior."""
        @mcp_tool(name="bare_name")
        def tool():
            """Tool."""
            pass

        assert tool._mcp_tool["name"] == "codomyrmex.bare_name"

    def test_module_field_present_in_metadata(self):
        """Verify module path is captured in metadata behavior."""
        @mcp_tool()
        def tracked():
            """Tool."""
            pass

        assert "module" in tracked._mcp_tool
        # The module will be this test file's module path
        assert tracked._mcp_tool["module"] is not None

    def test_version_defaults_to_one_point_zero(self):
        """Verify version defaults to '1.0' when not specified behavior."""
        @mcp_tool()
        def versioned():
            """Tool."""
            pass

        assert versioned._mcp_tool["version"] == "1.0"

    def test_explicit_version_stored(self):
        """Verify explicit version parameter is stored behavior."""
        @mcp_tool(version="2.5")
        def v2():
            """Tool."""
            pass

        assert v2._mcp_tool["version"] == "2.5"

    def test_deprecated_in_stored(self):
        """Verify deprecated_in metadata is stored behavior."""
        @mcp_tool(deprecated_in="1.5")
        def old_tool():
            """Old tool."""
            pass

        assert old_tool._mcp_tool["deprecated_in"] == "1.5"


@pytest.mark.unit
class TestMCPToolDecoratorBehavior:
    """Tests that @mcp_tool preserves the original function behavior."""

    def test_decorated_function_returns_correct_result(self):
        """Verify decorated function still computes correctly behavior."""
        @mcp_tool()
        def multiply(a: int, b: int) -> int:
            """Multiply."""
            return a * b

        assert multiply(3, 7) == 21

    def test_decorated_function_with_kwargs(self):
        """Verify keyword arguments work after decoration behavior."""
        @mcp_tool()
        def greet(name: str, greeting: str = "Hello") -> str:
            """Greet someone."""
            return f"{greeting}, {name}!"

        assert greet(name="World") == "Hello, World!"
        assert greet(name="World", greeting="Hi") == "Hi, World!"

    def test_decorated_function_preserves_name(self):
        """Verify functools.wraps preserves __name__ behavior."""
        @mcp_tool()
        def original_name():
            """Original."""
            pass

        assert original_name.__name__ == "original_name"

    def test_decorated_function_preserves_docstring(self):
        """Verify functools.wraps preserves __doc__ behavior."""
        @mcp_tool()
        def with_doc():
            """My docstring."""
            pass

        assert with_doc.__doc__ == "My docstring."

    def test_deprecation_warning_emitted_when_deprecated(self):
        """Verify calling a deprecated tool emits DeprecationWarning behavior."""
        @mcp_tool(deprecated_in="0.9")
        def legacy():
            """Legacy tool."""
            return "old"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = legacy()
            assert result == "old"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "0.9" in str(w[0].message)

    def test_no_warning_when_not_deprecated(self):
        """Verify non-deprecated tool does not emit warnings behavior."""
        @mcp_tool()
        def current():
            """Current tool."""
            return "new"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = current()
            assert result == "new"
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 0


@pytest.mark.unit
class TestSchemaGeneration:
    """Tests for _generate_schema_from_signature and related helpers."""

    def test_schema_for_typed_parameters(self):
        """Verify schema generated from type hints behavior."""
        def func(name: str, count: int, ratio: float, flag: bool) -> str:
            pass

        schema = _generate_schema_from_signature(func)
        assert schema["type"] == "object"
        props = schema["properties"]
        assert props["name"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["ratio"]["type"] == "number"
        assert props["flag"]["type"] == "boolean"

    def test_schema_required_vs_optional(self):
        """Verify params without defaults are required behavior."""
        def func(required_param: str, optional_param: int = 42) -> None:
            pass

        schema = _generate_schema_from_signature(func)
        assert "required_param" in schema["required"]
        assert "optional_param" not in schema["required"]

    def test_schema_skips_self_and_cls(self):
        """Verify self and cls are excluded from schema behavior."""
        class MyClass:
            def method(self, x: int) -> int:
                return x

        schema = _generate_schema_from_signature(MyClass.method)
        assert "self" not in schema.get("properties", {})
        assert "x" in schema["properties"]

    def test_schema_skips_var_positional_and_var_keyword(self):
        """Verify *args and **kwargs are excluded from schema behavior."""
        def func(a: int, *args, **kwargs) -> None:
            pass

        schema = _generate_schema_from_signature(func)
        assert "args" not in schema.get("properties", {})
        assert "kwargs" not in schema.get("properties", {})
        assert "a" in schema["properties"]

    def test_schema_default_value_captured(self):
        """Verify default values appear in schema behavior."""
        def func(name: str = "world") -> str:
            return name

        schema = _generate_schema_from_signature(func)
        assert schema["properties"]["name"].get("default") == "world"

    def test_schema_list_type_mapped_to_array(self):
        """Verify list type maps to JSON array behavior."""
        def func(items: list) -> None:
            pass

        schema = _generate_schema_from_signature(func)
        assert schema["properties"]["items"]["type"] == "array"

    def test_schema_dict_type_mapped_to_object(self):
        """Verify dict type maps to JSON object behavior."""
        def func(data: dict) -> None:
            pass

        schema = _generate_schema_from_signature(func)
        assert schema["properties"]["data"]["type"] == "object"

    def test_schema_auto_generated_by_decorator(self):
        """Verify decorator auto-generates schema in metadata behavior."""
        @mcp_tool()
        def auto_schema(name: str, count: int = 1) -> str:
            """Has schema."""
            return name * count

        schema = auto_schema._mcp_tool["schema"]
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "name" in schema["required"]
        assert "count" not in schema["required"]

    def test_explicit_schema_overrides_auto(self):
        """Verify explicit schema parameter overrides auto-generation behavior."""
        custom_schema = {
            "type": "object",
            "properties": {"custom": {"type": "string"}},
            "required": ["custom"],
        }

        @mcp_tool(schema=custom_schema)
        def with_custom(a: int) -> int:
            """Custom."""
            return a

        assert with_custom._mcp_tool["schema"] is custom_schema


@pytest.mark.unit
class TestTypeMapping:
    """Tests for _map_python_type_to_json helper."""

    def test_str_maps_to_string(self):
        """Verify Python str maps to JSON string behavior."""
        assert _map_python_type_to_json(str) == "string"

    def test_int_maps_to_integer(self):
        """Verify Python int maps to JSON integer behavior."""
        assert _map_python_type_to_json(int) == "integer"

    def test_float_maps_to_number(self):
        """Verify Python float maps to JSON number behavior."""
        assert _map_python_type_to_json(float) == "number"

    def test_bool_maps_to_boolean(self):
        """Verify Python bool maps to JSON boolean behavior."""
        assert _map_python_type_to_json(bool) == "boolean"

    def test_list_maps_to_array(self):
        """Verify Python list maps to JSON array behavior."""
        assert _map_python_type_to_json(list) == "array"

    def test_dict_maps_to_object(self):
        """Verify Python dict maps to JSON object behavior."""
        assert _map_python_type_to_json(dict) == "object"

    def test_unknown_type_defaults_to_string(self):
        """Verify unrecognized types default to string behavior."""
        assert _map_python_type_to_json(bytes) == "string"


@pytest.mark.unit
class TestSafeDefault:
    """Tests for _safe_default helper that converts defaults to JSON-safe values."""

    def test_none_returns_none(self):
        """Verify None input returns None behavior."""
        assert _safe_default(None) is None

    def test_primitive_types_passthrough(self):
        """Verify str, int, float, bool pass through unchanged behavior."""
        assert _safe_default("hello") == "hello"
        assert _safe_default(42) == 42
        assert _safe_default(3.14) == 3.14
        assert _safe_default(True) is True

    def test_list_recursively_converted(self):
        """Verify lists are recursively converted behavior."""
        assert _safe_default([1, "two", 3.0]) == [1, "two", 3.0]

    def test_dict_recursively_converted(self):
        """Verify dicts have keys stringified and values converted behavior."""
        result = _safe_default({1: "one", "two": 2})
        assert result == {"1": "one", "two": 2}

    def test_callable_returns_none(self):
        """Verify callables (factory defaults) return None behavior."""
        assert _safe_default(list) is None
        assert _safe_default(lambda: 42) is None

    def test_enum_returns_value(self):
        """Verify enum members return their .value behavior."""
        import enum

        class Color(enum.Enum):
            RED = "red"
            BLUE = "blue"

        assert _safe_default(Color.RED) == "red"

    def test_arbitrary_object_stringified(self):
        """Verify other objects are stringified as fallback behavior."""
        class Custom:
            def __str__(self):
                return "custom_str"

        result = _safe_default(Custom())
        assert result == "custom_str"
