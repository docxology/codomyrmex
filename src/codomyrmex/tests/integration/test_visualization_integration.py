from codomyrmex.documentation.education.curriculum import Curriculum
from codomyrmex.relations.crm.crm import ContactManager
from codomyrmex.relations.visualization import render_social_graph


def test_relations_visualization():
    """Verify relations visualization behavior."""
    cm = ContactManager()
    cm.add_contact("Alice", email="alice@example.com")
    diagram = render_social_graph(cm)
    assert "nodes" in diagram
    assert diagram["node_count"] == 1
    assert any(n["id"] == "Alice" for n in diagram["nodes"])


def test_education_curriculum_structure():
    """Verify education curriculum structure behavior."""
    curr = Curriculum("Test", "beginner")
    lesson = curr.add_module("Intro", content="Introduction content", duration_minutes=10)
    assert lesson.title == "Intro"
    assert len(curr._modules) == 1
