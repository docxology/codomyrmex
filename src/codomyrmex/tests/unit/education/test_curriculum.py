from codomyrmex.documentation.education.curriculum import Curriculum, Lesson


def test_curriculum_basics():
    """Test functionality: curriculum basics."""
    curr = Curriculum("Python", "beginner")
    assert len(curr._modules) == 0

    lesson = curr.add_module("Intro", content="Hello World", duration_minutes=30)

    assert len(curr._modules) == 1
    assert curr._modules["Intro"] == lesson


def test_lesson_prerequisites():
    """Test functionality: lesson prerequisites."""
    Lesson(
        title="A",
        objectives=["Learn A"],
        content="...",
        duration_minutes=10,
    )
    l2 = Lesson(
        title="B",
        objectives=["Learn B"],
        content="...",
        duration_minutes=10,
        prerequisites=["A"],
    )

    assert "A" in l2.prerequisites
