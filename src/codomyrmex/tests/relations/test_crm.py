from codomyrmex.relations.crm import CRM, Contact, Interaction, InteractionType

def test_contact_management():
    crm = CRM()
    c1 = Contact("Alice", email="alice@example.com")
    crm.add_contact(c1)
    
    assert len(crm.search("Alice")) == 1
    assert len(crm.search("alice@example.com")) == 1
    assert len(crm.search("Bob")) == 0

def test_interaction_logging():
    c1 = Contact("Bob")
    interaction = Interaction(InteractionType.EMAIL, "Intro")
    c1.log_interaction(interaction)
    
    assert len(c1.history) == 1
    assert c1.history[0].summary == "Intro"
    assert c1.history[0].type == InteractionType.EMAIL
