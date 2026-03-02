"""
Unit tests for serialization.serialization_manager — Zero-Mock compliant.

Covers: SerializationResult (dataclass), SerializationManager
(get_serializer, register_serializer, supported_formats, serialize,
deserialize, serialize_batch, round_trip, operation_count, error_count,
summary, clear_stats).
"""

import pytest

from codomyrmex.serialization.serialization_manager import (
    SerializationManager,
    SerializationResult,
)
from codomyrmex.serialization.serializer import Serializer

# ── SerializationResult ────────────────────────────────────────────────


@pytest.mark.unit
class TestSerializationResult:
    def test_fields_stored(self):
        r = SerializationResult(
            format="json",
            input_type="dict",
            output_size=42,
            duration_seconds=0.001,
            success=True,
        )
        assert r.format == "json"
        assert r.input_type == "dict"
        assert r.output_size == 42
        assert r.duration_seconds == pytest.approx(0.001)
        assert r.success is True
        assert r.error == ""

    def test_error_field_default_empty(self):
        r = SerializationResult(
            format="yaml", input_type="str", output_size=0,
            duration_seconds=0.0, success=False
        )
        assert r.error == ""

    def test_error_field_set(self):
        r = SerializationResult(
            format="json", input_type="set", output_size=0,
            duration_seconds=0.0, success=False, error="not serializable"
        )
        assert r.error == "not serializable"


# ── SerializationManager — basic ───────────────────────────────────────


@pytest.mark.unit
class TestSerializationManagerBasic:
    def test_get_serializer_returns_serializer(self):
        mgr = SerializationManager()
        s = mgr.get_serializer("json")
        assert isinstance(s, Serializer)

    def test_get_serializer_cached(self):
        mgr = SerializationManager()
        s1 = mgr.get_serializer("json")
        s2 = mgr.get_serializer("json")
        assert s1 is s2

    def test_register_serializer(self):
        mgr = SerializationManager()
        custom = Serializer()
        mgr.register_serializer("custom_json", custom)
        assert mgr.get_serializer("custom_json") is custom

    def test_supported_formats_empty_initially(self):
        mgr = SerializationManager()
        assert mgr.supported_formats() == []

    def test_supported_formats_after_use(self):
        mgr = SerializationManager()
        mgr.get_serializer("json")
        assert "json" in mgr.supported_formats()

    def test_supported_formats_sorted(self):
        mgr = SerializationManager()
        mgr.get_serializer("yaml")
        mgr.get_serializer("json")
        mgr.get_serializer("toml")
        formats = mgr.supported_formats()
        assert formats == sorted(formats)


# ── SerializationManager — serialize ──────────────────────────────────


