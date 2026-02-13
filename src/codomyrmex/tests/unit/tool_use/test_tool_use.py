"""Tests for tool_use module."""

import pytest

try:
    from codomyrmex.tool_use import (
        ChainResult,
        ChainStep,
        ToolChain,
        ToolEntry,
        ToolRegistry,
        ValidationResult,
        tool,
        validate_input,
        validate_output,
    )

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("tool_use module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestValidationResult:
    def test_default_valid(self):
        vr = ValidationResult()
        assert vr.valid is True
        assert vr.errors == []

    def test_invalid_with_errors(self):
        vr = ValidationResult(valid=False, errors=["field missing"])
        assert vr.valid is False
        assert len(vr.errors) == 1

    def test_merge_two_valid(self):
        a = ValidationResult(valid=True)
        b = ValidationResult(valid=True)
        merged = a.merge(b)
        assert merged.valid is True
        assert merged.errors == []

    def test_merge_valid_and_invalid(self):
        a = ValidationResult(valid=True)
        b = ValidationResult(valid=False, errors=["bad"])
        merged = a.merge(b)
        assert merged.valid is False
        assert "bad" in merged.errors

    def test_to_dict(self):
        vr = ValidationResult(valid=False, errors=["err1", "err2"])
        d = vr.to_dict()
        assert d["valid"] is False
        assert len(d["errors"]) == 2


# ---------------------------------------------------------------------------
# validate_input / validate_output
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestValidation:
    def test_empty_schema_is_valid(self):
        result = validate_input({"anything": True}, {})
        assert result.valid

    def test_type_check_string(self):
        schema = {"type": "string"}
        assert validate_input("hello", schema).valid
        assert not validate_input(42, schema).valid

    def test_type_check_integer(self):
        schema = {"type": "integer"}
        assert validate_input(10, schema).valid
        assert not validate_input("10", schema).valid

    def test_type_check_number_accepts_int_and_float(self):
        schema = {"type": "number"}
        assert validate_input(10, schema).valid
        assert validate_input(3.14, schema).valid
        assert not validate_input("3.14", schema).valid

    def test_type_check_boolean(self):
        schema = {"type": "boolean"}
        assert validate_input(True, schema).valid
        assert not validate_input(1, schema).valid

    def test_type_check_array(self):
        schema = {"type": "array"}
        assert validate_input([1, 2], schema).valid
        assert not validate_input("not array", schema).valid

    def test_enum_constraint(self):
        schema = {"type": "string", "enum": ["a", "b", "c"]}
        assert validate_input("a", schema).valid
        assert not validate_input("d", schema).valid

    def test_string_min_max_length(self):
        schema = {"type": "string", "minLength": 2, "maxLength": 5}
        assert validate_input("ab", schema).valid
        assert validate_input("abcde", schema).valid
        assert not validate_input("a", schema).valid
        assert not validate_input("abcdef", schema).valid

    def test_numeric_min_max(self):
        schema = {"type": "integer", "minimum": 0, "maximum": 100}
        assert validate_input(50, schema).valid
        assert not validate_input(-1, schema).valid
        assert not validate_input(101, schema).valid

    def test_array_min_max_items(self):
        schema = {"type": "array", "minItems": 1, "maxItems": 3}
        assert validate_input([1], schema).valid
        assert not validate_input([], schema).valid
        assert not validate_input([1, 2, 3, 4], schema).valid

    def test_array_items_validation(self):
        schema = {"type": "array", "items": {"type": "string"}}
        assert validate_input(["a", "b"], schema).valid
        result = validate_input(["a", 1], schema)
        assert not result.valid

    def test_object_required_fields(self):
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        assert validate_input({"name": "test"}, schema).valid
        assert not validate_input({}, schema).valid

    def test_object_additional_properties_false(self):
        schema = {
            "type": "object",
            "properties": {"a": {"type": "string"}},
            "additionalProperties": False,
        }
        assert validate_input({"a": "ok"}, schema).valid
        assert not validate_input({"a": "ok", "b": "extra"}, schema).valid

    def test_validate_output_works_same_as_input(self):
        schema = {"type": "string"}
        assert validate_output("hello", schema).valid
        assert not validate_output(42, schema).valid

    def test_nested_object_validation(self):
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string"}},
                }
            },
        }
        assert validate_input({"user": {"name": "alice"}}, schema).valid
        result = validate_input({"user": {"name": 42}}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# ToolEntry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestToolEntry:
    def test_create_entry(self):
        entry = ToolEntry(
            name="test",
            description="A test tool",
            handler=lambda d: d,
        )
        assert entry.name == "test"
        assert entry.description == "A test tool"
        assert entry.input_schema == {}
        assert entry.output_schema == {}
        assert entry.tags == []

    def test_to_dict(self):
        entry = ToolEntry(
            name="greet",
            description="Say hello",
            handler=lambda d: d,
            tags=["demo"],
        )
        d = entry.to_dict()
        assert d["name"] == "greet"
        assert d["tags"] == ["demo"]
        assert "handler" not in d


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestToolRegistry:
    def _make_entry(self, name="tool1", tags=None):
        return ToolEntry(
            name=name,
            description=f"Tool {name}",
            handler=lambda d: {"echo": d},
            tags=tags or [],
        )

    def test_register_and_get(self):
        reg = ToolRegistry()
        entry = self._make_entry("greet")
        reg.register(entry)
        assert reg.get("greet") is entry

    def test_register_duplicate_raises(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("dup"))
        with pytest.raises(ValueError, match="already registered"):
            reg.register(self._make_entry("dup"))

    def test_unregister(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("rm"))
        assert reg.unregister("rm") is True
        assert reg.get("rm") is None
        assert reg.unregister("rm") is False

    def test_list_and_list_names(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("b"))
        reg.register(self._make_entry("a"))
        assert reg.list_names() == ["a", "b"]
        entries = reg.list()
        assert [e.name for e in entries] == ["a", "b"]

    def test_search_by_name(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("fetch_data"))
        reg.register(self._make_entry("parse_data"))
        reg.register(self._make_entry("send_email"))
        results = reg.search(name_contains="data")
        assert len(results) == 2

    def test_search_by_tags(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("a", tags=["io", "network"]))
        reg.register(self._make_entry("b", tags=["io"]))
        reg.register(self._make_entry("c", tags=["compute"]))
        results = reg.search(tags=["io"])
        assert len(results) == 2
        results = reg.search(tags=["io", "network"], match_all_tags=True)
        assert len(results) == 1

    def test_len_and_contains(self):
        reg = ToolRegistry()
        reg.register(self._make_entry("x"))
        assert len(reg) == 1
        assert "x" in reg
        assert "y" not in reg

    def test_invoke_success(self):
        reg = ToolRegistry()
        reg.register(
            ToolEntry(
                name="echo",
                description="Echo input",
                handler=lambda d: {"value": d},
            )
        )
        result = reg.invoke("echo", "hello")
        assert result.ok
        assert result.data == {"value": "hello"}

    def test_invoke_not_found(self):
        reg = ToolRegistry()
        result = reg.invoke("missing", {})
        assert not result.ok
        assert "not found" in result.message

    def test_invoke_input_validation_failure(self):
        reg = ToolRegistry()
        reg.register(
            ToolEntry(
                name="strict",
                description="Strict input",
                handler=lambda d: d,
                input_schema={"type": "object", "required": ["name"]},
            )
        )
        result = reg.invoke("strict", {})
        assert not result.ok
        assert "validation failed" in result.message.lower()

    def test_invoke_handler_exception(self):
        def bad_handler(d):
            raise RuntimeError("boom")

        reg = ToolRegistry()
        reg.register(
            ToolEntry(name="bad", description="Breaks", handler=bad_handler)
        )
        result = reg.invoke("bad", {})
        assert not result.ok
        assert "boom" in result.message


# ---------------------------------------------------------------------------
# @tool decorator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestToolDecorator:
    def test_decorator_creates_tool_entry(self):
        @tool(name="add", description="Add numbers")
        def add(data):
            return {"sum": data["a"] + data["b"]}

        assert hasattr(add, "tool_entry")
        assert add.tool_entry.name == "add"
        assert add.tool_entry.description == "Add numbers"

    def test_decorator_auto_registers(self):
        reg = ToolRegistry()

        @tool(name="mul", description="Multiply", registry=reg)
        def mul(data):
            return data["a"] * data["b"]

        assert "mul" in reg
        result = reg.invoke("mul", {"a": 3, "b": 4}, validate=False)
        assert result.ok

    def test_decorated_function_still_callable(self):
        @tool(name="fn", description="Test")
        def fn(data):
            return data * 2

        assert fn(5) == 10


# ---------------------------------------------------------------------------
# ToolChain
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestToolChain:
    def _setup_registry(self):
        reg = ToolRegistry()
        reg.register(
            ToolEntry(
                name="double",
                description="Double a value",
                handler=lambda d: {"value": d.get("value", 0) * 2},
            )
        )
        reg.register(
            ToolEntry(
                name="add_ten",
                description="Add 10",
                handler=lambda d: {"value": d.get("value", 0) + 10},
            )
        )
        return reg

    def test_chain_execute_sequential(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="double"))
        chain.add_step(ChainStep(tool_name="add_ten"))
        result = chain.execute({"value": 5})
        assert result.success
        assert result.context["value"] == 20  # (5*2) + 10

    def test_chain_with_output_key(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="double", output_key="doubled"))
        result = chain.execute({"value": 7})
        assert result.success
        assert "doubled" in result.context
        assert result.context["doubled"]["value"] == 14

    def test_chain_validate_missing_tool(self):
        reg = ToolRegistry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="nonexistent"))
        vr = chain.validate()
        assert not vr.valid
        assert any("not found" in e for e in vr.errors)

    def test_chain_validate_empty(self):
        reg = ToolRegistry()
        chain = ToolChain(registry=reg)
        vr = chain.validate()
        assert not vr.valid
        assert any("no steps" in e.lower() for e in vr.errors)

    def test_chain_fluent_api(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        returned = chain.add_step(ChainStep(tool_name="double"))
        assert returned is chain

    def test_chain_stop_on_failure(self):
        reg = ToolRegistry()
        reg.register(
            ToolEntry(
                name="fail",
                description="Always fails",
                handler=lambda d: (_ for _ in ()).throw(RuntimeError("fail")),
            )
        )
        reg.register(
            ToolEntry(
                name="ok",
                description="Ok",
                handler=lambda d: {"done": True},
            )
        )
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="fail"))
        chain.add_step(ChainStep(tool_name="ok"))
        result = chain.execute(stop_on_failure=True, validate_tools=False)
        assert not result.success
        assert len(result.step_results) == 1

    def test_chain_len_and_repr(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="double"))
        chain.add_step(ChainStep(tool_name="add_ten"))
        assert len(chain) == 2
        assert "double" in repr(chain)

    def test_chain_clear(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="double"))
        chain.clear()
        assert len(chain) == 0

    def test_chain_result_has_duration(self):
        reg = self._setup_registry()
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="double"))
        result = chain.execute({"value": 1})
        assert result.duration_ms >= 0

    def test_chain_input_mapping(self):
        reg = ToolRegistry()
        reg.register(
            ToolEntry(
                name="extract",
                description="Extract",
                handler=lambda d: {"content": f"extracted: {d.get('url', '')}"},
            )
        )
        reg.register(
            ToolEntry(
                name="process",
                description="Process",
                handler=lambda d: {"result": d.get("text", "").upper()},
            )
        )
        chain = ToolChain(registry=reg)
        chain.add_step(ChainStep(tool_name="extract", output_key="raw"))
        chain.add_step(
            ChainStep(
                tool_name="process",
                input_mapping={"text": "raw.content"},
                output_key="processed",
            )
        )
        result = chain.execute({"url": "test.com"})
        assert result.success
        assert result.context["processed"]["result"] == "EXTRACTED: TEST.COM"
