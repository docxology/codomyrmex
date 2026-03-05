import pytest

from codomyrmex.agents.learning.skills import Skill, SkillLibrary


def test_skill_management():
    """Verify skill management behavior."""
    lib = SkillLibrary()
    s1 = Skill("Python", "Coding", "print('Hello')", tags=["code"])

    lib.add_skill(s1)

    assert lib.get_skill("Python") == s1
    assert len(lib.search("code")) == 1
    assert len(lib.search("music")) == 0


def test_duplicate_skill():
    """Verify duplicate skill behavior."""
    lib = SkillLibrary()
    lib.add_skill(Skill("A", "", ""))
    with pytest.raises(ValueError):
        lib.add_skill(Skill("A", "", ""))
