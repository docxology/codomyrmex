"""Zero-mock tests for serialization: serializer.py, mcp_tools.py, and exceptions.

Targets uncovered lines:
- serializer.py: pickle round-trip (lines 76-86), yaml round-trip (104-116),
  Path objects (134), file I/O (161-170)
- mcp_tools.py: pickle base64 path (lines 54-67)
- exceptions.py: all exception classes

No mocks, no monkeypatch, no unittest.mock.

External dependencies:
- yaml (PyYAML) — skipif guard if unavailable
"""

import os
import pickle
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

try:
    import yaml as _yaml_check

    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

_SKIP_YAML = pytest.mark.skipif(
    not _YAML_AVAILABLE, reason="PyYAML not installed"
)


# ===========================================================================
# Class: TestSerializationFormatEnum
# ===========================================================================


class TestSerializationFormatEnum:
    """Verify the SerializationFormat enum values."""

    def test_json_format_value(self):
        from codomyrmex.serialization.serializer import SerializationFormat

        assert SerializationFormat.JSON.value == "json"

    def test_pickle_format_value(self):
        from codomyrmex.serialization.serializer import SerializationFormat

        assert SerializationFormat.PICKLE.value == "pickle"

    def test_yaml_format_value(self):
        from codomyrmex.serialization.serializer import SerializationFormat

        assert SerializationFormat.YAML.value == "yaml"

    def test_all_three_formats_present(self):
        from codomyrmex.serialization.serializer import SerializationFormat

        values = {f.value for f in SerializationFormat}
        assert {"json", "pickle", "yaml"} == values


# ===========================================================================
# Class: TestSerializerJson
# ===========================================================================


