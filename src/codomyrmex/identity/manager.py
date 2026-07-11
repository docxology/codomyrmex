"""Identity Manager Module.

Orchestrates multiple personas and manages the active identity context,
including persona rotation via :class:`PersonaRotator`.
"""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime

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


# ── Persona Rotation ───────────────────────────────────────────────────


class RotationRecord:
    """Record of a single persona rotation event."""

    def __init__(
        self,
        from_id: str | None,
        to_id: str,
        timestamp: datetime | None = None,
        reason: str = "",
    ) -> None:
        self.from_id = from_id
        self.to_id = to_id
        self.timestamp = timestamp or datetime.now(UTC)
        self.reason = reason

    def to_dict(self) -> dict[str, str]:
        """Serialize rotation record to a dict."""
        return {
            "from": self.from_id or "none",
            "to": self.to_id,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


class PersonaRotator:
    """Persona rotation system for switching between identity personas.

    Wraps an :class:`IdentityManager` and adds rotation, history tracking,
    round-robin cycling, and sticky (preferred) persona support.

    Parameters
    ----------
    manager:
        The :class:`IdentityManager` to operate on. If ``None``, a new
        empty manager is created.
    max_history:
        Maximum number of rotation records to retain (default 50).

    Example::

        manager = IdentityManager()
        manager.create_persona("p1", "Alice", VerificationLevel.KYC)
        manager.create_persona("p2", "Bob", VerificationLevel.ANON)
        rotator = PersonaRotator(manager)
        rotator.rotate_to("p2", reason="session switch")
        assert rotator.current_id == "p2"
    """

    def __init__(
        self,
        manager: IdentityManager | None = None,
        max_history: int = 50,
    ) -> None:
        self.manager = manager or IdentityManager()
        self.max_history = max_history
        self._history: deque[RotationRecord] = deque(maxlen=max_history)
        self._preferred_id: str | None = None

    # -- properties -------------------------------------------------------

    @property
    def current_id(self) -> str | None:
        """ID of the currently active persona, or ``None``."""
        return self.manager._active_persona_id

    @property
    def current_persona(self) -> Persona | None:
        """The currently active :class:`Persona`."""
        return self.manager.active_persona

    @property
    def history(self) -> list[RotationRecord]:
        """Return a list copy of the rotation history."""
        return list(self._history)

    @property
    def preferred_id(self) -> str | None:
        """The sticky/preferred persona ID, if set."""
        return self._preferred_id

    # -- rotation ---------------------------------------------------------

    def rotate_to(
        self,
        persona_id: str,
        reason: str = "",
    ) -> Persona:
        """Rotate the active persona to *persona_id*.

        Args:
            persona_id: The ID of the persona to activate.
            reason: Optional reason for the rotation (recorded in history).

        Returns:
            The newly activated Persona.

        Raises:
            ValueError: If *persona_id* is not registered in the manager.
        """
        if self.manager.get_persona(persona_id) is None:
            raise ValueError(f"Persona ID {persona_id} not found")

        from_id = self.current_id
        if from_id == persona_id:
            # Already active; no rotation needed
            logger.info("Persona %s already active; no rotation", persona_id)
            return self.manager.active_persona  # type: ignore[return-value]

        self.manager.set_active_persona(persona_id)
        record = RotationRecord(from_id=from_id, to_id=persona_id, reason=reason)
        self._history.append(record)
        logger.info("Rotated persona: %s -> %s (%s)", from_id, persona_id, reason or "unspecified")
        return self.manager.active_persona  # type: ignore[return-value]

    def rotate_next(self, reason: str = "") -> Persona:
        """Rotate to the next persona in round-robin order.

        If there is no active persona, activates the first registered one.
        If only one persona exists, it stays active (no-op rotation).

        Raises:
            ValueError: If no personas are registered.
        """
        personas = self.manager.list_personas()
        if not personas:
            raise ValueError("No personas registered for rotation")

        if self.current_id is None:
            return self.rotate_to(personas[0].id, reason=reason)

        # Find current index and wrap around
        ids = [p.id for p in personas]
        try:
            idx = ids.index(self.current_id)
        except ValueError:
            return self.rotate_to(personas[0].id, reason=reason)

        next_idx = (idx + 1) % len(ids)
        return self.rotate_to(ids[next_idx], reason=reason)

    def rotate_to_preferred(self, reason: str = "") -> Persona | None:
        """Rotate to the preferred/sticky persona if one is set.

        Returns the activated Persona, or ``None`` if no preferred persona
        is configured.
        """
        if self._preferred_id is None:
            logger.warning("No preferred persona set")
            return None
        return self.rotate_to(self._preferred_id, reason=reason or "preferred")

    def set_preferred(self, persona_id: str) -> None:
        """Set the preferred/sticky persona ID.

        The persona need not be registered yet, but
        :meth:`rotate_to_preferred` will fail if it hasn't been registered
        by the time it's called.
        """
        self._preferred_id = persona_id
        logger.info("Preferred persona set to: %s", persona_id)

    def clear_preferred(self) -> None:
        """Clear the preferred persona."""
        self._preferred_id = None

    # -- inspection -------------------------------------------------------

    def rotation_count(self) -> int:
        """Return the total number of rotations performed."""
        return len(self._history)

    def last_rotation(self) -> RotationRecord | None:
        """Return the most recent rotation record, or ``None``."""
        if not self._history:
            return None
        return self._history[-1]

    def get_history_dicts(self) -> list[dict[str, str]]:
        """Return rotation history as a list of dicts (for serialization)."""
        return [r.to_dict() for r in self._history]
