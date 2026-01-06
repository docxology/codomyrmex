"""Real-world scenario tests for agent usage patterns."""

import pytest
from unittest.mock import Mock, patch

from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.generic import BaseAgent, AgentOrchestrator
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter


class MockAgent(BaseAgent):
    """Mock agent for real-world scenario testing."""

    def __init__(self, name: str, capabilities: list[AgentCapabilities], should_succeed: bool = True):
        super().__init__(name=name, capabilities=capabilities, config={})
        self.execution_history = []
        self.execution_count = 0
        self.should_succeed = should_succeed

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        self.execution_count += 1
        self.execution_history.append({
            "prompt": request.prompt,
            "context": request.context,
            "capabilities": request.capabilities
        })
        
        if not self.should_succeed:
            return AgentResponse(content="", error="Simulated failure")
        
        # Simulate different responses based on prompt
        if "generate" in request.prompt.lower():
            return AgentResponse(
                content="def generated_function():\n    return 'result'",
                metadata={"type": "code_generation"}
            )
        elif "review" in request.prompt.lower():
            return AgentResponse(
                content="Code review: Looks good, minor suggestions",
                metadata={"type": "code_review"}
            )
        elif "analyze" in request.prompt.lower():
            return AgentResponse(
                content="Analysis: Code complexity is moderate",
                metadata={"type": "analysis"}
            )
        else:
            return AgentResponse(
                content=f"Response to: {request.prompt}",
                metadata={"type": "general"}
            )

    def _stream_impl(self, request: AgentRequest):
        response = self._execute_impl(request)
        for word in response.content.split():
            yield word + " "


class TestSimpleScenarios:
    """Simple real-world scenarios."""

    def test_basic_code_generation_request(self):
        """Test basic code generation request."""
        agent = MockAgent("code_gen", [AgentCapabilities.CODE_GENERATION])
        
        request = AgentRequest(
            prompt="Generate a Python function to calculate fibonacci",
            capabilities=[AgentCapabilities.CODE_GENERATION]
        )
        
        response = agent.execute(request)
        
        assert response.is_success()
        assert "def" in response.content
        assert response.metadata["type"] == "code_generation"

    def test_simple_text_completion(self):
        """Test simple text completion."""
        agent = MockAgent("text", [AgentCapabilities.TEXT_COMPLETION])
        
        request = AgentRequest(
            prompt="Complete this sentence: The weather today is",
            capabilities=[AgentCapabilities.TEXT_COMPLETION]
        )
        
        response = agent.execute(request)
        
        assert response.is_success()
        assert len(response.content) > 0

    def test_single_file_code_analysis(self):
        """Test analyzing a single file."""
        agent = MockAgent("analyzer", [AgentCapabilities.CODE_ANALYSIS])
        
        code_content = """
def example_function():
    x = 1
    y = 2
    return x + y
"""
        
        request = AgentRequest(
            prompt="Analyze this code",
            context={"code": code_content, "language": "python"},
            capabilities=[AgentCapabilities.CODE_ANALYSIS]
        )
        
        response = agent.execute(request)
        
        assert response.is_success()
        assert response.metadata["type"] == "analysis"


