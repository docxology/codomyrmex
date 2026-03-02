import pytest
from codomyrmex.cerebrum import (
    WorkingMemory, 
    ReasoningChain, 
    DecisionModule, 
    CerebrumEngine,
    Case
)

@pytest.mark.unit
class TestCognitiveComponents:
    """Zero-mock tests for new cognitive components."""

    def test_working_memory(self):
        memory = WorkingMemory()
        memory.store("goal", "test")
        assert memory.retrieve("goal") == "test"
        assert "goal" in memory.list_keys()
        
        memory.delete("goal")
        assert memory.retrieve("goal") is None
        
        memory.store("x", 1)
        memory.clear()
        assert memory.list_keys() == []

    def test_reasoning_chain(self):
        chain = ReasoningChain()
        memory = WorkingMemory()
        
        chain.add_step("Step 1", lambda m: m.store("val", 10))
        chain.add_step("Step 2", lambda m: m.retrieve("val") * 2)
        
        result = chain.execute(memory)
        assert result.success
        assert result.steps_completed == 2
        assert result.steps[1].result == 20
        assert memory.retrieve("val") == 10

    def test_reasoning_chain_failure(self):
        chain = ReasoningChain()
        memory = WorkingMemory()
        
        def failing_action(m):
            raise ValueError("Failure")
            
        chain.add_step("Good step", lambda m: "ok")
        chain.add_step("Bad step", failing_action)
        chain.add_step("Unreached step", lambda m: "never")
        
        result = chain.execute(memory)
        assert not result.success
        assert result.steps_completed == 1
        assert result.steps[1].status == "failed"
        assert result.steps[2].status == "pending"

    def test_decision_module(self):
        dm = DecisionModule()
        options = ["A", "B", "C"]
        criteria = {"cost": 0.5, "quality": 0.5}
        context = {}
        
        decision = dm.decide(options, criteria, context)
        assert decision.choice in options
        assert 0 <= decision.confidence <= 1
        assert decision.rationale != ""

    def test_engine_integration(self):
        engine = CerebrumEngine()
        
        # Test decide via engine
        decision = engine.decide(["Option 1"], {"weight": 1.0})
        assert decision.choice == "Option 1"
        
        # Test reasoning chain via engine
        chain = engine.create_reasoning_chain()
        chain.add_step("test", lambda m: "done")
        res = chain.execute(engine.working_memory)
        assert res.success
        assert res.steps[0].result == "done"

@pytest.mark.unit
class TestReasoningEngineEnhanced:
    """Test ReasoningEngine with enhanced functionality."""
    
    def test_reasoning_with_retrieval(self):
        engine = CerebrumEngine()
        engine.add_case(Case(case_id="c1", features={"f1": 1}, outcome="out1"))
        
        query = Case(case_id="q", features={"f1": 1})
        result = engine.reason(query)
        
        assert result.prediction == "out1"
        assert len(result.retrieved_cases) == 1
        assert result.retrieved_cases[0].case_id == "c1"
