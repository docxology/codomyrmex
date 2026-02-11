from codomyrmex.education.curriculum import Curriculum, Lesson, Difficulty

def test_curriculum_basics():
    curr = Curriculum("Python", Difficulty.BEGINNER)
    assert curr.total_duration() == 0
    assert len(curr.lessons) == 0

    l1 = Lesson("Intro", "Hello World", Difficulty.BEGINNER, 30)
    curr.add_lesson(l1)
    
    assert curr.total_duration() == 30
    assert len(curr.lessons) == 1
    assert curr.get_lesson(l1.id) == l1

def test_lesson_prerequisites():
    l1 = Lesson("A", "...", Difficulty.BEGINNER, 10)
    l2 = Lesson("B", "...", Difficulty.BEGINNER, 10, prerequisites=[l1.id])
    
    assert l1.id in l2.prerequisites
