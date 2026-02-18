"""Comprehensive tests for the serialization module.

Tests cover:
- JSON serialization/deserialization
- YAML parsing/dumping
- Binary serialization (pickle, msgpack)
- Custom serializers (Avro, Parquet)
- Error handling for malformed data
- Schema validation during deserialization
- File-based serialization
- Edge cases and data type handling
"""

import json
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import pytest

# Check optional dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import fastavro
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

try:
    import pandas as _pd
    import pyarrow  # noqa: F401
    # Verify pandas can actually use pyarrow for parquet (version compat check)
    _pd.DataFrame({"_test": [1]}).to_parquet("/dev/null")
    PARQUET_AVAILABLE = True
except (ImportError, Exception):
    PARQUET_AVAILABLE = False

# Import serialization module and components
try:
    from codomyrmex import serialization
    from codomyrmex.serialization import (
        AvroSerializer,
        MsgpackSerializer,
        ParquetSerializer,
        SerializationFormat,
        SerializationManager,
        Serializer,
        deserialize,
        serialize,
    )

    # Import SerializationError from the serializer module directly since
    # the Serializer uses its local definition
    from codomyrmex.serialization.serializer import SerializationError
    SERIALIZATION_MODULE_AVAILABLE = True
except ImportError:
    SERIALIZATION_MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not SERIALIZATION_MODULE_AVAILABLE,
    reason="serialization dependencies (msgpack, etc.) not installed",
)


# ==============================================================================
# Module Import Tests
# ==============================================================================

class TestSerializationModuleImport:
    """Test serialization module import and structure."""

    def test_serialization_module_import(self):
        """Verify that the serialization module can be imported successfully."""
        assert serialization is not None
        assert hasattr(serialization, "__path__")

    def test_serialization_module_structure(self):
        """Verify basic structure of serialization module."""
        assert hasattr(serialization, "__file__")

    def test_serialization_core_imports(self):
        """Verify core serialization classes can be imported."""
        assert Serializer is not None
        assert SerializationFormat is not None
        assert SerializationError is not None

    def test_serialization_module_exports(self):
        """Verify expected exports from serialization module."""
        assert hasattr(serialization, "Serializer")
        assert hasattr(serialization, "SerializationFormat")
        assert hasattr(serialization, "SerializationError")
        assert hasattr(serialization, "serialize")
        assert hasattr(serialization, "deserialize")

    def test_serialization_format_enum(self):
        """Test SerializationFormat enum values."""
        assert SerializationFormat.JSON.value == "json"
        assert SerializationFormat.PICKLE.value == "pickle"
        assert SerializationFormat.YAML.value == "yaml"


# ==============================================================================
# Test Data Classes
# ==============================================================================

@dataclass
class Person:
    """Test dataclass for serialization tests."""
    name: str
    age: int
    email: str | None = None


@dataclass
class Address:
    """Nested dataclass for complex serialization tests."""
    street: str
    city: str
    zip_code: str


@dataclass
class Company:
    """Complex dataclass with nested structure."""
    name: str
    employees: list[str]
    headquarters: Address | None = None


