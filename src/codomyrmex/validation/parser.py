"""Type-safe parser for validated data conversion."""

from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)

class TypeSafeParser:
    """Parses and validates data into Pydantic models."""

    @staticmethod
    def parse_as(model: type[T], data: Any) -> T | None:
        """Attempt to parse data into a specific model."""
        try:
            return model.model_validate(data)
        except PydanticValidationError:
            return None

    @staticmethod
    def parse_dict(model: type[T], data: dict[str, Any]) -> T:
        """Parse dictionary and raise error if invalid."""
        return model.model_validate(data)
