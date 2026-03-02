"""
Unit tests for cache.serializers — Zero-Mock compliant.

Covers: JSONSerializer, PickleSerializer, CompressedSerializer,
Base64Serializer, StringSerializer, TypedSerializer, create_serializer.
"""

import pytest

from codomyrmex.cache.serializers import (
    Base64Serializer,
    CompressedSerializer,
    JSONSerializer,
    PickleSerializer,
    StringSerializer,
    TypedSerializer,
    create_serializer,
)

# ── JSONSerializer ────────────────────────────────────────────────────


@pytest.mark.unit
class TestJSONSerializer:
    def test_serialize_dict_to_bytes(self):
        s = JSONSerializer()
        data = s.serialize({"key": "val"})
        assert isinstance(data, bytes)

    def test_deserialize_recovers_dict(self):
        s = JSONSerializer()
        original = {"a": 1, "b": [2, 3]}
        assert s.deserialize(s.serialize(original)) == original

    def test_serialize_list(self):
        s = JSONSerializer()
        original = [1, 2, 3]
        assert s.deserialize(s.serialize(original)) == original

    def test_serialize_with_indent(self):
        s = JSONSerializer(indent=2)
        data = s.serialize({"k": "v"})
        assert b"\n" in data  # indented output has newlines

    def test_default_indent_is_none(self):
        s = JSONSerializer()
        assert s.indent is None

    def test_roundtrip_nested(self):
        s = JSONSerializer()
        original = {"nested": {"x": [1, 2], "y": None}}
        assert s.deserialize(s.serialize(original)) == original


# ── PickleSerializer ──────────────────────────────────────────────────


@pytest.mark.unit
class TestPickleSerializer:
    def test_serialize_to_bytes(self):
        s = PickleSerializer()
        data = s.serialize({"key": "val"})
        assert isinstance(data, bytes)

    def test_deserialize_recovers_object(self):
        s = PickleSerializer()
        original = {"a": 1, "b": [2, 3]}
        assert s.deserialize(s.serialize(original)) == original

    def test_default_protocol(self):
        import pickle
        s = PickleSerializer()
        assert s.protocol == pickle.HIGHEST_PROTOCOL

    def test_custom_protocol(self):
        s = PickleSerializer(protocol=2)
        assert s.protocol == 2


# ── CompressedSerializer ──────────────────────────────────────────────


@pytest.mark.unit
class TestCompressedSerializer:
    def test_serialize_to_bytes(self):
        s = CompressedSerializer(base_serializer=JSONSerializer())
        data = s.serialize({"key": "value"})
        assert isinstance(data, bytes)

    def test_deserialize_recovers_value(self):
        s = CompressedSerializer(base_serializer=JSONSerializer())
        original = {"k": "v", "n": 123}
        assert s.deserialize(s.serialize(original)) == original

    def test_compressed_smaller_than_raw_for_large_data(self):
        s = CompressedSerializer(base_serializer=JSONSerializer())
        raw_s = JSONSerializer()
        large = {"data": "x" * 1000}
        assert len(s.serialize(large)) < len(raw_s.serialize(large))

    def test_custom_compression_level(self):
        s = CompressedSerializer(base_serializer=JSONSerializer(), compression_level=1)
        assert s.level == 1

    def test_roundtrip_list(self):
        s = CompressedSerializer(base_serializer=JSONSerializer())
        original = list(range(100))
        assert s.deserialize(s.serialize(original)) == original


# ── Base64Serializer ──────────────────────────────────────────────────


@pytest.mark.unit
class TestBase64Serializer:
    def test_serialize_to_bytes(self):
        s = Base64Serializer(base_serializer=JSONSerializer())
        data = s.serialize({"k": "v"})
        assert isinstance(data, bytes)

    def test_deserialize_recovers_value(self):
        s = Base64Serializer(base_serializer=JSONSerializer())
        original = {"x": 42}
        assert s.deserialize(s.serialize(original)) == original

    def test_output_is_valid_base64(self):
        import base64
        s = Base64Serializer(base_serializer=JSONSerializer())
        data = s.serialize({"k": "v"})
        # Should not raise
        base64.b64decode(data)

    def test_roundtrip_string_values(self):
        s = Base64Serializer(base_serializer=JSONSerializer())
        original = "hello world"
        assert s.deserialize(s.serialize(original)) == original


