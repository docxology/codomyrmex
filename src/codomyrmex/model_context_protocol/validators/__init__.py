"""
MCP Schema Validators Module

Provides validation utilities for MCP messages, tool specifications,
and runtime tool calls.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Execute   Bool   operations natively."""
        return self.valid


class SchemaValidator:
    """
    Validates data against JSON Schema.
    """

    def __init__(self, schema: dict[str, Any]):
        """Execute   Init   operations natively."""
        self.schema = schema

    def validate(self, data: Any) -> ValidationResult:
        """Validate data against the schema."""
        errors: list[str] = []
        warnings: list[str] = []

        schema_type = self.schema.get("type")

        if schema_type == "object":
            if not isinstance(data, dict):
                errors.append(f"Expected object, got {type(data).__name__}")
            else:
                errors.extend(self._validate_object(data))
        elif schema_type == "array":
            if not isinstance(data, list):
                errors.append(f"Expected array, got {type(data).__name__}")
            else:
                errors.extend(self._validate_array(data))
        elif schema_type == "string":
            if not isinstance(data, str):
                errors.append(f"Expected string, got {type(data).__name__}")
        elif schema_type == "integer":
            if not isinstance(data, int) or isinstance(data, bool):
                errors.append(f"Expected integer, got {type(data).__name__}")
        elif schema_type == "number":
            if not isinstance(data, (int, float)) or isinstance(data, bool):
                errors.append(f"Expected number, got {type(data).__name__}")
        elif schema_type == "boolean":
            if not isinstance(data, bool):
                errors.append(f"Expected boolean, got {type(data).__name__}")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _validate_object(self, data: dict[str, Any]) -> list[str]:
        """Validate object properties."""
        errors = []

        properties = self.schema.get("properties", {})
        required = self.schema.get("required", [])

        # Check required fields
        for req in required:
            if req not in data:
                errors.append(f"Missing required field: {req}")

        # Validate each property
        for prop, value in data.items():
            if prop in properties:
                prop_schema = properties[prop]
                prop_validator = SchemaValidator(prop_schema)
                result = prop_validator.validate(value)
                for err in result.errors:
                    errors.append(f"{prop}: {err}")

        return errors

    def _validate_array(self, data: list[Any]) -> list[str]:
        """Validate array items."""
        errors = []

        items_schema = self.schema.get("items")
        if items_schema:
            item_validator = SchemaValidator(items_schema)
            for i, item in enumerate(data):
                result = item_validator.validate(item)
                for err in result.errors:
                    errors.append(f"[{i}]: {err}")

        return errors


class ToolCallValidator:
    """
    Validates MCP tool calls.
    """

    def __init__(self, tool_schemas: dict[str, dict[str, Any]]):
        """
        Args:
            tool_schemas: Dict mapping tool names to their input schemas
        """
        self.tool_schemas = tool_schemas

    def validate_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ValidationResult:
        """Validate a tool call."""
        errors: list[str] = []
        warnings: list[str] = []

        # Check tool exists
        if tool_name not in self.tool_schemas:
            return ValidationResult(
                valid=False,
                errors=[f"Unknown tool: {tool_name}"],
            )

        # Validate arguments against schema
        schema = self.tool_schemas[tool_name]
        validator = SchemaValidator(schema)
        result = validator.validate(arguments)

        return result

    def validate_result(
        self,
        result: dict[str, Any],
    ) -> ValidationResult:
        """Validate a tool result."""
        errors = []
        warnings = []

        # Check required fields
        if "status" not in result:
            errors.append("Missing required field: status")
        else:
            status = result["status"]
            if status not in ["success", "failure", "partial"]:
                warnings.append(f"Non-standard status: {status}")

            # Validation logic
            if "fail" in str(status).lower():
                if "error" not in result or result["error"] is None:
                    errors.append("Error field required on failure")
                if "data" in result and result["data"] is not None:
                    warnings.append("Data should be null on failure")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


class MessageValidator:
    """
    Validates MCP JSON-RPC messages.
    """

    JSONRPC_VERSION = "2.0"

    def validate_request(self, message: dict[str, Any]) -> ValidationResult:
        """Validate a JSON-RPC request."""
        errors = []
        warnings: list[str] = []

        # Check jsonrpc version
        if message.get("jsonrpc") != self.JSONRPC_VERSION:
            errors.append(f"Invalid jsonrpc version: {message.get('jsonrpc')}")

        # Check method
        if "method" not in message:
            errors.append("Missing required field: method")
        elif not isinstance(message["method"], str):
            errors.append("method must be a string")

        # Check id (required for requests, absent for notifications)
        if "id" in message:
            if not isinstance(message["id"], (str, int, type(None))):
                errors.append("id must be string, number, or null")

        # Check params if present
        if "params" in message:
            params = message["params"]
            if not isinstance(params, (dict, list)):
                errors.append("params must be object or array")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_response(self, message: dict[str, Any]) -> ValidationResult:
        """Validate a JSON-RPC response."""
        errors = []
        warnings: list[str] = []

        # Check jsonrpc version
        if message.get("jsonrpc") != self.JSONRPC_VERSION:
            errors.append(f"Invalid jsonrpc version: {message.get('jsonrpc')}")

        # Check id
        if "id" not in message:
            errors.append("Missing required field: id")

        # Must have either result or error, not both
        has_result = "result" in message
        has_error = "error" in message

        if has_result and has_error:
            errors.append("Response cannot have both result and error")
        elif not has_result and not has_error:
            errors.append("Response must have either result or error")

        # Validate error structure
        if has_error:
            error = message["error"]
            if not isinstance(error, dict):
                errors.append("error must be an object")
            else:
                if "code" not in error:
                    errors.append("error.code is required")
                elif not isinstance(error["code"], int):
                    errors.append("error.code must be an integer")

                if "message" not in error:
                    errors.append("error.message is required")
                elif not isinstance(error["message"], str):
                    errors.append("error.message must be a string")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


class SpecificationValidator:
    """
    Validates MCP_TOOL_SPECIFICATION.md files.
    """

    REQUIRED_SECTIONS = [
        "description",
        "invocation name",
        "input schema",
        "output schema",
    ]

    def validate_spec_file(self, content: str) -> ValidationResult:
        """Validate specification file content."""
        errors: list[str] = []
        warnings: list[str] = []

        content_lower = content.lower()

        # Check for required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in content_lower:
                warnings.append(f"Missing recommended section: {section}")

        # Check for tool definitions
        if "## " not in content:
            warnings.append("No tool definitions found (expected ## headers)")

        # Check for JSON Schema examples
        if "```json" not in content:
            warnings.append("No JSON examples found (recommended for schemas)")

        # Check for security considerations
        if "security" not in content_lower:
            warnings.append("Missing security considerations section")

        return ValidationResult(valid=True, errors=errors, warnings=warnings)


def validate_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
) -> ValidationResult:
    """Convenience function to validate a tool call."""
    validator = ToolCallValidator(schemas)
    return validator.validate_call(tool_name, arguments)


def validate_message(
    message: dict[str, Any],
    message_type: str = "request",
) -> ValidationResult:
    """Convenience function to validate a message."""
    validator = MessageValidator()
    if message_type == "request":
        return validator.validate_request(message)
    else:
        return validator.validate_response(message)


__all__ = [
    "ValidationResult",
    "SchemaValidator",
    "ToolCallValidator",
    "MessageValidator",
    "SpecificationValidator",
    "validate_tool_call",
    "validate_message",
]