class TestSerializerJson:
    """JSON serialization round-trips."""

    def _serializer(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        return Serializer(default_format=SerializationFormat.JSON)

    def test_roundtrip_dict(self):
        s = self._serializer()
        data = {"key": "value", "num": 42}
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_roundtrip_list(self):
        s = self._serializer()
        data = [1, "two", 3.0, None]
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_roundtrip_nested(self):
        s = self._serializer()
        data = {"a": {"b": {"c": [1, 2, 3]}}}
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_serialize_returns_bytes(self):
        s = self._serializer()
        assert isinstance(s.serialize({"x": 1}), bytes)

    def test_serializes_datetime_as_isostring(self):
        from datetime import datetime

        s = self._serializer()
        from codomyrmex.serialization.serializer import SerializationFormat

        now = datetime(2024, 6, 1, 12, 0, 0)
        raw = s.serialize({"ts": now}, format=SerializationFormat.JSON)
        import json

        parsed = json.loads(raw.decode())
        assert "2024-06-01" in parsed["ts"]

    def test_serializes_enum_as_value(self):
        from enum import Enum

        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        class Color(Enum):
            RED = "red"

        s = Serializer(SerializationFormat.JSON)
        raw = s.serialize({"color": Color.RED})
        import json

        parsed = json.loads(raw.decode())
        assert parsed["color"] == "red"

    def test_serializes_path_as_string(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.JSON)
        raw = s.serialize({"p": Path("/tmp/test.txt")})
        import json

        parsed = json.loads(raw.decode())
        assert parsed["p"] == "/tmp/test.txt"

    def test_deserialize_json_to_dataclass(self):
        import json

        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        @dataclass
        class Point:
            x: int
            y: int

        s = Serializer(SerializationFormat.JSON)
        raw = json.dumps({"x": 3, "y": 7}).encode()
        obj = s.deserialize(raw, target_type=Point)
        assert isinstance(obj, Point)
        assert obj.x == 3
        assert obj.y == 7


# ===========================================================================
# Class: TestSerializerPickle
# ===========================================================================


class TestSerializerPickle:
    """Pickle serialization round-trips — exercising previously uncovered lines."""

    def _serializer(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        return Serializer(default_format=SerializationFormat.PICKLE)

    def test_roundtrip_dict(self):
        s = self._serializer()
        data = {"a": 1, "b": [2, 3]}
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_roundtrip_arbitrary_object(self):
        s = self._serializer()
        original = {"nested": {"list": [1, 2, 3], "val": "ok"}}
        result = s.deserialize(s.serialize(original))
        assert result == original

    def test_deserialize_requires_bytes(self):
        from codomyrmex.serialization.serializer import (
            SerializationError,
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.PICKLE)
        with pytest.raises(SerializationError):
            s.deserialize("not_bytes", format=SerializationFormat.PICKLE)

    def test_deserialize_rejects_oversized_payload(self):
        from codomyrmex.serialization.serializer import (
            SerializationError,
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.PICKLE)
        # Create fake payload > 100 MB
        huge = b"x" * (101 * 1024 * 1024)
        with pytest.raises(SerializationError):
            s.deserialize(huge, format=SerializationFormat.PICKLE)

    def test_serialize_pickle_returns_bytes(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.PICKLE)
        raw = s.serialize({"k": "v"})
        assert isinstance(raw, bytes)
        # Confirm it's valid pickle
        assert pickle.loads(raw) == {"k": "v"}


# ===========================================================================
# Class: TestSerializerYaml
# ===========================================================================


@_SKIP_YAML
class TestSerializerYaml:
    """YAML serialization round-trips — exercising previously uncovered lines."""

    def _serializer(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        return Serializer(default_format=SerializationFormat.YAML)

    def test_roundtrip_dict(self):
        s = self._serializer()
        data = {"host": "localhost", "port": 5432}
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_serialize_returns_bytes(self):
        s = self._serializer()
        raw = s.serialize({"k": "v"})
        assert isinstance(raw, bytes)
        assert b":" in raw  # YAML key-value separator

    def test_roundtrip_list(self):
        s = self._serializer()
        data = ["alpha", "beta", "gamma"]
        result = s.deserialize(s.serialize(data))
        assert result == data

    def test_deserialize_yaml_to_dataclass(self):
        import yaml

        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        @dataclass
        class Config:
            name: str
            count: int

        s = Serializer(SerializationFormat.YAML)
        raw = yaml.dump({"name": "test", "count": 7}).encode()
        obj = s.deserialize(raw, target_type=Config)
        assert isinstance(obj, Config)
        assert obj.name == "test"
        assert obj.count == 7


# ===========================================================================
# Class: TestSerializerFileIO
# ===========================================================================


class TestSerializerFileIO:
    """Tests for to_file and from_file — lines 136-153 in serializer.py."""

    def test_to_file_and_from_file_json(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.JSON)
        data = {"config": "value", "count": 5}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            s.to_file(data, path)
            result = s.from_file(path)
            assert result == data
        finally:
            os.unlink(path)

    def test_to_file_and_from_file_pickle(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.PICKLE)
        data = {"nested": [1, 2, 3]}
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            path = f.name
        try:
            s.to_file(data, path)
            result = s.from_file(path, format=SerializationFormat.PICKLE)
            assert result == data
        finally:
            os.unlink(path)

    @_SKIP_YAML
    def test_to_file_and_from_file_yaml(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            Serializer,
        )

        s = Serializer(SerializationFormat.YAML)
        data = {"env": "prod", "debug": False}
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = f.name
        try:
            s.to_file(data, path)
            result = s.from_file(path, format=SerializationFormat.YAML)
            assert result == data
        finally:
            os.unlink(path)


# ===========================================================================
# Class: TestSerializeConvenienceFunctions
# ===========================================================================


class TestSerializeConvenienceFunctions:
    """Tests for module-level serialize() and deserialize() helpers."""

    def test_serialize_default_json(self):
        from codomyrmex.serialization.serializer import deserialize, serialize

        data = {"hello": "world"}
        raw = serialize(data)
        assert isinstance(raw, bytes)
        result = deserialize(raw)
        assert result == data

    def test_serialize_pickle_format(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            deserialize,
            serialize,
        )

        data = {"key": [1, 2, 3]}
        raw = serialize(data, SerializationFormat.PICKLE)
        result = deserialize(raw, SerializationFormat.PICKLE)
        assert result == data

    @_SKIP_YAML
    def test_serialize_yaml_format(self):
        from codomyrmex.serialization.serializer import (
            SerializationFormat,
            deserialize,
            serialize,
        )

        data = {"mode": "yaml_test"}
        raw = serialize(data, SerializationFormat.YAML)
        result = deserialize(raw, SerializationFormat.YAML)
        assert result == data


# ===========================================================================
# Class: TestSerializationExceptions
# ===========================================================================


class TestSerializationExceptions:
    """Verify exception hierarchy from exceptions.py."""

    def test_serialization_error_is_exception(self):
        from codomyrmex.serialization.exceptions import SerializationError

        err = SerializationError("test error")
        assert isinstance(err, Exception)
        # CodomyrmexError stores message in args[0]
        assert err.args[0] == "test error"

    def test_deserialization_error_is_exception(self):
        from codomyrmex.serialization.exceptions import DeserializationError

        err = DeserializationError("bad data")
        assert isinstance(err, Exception)
        assert err.args[0] == "bad data"

    def test_format_not_supported_error(self):
        from codomyrmex.serialization.exceptions import FormatNotSupportedError

        err = FormatNotSupportedError("xml not supported")
        assert isinstance(err, Exception)

    def test_format_not_supported_stores_format(self):
        from codomyrmex.serialization.exceptions import FormatNotSupportedError

        err = FormatNotSupportedError("no xml", requested_format="xml")
        assert err.context.get("requested_format") == "xml"

    def test_circular_reference_error(self):
        from codomyrmex.serialization.exceptions import CircularReferenceError

        err = CircularReferenceError("cycle detected")
        assert isinstance(err, Exception)

    def test_binary_format_error(self):
        from codomyrmex.serialization.exceptions import BinaryFormatError

        err = BinaryFormatError("bad binary")
        assert isinstance(err, Exception)

    def test_binary_format_error_stores_operation(self):
        from codomyrmex.serialization.exceptions import BinaryFormatError

        err = BinaryFormatError("pack failed", operation="pack")
        assert err.context.get("operation") == "pack"

    def test_schema_validation_error(self):
        from codomyrmex.serialization.exceptions import SchemaValidationError

        err = SchemaValidationError("schema mismatch")
        assert isinstance(err, Exception)

    def test_schema_validation_stores_schema_name(self):
        from codomyrmex.serialization.exceptions import SchemaValidationError

        err = SchemaValidationError("mismatch", schema_name="my_schema")
        assert err.context.get("schema_name") == "my_schema"

    def test_type_conversion_error(self):
        from codomyrmex.serialization.exceptions import TypeConversionError

        err = TypeConversionError("cannot convert")
        assert isinstance(err, Exception)

    def test_encoding_error(self):
        from codomyrmex.serialization.exceptions import EncodingError

        err = EncodingError("bad encoding")
        assert isinstance(err, Exception)

    def test_encoding_error_stores_encoding(self):
        from codomyrmex.serialization.exceptions import EncodingError

        err = EncodingError("utf-8 failed", encoding="utf-8")
        assert err.context.get("encoding") == "utf-8"


# ===========================================================================
# Class: TestMcpToolsSerializer
# ===========================================================================


class TestMcpToolsSerializer:
    """Tests for serialization MCP tools: serialize_data, deserialize_data,
    serialization_list_formats."""

    def test_serialize_data_json_returns_string(self):
        from codomyrmex.serialization.mcp_tools import serialize_data

        result = serialize_data({"key": "val"}, format="json")
        assert isinstance(result, str)
        import json

        parsed = json.loads(result)
        assert parsed["key"] == "val"

    @_SKIP_YAML
    def test_serialize_data_yaml_returns_string(self):
        from codomyrmex.serialization.mcp_tools import serialize_data

        result = serialize_data({"mode": "yaml"}, format="yaml")
        assert isinstance(result, str)
        import yaml

        parsed = yaml.safe_load(result)
        assert parsed["mode"] == "yaml"

    def test_serialize_data_pickle_returns_base64(self):
        import base64

        from codomyrmex.serialization.mcp_tools import serialize_data

        result = serialize_data({"x": 1}, format="pickle")
        # Should be base64-encoded (ASCII only)
        assert isinstance(result, str)
        # Should be decodeable as base64
        raw = base64.b64decode(result.encode("ascii"))
        assert pickle.loads(raw) == {"x": 1}

    def test_deserialize_data_json_roundtrip(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

        original = {"foo": "bar", "n": 42}
        serialized = serialize_data(original, format="json")
        result = deserialize_data(serialized, format="json")
        assert result == original

    def test_deserialize_data_pickle_roundtrip(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

        original = {"nested": [1, 2, 3]}
        serialized = serialize_data(original, format="pickle")
        result = deserialize_data(serialized, format="pickle")
        assert result == original

    def test_serialization_list_formats_returns_list(self):
        from codomyrmex.serialization.mcp_tools import serialization_list_formats

        formats = serialization_list_formats()
        assert isinstance(formats, list)
        assert "json" in formats
        assert "pickle" in formats
        assert "yaml" in formats

    def test_serialization_list_formats_has_three_items(self):
        from codomyrmex.serialization.mcp_tools import serialization_list_formats

        assert len(serialization_list_formats()) == 3

    def test_deserialize_data_invalid_json_raises(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data
        from codomyrmex.serialization.serializer import SerializationError

        with pytest.raises(SerializationError):
            deserialize_data("not valid json{{{", format="json")

    def test_deserialize_data_bad_base64_pickle_raises(self):
        """Exercises the fallback path (lines 61-67) — bad base64 for pickle."""
        from codomyrmex.serialization.mcp_tools import deserialize_data

        # Pass a string that is not valid base64 at all
        with pytest.raises(Exception):  # noqa: B017
            deserialize_data("!!!not_base64!!!", format="pickle")

    def test_serialize_deserialize_list_json(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

        original = [1, "two", 3.0]
        serialized = serialize_data(original, format="json")
        result = deserialize_data(serialized, format="json")
        assert result == original

    def test_serialize_deserialize_list_pickle(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

        original = ["a", "b", "c"]
        serialized = serialize_data(original, format="pickle")
        result = deserialize_data(serialized, format="pickle")
        assert result == original

    @_SKIP_YAML
    def test_deserialize_data_yaml_roundtrip(self):
        from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

        original = {"env": "staging", "retries": 3}
        serialized = serialize_data(original, format="yaml")
        result = deserialize_data(serialized, format="yaml")
        assert result == original

    def test_deserialize_data_pickle_corrupted_data_raises(self):
        """Corrupt base64-encoded payload that decodes but is invalid pickle."""
        import base64

        from codomyrmex.serialization.mcp_tools import deserialize_data
        from codomyrmex.serialization.serializer import SerializationError

        # Valid base64 but not valid pickle bytes
        corrupt_b64 = base64.b64encode(b"this is not pickle data").decode("ascii")
        with pytest.raises(SerializationError):
            deserialize_data(corrupt_b64, format="pickle")


# ===========================================================================
# Class: TestCliCommands
# ===========================================================================


class TestCliCommands:
    """Tests for the cli_commands() function in __init__.py (lines 34-61)."""

    def test_cli_commands_returns_dict(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert isinstance(cmds, dict)

    def test_cli_commands_has_formats_key(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert "formats" in cmds

    def test_cli_commands_has_convert_key(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert "convert" in cmds

    def test_cli_commands_formats_has_handler(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert callable(cmds["formats"]["handler"])

    def test_cli_commands_convert_has_handler(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert callable(cmds["convert"]["handler"])

    def test_formats_handler_prints_json(self, capsys):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        cmds["formats"]["handler"]()
        output = capsys.readouterr().out
        assert "json" in output

    def test_formats_handler_prints_pickle(self, capsys):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        cmds["formats"]["handler"]()
        output = capsys.readouterr().out
        assert "pickle" in output

    def test_formats_handler_prints_msgpack(self, capsys):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        cmds["formats"]["handler"]()
        output = capsys.readouterr().out
        assert "msgpack" in output.lower()

    def test_convert_handler_no_path_prints_usage(self, capsys):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        cmds["convert"]["handler"]()
        output = capsys.readouterr().out
        assert "Usage" in output

    def test_convert_handler_with_real_json_file(self, capsys):
        """_convert with a real JSON file path round-trips to JSON output."""
        import json
        import tempfile

        from codomyrmex.serialization import cli_commands

        data = {"hello": "world"}
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="wb"
        ) as f:
            f.write(json.dumps(data).encode())
            path = f.name
        try:
            cmds = cli_commands()
            cmds["convert"]["handler"](path=path, **{"from": "json", "to": "json"})
            output = capsys.readouterr().out
            # Output should be valid JSON containing "hello"
            assert "hello" in output
        finally:
            os.unlink(path)

    @_SKIP_YAML
    def test_convert_handler_json_to_yaml(self, capsys):
        """_convert writes JSON-to-YAML conversion to stdout."""
        import json
        import tempfile

        from codomyrmex.serialization import cli_commands

        data = {"service": "test", "port": 8080}
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="wb"
        ) as f:
            f.write(json.dumps(data).encode())
            path = f.name
        try:
            cmds = cli_commands()
            cmds["convert"]["handler"](path=path, **{"from": "json", "to": "yaml"})
            output = capsys.readouterr().out
            assert "service" in output
        finally:
            os.unlink(path)

    def test_convert_handler_bad_path_prints_error(self, capsys):
        """_convert with a non-existent path prints conversion error."""
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        cmds["convert"]["handler"](
            path="/nonexistent/path/file.json", **{"from": "json", "to": "json"}
        )
        output = capsys.readouterr().out
        assert "error" in output.lower() or "Error" in output

    def test_cli_commands_formats_help_string(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert isinstance(cmds["formats"].get("help"), str)

    def test_cli_commands_convert_help_string(self):
        from codomyrmex.serialization import cli_commands

        cmds = cli_commands()
        assert isinstance(cmds["convert"].get("help"), str)


# ===========================================================================
# Class: TestModulePublicApi
# ===========================================================================


class TestModulePublicApi:
    """Tests for module-level serialize/deserialize helpers in __init__.py."""

    def test_module_serialize_json_string_format(self):
        """__init__.py serialize() accepts string format name."""
        from codomyrmex.serialization import serialize

        raw = serialize({"a": 1}, format="json")
        assert isinstance(raw, bytes)
        import json

        assert json.loads(raw) == {"a": 1}

    def test_module_deserialize_json_string_format(self):
        """__init__.py deserialize() accepts string format name."""
        import json

        from codomyrmex.serialization import deserialize

        raw = json.dumps({"x": 99}).encode()
        result = deserialize(raw, format="json")
        assert result == {"x": 99}

    def test_module_serialize_pickle_string_format(self):
        from codomyrmex.serialization import serialize

        raw = serialize([1, 2, 3], format="pickle")
        assert isinstance(raw, bytes)
        assert pickle.loads(raw) == [1, 2, 3]

    def test_module_deserialize_pickle_string_format(self):
        from codomyrmex.serialization import deserialize

        raw = pickle.dumps({"key": "value"})
        result = deserialize(raw, format="pickle")
        assert result == {"key": "value"}

    @_SKIP_YAML
    def test_module_serialize_yaml_string_format(self):
        import yaml

        from codomyrmex.serialization import deserialize, serialize

        raw = serialize({"env": "test"}, format="yaml")
        assert isinstance(raw, bytes)
        result = deserialize(raw, format="yaml")
        assert result == {"env": "test"}

    def test_module_all_exports_present(self):
        """Verify __all__ contains expected public symbols."""
        import codomyrmex.serialization as mod

        for name in [
            "Serializer",
            "SerializationFormat",
            "SerializationError",
            "DeserializationError",
            "SerializationManager",
            "serialize",
            "deserialize",
        ]:
            assert hasattr(mod, name), f"Missing export: {name}"

    def test_module_version_string(self):
        import codomyrmex.serialization as mod

        assert hasattr(mod, "__version__")
        assert isinstance(mod.__version__, str)
