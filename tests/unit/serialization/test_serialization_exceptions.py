"""
Unit tests for serialization.exceptions — Zero-Mock compliant.

Covers: SerializationError, DeserializationError, SchemaValidationError,
EncodingError, FormatNotSupportedError, CircularReferenceError,
TypeConversionError, BinaryFormatError.
"""

import pytest

from codomyrmex.serialization.exceptions import (
    BinaryFormatError,
    CircularReferenceError,
    DeserializationError,
    EncodingError,
    FormatNotSupportedError,
    SchemaValidationError,
    SerializationError,
    TypeConversionError,
)

# ── SerializationError ────────────────────────────────────────────────


@pytest.mark.unit
class TestSerializationError:
    def test_is_exception(self):
        e = SerializationError("fail")
        assert isinstance(e, Exception)

    def test_message_stored(self):
        e = SerializationError("some error")
        assert e.message == "some error"

    def test_context_empty_by_default(self):
        e = SerializationError("fail")
        assert "format" not in e.context
        assert "data_type" not in e.context

    def test_format_stored_in_context(self):
        e = SerializationError("fail", format="JSON")
        assert e.context["format"] == "JSON"

    def test_data_type_stored_in_context(self):
        e = SerializationError("fail", data_type="dict")
        assert e.context["data_type"] == "dict"

    def test_both_optional_fields(self):
        e = SerializationError("fail", format="YAML", data_type="list")
        assert e.context["format"] == "YAML"
        assert e.context["data_type"] == "list"

    def test_none_format_not_stored(self):
        e = SerializationError("fail", format=None)
        assert "format" not in e.context

    def test_none_data_type_not_stored(self):
        e = SerializationError("fail", data_type=None)
        assert "data_type" not in e.context

    def test_can_be_raised_and_caught(self):
        with pytest.raises(SerializationError):
            raise SerializationError("test raise")

    def test_str_contains_message(self):
        e = SerializationError("oops")
        assert "oops" in str(e)


# ── DeserializationError ──────────────────────────────────────────────


@pytest.mark.unit
class TestDeserializationError:
    def test_is_serialization_error(self):
        e = DeserializationError("fail")
        assert isinstance(e, SerializationError)

    def test_message_stored(self):
        e = DeserializationError("bad data")
        assert e.message == "bad data"

    def test_format_stored_in_context(self):
        e = DeserializationError("fail", format="JSON")
        assert e.context["format"] == "JSON"

    def test_short_raw_data_stored_as_is(self):
        e = DeserializationError("fail", raw_data_preview="short data")
        assert e.context["raw_data_preview"] == "short data"

    def test_long_raw_data_truncated_to_200(self):
        long_data = "x" * 300
        e = DeserializationError("fail", raw_data_preview=long_data)
        preview = e.context["raw_data_preview"]
        assert len(preview) == 203  # 200 + "..."
        assert preview.endswith("...")

    def test_raw_data_exactly_200_not_truncated(self):
        exact_data = "a" * 200
        e = DeserializationError("fail", raw_data_preview=exact_data)
        assert e.context["raw_data_preview"] == exact_data
        assert not e.context["raw_data_preview"].endswith("...")

    def test_none_raw_data_not_stored(self):
        e = DeserializationError("fail", raw_data_preview=None)
        assert "raw_data_preview" not in e.context

    def test_expected_type_stored_in_context(self):
        e = DeserializationError("fail", expected_type="dict")
        assert e.context["expected_type"] == "dict"

    def test_none_expected_type_not_stored(self):
        e = DeserializationError("fail", expected_type=None)
        assert "expected_type" not in e.context

    def test_all_fields_populated(self):
        e = DeserializationError(
            "fail",
            format="JSON",
            raw_data_preview="bad{}",
            expected_type="User",
        )
        assert e.context["format"] == "JSON"
        assert e.context["raw_data_preview"] == "bad{}"
        assert e.context["expected_type"] == "User"


# ── SchemaValidationError ─────────────────────────────────────────────


