from typing import Any, Optional, Union
import json

import msgpack
import msgpack
import tomli
import tomli
import tomli_w
import yaml
import yaml
import yaml

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger







Base serializer interface and implementations.
"""

logger = get_logger(__name__)

class SerializationError(CodomyrmexError):
    """Raised when serialization operations fail."""

    pass

class Serializer:
    """Base serializer class."""

    def __init__(self, format: str = "json"):
        """Initialize serializer.

        Args:
            format: Serialization format (json, yaml, toml, msgpack)
        """
        self.format = format
        self._serializers: dict[str, callable] = {}

    def serialize(self, obj: Any) -> Union[str, bytes]:
        """Serialize an object to string or bytes.

        Args:
            obj: Object to serialize

        Returns:
            Serialized data as string or bytes

        Raises:
            SerializationError: If serialization fails
        """
        try:
            if self.format == "json":
                return self._serialize_json(obj)
            elif self.format == "yaml":
                return self._serialize_yaml(obj)
            elif self.format == "toml":
                return self._serialize_toml(obj)
            elif self.format == "msgpack":
                return self._serialize_msgpack(obj)
            elif self.format in self._serializers:
                return self._serializers[self.format](obj)
            else:
                raise ValueError(f"Unknown format: {self.format}")
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise SerializationError(f"Failed to serialize: {str(e)}") from e

    def deserialize(self, data: Union[str, bytes], format: Optional[str] = None) -> Any:
        """Deserialize data to an object.

        Args:
            data: Serialized data
            format: Format to use (if None, auto-detect)

        Returns:
            Deserialized object

        Raises:
            SerializationError: If deserialization fails
        """
        try:
            format = format or self.format or self.detect_format(data)
            if format is None:
                raise SerializationError("Could not detect format")

            if format == "json":
                return self._deserialize_json(data)
            elif format == "yaml":
                return self._deserialize_yaml(data)
            elif format == "toml":
                return self._deserialize_toml(data)
            elif format == "msgpack":
                return self._deserialize_msgpack(data)
            elif format in self._serializers:
                return self._deserialize_custom(data, format)
            else:
                raise ValueError(f"Unknown format: {format}")
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise SerializationError(f"Failed to deserialize: {str(e)}") from e

    def detect_format(self, data: Union[str, bytes]) -> Optional[str]:
        """Detect serialization format from data.

        Args:
            data: Serialized data

        Returns:
            Format name if detected, None otherwise
        """
        if isinstance(data, bytes):
            # Try to detect from magic bytes
            if data.startswith(b"\x82\xa5"):
                return "msgpack"
            try:
                data_str = data.decode("utf-8")
            except UnicodeDecodeError:
                return None
        else:
            data_str = data

        # Try JSON
        try:
            json.loads(data_str)
            return "json"
        except (json.JSONDecodeError, TypeError):
            pass

        # Try YAML (check for YAML-like structure)
        if data_str.strip().startswith("---") or ":" in data_str and "\n" in data_str:
            try:
                yaml.safe_load(data_str)
                return "yaml"
            except (ImportError, yaml.YAMLError):
                pass

        # Try TOML (check for TOML-like structure)
        if "=" in data_str and "[" in data_str:
            try:
                tomli.loads(data_str)
                return "toml"
            except (ImportError, tomli.TOMLDecodeError):
                pass

        return None

    def _serialize_json(self, obj: Any) -> str:
        """Serialize to JSON."""
        return json.dumps(obj, default=str, indent=2)

    def _deserialize_json(self, data: Union[str, bytes]) -> Any:
        """Deserialize from JSON."""
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)

    def _serialize_yaml(self, obj: Any) -> str:
        """Serialize to YAML."""
        try:
            return yaml.dump(obj, default_flow_style=False)
        except ImportError:
            raise SerializationError("yaml package not available. Install with: pip install pyyaml")

    def _deserialize_yaml(self, data: Union[str, bytes]) -> Any:
        """Deserialize from YAML."""
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return yaml.safe_load(data)
        except ImportError:
            raise SerializationError("yaml package not available. Install with: pip install pyyaml")

    def _serialize_toml(self, obj: Any) -> str:
        """Serialize to TOML."""
        try:
            return tomli_w.dumps(obj)
        except ImportError:
            raise SerializationError("tomli-w package not available. Install with: pip install tomli-w")

    def _deserialize_toml(self, data: Union[str, bytes]) -> Any:
        """Deserialize from TOML."""
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return tomli.loads(data)
        except ImportError:
            raise SerializationError("tomli package not available. Install with: pip install tomli")

    def _serialize_msgpack(self, obj: Any) -> bytes:
        """Serialize to MessagePack."""
        try:
            return msgpack.packb(obj, default=str)
        except ImportError:
            raise SerializationError("msgpack package not available. Install with: pip install msgpack")

    def _deserialize_msgpack(self, data: Union[str, bytes]) -> Any:
        """Deserialize from MessagePack."""
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            return msgpack.unpackb(data, raw=False)
        except ImportError:
            raise SerializationError("msgpack package not available. Install with: pip install msgpack")

    def _deserialize_custom(self, data: Union[str, bytes], format: str) -> Any:
        """Deserialize using custom serializer."""
        # This would need to be implemented based on custom serializer requirements
        raise SerializationError(f"Custom deserialization not implemented for format: {format}")

    def register_serializer(self, format_name: str, serializer: callable, deserializer: Optional[callable] = None) -> None:
        """Register a custom serializer.

        Args:
            format_name: Format name
            serializer: Serializer function
            deserializer: Deserializer function (optional)
        """
        self._serializers[format_name] = serializer
        if deserializer:
            # Store deserializer separately - would need additional structure
            pass

