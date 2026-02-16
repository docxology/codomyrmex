"""Tests for the education module.

Tests cover:
- Module import
- DifficultyLevel enum values
- Lesson creation and defaults
- Lesson to_dict serialization
- Lesson prerequisites
- Curriculum construction
- Curriculum add_module
- Curriculum duplicate module raises
- Curriculum get_module by name
- Curriculum get_module returns None for missing
- Curriculum total_duration calculation
- Curriculum generate_learning_path
- Curriculum export (json, text)
- Curriculum repr and len
- Edge cases: empty curriculum, large curriculum, ordering
"""

import json

import pytest

from codomyrmex.education.curriculum import Curriculum, DifficultyLevel, Lesson


# ======================================================================
# Module & DifficultyLevel tests
# ======================================================================

@pytest.mark.unit
def test_module_import():
    """education module is importable."""
    from codomyrmex import education
    assert education is not None


@pytest.mark.unit
def test_difficulty_level_enum_values():
    """DifficultyLevel enum has four levels with string values."""
    assert DifficultyLevel.BEGINNER.value == "beginner"
    assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
    assert DifficultyLevel.ADVANCED.value == "advanced"
    assert DifficultyLevel.EXPERT.value == "expert"


@pytest.mark.unit
def test_difficulty_level_enum_member_count():
    """DifficultyLevel enum has exactly four members."""
    members = list(DifficultyLevel)
    assert len(members) == 4


@pytest.mark.unit
def test_difficulty_level_distinct_values():
    """Each DifficultyLevel member has a distinct value."""
    values = [d.value for d in DifficultyLevel]
    assert len(values) == len(set(values))


# ======================================================================
# Lesson tests
# ======================================================================

@pytest.mark.unit
def test_lesson_creation():
    """Lesson is created with required fields and defaults."""
    lesson = Lesson(
        title="Intro to Python",
        objectives=["Learn variables"],
        content="Variables and types",
    )
    assert lesson.title == "Intro to Python"
    assert lesson.objectives == ["Learn variables"]
    assert lesson.content == "Variables and types"
    assert lesson.duration_minutes == 30  # default
    assert lesson.id is not None
    assert lesson.prerequisites == []
    assert lesson.exercises == []


@pytest.mark.unit
def test_lesson_custom_duration():
    """Lesson can have a custom duration."""
    lesson = Lesson(
        title="Long Lesson",
        objectives=["Obj"],
        content="Content",
        duration_minutes=120,
    )
    assert lesson.duration_minutes == 120


@pytest.mark.unit
def test_lesson_with_prerequisites():
    """Lesson can have prerequisite titles."""
    lesson = Lesson(
        title="Advanced Topics",
        objectives=["Deep dive"],
        content="Decorators",
        prerequisites=["Intro to Python"],
    )
    assert "Intro to Python" in lesson.prerequisites


@pytest.mark.unit
def test_lesson_with_exercises():
    """Lesson can have exercises."""
    exercises = [
        {"prompt": "What is a variable?", "solution": "A named storage location"},
    ]
    lesson = Lesson(
        title="Test",
        objectives=["Obj"],
        content="Content",
        exercises=exercises,
    )
    assert len(lesson.exercises) == 1
    assert lesson.exercises[0]["prompt"] == "What is a variable?"


@pytest.mark.unit
def test_lesson_id_is_unique():
    """Each lesson gets a distinct auto-generated ID."""
    l1 = Lesson(title="A", objectives=["O"], content="C")
    l2 = Lesson(title="B", objectives=["O"], content="C")
    assert l1.id != l2.id


@pytest.mark.unit
def test_lesson_to_dict():
    """Lesson.to_dict returns a serializable dictionary."""
    lesson = Lesson(
        title="Serialization",
        objectives=["Learn JSON"],
        content="JSON basics",
        duration_minutes=45,
        prerequisites=["Intro"],
    )
    d = lesson.to_dict()
    assert d["title"] == "Serialization"
    assert d["objectives"] == ["Learn JSON"]
    assert d["content"] == "JSON basics"
    assert d["duration_minutes"] == 45
    assert d["prerequisites"] == ["Intro"]
    assert "id" in d