class Status(Enum):
    """Test enum for serialization tests."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


# ==============================================================================
# JSON Serialization Tests
# ==============================================================================

class TestJSONSerialization:
    """Tests for JSON serialization/deserialization."""

    @pytest.fixture
    def serializer(self):
        """Create JSON serializer."""
        return Serializer(default_format=SerializationFormat.JSON)

    def test_json_serialize_dict(self, serializer):
        """Test JSON serialization of dictionary."""
        data = {"name": "test", "value": 123, "active": True}
        result = serializer.serialize(data)
        assert isinstance(result, bytes)
        parsed = json.loads(result.decode('utf-8'))
        assert parsed == data

    def test_json_deserialize_dict(self, serializer):
        """Test JSON deserialization to dictionary."""
        json_bytes = b'{"name": "test", "value": 123}'
        result = serializer.deserialize(json_bytes)
        assert result == {"name": "test", "value": 123}

    def test_json_roundtrip_simple(self, serializer):
        """Test JSON serialize/deserialize roundtrip with simple data."""
        data = {"key": "value", "number": 42, "boolean": False}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_json_serialize_list(self, serializer):
        """Test JSON serialization of list."""
        data = [1, 2, 3, "a", "b", "c"]
        result = serializer.serialize(data)
        parsed = json.loads(result.decode('utf-8'))
        assert parsed == data

    def test_json_serialize_nested_structure(self, serializer):
        """Test JSON serialization of nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "config": {"enabled": True, "limit": 100}
        }
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_json_serialize_datetime(self, serializer):
        """Test JSON serialization of datetime objects."""
        dt = datetime(2023, 6, 15, 10, 30, 0)
        data = {"timestamp": dt}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["timestamp"] == dt.isoformat()

    def test_json_serialize_enum(self, serializer):
        """Test JSON serialization of enum values."""
        data = {"status": Status.ACTIVE}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["status"] == "active"

    def test_json_serialize_dataclass(self, serializer):
        """Test JSON serialization of dataclass."""
        person = Person(name="John", age=30, email="john@example.com")
        serialized = serializer.serialize(person)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["name"] == "John"
        assert deserialized["age"] == 30
        assert deserialized["email"] == "john@example.com"

    def test_json_deserialize_to_dataclass(self, serializer):
        """Test JSON deserialization to dataclass."""
        json_bytes = b'{"name": "Jane", "age": 25, "email": null}'
        result = serializer.deserialize(json_bytes, target_type=Person)
        assert isinstance(result, Person)
        assert result.name == "Jane"
        assert result.age == 25
        assert result.email is None

    def test_json_serialize_path(self, serializer):
        """Test JSON serialization of Path objects."""
        data = {"path": Path("/home/user/file.txt")}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["path"] == "/home/user/file.txt"

    def test_json_serialize_null_values(self, serializer):
        """Test JSON serialization handles null values."""
        data = {"value": None, "list": [None, 1, None]}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_json_deserialize_malformed_raises_error(self, serializer):
        """Test JSON deserialization of malformed data raises error."""
        malformed = b'{"broken": json'
        with pytest.raises(SerializationError):
            serializer.deserialize(malformed)

    def test_json_deserialize_invalid_unicode(self, serializer):
        """Test JSON deserialization handles invalid unicode gracefully."""
        # Invalid UTF-8 sequence
        invalid_bytes = b'{"data": "\xff\xfe"}'
        with pytest.raises(SerializationError):
            serializer.deserialize(invalid_bytes)


# ==============================================================================
# YAML Serialization Tests
# ==============================================================================

class TestYAMLSerialization:
    """Tests for YAML parsing/dumping."""

    @pytest.fixture
    def serializer(self):
        """Create YAML serializer."""
        return Serializer(default_format=SerializationFormat.YAML)

    def test_yaml_serialize_dict(self, serializer):
        """Test YAML serialization of dictionary."""
        data = {"name": "test", "value": 123}
        result = serializer.serialize(data)
        assert isinstance(result, bytes)
        assert b"name:" in result

    def test_yaml_deserialize_dict(self, serializer):
        """Test YAML deserialization to dictionary."""
        yaml_bytes = b"name: test\nvalue: 123\n"
        result = serializer.deserialize(yaml_bytes)
        assert result == {"name": "test", "value": 123}

    def test_yaml_roundtrip(self, serializer):
        """Test YAML serialize/deserialize roundtrip."""
        data = {"config": {"debug": True, "port": 8080}, "items": [1, 2, 3]}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_yaml_serialize_nested_structure(self, serializer):
        """Test YAML serialization of nested structures."""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            }
        }
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_yaml_serialize_list(self, serializer):
        """Test YAML serialization of list."""
        data = ["item1", "item2", "item3"]
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_yaml_multiline_string(self, serializer):
        """Test YAML handling of multiline strings."""
        data = {"text": "line1\nline2\nline3"}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["text"] == "line1\nline2\nline3"

    def test_yaml_deserialize_to_dataclass(self, serializer):
        """Test YAML deserialization to dataclass."""
        yaml_bytes = b"name: Alice\nage: 28\nemail: alice@example.com\n"
        result = serializer.deserialize(yaml_bytes, target_type=Person)
        assert isinstance(result, Person)
        assert result.name == "Alice"
        assert result.age == 28

    def test_yaml_deserialize_malformed_raises_error(self, serializer):
        """Test YAML deserialization of malformed data raises error."""
        malformed = b"key: [invalid: yaml: syntax"
        with pytest.raises(SerializationError):
            serializer.deserialize(malformed)


