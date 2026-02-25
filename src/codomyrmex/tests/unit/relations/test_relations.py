"""Tests for the relations module.

Tests cover:
- Module import
- Interaction creation and defaults
- Contact creation, fields, to_dict serialization
- ContactManager CRUD operations
- ContactManager search by name, email, tag
- ContactManager tag_contact
- ContactManager interaction logging and history
- ContactManager get_contacts_by_tag
- Edge cases: duplicate tags, empty search, nonexistent contacts
"""

import pytest

from codomyrmex.relations.crm.crm import Contact, ContactManager, Interaction

# ======================================================================
# Module import
# ======================================================================

@pytest.mark.unit
def test_module_import():
    """relations module is importable."""
    from codomyrmex import relations
    assert relations is not None


# ======================================================================
# Interaction tests
# ======================================================================

@pytest.mark.unit
def test_interaction_creation_defaults():
    """Interaction is created with auto-id, default type='note', empty notes."""
    interaction = Interaction()
    assert interaction.id is not None
    assert interaction.type == "note"
    assert interaction.notes == ""
    assert interaction.timestamp is not None


@pytest.mark.unit
def test_interaction_custom_fields():
    """Interaction stores custom type and notes."""
    interaction = Interaction(type="call", notes="Discussed pricing")
    assert interaction.type == "call"
    assert interaction.notes == "Discussed pricing"


@pytest.mark.unit
def test_interaction_ids_are_unique():
    """Each interaction gets a distinct UUID."""
    i1 = Interaction()
    i2 = Interaction()
    assert i1.id != i2.id


@pytest.mark.unit
def test_interaction_timestamp_is_string():
    """Interaction timestamp is an ISO-format string."""
    interaction = Interaction()
    assert isinstance(interaction.timestamp, str)
    # ISO format has 'T' separator
    assert "T" in interaction.timestamp


# ======================================================================
# Contact tests
# ======================================================================

@pytest.mark.unit
def test_contact_creation_defaults():
    """Contact is created with auto-id and empty defaults."""
    contact = Contact()
    assert contact.id is not None
    assert contact.name == ""
    assert contact.email == ""
    assert contact.tags == []
    assert contact.metadata == {}
    assert contact.interactions == []


@pytest.mark.unit
def test_contact_with_fields():
    """Contact stores name, email, tags, and metadata."""
    contact = Contact(
        name="Alice Smith",
        email="alice@example.com",
        tags=["vip", "partner"],
        metadata={"company": "Acme"},
    )
    assert contact.name == "Alice Smith"
    assert contact.email == "alice@example.com"
    assert "vip" in contact.tags
    assert contact.metadata["company"] == "Acme"


@pytest.mark.unit
def test_contact_ids_are_unique():
    """Each contact gets a distinct UUID."""
    c1 = Contact(name="A")
    c2 = Contact(name="B")
    assert c1.id != c2.id


@pytest.mark.unit
def test_contact_to_dict():
    """Contact.to_dict returns a serializable dictionary."""
    contact = Contact(name="Bob", email="bob@test.com", tags=["lead"])
    d = contact.to_dict()
    assert d["name"] == "Bob"
    assert d["email"] == "bob@test.com"
    assert d["tags"] == ["lead"]
    assert "id" in d
    assert "created_at" in d
    assert "interaction_count" in d
    assert d["interaction_count"] == 0


@pytest.mark.unit
def test_contact_to_dict_with_interactions():
    """Contact.to_dict includes interaction count."""
    contact = Contact(name="Charlie")
    contact.interactions.append(Interaction(type="email", notes="Sent proposal"))
    contact.interactions.append(Interaction(type="call", notes="Follow up"))
    d = contact.to_dict()
    assert d["interaction_count"] == 2


# ======================================================================
# ContactManager: add and get
# ======================================================================

