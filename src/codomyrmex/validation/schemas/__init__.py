"""
Validation Schemas Module

JSON Schema, Pydantic-style, and custom validation schemas.
"""

__version__ = "0.1.0"

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from collections.abc import Callable

T = TypeVar('T')


class SchemaType(Enum):
    """Supported schema types."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"


@dataclass
class ValidationError:
    """A validation error."""
    path: str
    message: str
    value: Any = None
    constraint: str | None = None

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool = True
    errors: list[ValidationError] = field(default_factory=list)

    def add_error(
        self,
        path: str,
        message: str,
        value: Any = None,
        constraint: str | None = None,
    ) -> None:
        """Add an error."""
        self.errors.append(ValidationError(path, message, value, constraint))
        self.valid = False

    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one."""
        self.errors.extend(other.errors)
        if not other.valid:
            self.valid = False

    @property
    def error_messages(self) -> list[str]:
        """Get list of error messages."""
        return [str(e) for e in self.errors]


class Constraint(ABC):
    """Base class for validation constraints."""

    @abstractmethod
    def validate(self, value: Any, path: str) -> ValidationError | None:
        """
        Validate a value.

        Returns:
            ValidationError if invalid, None if valid
        """
        pass


class TypeConstraint(Constraint):
    """Validate that value is of expected type."""

    TYPE_MAP = {
        SchemaType.STRING: str,
        SchemaType.INTEGER: int,
        SchemaType.NUMBER: (int, float),
        SchemaType.BOOLEAN: bool,
        SchemaType.ARRAY: list,
        SchemaType.OBJECT: dict,
        SchemaType.NULL: type(None),
    }

    def __init__(self, expected_type: SchemaType):
        self.expected_type = expected_type

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if self.expected_type == SchemaType.ANY:
            return None

        expected = self.TYPE_MAP.get(self.expected_type)
        if expected is None:
            return None

        if not isinstance(value, expected):
            return ValidationError(
                path=path,
                message=f"Expected {self.expected_type.value}, got {type(value).__name__}",
                value=value,
                constraint="type",
            )
        return None


class MinLengthConstraint(Constraint):
    """Validate minimum length."""

    def __init__(self, min_length: int):
        self.min_length = min_length

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if hasattr(value, '__len__'):
            if len(value) < self.min_length:
                return ValidationError(
                    path=path,
                    message=f"Length must be at least {self.min_length}",
                    value=value,
                    constraint="minLength",
                )
        return None


class MaxLengthConstraint(Constraint):
    """Validate maximum length."""

    def __init__(self, max_length: int):
        self.max_length = max_length

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if hasattr(value, '__len__'):
            if len(value) > self.max_length:
                return ValidationError(
                    path=path,
                    message=f"Length must be at most {self.max_length}",
                    value=value,
                    constraint="maxLength",
                )
        return None


class MinValueConstraint(Constraint):
    """Validate minimum value."""

    def __init__(self, minimum: int | float, exclusive: bool = False):
        self.minimum = minimum
        self.exclusive = exclusive

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if isinstance(value, (int, float)):
            if self.exclusive:
                if value <= self.minimum:
                    return ValidationError(
                        path=path,
                        message=f"Value must be greater than {self.minimum}",
                        value=value,
                        constraint="exclusiveMinimum",
                    )
            else:
                if value < self.minimum:
                    return ValidationError(
                        path=path,
                        message=f"Value must be at least {self.minimum}",
                        value=value,
                        constraint="minimum",
                    )
        return None


class MaxValueConstraint(Constraint):
    """Validate maximum value."""

    def __init__(self, maximum: int | float, exclusive: bool = False):
        self.maximum = maximum
        self.exclusive = exclusive

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if isinstance(value, (int, float)):
            if self.exclusive:
                if value >= self.maximum:
                    return ValidationError(
                        path=path,
                        message=f"Value must be less than {self.maximum}",
                        value=value,
                        constraint="exclusiveMaximum",
                    )
            else:
                if value > self.maximum:
                    return ValidationError(
                        path=path,
                        message=f"Value must be at most {self.maximum}",
                        value=value,
                        constraint="maximum",
                    )
        return None


