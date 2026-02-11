import pytest
from codomyrmex.finance.visualization import plot_account_balances, plot_transaction_volume
from codomyrmex.finance.ledger import Ledger, AccountType, Transaction
from codomyrmex.bio_simulation.visualization import render_colony_state
from codomyrmex.bio_simulation.colony import Colony
from codomyrmex.relations.visualization import render_social_graph
from codomyrmex.relations.crm import CRM, Contact
from codomyrmex.education.visualization import render_curriculum_path
from codomyrmex.education.curriculum import Curriculum, Lesson, Difficulty

def test_finance_visualization():
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Sales", AccountType.REVENUE)
    ledger.record(Transaction("Cash", "Sales", 100.0, "Sale"))
    
    # We just check that it runs without error and returns something (string or object)
    assert plot_account_balances(ledger) is not None
    assert plot_transaction_volume(ledger) is not None

def test_bio_sim_visualization():
    colony = Colony(population_size=10)
    assert render_colony_state(colony) is not None

def test_relations_visualization():
    crm = CRM()
    crm.add_contact(Contact("Alice"))
    diagram = render_social_graph(crm)
    assert "Alice" in diagram.data
    assert "graph TD" in diagram.data

def test_education_visualization():
    curr = Curriculum("Test", Difficulty.BEGINNER)
    l1 = Lesson("Intro", "", Difficulty.BEGINNER, 10)
    curr.add_lesson(l1)
    diagram = render_curriculum_path(curr)
    assert "Intro" in diagram.data
    assert "graph LR" in diagram.data