@pytest.mark.unit
class TestSchemaValidationError:
    def test_is_serialization_error(self):
        e = SchemaValidationError("schema fail")
        assert isinstance(e, SerializationError)

    def test_schema_name_stored(self):
        e = SchemaValidationError("fail", schema_name="UserSchema")
        assert e.context["schema_name"] == "UserSchema"

    def test_none_schema_name_not_stored(self):
        e = SchemaValidationError("fail", schema_name=None)
        assert "schema_name" not in e.context

    def test_validation_errors_stored(self):
        errs = ["field 'age' required", "field 'name' too short"]
        e = SchemaValidationError("fail", validation_errors=errs)
        assert e.context["validation_errors"] == errs

    def test_none_validation_errors_not_stored(self):
        e = SchemaValidationError("fail", validation_errors=None)
        assert "validation_errors" not in e.context

    def test_path_stored(self):
        e = SchemaValidationError("fail", path="$.user.address")
        assert e.context["path"] == "$.user.address"

    def test_none_path_not_stored(self):
        e = SchemaValidationError("fail", path=None)
        assert "path" not in e.context

    def test_all_fields_populated(self):
        e = SchemaValidationError(
            "invalid",
            schema_name="ProductSchema",
            validation_errors=["price must be positive"],
            path="$.product.price",
        )
        assert e.context["schema_name"] == "ProductSchema"
        assert "price must be positive" in e.context["validation_errors"]
        assert e.context["path"] == "$.product.price"


# ── EncodingError ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestEncodingError:
    def test_is_serialization_error(self):
        e = EncodingError("encoding fail")
        assert isinstance(e, SerializationError)

    def test_encoding_stored_in_context(self):
        e = EncodingError("fail", encoding="UTF-8")
        assert e.context["encoding"] == "UTF-8"

    def test_none_encoding_not_stored(self):
        e = EncodingError("fail", encoding=None)
        assert "encoding" not in e.context

    def test_position_stored_when_nonzero(self):
        e = EncodingError("fail", position=42)
        assert e.context["position"] == 42

    def test_position_stored_when_zero(self):
        # position=0 is falsy, but check uses `is not None` so 0 IS stored
        e = EncodingError("fail", position=0)
        assert e.context["position"] == 0

    def test_none_position_not_stored(self):
        e = EncodingError("fail", position=None)
        assert "position" not in e.context

    def test_all_fields_populated(self):
        e = EncodingError("bad char", encoding="ASCII", position=15)
        assert e.context["encoding"] == "ASCII"
        assert e.context["position"] == 15


# ── FormatNotSupportedError ───────────────────────────────────────────


@pytest.mark.unit
class TestFormatNotSupportedError:
    def test_is_serialization_error(self):
        e = FormatNotSupportedError("unsupported")
        assert isinstance(e, SerializationError)

    def test_requested_format_stored(self):
        e = FormatNotSupportedError("fail", requested_format="XML")
        assert e.context["requested_format"] == "XML"

    def test_none_requested_format_not_stored(self):
        e = FormatNotSupportedError("fail", requested_format=None)
        assert "requested_format" not in e.context

    def test_supported_formats_stored(self):
        fmts = ["JSON", "YAML", "TOML"]
        e = FormatNotSupportedError("fail", supported_formats=fmts)
        assert e.context["supported_formats"] == fmts

    def test_none_supported_formats_not_stored(self):
        e = FormatNotSupportedError("fail", supported_formats=None)
        assert "supported_formats" not in e.context

    def test_all_fields_populated(self):
        e = FormatNotSupportedError(
            "XML not supported",
            requested_format="XML",
            supported_formats=["JSON", "YAML"],
        )
        assert e.context["requested_format"] == "XML"
        assert "JSON" in e.context["supported_formats"]


# ── CircularReferenceError ────────────────────────────────────────────


