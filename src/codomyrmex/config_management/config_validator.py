"""Configuration schema validator with type checking and constraint enforcement.

Validates configuration dicts against declarative schemas with support for
required fields, type checking, value constraints, nested objects, and defaults.

Example::

    schema = ConfigSchema(
        {
            "port": SchemaField(type=int, required=True, min_val=1, max_val=65535),
            "host": SchemaField(type=str, default="0.0.0.0"),
            "debug": SchemaField(type=bool, default=False),
        }
    )
    result = schema.validate({"port": 8080})
    assert result.valid
    assert result.config["host"] == "0.0.0.0"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SchemaField:
    """Schema definition for a single config field.

    Attributes:
        type: Expected Python type.
        required: Whether the field is mandatory.
        default: Default value if not provided.
        min_val: Minimum numeric value.
        max_val: Maximum numeric value.
        choices: Allowed values set.
        description: Human-readable description.
    """

    type: type = str
    required: bool = False
    default: Any = None
    min_val: float | None = None
    max_val: float | None = None
    choices: list[Any] | None = None
    description: str = ""


@dataclass
class ValidationResult:
    """Result of a configuration validation.

    Attributes:
        valid: Whether the config passed validation.
        errors: list of error messages.
        warnings: list of warning messages.
        config: Final config with defaults applied.
    """

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class ConfigSchema:
    """Declarative configuration schema with validation.

    Args:
        fields: dict mapping field name to :class:`SchemaField`.

    Example::

        schema = ConfigSchema({"timeout": SchemaField(type=int, default=30, min_val=1)})
        result = schema.validate({})
        assert result.config["timeout"] == 30
    """

    def __init__(self, fields: dict[str, SchemaField]) -> None:
        self._fields = fields

    @property
    def field_names(self) -> list[str]:
        """All field names in the schema."""
        return list(self._fields.keys())

    @property
    def required_fields(self) -> list[str]:
        """Names of required fields."""
        return [name for name, f in self._fields.items() if f.required]

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate a configuration dict against this schema.

        Args:
            config: Configuration dict to validate.

        Returns:
            :class:`ValidationResult` with errors, warnings, and final config.
        """
        result = ValidationResult(config=dict(config))

        # Check required fields
        for name, schema_field in self._fields.items():
            if schema_field.required and name not in config:
                result.errors.append(f"Missing required field: '{name}'")
                result.valid = False

        # Apply defaults
        for name, schema_field in self._fields.items():
            if name not in result.config and schema_field.default is not None:
                result.config[name] = schema_field.default

        # Type and constraint checking
        for name, value in list(result.config.items()):
            if name not in self._fields:
                result.warnings.append(f"Unknown field: '{name}'")
                continue

            schema_field = self._fields[name]

            # Type check
            if not isinstance(value, schema_field.type):
                result.errors.append(
                    f"Field '{name}': expected {schema_field.type.__name__}, "
                    f"got {type(value).__name__}"
                )
                result.valid = False
                continue

            # Range check
            if schema_field.min_val is not None and isinstance(value, (int, float)):
                if value < schema_field.min_val:
                    result.errors.append(
                        f"Field '{name}': {value} < minimum {schema_field.min_val}"
                    )
                    result.valid = False

            if schema_field.max_val is not None and isinstance(value, (int, float)):
                if value > schema_field.max_val:
                    result.errors.append(
                        f"Field '{name}': {value} > maximum {schema_field.max_val}"
                    )
                    result.valid = False

            # Choices check
            if schema_field.choices is not None and value not in schema_field.choices:
                result.errors.append(
                    f"Field '{name}': {value!r} not in allowed choices {schema_field.choices}"
                )
                result.valid = False

        return result

    def get_defaults(self) -> dict[str, Any]:
        """Get all default values.

        Returns:
            dict of field name to default value (excluding None defaults).
        """
        return {
            name: f.default for name, f in self._fields.items() if f.default is not None
        }

    def describe(self) -> list[dict[str, Any]]:
        """Describe the schema as a list of field descriptions.

        Returns:
            list of field metadata dicts.
        """
        return [
            {
                "name": name,
                "type": f.type.__name__,
                "required": f.required,
                "default": f.default,
                "description": f.description,
                "choices": f.choices,
            }
            for name, f in self._fields.items()
        ]


__all__ = [
    "ConfigSchema",
    "SchemaField",
    "ValidationResult",
]