class PatternConstraint(Constraint):
    """Validate against regex pattern."""

    def __init__(self, pattern: str):
        self.pattern = pattern
        self._compiled = re.compile(pattern)

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if isinstance(value, str):
            if not self._compiled.search(value):
                return ValidationError(
                    path=path,
                    message=f"Value must match pattern: {self.pattern}",
                    value=value,
                    constraint="pattern",
                )
        return None


class EnumConstraint(Constraint):
    """Validate value is in allowed set."""

    def __init__(self, allowed: list[Any]):
        self.allowed = allowed

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if value not in self.allowed:
            return ValidationError(
                path=path,
                message=f"Value must be one of: {self.allowed}",
                value=value,
                constraint="enum",
            )
        return None


class RequiredConstraint(Constraint):
    """Validate required fields."""

    def __init__(self, required_fields: list[str]):
        self.required_fields = required_fields

    def validate(self, value: Any, path: str) -> ValidationError | None:
        if isinstance(value, dict):
            for field_name in self.required_fields:
                if field_name not in value:
                    return ValidationError(
                        path=f"{path}.{field_name}",
                        message=f"Required field '{field_name}' is missing",
                        value=value,
                        constraint="required",
                    )
        return None


@dataclass
class FieldSchema:
    """Schema for a single field."""
    type: SchemaType = SchemaType.ANY
    required: bool = False
    nullable: bool = False
    default: Any = None
    description: str = ""
    constraints: list[Constraint] = field(default_factory=list)
    items: Optional["FieldSchema"] = None  # For arrays
    properties: dict[str, "FieldSchema"] = field(default_factory=dict)  # For objects

    def validate(self, value: Any, path: str = "$") -> ValidationResult:
        """Validate a value against this schema."""
        result = ValidationResult()

        # Handle null
        if value is None:
            if self.nullable:
                return result
            result.add_error(path, "Value cannot be null", value, "nullable")
            return result

        # Type checking
        type_constraint = TypeConstraint(self.type)
        error = type_constraint.validate(value, path)
        if error:
            result.errors.append(error)
            result.valid = False
            return result

        # Apply constraints
        for constraint in self.constraints:
            error = constraint.validate(value, path)
            if error:
                result.errors.append(error)
                result.valid = False

        # Validate array items
        if self.type == SchemaType.ARRAY and self.items and isinstance(value, list):
            for i, item in enumerate(value):
                item_result = self.items.validate(item, f"{path}[{i}]")
                result.merge(item_result)

        # Validate object properties
        if self.type == SchemaType.OBJECT and self.properties and isinstance(value, dict):
            for prop_name, prop_schema in self.properties.items():
                if prop_name in value:
                    prop_result = prop_schema.validate(value[prop_name], f"{path}.{prop_name}")
                    result.merge(prop_result)
                elif prop_schema.required:
                    result.add_error(f"{path}.{prop_name}", "Required field is missing", None, "required")

        return result


