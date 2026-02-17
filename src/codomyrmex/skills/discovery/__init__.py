"""
Skill discovery and registration utilities.

Provides mechanisms for discovering and registering agent skills.
"""

import hashlib
import inspect
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SkillCategory(Enum):
    """Categories of skills."""
    CODE = "code"
    DATA = "data"
    WEB = "web"
    FILE = "file"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    REASONING = "reasoning"
    UTILITY = "utility"


@dataclass
class ParameterSchema:
    """Schema for a skill parameter."""
    name: str
    param_type: str  # string, int, float, bool, list, dict
    description: str
    required: bool = True
    default: Any = None
    enum_values: list[Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "name": self.name,
            "type": self.param_type,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.enum_values:
            result["enum"] = self.enum_values
        return result


@dataclass
class SkillMetadata:
    """Metadata for a skill."""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    category: SkillCategory = SkillCategory.UTILITY
    tags: list[str] = field(default_factory=list)
    parameters: list[ParameterSchema] = field(default_factory=list)
    returns: str | None = None
    examples: list[dict[str, Any]] = field(default_factory=list)
    author: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "tags": self.tags,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns,
            "examples": self.examples,
            "author": self.author,
            "enabled": self.enabled,
        }

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON schema format for LLM tool calling."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.param_type,
                "description": param.description,
            }
            if param.enum_values:
                properties[param.name]["enum"] = param.enum_values
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


