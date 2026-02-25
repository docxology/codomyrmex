from codomyrmex.relations.crm.crm import Contact, ContactManager, Interaction


def test_contact_management():
    """Test functionality: contact management."""
    cm = ContactManager()
    c1 = cm.add_contact("Alice", email="alice@example.com")

    assert len(cm.search_contacts("Alice")) == 1
    assert len(cm.search_contacts("alice@example.com")) == 1
    assert len(cm.search_contacts("Bob")) == 0


def test_interaction_logging():
    """Test functionality: interaction logging."""
    contact = Contact(name="Bob", email="bob@example.com")
    interaction = Interaction(type="email", notes="Intro")
    contact.interactions.append(interaction)

    assert len(contact.interactions) == 1
    assert contact.interactions[0].notes == "Intro"
    assert contact.interactions[0].type == "email"
