"""Unit tests for the documentation education submodule.

Covers: education/__init__.py, education/curriculum.py

Zero-mock policy: all tests use real objects with no patching.
"""

import json

import pytest

from codomyrmex.documentation.education import Curriculum, Difficulty, Lesson
from codomyrmex.documentation.education.curriculum import (
    _DIFFICULTY_ORDER,
    DifficultyLevel,
)

# ---------------------------------------------------------------------------
# education/__init__.py imports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEducationModuleImports:
    """Test that the education module exports its public symbols."""

    def test_curriculum_importable(self):
        assert Curriculum is not None

    def test_difficulty_importable(self):
        assert Difficulty is not None

    def test_lesson_importable(self):
        assert Lesson is not None

    def test_difficulty_level_alias(self):
        """DifficultyLevel is a backward-compat alias for Difficulty."""
        assert DifficultyLevel is Difficulty

    def test_optional_tutor_is_none_or_class(self):
        from codomyrmex.documentation.education import Tutor

        # Tutor is either None (not installed) or a class
        assert Tutor is None or callable(Tutor)

    def test_optional_assessment_is_none_or_class(self):
        from codomyrmex.documentation.education import Assessment

        assert Assessment is None or callable(Assessment)


# ---------------------------------------------------------------------------
# Difficulty enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDifficultyEnum:
    """Test Difficulty enum values and ordering."""

    def test_beginner_value(self):
        assert Difficulty.BEGINNER.value == "beginner"

    def test_intermediate_value(self):
        assert Difficulty.INTERMEDIATE.value == "intermediate"

    def test_advanced_value(self):
        assert Difficulty.ADVANCED.value == "advanced"

    def test_expert_value(self):
        assert Difficulty.EXPERT.value == "expert"

    def test_difficulty_order_has_four_members(self):
        assert len(_DIFFICULTY_ORDER) == 4

    def test_difficulty_order_starts_with_beginner(self):
        assert _DIFFICULTY_ORDER[0] == Difficulty.BEGINNER

    def test_difficulty_order_ends_with_expert(self):
        assert _DIFFICULTY_ORDER[-1] == Difficulty.EXPERT


# ---------------------------------------------------------------------------
# Lesson dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLessonDataclass:
    """Test Lesson creation, defaults, and serialization."""

    def test_lesson_title_set(self):
        lesson = Lesson(title="Intro to Python")
        assert lesson.title == "Intro to Python"

    def test_lesson_defaults(self):
        lesson = Lesson(title="Defaults")
        assert lesson.objectives == []
        assert lesson.content == ""
        assert lesson.difficulty == Difficulty.BEGINNER
        assert lesson.duration_minutes == 30
        assert lesson.prerequisites == []
        assert lesson.exercises == []

    def test_lesson_custom_difficulty(self):
        lesson = Lesson(title="Hard", difficulty=Difficulty.EXPERT)
        assert lesson.difficulty == Difficulty.EXPERT

    def test_lesson_to_dict_contains_title(self):
        lesson = Lesson(title="Test Lesson")
        d = lesson.to_dict()
        assert d["title"] == "Test Lesson"

    def test_lesson_to_dict_contains_id(self):
        lesson = Lesson(title="IDed")
        d = lesson.to_dict()
        assert "id" in d
        assert isinstance(d["id"], str)
        assert len(d["id"]) > 0

    def test_lesson_to_dict_difficulty_is_string(self):
        lesson = Lesson(title="Lvl", difficulty=Difficulty.INTERMEDIATE)
        d = lesson.to_dict()
        assert d["difficulty"] == "intermediate"

    def test_lesson_to_dict_duration(self):
        lesson = Lesson(title="Long", duration_minutes=90)
        d = lesson.to_dict()
        assert d["duration_minutes"] == 90

    def test_lesson_unique_ids(self):
        a = Lesson(title="A")
        b = Lesson(title="B")
        assert a.id != b.id


