"""Identity Manager Module.

Orchestrates multiple personas and manages the active identity context.
"""

from __future__ import annotations

from codomyrmex.logging_monitoring import get_logger

from .persona import Persona, VerificationLevel

logger = get_logger(__name__)


class IdentityManager:
    """Manages user personas and identity switching.

    This manager acts as the primary registry for multiple personas and tracks
    the current active identity context for an agent.
    """

    def __init__(self) -> None:
        self._personas: dict[str, Persona] = {}
        self._active_persona_id: str | None = None

    def create_persona(
        self,
        id: str,
        name: str,
        level: VerificationLevel = VerificationLevel.UNVERIFIED,
        capabilities: list[str] | None = None,
    ) -> Persona:
        """Create and register a new persona.

        Args:
            id: Unique identifier for the persona.
            name: Human-readable name for the persona.
            level: The trust level/verification level of this persona.
            capabilities: Optional list of permissions/actions this persona can perform.

        Returns:
            The newly created Persona object.

        Raises:
            ValueError: If a persona with the same ID already exists.
        """
        if id in self._personas:
            raise ValueError(f"Persona ID {id} already exists")

        persona = Persona(
            id=id, name=name, level=level, capabilities=capabilities or []
        )
        self._personas[id] = persona
        logger.info("Created persona: %s (%s)", name, level.value)
        return persona

    def register_persona(self, persona: Persona) -> None:
        """Register an existing persona instance.

        Args:
            persona: The Persona object to register.

        Raises:
            ValueError: If a persona with the same ID already exists.
        """
        if persona.id in self._personas:
            raise ValueError(f"Persona ID {persona.id} already exists")
        self._personas[persona.id] = persona
        logger.info("Registered persona: %s", persona.id)

    def get_persona(self, id: str) -> Persona | None:
        """Retrieve a persona by its ID."""
        return self._personas.get(id)

    def set_active_persona(self, id: str) -> None:
        """Switch the active persona context.

        Args:
            id: The ID of the persona to set as active.

        Raises:
            ValueError: If the persona ID is not found in the registry.
        """
        if id not in self._personas:
            raise ValueError(f"Persona ID {id} not found")

        self._active_persona_id = id
        logger.info("Switched active persona to: %s", self._personas[id].name)

    @property
    def active_persona(self) -> Persona | None:
        """Get the currently active persona."""
        if self._active_persona_id:
            return self._personas[self._active_persona_id]
        return None

    def list_personas(self, level: VerificationLevel | None = None) -> list[Persona]:
        """list all personas, optionally filtered by verification level.

        Args:
            level: Optional VerificationLevel to filter results.

        Returns:
            A list of matching Persona objects.
        """
        if level:
            return [p for p in self._personas.values() if p.level == level]
        return list(self._personas.values())

    def revoke_persona(self, id: str) -> bool:
        """Revoke a persona, making it inactive and removing it from management.

        Args:
            id: The ID of the persona to revoke.

        Returns:
            True if the persona was found and revoked, False otherwise.
        """
        if id not in self._personas:
            logger.warning("Attempted to revoke non-existent persona: %s", id)
            return False

        persona = self._personas[id]
        persona.is_active = False
        del self._personas[id]

        if self._active_persona_id == id:
            self._active_persona_id = None

        logger.warning("Revoked persona: %s", id)
        return True

    def export_persona(self, id: str) -> dict | None:
        """Export non-sensitive persona data.

        Args:
            id: The ID of the persona to export.

        Returns:
            A dictionary representation of the persona data if found, else None.
        """
        p = self.get_persona(id)
        if p is None:
            return None

        return p.to_dict()

    def promote_persona(self, id: str, new_level: VerificationLevel) -> bool:
        """Update the trust level of a persona.

        Args:
            id: The ID of the persona to promote.
            new_level: The new VerificationLevel to assign.

        Returns:
            True if promotion succeeded, False if persona not found.
        """
        p = self.get_persona(id)
        if p:
            old_level = p.level
            p.level = new_level
            logger.info(
                "Promoted persona %s: %s -> %s", id, old_level.value, new_level.value
            )
            return True
        return False
