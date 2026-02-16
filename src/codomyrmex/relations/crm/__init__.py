"""CRM subpackage for the relations module.

Provides contact management, interaction tracking, and search.
"""

from .crm import Contact, ContactManager, Interaction

__all__ = ["Contact", "ContactManager", "Interaction"]
