from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional
from uuid import uuid4, UUID

class Difficulty(Enum):
    """Learning difficulty level."""
    BEGINNER = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    EXPERT = auto()

@dataclass
class Lesson:
    """Individual unit of learning."""
    title: str
    content: str
    difficulty: Difficulty
    duration_minutes: int
    id: UUID = field(default_factory=uuid4)
    prerequisites: List[UUID] = field(default_factory=list)

class Curriculum:
    """Structured sequence of lessons."""
    
    def __init__(self, topic: str, difficulty: Difficulty):
        self.topic = topic
        self.target_difficulty = difficulty
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: Lesson) -> None:
        """Add a lesson to the curriculum."""
        self.lessons.append(lesson)

    def get_lesson(self, lesson_id: UUID) -> Optional[Lesson]:
        """Retrieve a lesson by ID."""
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None

    def total_duration(self) -> int:
        """Calculate total duration in minutes."""
        return sum(l.duration_minutes for l in self.lessons)

    def __repr__(self) -> str:
        return f"Curriculum(topic='{self.topic}', lessons={len(self.lessons)})"
