"""
Input/output validation for tool calls.

Provides JSON-schema-like validation for tool inputs and outputs,
ensuring data conforms to expected types and required fields before
and after tool execution.
"""

from dataclasses import dataclass, field
from typing import Any

# JSON-schema type name -> Python types mapping
_TYPE_MAP: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "integer": (int,),
    "number": (int, float),
    "boolean": (bool,),
    "array": (list,),
    "object": (dict,),
    "null": (type(None),),
}


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Attributes:
        valid: Whether the data passed all validation checks.
        errors: List of human-readable error descriptions.
    """

    valid: bool = True
    errors: list[str] = field(default_factory=list)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another ValidationResult into this one."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
        )

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "valid": self.valid,
            "errors": self.errors,
        }


def _validate_value(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    """
    Recursively validate a single value against a schema node.

    Returns a list of error strings (empty means valid).
    """
    errors: list[str] = []

    # --- type check ---
    expected_type = schema.get("type")
    if expected_type is not None:
        # Handle union types (e.g. ["string", "null"])
        if isinstance(expected_type, list):
            type_names = expected_type
        else:
            type_names = [expected_type]

        allowed_python_types: list[type] = []
        for tn in type_names:
            allowed_python_types.extend(_TYPE_MAP.get(tn, ()))

        if allowed_python_types and not isinstance(value, tuple(allowed_python_types)):
            actual = type(value).__name__
            errors.append(
                f"{path}: expected type {expected_type}, got {actual}"
            )
            # If the type is wrong, skip deeper checks that depend on it
            return errors

    # --- enum check ---
    enum_values = schema.get("enum")
    if enum_values is not None and value not in enum_values:
        errors.append(f"{path}: value {value!r} not in enum {enum_values}")

    # --- string constraints ---
    if isinstance(value, str):
        min_len = schema.get("minLength")
        if min_len is not None and len(value) < min_len:
            errors.append(f"{path}: string length {len(value)} < minLength {min_len}")
        max_len = schema.get("maxLength")
        if max_len is not None and len(value) > max_len:
            errors.append(f"{path}: string length {len(value)} > maxLength {max_len}")

    # --- numeric constraints ---
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{path}: value {value} < minimum {minimum}")
        maximum = schema.get("maximum")
        if maximum is not None and value > maximum:
            errors.append(f"{path}: value {value} > maximum {maximum}")

    # --- array constraints ---
    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            errors.append(f"{path}: array length {len(value)} < minItems {min_items}")
        max_items = schema.get("maxItems")
        if max_items is not None and len(value) > max_items:
            errors.append(f"{path}: array length {len(value)} > maxItems {max_items}")

        items_schema = schema.get("items")
        if items_schema is not None:
            for i, item in enumerate(value):
                errors.extend(_validate_value(item, items_schema, f"{path}[{i}]"))

    # --- object constraints (nested properties) ---
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        # Check required fields are present
        for req in required_fields:
            if req not in value:
                errors.append(f"{path}.{req}: required field missing")

        # Validate each declared property that exists in the data
        for prop_name, prop_schema in properties.items():
            if prop_name in value:
                errors.extend(
                    _validate_value(value[prop_name], prop_schema, f"{path}.{prop_name}")
                )

        # Check additionalProperties constraint
        additional = schema.get("additionalProperties")
        if additional is False:
            extra_keys = set(value.keys()) - set(properties.keys())
            for key in sorted(extra_keys):
                errors.append(f"{path}.{key}: additional property not allowed")

    return errors


def validate_input(data: Any, schema: dict[str, Any]) -> ValidationResult:
    """
    Validate tool input data against a JSON-schema-like specification.

    Args:
        data: The input data to validate (typically a dict).
        schema: A JSON-schema-like dict describing expected structure.
            Supported keywords: type, required, properties, items,
            enum, minimum, maximum, minLength, maxLength, minItems,
            maxItems, additionalProperties.

    Returns:
        ValidationResult with valid=True if data conforms, or
        valid=False with descriptive error messages.

    Example schema::

        {
            "type": "object",
            "required": ["name", "count"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "count": {"type": "integer", "minimum": 0},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    """
    if not schema:
        return ValidationResult(valid=True)

    errors = _validate_value(data, schema, "$")
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_output(data: Any, schema: dict[str, Any]) -> ValidationResult:
    """
    Validate tool output data against a JSON-schema-like specification.

    Uses the same validation logic as validate_input. Separated as a
    distinct function so callers can distinguish input vs output
    validation in error reporting and so each can be extended
    independently in the future.

    Args:
        data: The output data to validate.
        schema: A JSON-schema-like dict describing expected structure.

    Returns:
        ValidationResult with valid=True if data conforms.
    """
    if not schema:
        return ValidationResult(valid=True)

    errors = _validate_value(data, schema, "$")
    return ValidationResult(valid=len(errors) == 0, errors=errors)


__all__ = [
    "ValidationResult",
    "validate_input",
    "validate_output",
]