class Skill(ABC):
    """Abstract base class for skills."""

    metadata: SkillMetadata

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters."""
        pass

    def validate_params(self, **kwargs) -> list[str]:
        """Validate parameters against schema."""
        errors = []

        for param in self.metadata.parameters:
            if param.required and param.name not in kwargs:
                if param.default is None:
                    errors.append(f"Missing required parameter: {param.name}")

        return errors


class FunctionSkill(Skill):
    """Skill wrapping a function."""

    def __init__(
        self,
        func: Callable,
        metadata: SkillMetadata | None = None,
    ):
        self.func = func

        if metadata:
            self.metadata = metadata
        else:
            self.metadata = self._infer_metadata(func)

    def _infer_metadata(self, func: Callable) -> SkillMetadata:
        """Infer metadata from function signature and docstring."""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""

        # Parse parameters
        parameters = []
        type_hints = {}
        try:
            type_hints = func.__annotations__
        except AttributeError:
            pass

        for name, param in sig.parameters.items():
            if name in ('self', 'cls'):
                continue

            param_type = "string"
            if name in type_hints:
                hint = type_hints[name]
                if hint is int:
                    param_type = "integer"
                elif hint is float:
                    param_type = "number"
                elif hint is bool:
                    param_type = "boolean"
                elif hint is list:
                    param_type = "array"
                elif hint is dict:
                    param_type = "object"

            parameters.append(ParameterSchema(
                name=name,
                param_type=param_type,
                description=f"Parameter: {name}",
                required=param.default == inspect.Parameter.empty,
                default=None if param.default == inspect.Parameter.empty else param.default,
            ))

        # Generate ID from function name
        skill_id = hashlib.md5(f"{func.__module__}.{func.__name__}".encode()).hexdigest()[:12]

        return SkillMetadata(
            id=skill_id,
            name=func.__name__,
            description=doc.split('\n')[0] if doc else f"Skill: {func.__name__}",
            parameters=parameters,
        )

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)


class SkillRegistry:
    """Registry for managing skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._by_category: dict[SkillCategory, list[str]] = {}
        self._by_tag: dict[str, list[str]] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        skill_id = skill.metadata.id
        self._skills[skill_id] = skill

        # Index by category
        category = skill.metadata.category
        if category not in self._by_category:
            self._by_category[category] = []
        self._by_category[category].append(skill_id)

        # Index by tags
        for tag in skill.metadata.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(skill_id)

    def unregister(self, skill_id: str) -> None:
        """Unregister a skill."""
        if skill_id in self._skills:
            skill = self._skills[skill_id]

            # Remove from category index
            category = skill.metadata.category
            if category in self._by_category:
                self._by_category[category].remove(skill_id)

            # Remove from tag index
            for tag in skill.metadata.tags:
                if tag in self._by_tag:
                    self._by_tag[tag].remove(skill_id)

            del self._skills[skill_id]

    def get(self, skill_id: str) -> Skill | None:
        """Get a skill by ID."""
        return self._skills.get(skill_id)

    def get_by_name(self, name: str) -> Skill | None:
        """Get a skill by name."""
        for skill in self._skills.values():
            if skill.metadata.name == name:
                return skill
        return None

    def search(
        self,
        query: str | None = None,
        category: SkillCategory | None = None,
        tags: list[str] | None = None,
        enabled_only: bool = True,
    ) -> list[Skill]:
        """Search for skills."""
        results = list(self._skills.values())

        if enabled_only:
            results = [s for s in results if s.metadata.enabled]

        if category:
            category_ids = set(self._by_category.get(category, []))
            results = [s for s in results if s.metadata.id in category_ids]

        if tags:
            tag_ids = set()
            for tag in tags:
                tag_ids.update(self._by_tag.get(tag, []))
            results = [s for s in results if s.metadata.id in tag_ids]

        if query:
            query = query.lower()
            results = [
                s for s in results
                if query in s.metadata.name.lower() or
                   query in s.metadata.description.lower()
            ]

        return results

    def list_all(self) -> list[SkillMetadata]:
        """List all skill metadata."""
        return [s.metadata for s in self._skills.values()]

    def execute(self, skill_id: str, **kwargs) -> Any:
        """Execute a skill by ID."""
        skill = self.get(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        errors = skill.validate_params(**kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        return skill.execute(**kwargs)


def skill(
    name: str | None = None,
    description: str | None = None,
    category: SkillCategory = SkillCategory.UTILITY,
    tags: list[str] | None = None,
    registry: SkillRegistry | None = None,
):
    """Decorator to create a skill from a function."""
    def decorator(func: Callable) -> FunctionSkill:
        # Create skill
        skill_obj = FunctionSkill(func)

        # Override metadata if provided
        if name:
            skill_obj.metadata.name = name
        if description:
            skill_obj.metadata.description = description
        skill_obj.metadata.category = category
        if tags:
            skill_obj.metadata.tags = tags

        # Register if registry provided
        if registry:
            registry.register(skill_obj)

        return skill_obj

    return decorator


class SkillDiscoverer:
    """Discovers skills from modules and packages."""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def discover_from_module(self, module) -> list[Skill]:
        """Discover skills from a module."""
        discovered = []

        for name in dir(module):
            obj = getattr(module, name)

            if isinstance(obj, Skill):
                self.registry.register(obj)
                discovered.append(obj)
            elif isinstance(obj, type) and issubclass(obj, Skill) and obj != Skill:
                try:
                    instance = obj()
                    self.registry.register(instance)
                    discovered.append(instance)
                except TypeError:
                    pass

        return discovered

    def discover_from_decorated(self, module) -> list[Skill]:
        """Discover skills that were decorated with @skill."""
        discovered = []

        for name in dir(module):
            obj = getattr(module, name)

            if isinstance(obj, FunctionSkill):
                self.registry.register(obj)
                discovered.append(obj)

        return discovered


# Global registry
DEFAULT_REGISTRY = SkillRegistry()


def register_skill(skill: Skill) -> None:
    """Register a skill in the default registry."""
    DEFAULT_REGISTRY.register(skill)


def get_skill(skill_id: str) -> Skill | None:
    """Get a skill from the default registry."""
    return DEFAULT_REGISTRY.get(skill_id)


__all__ = [
    "SkillCategory",
    "ParameterSchema",
    "SkillMetadata",
    "Skill",
    "FunctionSkill",
    "SkillRegistry",
    "skill",
    "SkillDiscoverer",
    "DEFAULT_REGISTRY",
    "register_skill",
    "get_skill",
]
