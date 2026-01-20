"""Type-safe parser for validated data conversion."""

from typing import Any, Dict, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)

class TypeSafeParser:
    """Parses and validates data into Pydantic models."""
    
    @staticmethod
    def parse_as(model: Type[T], data: Any) -> Optional[T]:
        """Attempt to parse data into a specific model."""
        try:
            return model.model_validate(data)
        except PydanticValidationError:
            return None

    @staticmethod
    def parse_dict(model: Type[T], data: Dict[str, Any]) -> T:
        """Parse dictionary and raise error if invalid."""
        return model.model_validate(data)