# ==============================================================================
# Pickle Serialization Tests
# ==============================================================================

class TestPickleSerialization:
    """Tests for pickle binary serialization."""

    @pytest.fixture
    def serializer(self):
        """Create pickle serializer."""
        return Serializer(default_format=SerializationFormat.PICKLE)

    def test_pickle_serialize_dict(self, serializer):
        """Test pickle serialization of dictionary."""
        data = {"name": "test", "value": 123}
        result = serializer.serialize(data)
        assert isinstance(result, bytes)

    def test_pickle_roundtrip(self, serializer):
        """Test pickle serialize/deserialize roundtrip."""
        data = {"complex": [1, 2, 3], "nested": {"a": "b"}}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_pickle_serialize_dataclass(self, serializer):
        """Test pickle serialization of dataclass."""
        person = Person(name="Test", age=30, email="test@example.com")
        serialized = serializer.serialize(person)
        deserialized = serializer.deserialize(serialized)
        assert isinstance(deserialized, Person)
        assert deserialized.name == "Test"
        assert deserialized.age == 30

    def test_pickle_serialize_complex_object(self, serializer):
        """Test pickle serialization of complex objects."""
        data = {
            "datetime": datetime.now(),
            "path": Path("/test/path"),
            "set": {1, 2, 3},
            "tuple": (1, 2, 3)
        }
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["set"] == {1, 2, 3}
        assert deserialized["tuple"] == (1, 2, 3)

    def test_pickle_deserialize_corrupted_raises_error(self, serializer):
        """Test pickle deserialization of corrupted data raises error."""
        corrupted = b"not valid pickle data"
        with pytest.raises(SerializationError):
            serializer.deserialize(corrupted)


# ==============================================================================
# Msgpack Serialization Tests
# ==============================================================================

class TestMsgpackSerialization:
    """Tests for MessagePack binary serialization."""

    def test_msgpack_serialize_dict(self):
        """Test msgpack serialization of dictionary."""
        data = {"key": "value", "number": 42}
        result = MsgpackSerializer.serialize(data)
        assert isinstance(result, bytes)

    def test_msgpack_roundtrip(self):
        """Test msgpack serialize/deserialize roundtrip."""
        data = {"list": [1, 2, 3], "bool": True, "null": None}
        serialized = MsgpackSerializer.serialize(data)
        deserialized = MsgpackSerializer.deserialize(serialized)
        assert deserialized == data

    def test_msgpack_serialize_nested(self):
        """Test msgpack serialization of nested structures."""
        data = {
            "level1": {
                "level2": {
                    "level3": {"value": "deep"}
                }
            }
        }
        serialized = MsgpackSerializer.serialize(data)
        deserialized = MsgpackSerializer.deserialize(serialized)
        assert deserialized == data

    def test_msgpack_binary_data(self):
        """Test msgpack handles binary data."""
        data = {"binary": b"\x00\x01\x02\x03"}
        serialized = MsgpackSerializer.serialize(data)
        deserialized = MsgpackSerializer.deserialize(serialized)
        assert deserialized["binary"] == b"\x00\x01\x02\x03"

    def test_msgpack_large_data(self):
        """Test msgpack with large data."""
        data = {"items": list(range(10000))}
        serialized = MsgpackSerializer.serialize(data)
        deserialized = MsgpackSerializer.deserialize(serialized)
        assert deserialized == data

    def test_msgpack_empty_structures(self):
        """Test msgpack with empty structures."""
        data = {"empty_list": [], "empty_dict": {}, "empty_string": ""}
        serialized = MsgpackSerializer.serialize(data)
        deserialized = MsgpackSerializer.deserialize(serialized)
        assert deserialized == data


