"""Tests for the relations module.

Tests cover:
- Module import
- InteractionType enum values
- Interaction creation and defaults
- Contact creation with optional fields
- Contact log_interaction
- Contact add_tag
- CRM construction
- CRM add_contact and search by name
- CRM search by email
- CRM get_contact by UUID
- CRM get_contact returns None for missing
"""

import pytest
from uuid import uuid4

from codomyrmex.relations.crm import (
    CRM,
    Contact,
    Interaction,
    InteractionType,
)


@pytest.mark.unit
def test_module_import():
    """relations module is importable."""
    from codomyrmex import relations
    assert relations is not None


@pytest.mark.unit
def test_interaction_type_enum():
    """InteractionType enum has expected members."""
    assert InteractionType.EMAIL.name == "EMAIL"
    assert InteractionType.CALL.name == "CALL"
    assert InteractionType.MEETING.name == "MEETING"
    assert InteractionType.SOCIAL_MEDIA.name == "SOCIAL_MEDIA"


@pytest.mark.unit
def test_interaction_creation():
    """Interaction is created with type, summary, and auto timestamp."""
    interaction = Interaction(type=InteractionType.CALL, summary="Discussed pricing")
    assert interaction.type == InteractionType.CALL
    assert interaction.summary == "Discussed pricing"
    assert interaction.timestamp is not None
    assert interaction.id is not None


@pytest.mark.unit
def test_contact_creation_defaults():
    """Contact is created with required name and optional fields."""
    contact = Contact(name="Alice Smith")
    assert contact.name == "Alice Smith"
    assert contact.email is None
    assert contact.phone is None
    assert contact.tags == set()
    assert contact.history == []
    assert contact.id is not None


@pytest.mark.unit
def test_contact_with_all_fields():
    """Contact stores email, phone, and tags."""
    contact = Contact(
        name="Bob Jones",
        email="bob@example.com",
        phone="+1-555-0100",
        tags={"vip", "partner"},
    )
    assert contact.email == "bob@example.com"
    assert contact.phone == "+1-555-0100"
    assert "vip" in contact.tags


@pytest.mark.unit
def test_contact_log_interaction():
    """Contact.log_interaction appends to history."""
    contact = Contact(name="Charlie")
    interaction = Interaction(type=InteractionType.EMAIL, summary="Sent proposal")
    contact.log_interaction(interaction)
    assert len(contact.history) == 1
    assert contact.history[0].summary == "Sent proposal"


@pytest.mark.unit
def test_contact_add_tag():
    """Contact.add_tag adds a tag to the set."""
    contact = Contact(name="Diana")
    contact.add_tag("lead")
    contact.add_tag("hot")
    assert "lead" in contact.tags
    assert "hot" in contact.tags
    # Adding duplicate is idempotent
    contact.add_tag("lead")
    assert len(contact.tags) == 2


@pytest.mark.unit
def test_crm_add_and_search_by_name():
    """CRM adds contacts and searches by name."""
    crm = CRM()
    crm.add_contact(Contact(name="Alice Smith", email="alice@test.com"))
    crm.add_contact(Contact(name="Bob Jones", email="bob@test.com"))
    results = crm.search("alice")
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


@pytest.mark.unit
def test_crm_search_by_email():
    """CRM search matches email addresses."""
    crm = CRM()
    crm.add_contact(Contact(name="Charlie", email="charlie@example.org"))
    results = crm.search("example.org")
    assert len(results) == 1
    assert results[0].name == "Charlie"


@pytest.mark.unit
def test_crm_get_contact_by_id():
    """CRM.get_contact retrieves a contact by UUID."""
    crm = CRM()
    contact = Contact(name="Eve")
    crm.add_contact(contact)
    found = crm.get_contact(contact.id)
    assert found is contact


@pytest.mark.unit
def test_crm_get_contact_not_found():
    """CRM.get_contact returns None for unknown UUID."""
    crm = CRM()
    result = crm.get_contact(uuid4())
    assert result is None
