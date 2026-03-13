"""Property-based tests for binary serialization formats."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

try:
    from codomyrmex.serialization.binary_formats import (
        AvroSerializer,
        MsgpackSerializer,
        ParquetSerializer,
    )

    BINARY_AVAILABLE = True
except ImportError:
    BINARY_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not BINARY_AVAILABLE, reason="Binary formats not available"
)

# JSON-compatible primitives for msgpack
json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(2**53), max_value=2**53),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=100),
)

# Recursive JSON-compatible structures
json_values = st.recursive(
    json_primitives,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=5),
    ),
    max_leaves=20,
)

# Fixed schema rows for Parquet and Avro
row_strategy = st.fixed_dictionaries(
    {
        "id": st.integers(min_value=1, max_value=10000),
        "name": st.text(min_size=1, max_size=50),
        "score": st.floats(
            min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
        ),
        "active": st.booleans(),
    }
)
dataset_strategy = st.lists(row_strategy, min_size=1, max_size=20)


class TestMsgpackFuzzing:
    @given(data=json_values)
    @settings(max_examples=50, deadline=2000)
    def test_msgpack_roundtrip(self, data):
        """Msgpack perfectly round-trips JSON-like structures."""
        serialized = MsgpackSerializer.serialize(data)
        assert isinstance(serialized, bytes)
        result = MsgpackSerializer.deserialize(serialized)

        # msgpack might deserialize lists as tuples, so we compare without strict list type checking
        def normalize(obj):
            if isinstance(obj, (list, tuple)):
                return [normalize(item) for item in obj]
            if isinstance(obj, dict):
                return {k: normalize(v) for k, v in obj.items()}
            return obj

        assert normalize(result) == normalize(data)


class TestParquetFuzzing:
    @given(dataset=dataset_strategy)
    @settings(max_examples=30, deadline=None)
    def test_parquet_roundtrip(self, dataset):
        """Parquet perfectly round-trips tabular data."""
        serialized = ParquetSerializer.serialize(dataset)
        assert isinstance(serialized, bytes)
        result = ParquetSerializer.deserialize(serialized)

        assert len(result) == len(dataset)
        for original, res in zip(dataset, result, strict=True):
            assert res["id"] == original["id"]
            assert res["name"] == original["name"]
            assert abs(res["score"] - original["score"]) < 1e-6
            assert res["active"] == original["active"]


class TestAvroFuzzing:
    AVRO_SCHEMA = {
        "type": "record",
        "name": "UserScore",
        "fields": [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "string"},
            {"name": "score", "type": "double"},
            {"name": "active", "type": "boolean"},
        ],
    }

    @given(dataset=dataset_strategy)
    @settings(max_examples=30, deadline=None)
    def test_avro_roundtrip(self, dataset):
        """Avro perfectly round-trips tabular data given a schema."""
        serialized = AvroSerializer.serialize(dataset, self.AVRO_SCHEMA)
        assert isinstance(serialized, bytes)
        result = AvroSerializer.deserialize(serialized)

        assert len(result) == len(dataset)
        for original, res in zip(dataset, result, strict=True):
            assert res["id"] == original["id"]
            assert res["name"] == original["name"]
            assert abs(res["score"] - original["score"]) < 1e-6
            assert res["active"] == original["active"]