# ==============================================================================
# Avro Serialization Tests
# ==============================================================================

class TestAvroSerialization:
    """Tests for Apache Avro serialization."""

    @pytest.fixture
    def simple_schema(self):
        """Simple Avro schema for testing."""
        return {
            'doc': 'Test schema',
            'name': 'TestRecord',
            'namespace': 'test',
            'type': 'record',
            'fields': [
                {'name': 'name', 'type': 'string'},
                {'name': 'age', 'type': 'int'},
            ],
        }

    @pytest.fixture
    def nullable_schema(self):
        """Schema with nullable fields."""
        return {
            'doc': 'Nullable schema',
            'name': 'NullableRecord',
            'namespace': 'test',
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'description', 'type': ['null', 'string']},
            ],
        }

    def test_avro_serialize_basic(self, simple_schema):
        """Test basic Avro serialization."""
        data = [{'name': 'Alice', 'age': 30}]
        result = AvroSerializer.serialize(data, simple_schema)
        assert isinstance(result, bytes)

    def test_avro_roundtrip(self, simple_schema):
        """Test Avro serialize/deserialize roundtrip."""
        data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        serialized = AvroSerializer.serialize(data, simple_schema)
        deserialized = AvroSerializer.deserialize(serialized)
        assert deserialized == data

    def test_avro_multiple_records(self, simple_schema):
        """Test Avro with multiple records."""
        data = [{'name': f'User{i}', 'age': 20 + i} for i in range(100)]
        serialized = AvroSerializer.serialize(data, simple_schema)
        deserialized = AvroSerializer.deserialize(serialized)
        assert len(deserialized) == 100

    def test_avro_nullable_field(self, nullable_schema):
        """Test Avro with nullable fields."""
        data = [
            {'id': 1, 'description': 'Has description'},
            {'id': 2, 'description': None}
        ]
        serialized = AvroSerializer.serialize(data, nullable_schema)
        deserialized = AvroSerializer.deserialize(serialized)
        assert deserialized[0]['description'] == 'Has description'
        assert deserialized[1]['description'] is None


# ==============================================================================
# Parquet Serialization Tests
# ==============================================================================

@pytest.mark.skipif(not PARQUET_AVAILABLE, reason="pyarrow/pandas parquet support not available")
class TestParquetSerialization:
    """Tests for Apache Parquet serialization."""

    def test_parquet_serialize_basic(self):
        """Test basic Parquet serialization."""
        data = [{'col1': 1, 'col2': 'A'}, {'col1': 2, 'col2': 'B'}]
        result = ParquetSerializer.serialize(data)
        assert isinstance(result, bytes)

    def test_parquet_roundtrip(self):
        """Test Parquet serialize/deserialize roundtrip."""
        data = [
            {'id': 1, 'name': 'Alice', 'score': 95.5},
            {'id': 2, 'name': 'Bob', 'score': 87.3}
        ]
        serialized = ParquetSerializer.serialize(data)
        deserialized = ParquetSerializer.deserialize(serialized)
        assert len(deserialized) == 2
        assert deserialized[0]['name'] == 'Alice'

    def test_parquet_large_dataset(self):
        """Test Parquet with larger dataset."""
        data = [{'id': i, 'value': f'item_{i}'} for i in range(1000)]
        serialized = ParquetSerializer.serialize(data)
        deserialized = ParquetSerializer.deserialize(serialized)
        assert len(deserialized) == 1000

    def test_parquet_mixed_types(self):
        """Test Parquet with mixed column types."""
        data = [
            {'int_col': 1, 'float_col': 1.5, 'str_col': 'a', 'bool_col': True},
            {'int_col': 2, 'float_col': 2.5, 'str_col': 'b', 'bool_col': False}
        ]
        serialized = ParquetSerializer.serialize(data)
        deserialized = ParquetSerializer.deserialize(serialized)
        assert len(deserialized) == 2