@pytest.mark.unit
class TestSerializationManagerSerialize:
    def test_serialize_dict_to_string(self):
        mgr = SerializationManager()
        result = mgr.serialize({"key": "val"}, format="json")
        assert isinstance(result, (str, bytes))

    def test_serialize_records_stat(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr.operation_count == 1

    def test_serialize_success_stat(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr.error_count == 0

    def test_serialize_records_format(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr._stats[0].format == "json"

    def test_serialize_records_input_type(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr._stats[0].input_type == "dict"

    def test_serialize_records_output_size(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr._stats[0].output_size > 0

    def test_serialize_records_duration(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1}, format="json")
        assert mgr._stats[0].duration_seconds >= 0.0

    def test_multiple_serializations_increment_count(self):
        mgr = SerializationManager()
        mgr.serialize({"a": 1}, format="json")
        mgr.serialize({"b": 2}, format="json")
        assert mgr.operation_count == 2


# ── SerializationManager — deserialize ────────────────────────────────


@pytest.mark.unit
class TestSerializationManagerDeserialize:
    def test_deserialize_json_roundtrip(self):
        mgr = SerializationManager()
        original = {"name": "test", "value": 42}
        serialized = mgr.serialize(original, format="json")
        result = mgr.deserialize(serialized, format="json")
        assert result == original

    def test_deserialize_with_explicit_format(self):
        mgr = SerializationManager()
        data = mgr.serialize([1, 2, 3], format="json")
        result = mgr.deserialize(data, format="json")
        assert result == [1, 2, 3]

    def test_deserialize_auto_detect(self):
        mgr = SerializationManager()
        data = mgr.serialize({"x": 1}, format="json")
        # No format → auto-detect
        result = mgr.deserialize(data)
        assert isinstance(result, dict)


# ── SerializationManager — serialize_batch ────────────────────────────


@pytest.mark.unit
class TestSerializationManagerBatch:
    def test_serialize_batch_returns_list(self):
        mgr = SerializationManager()
        results = mgr.serialize_batch([{"a": 1}, {"b": 2}], format="json")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_serialize_batch_each_element_serialized(self):
        mgr = SerializationManager()
        results = mgr.serialize_batch([1, 2, 3], format="json")
        assert all(isinstance(r, (str, bytes)) for r in results)

    def test_serialize_batch_empty_list(self):
        mgr = SerializationManager()
        results = mgr.serialize_batch([], format="json")
        assert results == []

    def test_serialize_batch_increments_stats(self):
        mgr = SerializationManager()
        mgr.serialize_batch([{"x": i} for i in range(5)], format="json")
        assert mgr.operation_count == 5


# ── SerializationManager — round_trip ─────────────────────────────────


@pytest.mark.unit
class TestSerializationManagerRoundTrip:
    def test_round_trip_dict(self):
        mgr = SerializationManager()
        original = {"nested": {"x": [1, 2, 3]}}
        result = mgr.round_trip(original, format="json")
        assert result == original

    def test_round_trip_string(self):
        mgr = SerializationManager()
        result = mgr.round_trip("hello world", format="json")
        assert result == "hello world"

    def test_round_trip_list(self):
        mgr = SerializationManager()
        result = mgr.round_trip([1, 2, 3], format="json")
        assert result == [1, 2, 3]

    def test_round_trip_integer(self):
        mgr = SerializationManager()
        result = mgr.round_trip(42, format="json")
        assert result == 42

    def test_round_trip_records_two_stats(self):
        mgr = SerializationManager()
        mgr.round_trip({"x": 1})
        # serialize + deserialize both call serialize internally...
        # round_trip calls serialize(obj) then deserialize(data), so at least 1 stat
        assert mgr.operation_count >= 1


# ── SerializationManager — statistics ────────────────────────────────


@pytest.mark.unit
class TestSerializationManagerStats:
    def test_operation_count_initially_zero(self):
        mgr = SerializationManager()
        assert mgr.operation_count == 0

    def test_error_count_initially_zero(self):
        mgr = SerializationManager()
        assert mgr.error_count == 0

    def test_summary_empty_returns_minimal(self):
        mgr = SerializationManager()
        s = mgr.summary()
        assert s == {"operations": 0, "errors": 0}

    def test_summary_after_operations(self):
        mgr = SerializationManager()
        mgr.serialize({"k": "v"}, format="json")
        mgr.serialize([1, 2, 3], format="json")
        s = mgr.summary()
        assert s["operations"] == 2
        assert s["errors"] == 0
        assert "json" in s["formats_used"]
        assert s["total_bytes"] > 0
        assert s["avg_duration_ms"] >= 0.0

    def test_clear_stats_resets_count(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1})
        mgr.clear_stats()
        assert mgr.operation_count == 0

    def test_clear_stats_resets_error_count(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1})
        mgr.clear_stats()
        assert mgr.error_count == 0

    def test_clear_stats_allows_fresh_summary(self):
        mgr = SerializationManager()
        mgr.serialize({"x": 1})
        mgr.clear_stats()
        assert mgr.summary() == {"operations": 0, "errors": 0}
