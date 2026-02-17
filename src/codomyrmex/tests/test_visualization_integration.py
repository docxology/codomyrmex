import pytest
from codomyrmex.relations.visualization import render_social_graph
from codomyrmex.relations.crm import ContactManager
from codomyrmex.documentation.education.curriculum import Curriculum, Lesson, DifficultyLevel


def test_relations_visualization():
    cm = ContactManager()
    cm.add_contact("Alice", email="alice@example.com")
    diagram = render_social_graph(cm)
    assert "Alice" in diagram.data
    assert "graph TD" in diagram.data


def test_education_curriculum_structure():
    curr = Curriculum("Test", "beginner")
    lesson = curr.add_module("Intro", "Introduction content", duration_minutes=10)
    assert lesson.title == "Intro"
    assert len(curr._modules) == 1
