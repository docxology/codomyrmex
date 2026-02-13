"""Tests for the education module.

Tests cover:
- Module import
- Difficulty enum values
- Lesson creation and defaults
- Lesson prerequisites
- Curriculum construction
- Curriculum add_lesson
- Curriculum get_lesson by ID
- Curriculum get_lesson returns None for missing
- Curriculum total_duration calculation
- Curriculum repr
"""

import pytest
from uuid import uuid4

from codomyrmex.education.curriculum import Curriculum, Difficulty, Lesson


@pytest.mark.unit
def test_module_import():
    """education module is importable."""
    from codomyrmex import education
    assert education is not None


@pytest.mark.unit
def test_difficulty_enum_values():
    """Difficulty enum has four levels."""
    assert Difficulty.BEGINNER.name == "BEGINNER"
    assert Difficulty.INTERMEDIATE.name == "INTERMEDIATE"
    assert Difficulty.ADVANCED.name == "ADVANCED"
    assert Difficulty.EXPERT.name == "EXPERT"


@pytest.mark.unit
def test_lesson_creation():
    """Lesson is created with required fields and auto-generated UUID."""
    lesson = Lesson(
        title="Intro to Python",
        content="Variables and types",
        difficulty=Difficulty.BEGINNER,
        duration_minutes=30,
    )
    assert lesson.title == "Intro to Python"
    assert lesson.content == "Variables and types"
    assert lesson.difficulty == Difficulty.BEGINNER
    assert lesson.duration_minutes == 30
    assert lesson.id is not None
    assert lesson.prerequisites == []


@pytest.mark.unit
def test_lesson_prerequisites():
    """Lesson can have prerequisite IDs."""
    prereq_id = uuid4()
    lesson = Lesson(
        title="Advanced Topics",
        content="Decorators",
        difficulty=Difficulty.ADVANCED,
        duration_minutes=60,
        prerequisites=[prereq_id],
    )
    assert prereq_id in lesson.prerequisites


@pytest.mark.unit
def test_curriculum_construction():
    """Curriculum is created with topic and target difficulty."""
    curriculum = Curriculum(topic="Python", difficulty=Difficulty.INTERMEDIATE)
    assert curriculum.topic == "Python"
    assert curriculum.target_difficulty == Difficulty.INTERMEDIATE
    assert curriculum.lessons == []


@pytest.mark.unit
def test_curriculum_add_lesson():
    """Curriculum.add_lesson appends a lesson."""
    curriculum = Curriculum(topic="Data Science", difficulty=Difficulty.BEGINNER)
    lesson = Lesson(
        title="Statistics Basics",
        content="Mean, median, mode",
        difficulty=Difficulty.BEGINNER,
        duration_minutes=45,
    )
    curriculum.add_lesson(lesson)
    assert len(curriculum.lessons) == 1
    assert curriculum.lessons[0].title == "Statistics Basics"


@pytest.mark.unit
def test_curriculum_get_lesson_found():
    """Curriculum.get_lesson retrieves a lesson by its UUID."""
    curriculum = Curriculum(topic="ML", difficulty=Difficulty.ADVANCED)
    lesson = Lesson(
        title="Neural Networks",
        content="Backpropagation",
        difficulty=Difficulty.ADVANCED,
        duration_minutes=90,
    )
    curriculum.add_lesson(lesson)
    found = curriculum.get_lesson(lesson.id)
    assert found is lesson


@pytest.mark.unit
def test_curriculum_get_lesson_not_found():
    """Curriculum.get_lesson returns None for nonexistent UUID."""
    curriculum = Curriculum(topic="Web Dev", difficulty=Difficulty.BEGINNER)
    result = curriculum.get_lesson(uuid4())
    assert result is None


@pytest.mark.unit
def test_curriculum_total_duration():
    """Curriculum.total_duration sums all lesson durations."""
    curriculum = Curriculum(topic="DevOps", difficulty=Difficulty.INTERMEDIATE)
    curriculum.add_lesson(
        Lesson(title="Docker", content="Containers", difficulty=Difficulty.INTERMEDIATE, duration_minutes=30)
    )
    curriculum.add_lesson(
        Lesson(title="K8s", content="Orchestration", difficulty=Difficulty.INTERMEDIATE, duration_minutes=60)
    )
    assert curriculum.total_duration() == 90


@pytest.mark.unit
def test_curriculum_total_duration_empty():
    """Curriculum.total_duration returns 0 when empty."""
    curriculum = Curriculum(topic="Empty", difficulty=Difficulty.BEGINNER)
    assert curriculum.total_duration() == 0


@pytest.mark.unit
def test_curriculum_repr():
    """Curriculum repr shows topic and lesson count."""
    curriculum = Curriculum(topic="Security", difficulty=Difficulty.EXPERT)
    curriculum.add_lesson(
        Lesson(title="Crypto", content="AES", difficulty=Difficulty.EXPERT, duration_minutes=45)
    )
    r = repr(curriculum)
    assert "Security" in r
    assert "1" in r