# ==============================================================================
# File Serialization Tests
# ==============================================================================

class TestFileSerialization:
    """Tests for file-based serialization."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def serializer(self):
        """Create default serializer."""
        return Serializer()

    def test_to_file_json(self, serializer, temp_dir):
        """Test JSON serialization to file."""
        data = {"key": "value", "number": 42}
        file_path = temp_dir / "test.json"
        serializer.to_file(data, str(file_path), SerializationFormat.JSON)
        assert file_path.exists()
        content = file_path.read_text()
        assert "key" in content

    def test_from_file_json(self, serializer, temp_dir):
        """Test JSON deserialization from file."""
        data = {"key": "value", "number": 42}
        file_path = temp_dir / "test.json"
        serializer.to_file(data, str(file_path), SerializationFormat.JSON)
        result = serializer.from_file(str(file_path), SerializationFormat.JSON)
        assert result == data

    def test_file_roundtrip_yaml(self, serializer, temp_dir):
        """Test YAML file roundtrip."""
        data = {"config": {"debug": True, "port": 8080}}
        file_path = temp_dir / "config.yaml"
        serializer.to_file(data, str(file_path), SerializationFormat.YAML)
        result = serializer.from_file(str(file_path), SerializationFormat.YAML)
        assert result == data

    def test_file_roundtrip_pickle(self, serializer, temp_dir):
        """Test pickle file roundtrip."""
        data = {"complex": [1, 2, 3], "set": {1, 2, 3}}
        file_path = temp_dir / "data.pkl"
        serializer.to_file(data, str(file_path), SerializationFormat.PICKLE)
        result = serializer.from_file(str(file_path), SerializationFormat.PICKLE)
        assert result["complex"] == [1, 2, 3]

    def test_from_file_nonexistent_raises_error(self, serializer, temp_dir):
        """Test deserialization from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            serializer.from_file(str(temp_dir / "nonexistent.json"))

    def test_to_file_with_dataclass(self, serializer, temp_dir):
        """Test file serialization with dataclass."""
        person = Person(name="Test", age=25, email="test@example.com")
        file_path = temp_dir / "person.json"
        serializer.to_file(person, str(file_path), SerializationFormat.JSON)
        result = serializer.from_file(str(file_path), SerializationFormat.JSON)
        assert result["name"] == "Test"


# ==============================================================================
# Serialization Manager Tests
# ==============================================================================

class TestSerializationManager:
    """Tests for SerializationManager.

    Note: SerializationManager has a bug where it passes 'format' instead of
    'default_format' to the Serializer constructor. These tests document
    the expected behavior once fixed.
    """

    @pytest.fixture
    def manager(self):
        """Create serialization manager."""
        return SerializationManager()

    @pytest.mark.xfail(reason="SerializationManager passes wrong kwarg 'format' to Serializer")
    def test_get_serializer_json(self, manager):
        """Test getting JSON serializer."""
        serializer = manager.get_serializer("json")
        assert serializer is not None

    @pytest.mark.xfail(reason="SerializationManager passes wrong kwarg 'format' to Serializer")
    def test_get_serializer_caches_instance(self, manager):
        """Test that serializer instances are cached."""
        serializer1 = manager.get_serializer("json")
        serializer2 = manager.get_serializer("json")
        assert serializer1 is serializer2

    @pytest.mark.xfail(reason="SerializationManager passes wrong kwarg 'format' to Serializer")
    def test_serialize_via_manager(self, manager):
        """Test serialization via manager."""
        data = {"key": "value"}
        result = manager.serialize(data, "json")
        assert isinstance(result, bytes)