@pytest.mark.unit
def test_lesson_to_dict_roundtrip():
    """Lesson.to_dict output is JSON-serializable."""
    lesson = Lesson(title="Test", objectives=["O"], content="C")
    d = lesson.to_dict()
    json_str = json.dumps(d)
    assert isinstance(json_str, str)
    loaded = json.loads(json_str)
    assert loaded["title"] == "Test"


@pytest.mark.unit
def test_lesson_multiple_objectives():
    """Lesson can have multiple learning objectives."""
    lesson = Lesson(
        title="Multi",
        objectives=["Learn A", "Learn B", "Learn C"],
        content="Content",
    )
    assert len(lesson.objectives) == 3


# ======================================================================
# Curriculum construction tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_construction():
    """Curriculum is created with name and default level."""
    c = Curriculum(name="Python Basics")
    assert c.name == "Python Basics"
    assert c.level == "beginner"
    assert len(c) == 0


@pytest.mark.unit
def test_curriculum_custom_level():
    """Curriculum can be created with custom level."""
    c = Curriculum(name="Advanced ML", level="advanced")
    assert c.level == "advanced"


# ======================================================================
# Curriculum add_module tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_add_module():
    """Curriculum.add_module adds a lesson and returns it."""
    c = Curriculum(name="Test")
    lesson = c.add_module("Introduction", content="Welcome")
    assert isinstance(lesson, Lesson)
    assert lesson.title == "Introduction"
    assert len(c) == 1


@pytest.mark.unit
def test_curriculum_add_module_with_params():
    """add_module accepts all optional parameters."""
    c = Curriculum(name="Test")
    lesson = c.add_module(
        "Advanced",
        content="Deep topic",
        prerequisites=["Intro"],
        objectives=["Master X"],
        exercises=[{"prompt": "Q?", "solution": "A"}],
        duration_minutes=60,
    )
    assert lesson.prerequisites == ["Intro"]
    assert lesson.objectives == ["Master X"]
    assert lesson.duration_minutes == 60
    assert len(lesson.exercises) == 1


@pytest.mark.unit
def test_curriculum_add_module_default_objectives():
    """add_module generates default objectives when none provided."""
    c = Curriculum(name="Test")
    lesson = c.add_module("Loops", content="For/while loops")
    assert len(lesson.objectives) > 0
    assert "Loops" in lesson.objectives[0]


@pytest.mark.unit
def test_curriculum_add_duplicate_module_raises():
    """Adding a module with an existing name raises ValueError."""
    c = Curriculum(name="Test")
    c.add_module("Intro", content="First")
    with pytest.raises(ValueError, match="already exists"):
        c.add_module("Intro", content="Duplicate")


# ======================================================================
# Curriculum get_module tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_get_module_found():
    """get_module retrieves a lesson by name."""
    c = Curriculum(name="Test")
    c.add_module("Target", content="Found me")
    result = c.get_module("Target")
    assert result is not None
    assert result.title == "Target"


@pytest.mark.unit
def test_curriculum_get_module_not_found():
    """get_module returns None for a nonexistent name."""
    c = Curriculum(name="Test")
    assert c.get_module("Nonexistent") is None


@pytest.mark.unit
def test_curriculum_get_module_among_many():
    """get_module finds the correct lesson among many."""
    c = Curriculum(name="Test")
    for i in range(10):
        c.add_module(f"Module {i}", content=f"Content {i}")
    result = c.get_module("Module 7")
    assert result is not None
    assert result.content == "Content 7"


# ======================================================================
# Curriculum total_duration tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_total_duration_empty():
    """Total duration of empty curriculum is 0."""
    c = Curriculum(name="Empty")
    assert c.total_duration() == 0


@pytest.mark.unit
def test_curriculum_total_duration_single():
    """Total duration with one module returns that module's duration."""
    c = Curriculum(name="Single")
    c.add_module("Only", content="Solo", duration_minutes=42)
    assert c.total_duration() == 42


@pytest.mark.unit
def test_curriculum_total_duration_multiple():
    """Total duration sums all module durations."""
    c = Curriculum(name="Multi")
    c.add_module("A", content="a", duration_minutes=30)
    c.add_module("B", content="b", duration_minutes=60)
    c.add_module("C", content="c", duration_minutes=45)
    assert c.total_duration() == 135