@pytest.mark.unit
def test_contact_manager_add_contact():
    """add_contact creates and stores a contact."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    assert isinstance(contact, Contact)
    assert contact.name == "Alice"
    assert contact.email == "alice@test.com"
    assert len(cm) == 1


@pytest.mark.unit
def test_contact_manager_add_contact_with_tags():
    """add_contact accepts tags kwarg."""
    cm = ContactManager()
    contact = cm.add_contact("Bob", "bob@test.com", tags=["vip", "partner"])
    assert "vip" in contact.tags
    assert "partner" in contact.tags


@pytest.mark.unit
def test_contact_manager_add_contact_with_metadata():
    """add_contact accepts metadata kwarg."""
    cm = ContactManager()
    contact = cm.add_contact("Charlie", "c@test.com", metadata={"role": "engineer"})
    assert contact.metadata["role"] == "engineer"


@pytest.mark.unit
def test_contact_manager_get_contact_found():
    """get_contact retrieves a contact by ID."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    found = cm.get_contact(contact.id)
    assert found is contact


@pytest.mark.unit
def test_contact_manager_get_contact_not_found():
    """get_contact returns None for unknown ID."""
    cm = ContactManager()
    assert cm.get_contact("nonexistent-id") is None


@pytest.mark.unit
def test_contact_manager_all_contacts():
    """all_contacts returns all stored contacts."""
    cm = ContactManager()
    cm.add_contact("Alice", "a@t.com")
    cm.add_contact("Bob", "b@t.com")
    assert len(cm.all_contacts) == 2


@pytest.mark.unit
def test_contact_manager_len():
    """len(cm) returns number of contacts."""
    cm = ContactManager()
    assert len(cm) == 0
    cm.add_contact("X", "x@t.com")
    assert len(cm) == 1


# ======================================================================
# ContactManager: remove
# ======================================================================

@pytest.mark.unit
def test_contact_manager_remove_contact():
    """remove_contact removes existing contact and returns True."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    result = cm.remove_contact(contact.id)
    assert result is True
    assert len(cm) == 0
    assert cm.get_contact(contact.id) is None


@pytest.mark.unit
def test_contact_manager_remove_nonexistent():
    """remove_contact returns False for unknown ID."""
    cm = ContactManager()
    assert cm.remove_contact("no-such-id") is False


# ======================================================================
# ContactManager: search
# ======================================================================

@pytest.mark.unit
def test_contact_manager_search_by_name():
    """search_contacts matches by name (case-insensitive)."""
    cm = ContactManager()
    cm.add_contact("Alice Smith", "alice@test.com")
    cm.add_contact("Bob Jones", "bob@test.com")
    results = cm.search_contacts("alice")
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


@pytest.mark.unit
def test_contact_manager_search_by_email():
    """search_contacts matches by email."""
    cm = ContactManager()
    cm.add_contact("Charlie", "charlie@example.org")
    results = cm.search_contacts("example.org")
    assert len(results) == 1
    assert results[0].name == "Charlie"


@pytest.mark.unit
def test_contact_manager_search_by_tag():
    """search_contacts matches by tag."""
    cm = ContactManager()
    cm.add_contact("Diana", "diana@test.com", tags=["engineering"])
    cm.add_contact("Eve", "eve@test.com", tags=["marketing"])
    results = cm.search_contacts("engineering")
    assert len(results) == 1
    assert results[0].name == "Diana"


@pytest.mark.unit
def test_contact_manager_search_case_insensitive():
    """search_contacts is case-insensitive."""
    cm = ContactManager()
    cm.add_contact("Alice", "alice@test.com")
    results = cm.search_contacts("ALICE")
    assert len(results) == 1


@pytest.mark.unit
def test_contact_manager_search_partial_match():
    """search_contacts matches partial strings."""
    cm = ContactManager()
    cm.add_contact("Alexander Hamilton", "alex@gov.us")
    results = cm.search_contacts("xander")
    assert len(results) == 1


@pytest.mark.unit
def test_contact_manager_search_no_results():
    """search_contacts returns empty list for no matches."""
    cm = ContactManager()
    cm.add_contact("Alice", "alice@test.com")
    results = cm.search_contacts("zzzzz")
    assert results == []


@pytest.mark.unit
def test_contact_manager_search_multiple_results():
    """search_contacts can return multiple matches."""
    cm = ContactManager()
    cm.add_contact("Smith Alice", "a@test.com")
    cm.add_contact("Smith Bob", "b@test.com")
    cm.add_contact("Jones Charlie", "c@test.com")
    results = cm.search_contacts("smith")
    assert len(results) == 2


# ======================================================================
# ContactManager: tagging
# ======================================================================

@pytest.mark.unit
def test_contact_manager_tag_contact():
    """tag_contact adds tags to an existing contact."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    result = cm.tag_contact(contact.id, ["vip", "partner"])
    assert result is True
    found = cm.get_contact(contact.id)
    assert "vip" in found.tags
    assert "partner" in found.tags