class TestComplexScenarios:
    """Complex real-world scenarios."""

    def test_multi_step_code_generation_with_context(self):
        """Test multi-step code generation with context passing."""
        agent = MockAgent("code_gen", [AgentCapabilities.CODE_GENERATION])
        
        # Step 1: Generate initial function
        request1 = AgentRequest(
            prompt="Generate a function to calculate factorial",
            context={"step": 1}
        )
        response1 = agent.execute(request1)
        
        assert response1.is_success()
        generated_code = response1.content
        
        # Step 2: Enhance with context from step 1
        request2 = AgentRequest(
            prompt="Add error handling to this function",
            context={
                "step": 2,
                "previous_code": generated_code,
                "previous_response": response1.content
            }
        )
        response2 = agent.execute(request2)
        
        assert response2.is_success()
        assert len(agent.execution_history) == 2

    def test_code_review_workflow_with_multiple_agents(self):
        """Test code review workflow using multiple agents."""
        code_gen_agent = MockAgent("code_gen", [AgentCapabilities.CODE_GENERATION])
        review_agent = MockAgent("reviewer", [AgentCapabilities.CODE_ANALYSIS])
        
        orchestrator = AgentOrchestrator([code_gen_agent, review_agent])
        
        # Step 1: Generate code
        gen_request = AgentRequest(
            prompt="Generate a REST API endpoint",
            capabilities=[AgentCapabilities.CODE_GENERATION]
        )
        gen_responses = orchestrator.execute_parallel(gen_request)
        generated_code = gen_responses[0].content
        
        # Step 2: Review the generated code
        review_request = AgentRequest(
            prompt="Review this code for best practices",
            context={"code": generated_code},
            capabilities=[AgentCapabilities.CODE_ANALYSIS]
        )
        review_responses = orchestrator.execute_parallel(review_request)
        
        assert len(gen_responses) == 2
        assert len(review_responses) == 2
        assert any("review" in r.content.lower() or "analysis" in r.content.lower() 
                  for r in review_responses)

    def test_complex_refactoring_across_multiple_files(self):
        """Test complex refactoring scenario across multiple files."""
        agent = MockAgent("refactor", [
            AgentCapabilities.CODE_GENERATION,
            AgentCapabilities.CODE_EDITING
        ])
        
        files = {
            "file1.py": "class OldClass:\n    pass",
            "file2.py": "from file1 import OldClass",
            "file3.py": "def use_old_class():\n    obj = OldClass()"
        }
        
        # Step 1: Analyze all files
        analyze_request = AgentRequest(
            prompt="Analyze these files for refactoring opportunities",
            context={"files": files}
        )
        analyze_response = agent.execute(analyze_request)
        
        # Step 2: Generate refactored version
        refactor_request = AgentRequest(
            prompt="Refactor OldClass to NewClass across all files",
            context={
                "files": files,
                "analysis": analyze_response.content
            }
        )
        refactor_response = agent.execute(refactor_request)
        
        assert analyze_response.is_success()
        assert refactor_response.is_success()
        assert len(agent.execution_history) == 2

    def test_multi_agent_codebase_analysis(self):
        """Test multi-agent codebase analysis."""
        structure_agent = MockAgent("structure", [AgentCapabilities.CODE_ANALYSIS])
        quality_agent = MockAgent("quality", [AgentCapabilities.CODE_ANALYSIS])
        security_agent = MockAgent("security", [AgentCapabilities.CODE_ANALYSIS])
        
        orchestrator = AgentOrchestrator([
            structure_agent,
            quality_agent,
            security_agent
        ])
        
        request = AgentRequest(
            prompt="Analyze codebase structure, quality, and security",
            context={"codebase_path": "/path/to/codebase"},
            capabilities=[AgentCapabilities.CODE_ANALYSIS]
        )
        
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)
        
        # Each agent should have executed
        assert structure_agent.execution_count == 1
        assert quality_agent.execution_count == 1
        assert security_agent.execution_count == 1

    def test_error_recovery_and_retry_scenarios(self):
        """Test error recovery and retry scenarios."""
        failing_agent = MockAgent("failing", [AgentCapabilities.CODE_GENERATION])
        backup_agent = MockAgent("backup", [AgentCapabilities.CODE_GENERATION])
        
        # Make first agent fail
        failing_agent.should_succeed = False
        
        orchestrator = AgentOrchestrator([failing_agent, backup_agent])
        
        request = AgentRequest(prompt="Generate code")
        
        # Use fallback strategy
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()
        assert "backup" in response.content or "backup" in str(response.metadata)

    def test_context_management_across_operations(self):
        """Test managing context across multiple operations."""
        agent = MockAgent("context_agent", [AgentCapabilities.CODE_GENERATION])
        
        # Build up context across operations
        context = {"project": "test_project", "language": "python"}
        
        request1 = AgentRequest(
            prompt="Generate initial structure",
            context=context
        )
        response1 = agent.execute(request1)
        
        # Update context with results
        context["initial_structure"] = response1.content
        context["step"] = 2
        
        request2 = AgentRequest(
            prompt="Add implementation details",
            context=context
        )
        response2 = agent.execute(request2)
        
        # Verify context was maintained
        assert len(agent.execution_history) == 2
        assert agent.execution_history[0]["context"]["project"] == "test_project"
        assert agent.execution_history[1]["context"]["step"] == 2
        assert "initial_structure" in agent.execution_history[1]["context"]

    def test_capability_based_workflow(self):
        """Test workflow that selects agents by capability."""
        code_gen = MockAgent("gen", [AgentCapabilities.CODE_GENERATION])
        code_edit = MockAgent("edit", [AgentCapabilities.CODE_EDITING])
        code_analyze = MockAgent("analyze", [AgentCapabilities.CODE_ANALYSIS])
        
        orchestrator = AgentOrchestrator([code_gen, code_edit, code_analyze])
        
        # Workflow: Generate -> Edit -> Analyze
        # Step 1: Generate
        gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        gen_request = AgentRequest(
            prompt="Generate code",
            capabilities=[AgentCapabilities.CODE_GENERATION]
        )
        gen_response = gen_agents[0].execute(gen_request)
        
        # Step 2: Edit
        edit_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_EDITING.value
        )
        edit_request = AgentRequest(
            prompt="Edit and improve",
            context={"code": gen_response.content},
            capabilities=[AgentCapabilities.CODE_EDITING]
        )
        edit_response = edit_agents[0].execute(edit_request)
        
        # Step 3: Analyze
        analyze_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_ANALYSIS.value
        )
        analyze_request = AgentRequest(
            prompt="Analyze final code",
            context={"code": edit_response.content},
            capabilities=[AgentCapabilities.CODE_ANALYSIS]
        )
        analyze_response = analyze_agents[0].execute(analyze_request)
        
        assert gen_response.is_success()
        assert edit_response.is_success()
        assert analyze_response.is_success()

    def test_integration_adapter_real_world_usage(self):
        """Test integration adapter in real-world usage."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="def api_endpoint():\n    return {'status': 'ok'}",
                stderr=""
            )
            
            client = OpenCodeClient()
            adapter = OpenCodeIntegrationAdapter(client)
            
            # Use adapter for code generation
            code = adapter.adapt_for_ai_code_editing(
                prompt="Create a REST API endpoint",
                language="python"
            )
            
            assert "def" in code or "api" in code.lower()

