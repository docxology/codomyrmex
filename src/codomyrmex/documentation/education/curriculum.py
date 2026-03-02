"""Education curriculum module.

Provides Difficulty enum, Lesson, and Curriculum
for building structured learning paths.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class Difficulty(Enum):
    """Learning difficulty level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# Backward-compatible alias used by tests and external consumers
DifficultyLevel = Difficulty



# Ordered difficulty levels for comparison
_DIFFICULTY_ORDER = [Difficulty.BEGINNER, Difficulty.INTERMEDIATE, Difficulty.ADVANCED, Difficulty.EXPERT]


@dataclass
class Lesson:
    """Individual unit of learning.

    Args:
        title: Lesson title.
        objectives: List of learning objectives.
        content: Lesson content text.
        difficulty: Difficulty level.
        duration_minutes: Expected duration (default 30).
        prerequisites: List of prerequisite module names.
        exercises: List of exercise dicts (prompt/solution).
    """
    title: str
    objectives: list[str] = field(default_factory=list)
    content: str = ""
    difficulty: Difficulty = Difficulty.BEGINNER
    duration_minutes: int = 30
    id: UUID = field(default_factory=uuid4)
    prerequisites: list[str] = field(default_factory=list)
    exercises: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize lesson to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "objectives": self.objectives,
            "content": self.content,
            "difficulty": self.difficulty.value,
            "duration_minutes": self.duration_minutes,
            "prerequisites": self.prerequisites,
            "exercises": self.exercises,
        }


class Curriculum:
    """Structured sequence of learning modules.

    Args:
        name: Curriculum name.
        level: Target difficulty level (string or Difficulty enum).
    """

    def __init__(self, name: str, level: str | Difficulty = Difficulty.BEGINNER):
        self.name = name
        if isinstance(level, Difficulty):
            self.level = level.value
        else:
            self.level = level
        self._modules: dict[str, Lesson] = {}

    # ------------------------------------------------------------------
    # Module management
    # ------------------------------------------------------------------

    def add_module(
        self,
        name: str,
        *,
        content: str = "",
        objectives: list[str] | None = None,
        exercises: list[dict[str, Any]] | None = None,
        duration_minutes: int = 30,
        prerequisites: list[str] | None = None,
        **kwargs: Any,
    ) -> Lesson:
        """Add a named module to the curriculum.

        Args:
            name: Module name (becomes the Lesson title).
            content: Module content text.
            objectives: Learning objectives (auto-generated if None).
            exercises: Exercise dicts with prompt/solution.
            duration_minutes: Expected duration.
            prerequisites: List of prerequisite module names.
            **kwargs: Additional module parameters.

        Returns:
            The created Lesson object.

        Raises:
            ValueError: If module name already exists.
        """
        if name in self._modules:
            raise ValueError(f"Module '{name}' already exists in curriculum")

        if objectives is None:
            objectives = [f"Understand {name}"]

        lesson = Lesson(
            title=name,
            content=content,
            objectives=objectives,
            exercises=exercises or [],
            duration_minutes=duration_minutes,
            prerequisites=prerequisites or [],
        )
        self._modules[name] = lesson
        return lesson

    def get_module(self, name: str) -> Lesson | None:
        """Retrieve a module by name.

        Returns:
            Lesson or None if not found.
        """
        return self._modules.get(name)

    def get_modules(self) -> list[dict[str, Any]]:
        """Return all modules as a list of serialized dicts."""
        return [lesson.to_dict() for lesson in self._modules.values()]

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    def total_duration(self) -> int:
        """Calculate total duration in minutes across all modules."""
        return sum(m.duration_minutes for m in self._modules.values())

    # ------------------------------------------------------------------
    # Learning path
    # ------------------------------------------------------------------

    def generate_learning_path(
        self, student_level: str | None = None
    ) -> list[str]:
        """Generate an ordered learning path (topological sort by prerequisites).

        Args:
            student_level: If provided, skip modules at or below this level.

        Returns:
            List of module names in dependency order.
        """
        # Build adjacency / in-degree for topological sort
        modules = dict(self._modules)
        in_degree: dict[str, int] = dict.fromkeys(modules, 0)
        dependents: dict[str, list[str]] = {name: [] for name in modules}

        for name, lesson in modules.items():
            for prereq in lesson.prerequisites:
                if prereq in modules:
                    in_degree[name] += 1
                    dependents[prereq].append(name)

        # Kahn's algorithm
        queue = [n for n, d in in_degree.items() if d == 0]
        path: list[str] = []

        while queue:
            queue.sort()  # Deterministic order
            node = queue.pop(0)
            path.append(node)
            for dep in dependents[node]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        # Filter by student level if provided
        if student_level:
            try:
                level = Difficulty(student_level)
                level_idx = _DIFFICULTY_ORDER.index(level)
                # Skip modules whose difficulty level index <= student's
                filtered = []
                for name in path:
                    mod = modules[name]
                    mod_idx = _DIFFICULTY_ORDER.index(mod.difficulty) if mod.difficulty in _DIFFICULTY_ORDER else 0
                    if mod_idx >= level_idx:
                        filtered.append(name)
                path = filtered
            except (ValueError, IndexError) as e:
                logger.warning("Failed to filter curriculum path by difficulty level '%s': %s", student_level, e)
                pass

        return path

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, format: str = "json") -> str:
        """Export curriculum to specified format.

        Args:
            format: 'json' or 'text'.

        Returns:
            Serialized curriculum string.

        Raises:
            ValueError: If format is unsupported.
        """
        if format == "json":
            return json.dumps({
                "name": self.name,
                "level": self.level,
                "total_duration_minutes": self.total_duration(),
                "modules": self.get_modules(),
            }, indent=2)
        elif format == "text":
            lines = [f"Curriculum: {self.name}"]
            lines.append(f"Level: {self.level}")
            lines.append(f"Modules: {len(self._modules)}")
            lines.append(f"Total Duration: {self.total_duration()} minutes")
            for name, lesson in self._modules.items():
                lines.append(f"\n  {name}")
                lines.append(f"  {lesson.duration_minutes} min")
            return "\n".join(lines)
        raise ValueError(f"Unsupported format: {format}")

    # ------------------------------------------------------------------
    # Python protocols
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of items."""
        return len(self._modules)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Curriculum(name='{self.name}', "
            f"level='{self.level}', "
            f"modules={len(self._modules)})"
        )
