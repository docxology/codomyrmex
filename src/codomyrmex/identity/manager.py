"""Identity Manager Module.

Orchestrates multiple personas and manages the active identity context.
"""


from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .persona import Persona, VerificationLevel

logger = get_logger(__name__)

class IdentityManager:
    """Manages user personas and identity switching."""

    def __init__(self):
        """Initialize this instance."""
        self._personas: dict[str, Persona] = {}
        self._active_persona_id: str | None = None

    def create_persona(self, id: str, name: str, level: VerificationLevel) -> Persona:
        """Create and register a new persona."""
        if id in self._personas:
            raise ValueError(f"Persona ID {id} already exists")

        persona = Persona(id=id, name=name, level=level)
        self._personas[id] = persona
        logger.info(f"Created persona: {name} ({level.value})")
        return persona

    def get_persona(self, id: str) -> Persona | None:
        """get Persona ."""
        return self._personas.get(id)

    def set_active_persona(self, id: str) -> None:
        """Switch the active persona context."""
        if id not in self._personas:
            raise ValueError(f"Persona ID {id} not found")

        self._active_persona_id = id
        logger.info(f"Switched active persona to: {self._personas[id].name}")

    @property
    def active_persona(self) -> Persona | None:
        """Get the currently active persona."""
        if self._active_persona_id:
            return self._personas[self._active_persona_id]
        return None

    def list_personas(self) -> list[Persona]:
        """list Personas ."""
        return list(self._personas.values())

    def revoke_persona(self, id: str) -> bool:
        """Revoke a persona, making it inactive."""
        if id not in self._personas:
            return False

        del self._personas[id]
        if self._active_persona_id == id:
            self._active_persona_id = None

        logger.warning(f"Revoked persona: {id}")
        return True

    def export_persona(self, id: str) -> dict | None:
        """Export non-sensitive persona data."""
        if id not in self._personas:
            return None

        p = self._personas[id]
        return {
            "id": p.id,
            "name": p.name,
            "level": p.level.value,
            "created_at": p.created_at.isoformat(),
            "attributes": p.attributes,
            "crumbs_count": len(p.crumbs)
        }