# ======================================================================
# Curriculum get_modules tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_get_modules_returns_list_of_dicts():
    """get_modules returns a list of serialized lesson dicts."""
    c = Curriculum(name="Test")
    c.add_module("A", content="a")
    c.add_module("B", content="b")
    modules = c.get_modules()
    assert len(modules) == 2
    assert all(isinstance(m, dict) for m in modules)
    titles = {m["title"] for m in modules}
    assert titles == {"A", "B"}


@pytest.mark.unit
def test_curriculum_get_modules_empty():
    """get_modules on empty curriculum returns empty list."""
    c = Curriculum(name="Empty")
    assert c.get_modules() == []


# ======================================================================
# Curriculum generate_learning_path tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_learning_path_no_prerequisites():
    """Learning path with no prerequisites returns all modules."""
    c = Curriculum(name="Test")
    c.add_module("A", content="a")
    c.add_module("B", content="b")
    path = c.generate_learning_path()
    assert set(path) == {"A", "B"}


@pytest.mark.unit
def test_curriculum_learning_path_respects_prerequisites():
    """Prerequisites come before dependent modules in the path."""
    c = Curriculum(name="Test")
    c.add_module("Intro", content="basics")
    c.add_module("Advanced", content="deep", prerequisites=["Intro"])
    path = c.generate_learning_path()
    assert path.index("Intro") < path.index("Advanced")


@pytest.mark.unit
def test_curriculum_learning_path_chain():
    """A chain of prerequisites is correctly ordered."""
    c = Curriculum(name="Test")
    c.add_module("Step1", content="a")
    c.add_module("Step2", content="b", prerequisites=["Step1"])
    c.add_module("Step3", content="c", prerequisites=["Step2"])
    path = c.generate_learning_path()
    assert path.index("Step1") < path.index("Step2") < path.index("Step3")


@pytest.mark.unit
def test_curriculum_learning_path_skips_for_advanced_student():
    """Advanced student may skip early modules in the path."""
    c = Curriculum(name="Test")
    c.add_module("Beginner", content="a")
    c.add_module("Intermediate", content="b", prerequisites=["Beginner"])
    c.add_module("Advanced", content="c", prerequisites=["Intermediate"])
    path = c.generate_learning_path(student_level="intermediate")
    # Should skip at least the first module
    assert len(path) < 3


# ======================================================================
# Curriculum export tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_export_json():
    """Export as JSON produces valid JSON with expected fields."""
    c = Curriculum(name="Export Test", level="intermediate")
    c.add_module("Mod1", content="Content 1", duration_minutes=20)
    output = c.export(format="json")
    data = json.loads(output)
    assert data["name"] == "Export Test"
    assert data["level"] == "intermediate"
    assert data["total_duration_minutes"] == 20
    assert len(data["modules"]) == 1


@pytest.mark.unit
def test_curriculum_export_text():
    """Export as text produces a human-readable string."""
    c = Curriculum(name="Text Test")
    c.add_module("Hello", content="World", duration_minutes=15)
    output = c.export(format="text")
    assert "Text Test" in output
    assert "Hello" in output
    assert "15 min" in output


@pytest.mark.unit
def test_curriculum_export_unsupported_format_raises():
    """Export with unsupported format raises ValueError."""
    c = Curriculum(name="Test")
    with pytest.raises(ValueError, match="Unsupported"):
        c.export(format="xml")


# ======================================================================
# Curriculum repr and len tests
# ======================================================================

@pytest.mark.unit
def test_curriculum_repr():
    """Curriculum repr shows name, level, and module count."""
    c = Curriculum(name="Repr Test", level="expert")
    c.add_module("Mod", content="c")
    r = repr(c)
    assert "Repr Test" in r
    assert "expert" in r
    assert "1" in r


@pytest.mark.unit
def test_curriculum_repr_empty():
    """Curriculum repr shows 0 modules when empty."""
    c = Curriculum(name="Empty")
    r = repr(c)
    assert "Empty" in r
    assert "0" in r


@pytest.mark.unit
def test_curriculum_len():
    """len(curriculum) returns number of modules."""
    c = Curriculum(name="Len Test")
    assert len(c) == 0
    c.add_module("A", content="a")
    c.add_module("B", content="b")
    assert len(c) == 2