class Schema:
    """
    A complete validation schema.

    Usage:
        schema = Schema.object({
            "name": Schema.string(min_length=1),
            "age": Schema.integer(minimum=0),
            "email": Schema.string(pattern=r"^[\w\.\-]+@[\w\.\-]+$"),
            "tags": Schema.array(Schema.string()),
        }, required=["name", "email"])

        result = schema.validate(data)
        if not result.valid:
            print(result.error_messages)
    """

    def __init__(self, field_schema: FieldSchema):
        self._schema = field_schema

    def validate(self, value: Any) -> ValidationResult:
        """Validate a value."""
        return self._schema.validate(value)

    def is_valid(self, value: Any) -> bool:
        """Quick check if value is valid."""
        return self.validate(value).valid

    # Factory methods

    @classmethod
    def string(
        cls,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        enum: list[str] | None = None,
        nullable: bool = False,
        required: bool = False,
    ) -> "Schema":
        """Create a string schema."""
        constraints = []
        if min_length is not None:
            constraints.append(MinLengthConstraint(min_length))
        if max_length is not None:
            constraints.append(MaxLengthConstraint(max_length))
        if pattern is not None:
            constraints.append(PatternConstraint(pattern))
        if enum is not None:
            constraints.append(EnumConstraint(enum))

        return cls(FieldSchema(
            type=SchemaType.STRING,
            nullable=nullable,
            required=required,
            constraints=constraints,
        ))

    @classmethod
    def integer(
        cls,
        minimum: int | None = None,
        maximum: int | None = None,
        enum: list[int] | None = None,
        nullable: bool = False,
        required: bool = False,
    ) -> "Schema":
        """Create an integer schema."""
        constraints = []
        if minimum is not None:
            constraints.append(MinValueConstraint(minimum))
        if maximum is not None:
            constraints.append(MaxValueConstraint(maximum))
        if enum is not None:
            constraints.append(EnumConstraint(enum))

        return cls(FieldSchema(
            type=SchemaType.INTEGER,
            nullable=nullable,
            required=required,
            constraints=constraints,
        ))

    @classmethod
    def number(
        cls,
        minimum: float | None = None,
        maximum: float | None = None,
        nullable: bool = False,
        required: bool = False,
    ) -> "Schema":
        """Create a number schema."""
        constraints = []
        if minimum is not None:
            constraints.append(MinValueConstraint(minimum))
        if maximum is not None:
            constraints.append(MaxValueConstraint(maximum))

        return cls(FieldSchema(
            type=SchemaType.NUMBER,
            nullable=nullable,
            required=required,
            constraints=constraints,
        ))

    @classmethod
    def boolean(cls, nullable: bool = False, required: bool = False) -> "Schema":
        """Create a boolean schema."""
        return cls(FieldSchema(
            type=SchemaType.BOOLEAN,
            nullable=nullable,
            required=required,
        ))

    @classmethod
    def array(
        cls,
        items: Optional["Schema"] = None,
        min_items: int | None = None,
        max_items: int | None = None,
        nullable: bool = False,
        required: bool = False,
    ) -> "Schema":
        """Create an array schema."""
        constraints = []
        if min_items is not None:
            constraints.append(MinLengthConstraint(min_items))
        if max_items is not None:
            constraints.append(MaxLengthConstraint(max_items))

        return cls(FieldSchema(
            type=SchemaType.ARRAY,
            nullable=nullable,
            required=required,
            constraints=constraints,
            items=items._schema if items else None,
        ))

    @classmethod
    def object(
        cls,
        properties: dict[str, "Schema"] | None = None,
        required: list[str] | None = None,
        nullable: bool = False,
        allow_additional: bool = True,
    ) -> "Schema":
        """Create an object schema."""
        prop_schemas = {}
        if properties:
            for name, schema in properties.items():
                prop_schemas[name] = schema._schema
                if required and name in required:
                    prop_schemas[name].required = True

        return cls(FieldSchema(
            type=SchemaType.OBJECT,
            nullable=nullable,
            properties=prop_schemas,
        ))

    @classmethod
    def any(cls, nullable: bool = True) -> "Schema":
        """Create an any schema."""
        return cls(FieldSchema(
            type=SchemaType.ANY,
            nullable=nullable,
        ))


def validate(data: Any, schema: Schema) -> ValidationResult:
    """Validate data against a schema."""
    return schema.validate(data)


def is_valid(data: Any, schema: Schema) -> bool:
    """Check if data is valid against schema."""
    return schema.is_valid(data)


# Common schemas
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
URL_PATTERN = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


def email_schema(required: bool = False) -> Schema:
    """Create an email schema."""
    return Schema.string(pattern=EMAIL_PATTERN, required=required)


def url_schema(required: bool = False) -> Schema:
    """Create a URL schema."""
    return Schema.string(pattern=URL_PATTERN, required=required)


def uuid_schema(required: bool = False) -> Schema:
    """Create a UUID schema."""
    return Schema.string(pattern=UUID_PATTERN, required=required)


__all__ = [
    # Enums
    "SchemaType",
    # Data classes
    "ValidationError",
    "ValidationResult",
    "FieldSchema",
    # Constraints
    "Constraint",
    "TypeConstraint",
    "MinLengthConstraint",
    "MaxLengthConstraint",
    "MinValueConstraint",
    "MaxValueConstraint",
    "PatternConstraint",
    "EnumConstraint",
    "RequiredConstraint",
    # Main class
    "Schema",
    # Functions
    "validate",
    "is_valid",
    # Common schemas
    "email_schema",
    "url_schema",
    "uuid_schema",
    # Patterns
    "EMAIL_PATTERN",
    "URL_PATTERN",
    "UUID_PATTERN",
]
