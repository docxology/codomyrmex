"""MCP tool definitions for the CRM submodule.

Exposes contact management and interaction logging as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

# Use a global ContactManager instance to store contacts across tool calls.
_MANAGER: Any = None


def _get_manager() -> Any:
    """Return the global ContactManager instance."""
    global _MANAGER
    if _MANAGER is None:
        from codomyrmex.relations.crm.crm import ContactManager

        _MANAGER = ContactManager()
    return _MANAGER


def _reset_manager() -> None:
    """Reset the global ContactManager (useful for testing)."""
    global _MANAGER
    _MANAGER = None


@mcp_tool(
    category="relations_crm",
    description="Add a new contact to the CRM.",
)
def crm_add_contact(
    name: str,
    email: str,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create and store a new contact in the CRM.

    Args:
        name: Contact display name.
        email: Contact email address.
        tags: Optional list of categorical tags.
        metadata: Optional dictionary of arbitrary key-value pairs.

    """
    try:
        manager = _get_manager()
        contact = manager.add_contact(
            name=name,
            email=email,
            tags=tags or [],
            metadata=metadata or {},
        )
        return {"status": "success", "contact": contact.to_dict()}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="relations_crm",
    description="Search for contacts in the CRM by name, email, or tag.",
)
def crm_search_contacts(query: str) -> dict[str, Any]:
    """Search for matching contacts in the CRM.

    Args:
        query: Search string to match against name, email, or tags.

    """
    try:
        manager = _get_manager()
        results = manager.search_contacts(query)
        return {
            "status": "success",
            "results": [c.to_dict() for c in results],
            "count": len(results),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="relations_crm",
    description="Log a new interaction with an existing contact in the CRM.",
)
def crm_add_interaction(
    contact_id: str,
    type: str,
    notes: str,
) -> dict[str, Any]:
    """Record a new interaction (e.g., email, meeting) with a contact.

    Args:
        contact_id: The unique identifier of the contact.
        type: Interaction category (e.g., 'email', 'call', 'meeting').
        notes: Free-text description of the interaction.

    """
    try:
        manager = _get_manager()
        interaction = manager.add_interaction(contact_id, type, notes)
        if interaction is None:
            return {"status": "error", "error": f"Contact '{contact_id}' not found"}

        return {
            "status": "success",
            "interaction": {
                "id": interaction.id,
                "type": interaction.type,
                "notes": interaction.notes,
                "timestamp": interaction.timestamp,
            },
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