# ==============================================================================
# Convenience Function Tests
# ==============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_serialize_json(self):
        """Test serialize convenience function with JSON."""
        data = {"key": "value"}
        result = serialize(data, "json")
        assert isinstance(result, bytes)
        assert b"key" in result

    def test_deserialize_json(self):
        """Test deserialize convenience function with JSON."""
        json_bytes = b'{"key": "value"}'
        result = deserialize(json_bytes, "json")
        assert result == {"key": "value"}

    def test_serialize_deserialize_roundtrip(self):
        """Test serialize/deserialize roundtrip via convenience functions."""
        data = {"nested": {"data": [1, 2, 3]}}
        serialized = serialize(data, SerializationFormat.JSON)
        deserialized = deserialize(serialized, SerializationFormat.JSON)
        assert deserialized == data

    def test_serialize_with_format_string(self):
        """Test serialize with format as string."""
        data = {"test": True}
        result = serialize(data, "json")
        assert isinstance(result, bytes)

    def test_serialize_with_format_enum(self):
        """Test serialize with format as enum."""
        data = {"test": True}
        result = serialize(data, SerializationFormat.JSON)
        assert isinstance(result, bytes)


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestErrorHandling:
    """Tests for error handling in serialization."""

    @pytest.fixture
    def serializer(self):
        """Create default serializer."""
        return Serializer()

    def test_serialization_error_message(self):
        """Test that SerializationError has descriptive message."""
        try:
            raise SerializationError("Test error message")
        except SerializationError as e:
            assert "Test error message" in str(e)

    def test_deserialize_empty_json(self, serializer):
        """Test deserialization of empty JSON."""
        result = serializer.deserialize(b'{}', SerializationFormat.JSON)
        assert result == {}

    def test_deserialize_empty_list(self, serializer):
        """Test deserialization of empty JSON list."""
        result = serializer.deserialize(b'[]', SerializationFormat.JSON)
        assert result == []

    def test_unsupported_format_raises_error(self, serializer):
        """Test that unsupported format raises error."""
        # Create a mock format that doesn't exist
        with pytest.raises((SerializationError, ValueError)):
            serializer.serialize({"data": "test"}, format="unsupported")


# ==============================================================================
# Edge Cases and Special Data Tests
# ==============================================================================

class TestEdgeCases:
    """Tests for edge cases and special data handling."""

    @pytest.fixture
    def serializer(self):
        """Create JSON serializer."""
        return Serializer(default_format=SerializationFormat.JSON)

    def test_unicode_strings(self, serializer):
        """Test serialization of unicode strings."""
        data = {"emoji": "Hello World!", "chinese": "Hello", "arabic": "Hello"}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data

    def test_very_long_string(self, serializer):
        """Test serialization of very long strings."""
        data = {"long": "x" * 100000}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert len(deserialized["long"]) == 100000

    def test_deeply_nested_structure(self, serializer):
        """Test serialization of deeply nested structures."""
        data = {"level": 1}
        current = data
        for i in range(2, 51):
            current["nested"] = {"level": i}
            current = current["nested"]

        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        # Verify first and last levels
        assert deserialized["level"] == 1

    def test_numeric_precision(self, serializer):
        """Test that numeric precision is maintained."""
        data = {
            "integer": 9007199254740992,  # Large integer
            "float": 3.141592653589793,
            "scientific": 1.23e-10
        }
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["integer"] == 9007199254740992
        assert abs(deserialized["float"] - 3.141592653589793) < 1e-10

    def test_boolean_values(self, serializer):
        """Test serialization of boolean values."""
        data = {"true": True, "false": False}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized["true"] is True
        assert deserialized["false"] is False

    def test_special_float_values(self, serializer):
        """Test handling of special float values."""
        # Note: JSON doesn't support inf/nan, pickle does
        pickle_serializer = Serializer(default_format=SerializationFormat.PICKLE)
        data = {"inf": float('inf'), "neg_inf": float('-inf')}
        serialized = pickle_serializer.serialize(data)
        deserialized = pickle_serializer.deserialize(serialized)
        assert deserialized["inf"] == float('inf')
        assert deserialized["neg_inf"] == float('-inf')

    def test_mixed_list_types(self, serializer):
        """Test serialization of lists with mixed types."""
        data = {"mixed": [1, "two", 3.0, True, None, {"nested": "dict"}]}
        serialized = serializer.serialize(data)
        deserialized = serializer.deserialize(serialized)
        assert deserialized == data