# ── StringSerializer ──────────────────────────────────────────────────


@pytest.mark.unit
class TestStringSerializer:
    def test_serialize_string_to_bytes(self):
        s = StringSerializer()
        data = s.serialize("hello")
        assert data == b"hello"

    def test_deserialize_bytes_to_string(self):
        s = StringSerializer()
        assert s.deserialize(b"hello") == "hello"

    def test_serialize_int_to_bytes(self):
        s = StringSerializer()
        data = s.serialize(42)
        assert data == b"42"

    def test_custom_encoding(self):
        s = StringSerializer(encoding="latin-1")
        assert s.encoding == "latin-1"
        data = s.serialize("caf\xe9")
        assert s.deserialize(data) == "caf\xe9"

    def test_default_encoding_utf8(self):
        s = StringSerializer()
        assert s.encoding == "utf-8"


# ── TypedSerializer ───────────────────────────────────────────────────


@pytest.mark.unit
class TestTypedSerializer:
    def test_serialize_int_preserved(self):
        s = TypedSerializer()
        result = s.deserialize(s.serialize(42))
        assert result == 42
        assert isinstance(result, int)

    def test_serialize_float_preserved(self):
        s = TypedSerializer()
        result = s.deserialize(s.serialize(3.14))
        assert result == pytest.approx(3.14)
        assert isinstance(result, float)

    def test_serialize_bool_preserved(self):
        s = TypedSerializer()
        result = s.deserialize(s.serialize(True))
        assert result is True

    def test_serialize_str_preserved(self):
        s = TypedSerializer()
        result = s.deserialize(s.serialize("hello"))
        assert result == "hello"

    def test_serialize_list_preserved(self):
        s = TypedSerializer()
        original = [1, 2, 3]
        result = s.deserialize(s.serialize(original))
        assert result == original

    def test_serialize_dict_preserved(self):
        s = TypedSerializer()
        original = {"k": "v"}
        result = s.deserialize(s.serialize(original))
        assert result == original

    def test_non_json_serializable_uses_str(self):
        s = TypedSerializer()
        # A set is not JSON serializable — it falls back to str
        data = s.serialize({1, 2, 3})
        assert isinstance(data, bytes)

    def test_custom_base_serializer(self):
        s = TypedSerializer(base_serializer=JSONSerializer())
        result = s.deserialize(s.serialize(99))
        assert result == 99


# ── create_serializer ─────────────────────────────────────────────────


@pytest.mark.unit
class TestCreateSerializer:
    def test_create_json_serializer(self):
        s = create_serializer("json")
        assert isinstance(s, JSONSerializer)

    def test_create_pickle_serializer(self):
        s = create_serializer("pickle")
        assert isinstance(s, PickleSerializer)

    def test_create_string_serializer(self):
        s = create_serializer("string")
        assert isinstance(s, StringSerializer)

    def test_create_typed_serializer(self):
        s = create_serializer("typed")
        assert isinstance(s, TypedSerializer)

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown serializer"):
            create_serializer("xml")

    def test_compress_wraps_in_compressed(self):
        s = create_serializer("json", compress=True)
        assert isinstance(s, CompressedSerializer)

    def test_compress_false_no_wrapping(self):
        s = create_serializer("json", compress=False)
        assert isinstance(s, JSONSerializer)

    def test_default_is_json(self):
        s = create_serializer()
        assert isinstance(s, JSONSerializer)

    def test_kwargs_passed_to_serializer(self):
        s = create_serializer("json", indent=2)
        assert isinstance(s, JSONSerializer)
        assert s.indent == 2
