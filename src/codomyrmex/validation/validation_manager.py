"""
Validation manager for registering and managing validators.
"""

from typing import Any, Callable, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from .validator import ValidationError, ValidationResult, Validator

logger = get_logger(__name__)


class ValidationManager:
    """Manager for validation operations and custom validators."""

    def __init__(self):
        """Initialize validation manager."""
        self._validators: dict[str, Callable] = {}
        self._default_validator = Validator()

    def register_validator(self, name: str, validator: Callable) -> None:
        """Register a custom validator function.

        Args:
            name: Validator name
            validator: Validator function that takes (data, schema) and returns ValidationResult or bool
        """
        self._validators[name] = validator
        logger.info(f"Registered custom validator: {name}")

    def get_validator(self, name: str) -> Optional[Callable]:
        """Get a registered validator.

        Args:
            name: Validator name

        Returns:
            Validator function if found, None otherwise
        """
        return self._validators.get(name)

    def validate(self, data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult:
        """Validate data against a schema.

        Args:
            data: Data to validate
            schema: Validation schema
            validator_type: Type of validator to use

        Returns:
            ValidationResult
        """
        if validator_type in self._validators:
            validator_func = self._validators[validator_type]
            validator = Validator(validator_type="custom")
            return validator._validate_custom(data, lambda d: validator_func(d, schema))
        else:
            validator = Validator(validator_type=validator_type)
            return validator.validate(data, schema)

