"""Serialization Exception Classes.

This module defines exceptions specific to serialization and deserialization
operations including format handling, schema validation, and encoding errors.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class SerializationError(CodomyrmexError):
    """Base exception for serialization-related errors.

    Attributes:
        message: Error description.
        format: Serialization format (JSON, YAML, MessagePack, etc.).
        data_type: Type of data being serialized.
    """

    def __init__(
        self,
        message: str,
        format: str | None = None,
        data_type: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if format:
            self.context["format"] = format
        if data_type:
            self.context["data_type"] = data_type


class DeserializationError(SerializationError):
    """Raised when deserialization of data fails.

    Attributes:
        message: Error description.
        format: Expected serialization format.
        raw_data_preview: Preview of the raw data that failed to deserialize.
        expected_type: The expected output type.
    """

    def __init__(
        self,
        message: str,
        format: str | None = None,
        raw_data_preview: str | None = None,
        expected_type: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, format=format, **kwargs)
        # Truncate raw data preview to avoid huge context
        if raw_data_preview:
            self.context["raw_data_preview"] = (
                raw_data_preview[:200] + "..." if len(raw_data_preview) > 200 else raw_data_preview
            )
        if expected_type:
            self.context["expected_type"] = expected_type


class SchemaValidationError(SerializationError):
    """Raised when data fails schema validation during serialization.

    Attributes:
        message: Error description.
        schema_name: Name of the schema.
        validation_errors: List of specific validation failures.
        path: JSON path or location of the validation error.
    """

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        validation_errors: list[str] | None = None,
        path: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if schema_name:
            self.context["schema_name"] = schema_name
        if validation_errors:
            self.context["validation_errors"] = validation_errors
        if path:
            self.context["path"] = path


class EncodingError(SerializationError):
    """Raised when character encoding fails.

    Attributes:
        message: Error description.
        encoding: The encoding that failed (UTF-8, ASCII, etc.).
        position: Position in data where encoding error occurred.
    """

    def __init__(
        self,
        message: str,
        encoding: str | None = None,
        position: int | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if encoding:
            self.context["encoding"] = encoding
        if position is not None:
            self.context["position"] = position


class FormatNotSupportedError(SerializationError):
    """Raised when an unsupported serialization format is requested.

    Attributes:
        message: Error description.
        requested_format: The format that was requested.
        supported_formats: List of supported formats.
    """

    def __init__(
        self,
        message: str,
        requested_format: str | None = None,
        supported_formats: list[str] | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if requested_format:
            self.context["requested_format"] = requested_format
        if supported_formats:
            self.context["supported_formats"] = supported_formats


class CircularReferenceError(SerializationError):
    """Raised when circular references are detected during serialization.

    Attributes:
        message: Error description.
        object_type: Type of object with circular reference.
        reference_path: Path to the circular reference.
    """

    def __init__(
        self,
        message: str,
        object_type: str | None = None,
        reference_path: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if object_type:
            self.context["object_type"] = object_type
        if reference_path:
            self.context["reference_path"] = reference_path


class TypeConversionError(SerializationError):
    """Raised when type conversion fails during serialization.

    Attributes:
        message: Error description.
        source_type: The source type.
        target_type: The target type.
        value_preview: Preview of the value that failed conversion.
    """

    def __init__(
        self,
        message: str,
        source_type: str | None = None,
        target_type: str | None = None,
        value_preview: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if source_type:
            self.context["source_type"] = source_type
        if target_type:
            self.context["target_type"] = target_type
        if value_preview:
            self.context["value_preview"] = (
                value_preview[:100] + "..." if len(value_preview) > 100 else value_preview
            )


class BinaryFormatError(SerializationError):
    """Raised when binary format operations fail.

    Attributes:
        message: Error description.
        format: Binary format (MessagePack, Protobuf, Avro, etc.).
        operation: The operation that failed (pack, unpack, etc.).
    """

    def __init__(
        self,
        message: str,
        format: str | None = None,
        operation: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, format=format, **kwargs)
        if operation:
            self.context["operation"] = operation
