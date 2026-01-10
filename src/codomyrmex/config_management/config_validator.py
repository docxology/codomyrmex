from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import logging
import re

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger







"""Configuration Validator for Codomyrmex."""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    field_path: str
    message: str
    severity: ValidationSeverity
    suggestion: Optional[str] = None
    actual_value: Any = None
    expected_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "field_path": self.field_path,
            "message": self.message,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value
        }

@dataclass
class ValidationResult:
    """Result of a configuration validation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.errors.append(issue)
            self.is_valid = False
        elif issue.severity == ValidationSeverity.WARNING:
            self.warnings.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "total_issues": len(self.issues),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "issues": [issue.to_dict() for issue in self.issues]
        }

@dataclass
class ConfigSchema:
    """Schema definition for configuration validation."""
    type: str
    required: bool = False
    default: Any = None
    description: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)
    nested_schema: Optional[Dict[str, 'ConfigSchema']] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "type": self.type,
            "required": self.required,
            "description": self.description,
            "constraints": self.constraints
        }
        if self.default is not None:
            result["default"] = self.default
        if self.nested_schema:
            result["nested_schema"] = {k: v.to_dict() for k, v in self.nested_schema.items()}
        return result

class ConfigValidator:
    """
    Advanced configuration validator with schema support.

    Provides comprehensive validation including type checking, constraint validation,
    required field checking, and detailed error reporting with suggestions.
    """

    def __init__(self, schema: Optional[Dict[str, ConfigSchema]] = None):
        """
        Initialize the configuration validator.

        Args:
            schema: Configuration schema for validation
        """
        self.schema = schema or {}
        self.custom_validators: Dict[str, Callable] = {}

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate a configuration against the schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            ValidationResult with detailed issues and status
        """
        result = ValidationResult(is_valid=True)

        # Validate against schema
        if self.schema:
            result = self._validate_against_schema(config, self.schema, "")

        # Run custom validators
        for validator_name, validator_func in self.custom_validators.items():
            try:
                custom_result = validator_func(config)
                if isinstance(custom_result, ValidationResult):
                    # Merge results
                    result.issues.extend(custom_result.issues)
                    result.errors.extend(custom_result.errors)
                    result.warnings.extend(custom_result.warnings)
                    if not custom_result.is_valid:
                        result.is_valid = False
                elif isinstance(custom_result, list):
                    # List of issues
                    for issue in custom_result:
                        if isinstance(issue, ValidationIssue):
                            result.add_issue(issue)
            except Exception as e:
                logger.error(f"Custom validator '{validator_name}' failed: {e}")
                result.add_issue(ValidationIssue(
                    field_path="",
                    message=f"Custom validator '{validator_name}' failed: {e}",
                    severity=ValidationSeverity.ERROR
                ))

        return result

    def validate_required_fields(self, config: Dict[str, Any], required: List[str]) -> List[str]:
        """
        Validate that required fields are present.

        Args:
            config: Configuration dictionary
            required: List of required field names

        Returns:
            List of missing field names
        """
        missing = []
        for field in required:
            if field not in config or config[field] is None:
                missing.append(field)
        return missing

    def validate_types(self, config: Dict[str, Any], schema: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate types of configuration values.

        Args:
            config: Configuration dictionary
            schema: Type schema dictionary

        Returns:
            List of validation issues
        """
        issues = []

        for field, expected_type in schema.items():
            if field in config:
                actual_value = config[field]
                if not self._check_type(actual_value, expected_type):
                    issues.append(ValidationIssue(
                        field_path=field,
                        message=f"Type mismatch for '{field}': expected {expected_type}, got {type(actual_value).__name__}",
                        severity=ValidationSeverity.ERROR,
                        actual_value=type(actual_value).__name__,
                        expected_value=expected_type,
                        suggestion=f"Convert value to {expected_type}"
                    ))

        return issues

    def validate_values(self, config: Dict[str, Any], constraints: Dict[str, Dict[str, Any]]) -> List[ValidationIssue]:
        """
        Validate configuration values against constraints.

        Args:
            config: Configuration dictionary
            constraints: Constraint dictionary mapping fields to constraint rules

        Returns:
            List of validation issues
        """
        issues = []

        for field, field_constraints in constraints.items():
            if field in config:
                value = config[field]
                field_issues = self._validate_field_constraints(field, value, field_constraints)
                issues.extend(field_issues)

        return issues

    def add_custom_validator(self, name: str, validator: Callable[[Dict[str, Any]], Union[ValidationResult, List[ValidationIssue]]]) -> None:
        """
        Add a custom validation function.

        Args:
            name: Name of the validator
            validator: Function that takes config and returns ValidationResult or list of ValidationIssue
        """
        self.custom_validators[name] = validator

    def _validate_against_schema(self, config: Dict[str, Any], schema: Dict[str, ConfigSchema], path: str) -> ValidationResult:
        """Validate configuration against a schema."""
        result = ValidationResult(is_valid=True)

        # Check required fields
        for field_name, field_schema in schema.items():
            field_path = f"{path}.{field_name}" if path else field_name

            if field_schema.required and field_name not in config:
                result.add_issue(ValidationIssue(
                    field_path=field_path,
                    message=f"Required field '{field_name}' is missing",
                    severity=ValidationSeverity.ERROR,
                    suggestion=f"Add '{field_name}' to configuration"
                ))
                continue

            if field_name in config:
                value = config[field_name]
                issues = self._validate_field_schema(field_name, value, field_schema, field_path)
                for issue in issues:
                    result.add_issue(issue)

        # Check for unknown fields
        for field_name in config:
            if field_name not in schema:
                field_path = f"{path}.{field_name}" if path else field_name
                result.add_issue(ValidationIssue(
                    field_path=field_path,
                    message=f"Unknown field '{field_name}' not defined in schema",
                    severity=ValidationSeverity.WARNING,
                    suggestion="Remove unknown field or add to schema"
                ))

        return result

    def _validate_field_schema(self, field_name: str, value: Any, schema: ConfigSchema, path: str) -> List[ValidationIssue]:
        """Validate a single field against its schema."""
        issues = []

        # Type validation
        if not self._check_type(value, schema.type):
            issues.append(ValidationIssue(
                field_path=path,
                message=f"Type mismatch for '{field_name}': expected {schema.type}, got {type(value).__name__}",
                severity=ValidationSeverity.ERROR,
                actual_value=type(value).__name__,
                expected_value=schema.type
            ))
            return issues  # Don't continue if type is wrong

        # Constraint validation
        if schema.constraints:
            constraint_issues = self._validate_field_constraints(path, value, schema.constraints)
            issues.extend(constraint_issues)

        # Nested schema validation
        if schema.nested_schema and isinstance(value, dict):
            nested_result = self._validate_against_schema(value, schema.nested_schema, path)
            issues.extend(nested_result.issues)

        return issues

    def _validate_field_constraints(self, field_path: str, value: Any, constraints: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate field value against constraints."""
        issues = []

        for constraint_name, constraint_value in constraints.items():
            if constraint_name == "min":
                if isinstance(value, (int, float)) and value < constraint_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Value {value} is below minimum {constraint_value}",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Increase value to at least {constraint_value}"
                    ))

            elif constraint_name == "max":
                if isinstance(value, (int, float)) and value > constraint_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Value {value} is above maximum {constraint_value}",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Decrease value to at most {constraint_value}"
                    ))

            elif constraint_name == "min_length":
                if isinstance(value, (str, list)) and len(value) < constraint_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Length {len(value)} is below minimum {constraint_value}",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Add more items to reach length {constraint_value}"
                    ))

            elif constraint_name == "max_length":
                if isinstance(value, (str, list)) and len(value) > constraint_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Length {len(value)} exceeds maximum {constraint_value}",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Remove items to reduce length to {constraint_value}"
                    ))

            elif constraint_name == "pattern":
                if isinstance(value, str) and not re.match(constraint_value, value):
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Value does not match required pattern",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Value must match pattern: {constraint_value}"
                    ))

            elif constraint_name == "enum":
                if isinstance(constraint_value, list) and value not in constraint_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        message=f"Value '{value}' not in allowed values: {constraint_value}",
                        severity=ValidationSeverity.ERROR,
                        suggestion=f"Choose from: {', '.join(str(v) for v in constraint_value)}"
                    ))

            elif constraint_name == "custom":
                # Custom constraint function
                if callable(constraint_value):
                    try:
                        custom_result = constraint_value(value)
                        if not custom_result:
                            issues.append(ValidationIssue(
                                field_path=field_path,
                                message=f"Custom constraint failed for value: {value}",
                                severity=ValidationSeverity.ERROR
                            ))
                    except Exception as e:
                        issues.append(ValidationIssue(
                            field_path=field_path,
                            message=f"Custom constraint error: {e}",
                            severity=ValidationSeverity.ERROR
                        ))

        return issues

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "any": lambda x: True  # Accept any type
        }

        type_checker = type_map.get(expected_type)
        if type_checker:
            if callable(type_checker):
                return type_checker(value)
            else:
                return isinstance(value, type_checker)

        return False

