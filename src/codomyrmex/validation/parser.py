"""Type-safe parser for validated data conversion."""

from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class TypeSafeParser:
    """Parses and validates data into Pydantic models."""

    @staticmethod
    def parse_as(model: type[T], data: Any) -> T | None:
        """Attempt to parse data into a specific model."""
        try:
            return model.model_validate(data)
        except PydanticValidationError as e:
            logger.warning("Failed to parse data as %s: %s", model.__name__, e)
            return None

    @staticmethod
    def parse_dict(model: type[T], data: dict[str, Any]) -> T:
        """Parse dictionary and raise error if invalid."""
        return model.model_validate(data)
