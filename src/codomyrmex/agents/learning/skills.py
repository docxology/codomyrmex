from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Skill:
    """A learnable capability."""
    name: str
    description: str
    code_snippet: str
    tags: list[str] = field(default_factory=list)
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

class SkillLibrary:
    """Repository of agent skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def add_skill(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already exists.")
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def search(self, tag: str) -> list[Skill]:
        """search ."""
        return [s for s in self._skills.values() if tag in s.tags]
