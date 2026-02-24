from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4, UUID

@dataclass
class Skill:
    """A learnable capability."""
    name: str
    description: str
    code_snippet: str
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

class SkillLibrary:
    """Repository of agent skills."""
    
    def __init__(self):
        """Execute   Init   operations natively."""
        self._skills: Dict[str, Skill] = {}

    def add_skill(self, skill: Skill) -> None:
        """Execute Add Skill operations natively."""
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already exists.")
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> Optional[Skill]:
        """Execute Get Skill operations natively."""
        return self._skills.get(name)

    def search(self, tag: str) -> List[Skill]:
        """Execute Search operations natively."""
        return [s for s in self._skills.values() if tag in s.tags]
