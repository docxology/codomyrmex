"""Unit tests for serialization module expansion."""

import pytest
from codomyrmex.serialization import MsgpackSerializer, AvroSerializer, ParquetSerializer

@pytest.mark.unit
def test_msgpack_serialization():
    """Test Msgpack serialization/deserialization."""
    data = {"key": "value", "list": [1, 2, 3], "bool": True}
    serialized = MsgpackSerializer.serialize(data)
    deserialized = MsgpackSerializer.deserialize(serialized)
    assert deserialized == data

@pytest.mark.unit
def test_avro_serialization():
    """Test Avro serialization/deserialization."""
    schema = {
        'doc': 'Test schema',
        'name': 'Test',
        'namespace': 'test',
        'type': 'record',
        'fields': [
            {'name': 'name', 'type': 'string'},
            {'name': 'age', 'type': 'int'},
        ],
    }
    data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    serialized = AvroSerializer.serialize(data, schema)
    deserialized = AvroSerializer.deserialize(serialized)
    assert deserialized == data

@pytest.mark.unit
def test_parquet_serialization():
    """Test Parquet serialization/deserialization."""
    data = [
        {'col1': 1, 'col2': 'A'},
        {'col1': 2, 'col2': 'B'}
    ]
    serialized = ParquetSerializer.serialize(data)
    deserialized = ParquetSerializer.deserialize(serialized)
    # Pandas might return records in different order or with slightly different types, 
    # but for simple dicts it should match.
    assert deserialized == data