# ---------------------------------------------------------------------------
# Curriculum class
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCurriculumCreation:
    """Test Curriculum __init__ and basic properties."""

    def test_curriculum_name(self):
        c = Curriculum(name="Python Basics")
        assert c.name == "Python Basics"

    def test_default_level_is_beginner(self):
        c = Curriculum(name="Default")
        assert c.level == "beginner"

    def test_level_from_difficulty_enum(self):
        c = Curriculum(name="Advanced", level=Difficulty.ADVANCED)
        assert c.level == "advanced"

    def test_level_from_string(self):
        c = Curriculum(name="Expert", level="expert")
        assert c.level == "expert"

    def test_empty_curriculum_len(self):
        c = Curriculum(name="Empty")
        assert len(c) == 0

    def test_repr_contains_name(self):
        c = Curriculum(name="Demo")
        assert "Demo" in repr(c)

    def test_repr_contains_module_count(self):
        c = Curriculum(name="Demo")
        assert "modules=0" in repr(c)


@pytest.mark.unit
class TestCurriculumAddModule:
    """Test Curriculum.add_module behavior."""

    def test_add_module_returns_lesson(self):
        c = Curriculum(name="C")
        result = c.add_module("module_a")
        assert isinstance(result, Lesson)

    def test_add_module_increases_len(self):
        c = Curriculum(name="C")
        c.add_module("m1")
        assert len(c) == 1

    def test_add_two_modules(self):
        c = Curriculum(name="C")
        c.add_module("m1")
        c.add_module("m2")
        assert len(c) == 2

    def test_add_module_auto_objective(self):
        c = Curriculum(name="C")
        lesson = c.add_module("my_topic")
        assert "my_topic" in lesson.objectives[0]

    def test_add_module_custom_objectives(self):
        c = Curriculum(name="C")
        lesson = c.add_module("t", objectives=["obj1", "obj2"])
        assert lesson.objectives == ["obj1", "obj2"]

    def test_add_module_duplicate_raises(self):
        c = Curriculum(name="C")
        c.add_module("dup")
        with pytest.raises(ValueError, match="already exists"):
            c.add_module("dup")

    def test_add_module_with_content(self):
        c = Curriculum(name="C")
        lesson = c.add_module("topic", content="Deep content here.")
        assert lesson.content == "Deep content here."

    def test_add_module_custom_duration(self):
        c = Curriculum(name="C")
        lesson = c.add_module("long", duration_minutes=60)
        assert lesson.duration_minutes == 60

    def test_add_module_with_prerequisites(self):
        c = Curriculum(name="C")
        c.add_module("intro")
        lesson = c.add_module("advanced", prerequisites=["intro"])
        assert "intro" in lesson.prerequisites


@pytest.mark.unit
class TestCurriculumGetModule:
    """Test Curriculum.get_module and get_modules."""

    def test_get_existing_module(self):
        c = Curriculum(name="C")
        c.add_module("foo")
        result = c.get_module("foo")
        assert result is not None
        assert result.title == "foo"

    def test_get_nonexistent_module_returns_none(self):
        c = Curriculum(name="C")
        result = c.get_module("nonexistent")
        assert result is None

    def test_get_modules_empty(self):
        c = Curriculum(name="C")
        assert c.get_modules() == []

    def test_get_modules_returns_dicts(self):
        c = Curriculum(name="C")
        c.add_module("a")
        c.add_module("b")
        modules = c.get_modules()
        assert len(modules) == 2
        assert all(isinstance(m, dict) for m in modules)


@pytest.mark.unit
class TestCurriculumDuration:
    """Test Curriculum.total_duration calculation."""

    def test_empty_curriculum_duration_zero(self):
        c = Curriculum(name="C")
        assert c.total_duration() == 0

    def test_single_module_duration(self):
        c = Curriculum(name="C")
        c.add_module("m", duration_minutes=45)
        assert c.total_duration() == 45

    def test_multiple_module_duration_sum(self):
        c = Curriculum(name="C")
        c.add_module("m1", duration_minutes=30)
        c.add_module("m2", duration_minutes=60)
        assert c.total_duration() == 90