@pytest.mark.unit
def test_contact_manager_tag_contact_no_duplicates():
    """tag_contact does not add duplicate tags."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com", tags=["vip"])
    cm.tag_contact(contact.id, ["vip", "new"])
    found = cm.get_contact(contact.id)
    assert found.tags.count("vip") == 1
    assert "new" in found.tags


@pytest.mark.unit
def test_contact_manager_tag_nonexistent():
    """tag_contact returns False for unknown contact."""
    cm = ContactManager()
    assert cm.tag_contact("no-id", ["tag"]) is False


@pytest.mark.unit
def test_contact_manager_get_contacts_by_tag():
    """get_contacts_by_tag filters contacts by a specific tag."""
    cm = ContactManager()
    cm.add_contact("Alice", "a@t.com", tags=["eng"])
    cm.add_contact("Bob", "b@t.com", tags=["eng", "lead"])
    cm.add_contact("Charlie", "c@t.com", tags=["design"])
    results = cm.get_contacts_by_tag("eng")
    assert len(results) == 2
    names = {c.name for c in results}
    assert names == {"Alice", "Bob"}


@pytest.mark.unit
def test_contact_manager_get_contacts_by_tag_empty():
    """get_contacts_by_tag returns empty for a tag no one has."""
    cm = ContactManager()
    cm.add_contact("Alice", "a@t.com", tags=["eng"])
    assert cm.get_contacts_by_tag("nonexistent") == []


# ======================================================================
# ContactManager: interactions
# ======================================================================

@pytest.mark.unit
def test_contact_manager_add_interaction():
    """add_interaction logs an interaction for a contact."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    interaction = cm.add_interaction(contact.id, "call", "Discussed project")
    assert isinstance(interaction, Interaction)
    assert interaction.type == "call"
    assert interaction.notes == "Discussed project"
    assert len(contact.interactions) == 1


@pytest.mark.unit
def test_contact_manager_add_interaction_nonexistent():
    """add_interaction returns None for unknown contact."""
    cm = ContactManager()
    result = cm.add_interaction("no-id", "email", "Lost message")
    assert result is None


@pytest.mark.unit
def test_contact_manager_get_interaction_history():
    """get_interaction_history returns interactions as dicts."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    cm.add_interaction(contact.id, "email", "Sent proposal")
    cm.add_interaction(contact.id, "call", "Follow up")
    history = cm.get_interaction_history(contact.id)
    assert len(history) == 2
    assert all(isinstance(h, dict) for h in history)
    assert all("type" in h and "notes" in h for h in history)


@pytest.mark.unit
def test_contact_manager_get_interaction_history_nonexistent():
    """get_interaction_history returns empty list for unknown contact."""
    cm = ContactManager()
    assert cm.get_interaction_history("no-id") == []


@pytest.mark.unit
def test_contact_manager_interaction_history_order():
    """Interaction history is sorted newest-first."""
    cm = ContactManager()
    contact = cm.add_contact("Alice", "alice@test.com")
    # Add interactions with explicit timestamps to test ordering
    i1 = Interaction(type="email", notes="First", timestamp="2025-01-01T00:00:00")
    i2 = Interaction(type="call", notes="Second", timestamp="2025-06-01T00:00:00")
    contact.interactions.extend([i1, i2])
    history = cm.get_interaction_history(contact.id)
    assert history[0]["notes"] == "Second"
    assert history[1]["notes"] == "First"
