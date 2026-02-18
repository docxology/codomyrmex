"""Curriculum management for structured learning paths.

Provides Curriculum and Lesson classes for organizing educational
content with prerequisites, difficulty levels, and learning paths.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class DifficultyLevel(Enum):
    """Difficulty levels for educational content."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Lesson:
    """An individual unit of learning within a curriculum.

    Attributes:
        title: Human-readable lesson title.
        objectives: List of learning objectives for this lesson.
        content: The lesson body text / material.
        exercises: List of exercise dicts with 'prompt' and optional 'solution'.
        duration_minutes: Estimated time to complete in minutes.
        id: Unique identifier.
        prerequisites: List of lesson titles that must be completed first.
    """

    title: str
    objectives: list[str]
    content: str
    exercises: list[dict[str, str]] = field(default_factory=list)
    duration_minutes: int = 30
    id: str = field(default_factory=lambda: str(uuid4()))
    prerequisites: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the lesson to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "objectives": self.objectives,
            "content": self.content,
            "exercises": self.exercises,
            "duration_minutes": self.duration_minutes,
            "prerequisites": self.prerequisites,
        }


class Curriculum:
    """A structured collection of lessons forming a learning program.

    Modules can be added with optional prerequisites, and a personalized
    learning path can be generated based on a student's current level.

    Attributes:
        name: Curriculum name / title.
        level: Target difficulty level.
    """

    def __init__(self, name: str, level: str = "beginner") -> None:
        """Initialize a new curriculum.

        Args:
            name: Name of the curriculum.
            level: Default difficulty level (beginner, intermediate, advanced, expert).
        """
        self.name = name
        self.level = level
        self._modules: dict[str, Lesson] = {}  # name -> Lesson

    def add_module(
        self,
        name: str,
        content: str,
        prerequisites: list[str] | None = None,
        objectives: list[str] | None = None,
        exercises: list[dict[str, str]] | None = None,
        duration_minutes: int = 30,
    ) -> Lesson:
        """Add a module (lesson) to the curriculum.

        Args:
            name: Module name (must be unique within the curriculum).
            content: Module body text.
            prerequisites: Names of modules that must come before this one.
            objectives: Learning objectives.
            exercises: List of exercise dicts.
            duration_minutes: Estimated completion time.

        Returns:
            The newly created Lesson instance.

        Raises:
            ValueError: If a module with the same name already exists.
        """
        if name in self._modules:
            raise ValueError(
                f"Module '{name}' already exists in curriculum '{self.name}'"
            )

        lesson = Lesson(
            title=name,
            objectives=objectives or [f"Understand {name}"],
            content=content,
            exercises=exercises or [],
            duration_minutes=duration_minutes,
            prerequisites=prerequisites or [],
        )
        self._modules[name] = lesson
        return lesson

    def generate_learning_path(self, student_level: str = "beginner") -> list[str]:
        """Generate a topologically-sorted learning path.

        Modules are ordered so that prerequisites always come before
        the modules that depend on them.  If the student's level is
        above beginner, introductory modules may be skipped.

        Args:
            student_level: The student's current knowledge level.

        Returns:
            Ordered list of module names forming the learning path.
        """
        level_order = ["beginner", "intermediate", "advanced", "expert"]
        student_idx = (
            level_order.index(student_level) if student_level in level_order else 0
        )

        # Simple topological sort (Kahn's algorithm)
        in_degree: dict[str, int] = dict.fromkeys(self._modules, 0)
        adjacency: dict[str, list[str]] = {name: [] for name in self._modules}

        for name, lesson in self._modules.items():
            for prereq in lesson.prerequisites:
                if prereq in self._modules:
                    adjacency[prereq].append(name)
                    in_degree[name] += 1

        queue: list[str] = [n for n, d in in_degree.items() if d == 0]
        path: list[str] = []

        while queue:
            # Sort for deterministic output
            queue.sort()
            node = queue.pop(0)
            path.append(node)
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Optionally skip early modules for advanced students
        if student_idx > 0:
            path = path[min(student_idx, len(path)) :]

        return path

    def get_modules(self) -> list[dict[str, Any]]:
        """Return all modules as a list of dictionaries.

        Returns:
            List of module dictionaries with id, title, content, etc.
        """
        return [lesson.to_dict() for lesson in self._modules.values()]

    def get_module(self, name: str) -> Lesson | None:
        """Retrieve a single module by name."""
        return self._modules.get(name)

    def total_duration(self) -> int:
        """Total estimated duration of all modules in minutes."""
        return sum(m.duration_minutes for m in self._modules.values())

    def export(self, format: str = "json") -> str:
        """Export the curriculum in the specified format.

        Args:
            format: Output format ('json' or 'text').

        Returns:
            String representation of the curriculum.

        Raises:
            ValueError: If the format is not supported.
        """
        if format == "json":
            data = {
                "name": self.name,
                "level": self.level,
                "total_duration_minutes": self.total_duration(),
                "modules": self.get_modules(),
            }
            return json.dumps(data, indent=2)
        elif format == "text":
            lines = [f"Curriculum: {self.name} (Level: {self.level})", "=" * 50]
            for i, lesson in enumerate(self._modules.values(), 1):
                lines.append(f"\n{i}. {lesson.title} ({lesson.duration_minutes} min)")
                lines.append(
                    f"   Prerequisites: {', '.join(lesson.prerequisites) or 'None'}"
                )
                for obj in lesson.objectives:
                    lines.append(f"   - {obj}")
            lines.append(f"\nTotal duration: {self.total_duration()} minutes")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def __repr__(self) -> str:
        return f"Curriculum(name='{self.name}', level='{self.level}', modules={len(self._modules)})"

    def __len__(self) -> int:
        return len(self._modules)