@pytest.mark.unit
class TestCurriculumLearningPath:
    """Test Curriculum.generate_learning_path topological sort."""

    def test_empty_curriculum_path(self):
        c = Curriculum(name="C")
        path = c.generate_learning_path()
        assert path == []

    def test_single_module_path(self):
        c = Curriculum(name="C")
        c.add_module("solo")
        path = c.generate_learning_path()
        assert path == ["solo"]

    def test_linear_prerequisite_order(self):
        c = Curriculum(name="C")
        c.add_module("intro")
        c.add_module("middle", prerequisites=["intro"])
        c.add_module("advanced", prerequisites=["middle"])
        path = c.generate_learning_path()
        assert path.index("intro") < path.index("middle")
        assert path.index("middle") < path.index("advanced")

    def test_no_filter_without_student_level(self):
        c = Curriculum(name="C")
        c.add_module("a")
        c.add_module("b")
        path = c.generate_learning_path()
        assert len(path) == 2

    def test_student_level_filter_expert_only(self):
        c = Curriculum(name="C")
        # EXPERT difficulty index=3, BEGINNER index=0
        c.add_module("basic")  # default BEGINNER
        c.add_module("hard", )
        # Manually set difficulty on the hard module
        c.get_module("hard").difficulty = Difficulty.EXPERT
        path = c.generate_learning_path(student_level="expert")
        # Only expert-level or above survives
        assert "hard" in path
        assert "basic" not in path

    def test_invalid_student_level_returns_full_path(self):
        c = Curriculum(name="C")
        c.add_module("m1")
        path = c.generate_learning_path(student_level="nonexistent_level")
        # Falls back to full path (warning logged, no crash)
        assert "m1" in path


@pytest.mark.unit
class TestCurriculumExport:
    """Test Curriculum.export() in JSON and text formats."""

    def test_export_json_is_valid_json(self):
        c = Curriculum(name="Test")
        c.add_module("m1")
        exported = c.export("json")
        parsed = json.loads(exported)
        assert parsed["name"] == "Test"

    def test_export_json_contains_modules(self):
        c = Curriculum(name="Test")
        c.add_module("alpha")
        exported = c.export("json")
        parsed = json.loads(exported)
        assert len(parsed["modules"]) == 1
        assert parsed["modules"][0]["title"] == "alpha"

    def test_export_json_total_duration(self):
        c = Curriculum(name="Test")
        c.add_module("m", duration_minutes=45)
        parsed = json.loads(c.export("json"))
        assert parsed["total_duration_minutes"] == 45

    def test_export_text_contains_curriculum_name(self):
        c = Curriculum(name="My Course")
        exported = c.export("text")
        assert "My Course" in exported

    def test_export_text_contains_module_name(self):
        c = Curriculum(name="C")
        c.add_module("module_x")
        exported = c.export("text")
        assert "module_x" in exported

    def test_export_unsupported_format_raises(self):
        c = Curriculum(name="C")
        with pytest.raises(ValueError, match="Unsupported format"):
            c.export("xml")

    def test_export_empty_curriculum_json(self):
        c = Curriculum(name="Empty")
        parsed = json.loads(c.export("json"))
        assert parsed["modules"] == []


# ---------------------------------------------------------------------------
# education/visualization.py — import guard test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVisualizationImport:
    """Test that visualization module handles optional deps gracefully."""

    def test_visualization_module_importable_or_raises_import_error(self):
        """render_curriculum_path requires MermaidDiagram from data_visualization."""
        try:
            from codomyrmex.documentation.education import visualization  # noqa: F401

            assert hasattr(visualization, "render_curriculum_path")
        except ImportError:
            # Acceptable: optional dependency not installed
            pass