# Predefined schemas for common Codomyrmex configurations

def get_logging_config_schema() -> Dict[str, ConfigSchema]:
    """Get schema for logging configuration."""
    return {
        "level": ConfigSchema(
            type="str",
            required=False,
            default="INFO",
            constraints={"enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
        ),
        "format": ConfigSchema(
            type="str",
            required=False,
            default="TEXT",
            constraints={"enum": ["TEXT", "JSON"]}
        ),
        "file": ConfigSchema(
            type="str",
            required=False,
            constraints={"pattern": r"^/.*|\./.*|\.\./.*"}  # Path pattern
        ),
        "max_file_size": ConfigSchema(
            type="int",
            required=False,
            default=10485760,  # 10MB
            constraints={"min": 1024, "max": 1073741824}  # 1KB to 1GB
        )
    }

def get_database_config_schema() -> Dict[str, ConfigSchema]:
    """Get schema for database configuration."""
    return {
        "host": ConfigSchema(type="str", required=True),
        "port": ConfigSchema(type="int", required=False, default=5432, constraints={"min": 1, "max": 65535}),
        "database": ConfigSchema(type="str", required=True),
        "username": ConfigSchema(type="str", required=True),
        "password": ConfigSchema(type="str", required=True),
        "ssl_mode": ConfigSchema(
            type="str",
            required=False,
            default="require",
            constraints={"enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]}
        ),
        "connection_pool": ConfigSchema(
            type="dict",
            required=False,
            nested_schema={
                "min_connections": ConfigSchema(type="int", required=False, default=1, constraints={"min": 1}),
                "max_connections": ConfigSchema(type="int", required=False, default=10, constraints={"min": 1, "max": 100}),
                "connection_timeout": ConfigSchema(type="float", required=False, default=30.0, constraints={"min": 1.0})
            }
        )
    }

def get_ai_model_config_schema() -> Dict[str, ConfigSchema]:
    """Get schema for AI model configuration."""
    return {
        "provider": ConfigSchema(
            type="str",
            required=True,
            constraints={"enum": ["openai", "anthropic", "ollama", "huggingface"]}
        ),
        "model": ConfigSchema(type="str", required=True),
        "api_key": ConfigSchema(type="str", required=False),  # May come from env
        "temperature": ConfigSchema(type="float", required=False, default=0.7, constraints={"min": 0.0, "max": 2.0}),
        "max_tokens": ConfigSchema(type="int", required=False, default=1000, constraints={"min": 1, "max": 32768}),
        "timeout": ConfigSchema(type="float", required=False, default=60.0, constraints={"min": 1.0}),
        "retry_config": ConfigSchema(
            type="dict",
            required=False,
            nested_schema={
                "max_retries": ConfigSchema(type="int", required=False, default=3, constraints={"min": 0, "max": 10}),
                "backoff_factor": ConfigSchema(type="float", required=False, default=2.0, constraints={"min": 1.0}),
                "retry_on_timeout": ConfigSchema(type="bool", required=False, default=True)
            }
        )
    }

# Convenience functions

def validate_config_schema(config: Dict[str, Any], schema: Dict[str, ConfigSchema]) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate config against schema.

    Args:
        config: Configuration to validate
        schema: Schema to validate against

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    validator = ConfigValidator(schema)
    result = validator.validate(config)

    errors = [issue.message for issue in result.errors]
    return result.is_valid, errors