@pytest.mark.unit
class TestCircularReferenceError:
    def test_is_serialization_error(self):
        e = CircularReferenceError("circular!")
        assert isinstance(e, SerializationError)

    def test_object_type_stored(self):
        e = CircularReferenceError("fail", object_type="TreeNode")
        assert e.context["object_type"] == "TreeNode"

    def test_none_object_type_not_stored(self):
        e = CircularReferenceError("fail", object_type=None)
        assert "object_type" not in e.context

    def test_reference_path_stored(self):
        e = CircularReferenceError("fail", reference_path="root.child.root")
        assert e.context["reference_path"] == "root.child.root"

    def test_none_reference_path_not_stored(self):
        e = CircularReferenceError("fail", reference_path=None)
        assert "reference_path" not in e.context

    def test_all_fields_populated(self):
        e = CircularReferenceError(
            "detected cycle",
            object_type="Graph",
            reference_path="a->b->c->a",
        )
        assert e.context["object_type"] == "Graph"
        assert e.context["reference_path"] == "a->b->c->a"


# ── TypeConversionError ───────────────────────────────────────────────


@pytest.mark.unit
class TestTypeConversionError:
    def test_is_serialization_error(self):
        e = TypeConversionError("type fail")
        assert isinstance(e, SerializationError)

    def test_source_type_stored(self):
        e = TypeConversionError("fail", source_type="str")
        assert e.context["source_type"] == "str"

    def test_none_source_type_not_stored(self):
        e = TypeConversionError("fail", source_type=None)
        assert "source_type" not in e.context

    def test_target_type_stored(self):
        e = TypeConversionError("fail", target_type="int")
        assert e.context["target_type"] == "int"

    def test_none_target_type_not_stored(self):
        e = TypeConversionError("fail", target_type=None)
        assert "target_type" not in e.context

    def test_short_value_preview_stored_as_is(self):
        e = TypeConversionError("fail", value_preview="abc")
        assert e.context["value_preview"] == "abc"

    def test_long_value_preview_truncated_to_100(self):
        long_val = "v" * 200
        e = TypeConversionError("fail", value_preview=long_val)
        preview = e.context["value_preview"]
        assert len(preview) == 103  # 100 + "..."
        assert preview.endswith("...")

    def test_value_preview_exactly_100_not_truncated(self):
        exact_val = "z" * 100
        e = TypeConversionError("fail", value_preview=exact_val)
        assert e.context["value_preview"] == exact_val
        assert not e.context["value_preview"].endswith("...")

    def test_none_value_preview_not_stored(self):
        e = TypeConversionError("fail", value_preview=None)
        assert "value_preview" not in e.context

    def test_all_fields_populated(self):
        e = TypeConversionError(
            "cannot convert",
            source_type="str",
            target_type="datetime",
            value_preview="not-a-date",
        )
        assert e.context["source_type"] == "str"
        assert e.context["target_type"] == "datetime"
        assert e.context["value_preview"] == "not-a-date"


# ── BinaryFormatError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestBinaryFormatError:
    def test_is_serialization_error(self):
        e = BinaryFormatError("binary fail")
        assert isinstance(e, SerializationError)

    def test_format_stored_in_context(self):
        e = BinaryFormatError("fail", format="MessagePack")
        assert e.context["format"] == "MessagePack"

    def test_none_format_not_stored(self):
        e = BinaryFormatError("fail", format=None)
        assert "format" not in e.context

    def test_operation_stored_in_context(self):
        e = BinaryFormatError("fail", operation="unpack")
        assert e.context["operation"] == "unpack"

    def test_none_operation_not_stored(self):
        e = BinaryFormatError("fail", operation=None)
        assert "operation" not in e.context

    def test_all_fields_populated(self):
        e = BinaryFormatError("decode error", format="Protobuf", operation="decode")
        assert e.context["format"] == "Protobuf"
        assert e.context["operation"] == "decode"

    def test_can_be_raised_and_caught_as_serialization_error(self):
        with pytest.raises(SerializationError):
            raise BinaryFormatError("bad binary")
