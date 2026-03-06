"""
Tests for LLM Chain implementations.
"""

import json

import pytest

from codomyrmex.llm.chains import (
    ChainOfThought,
    ChainStep,
    ChainType,
    ReActChain,
    SequentialChain,
    SimpleChain,
    create_chain,
    json_parser,
    list_parser,
)


class TestChainStep:
    """Tests for ChainStep."""

    def test_format_prompt(self):
        """Should format prompt with context."""
        step = ChainStep(
            name="test",
            prompt_template="Hello {name}, welcome to {place}!",
        )
        prompt = step.format_prompt({"name": "Alice", "place": "Wonderland"})
        assert prompt == "Hello Alice, welcome to Wonderland!"

    def test_parse_output(self):
        """Should parse output using parser function."""
        step = ChainStep(
            name="test",
            prompt_template="test",
            parser=lambda x: x.upper(),
        )
        assert step.parse_output("hello") == "HELLO"

class TestSimpleChain:
    """Tests for SimpleChain."""

    def test_run_success(self):
        """Should run single step successfully."""
        chain = SimpleChain(prompt_template="Echo: {input}", name="echo_chain")

        def mock_llm(prompt):
            return f"LLM received: {prompt}"

        result = chain.run({"input": "hello"}, mock_llm)

        assert result.success is True
        assert result.output == "LLM received: Echo: hello"
        assert len(result.steps) == 1
        assert result.steps[0]["name"] == "echo_chain"

    def test_run_failure(self):
        """Should handle exceptions in llm_func."""
        chain = SimpleChain(prompt_template="test")

        def failing_llm(prompt):
            raise ValueError("LLM error")

        result = chain.run({}, failing_llm)
        assert result.success is False
        assert "LLM error" in (result.error or "")

class TestSequentialChain:
    """Tests for SequentialChain."""

    def test_run_sequential_steps(self):
        """Should pass context between steps."""
        chain = SequentialChain(name="seq_chain")
        chain.add_step(ChainStep(
            name="step1",
            prompt_template="Upper {input}",
            output_key="upper_val",
            parser=lambda x: x.upper()
        ))
        chain.add_step(ChainStep(
            name="step2",
            prompt_template="Reverse {upper_val}",
            output_key="final_val",
            parser=lambda x: x[::-1]
        ))

        def mock_llm(prompt):
            if "Upper" in prompt:
                return prompt.split(" ")[1]
            if "Reverse" in prompt:
                return prompt.split(" ")[1]
            return "error"

        result = chain.run({"input": "hello"}, mock_llm)

        assert result.success is True
        assert result.output == "OLLEH"
        assert result.context["upper_val"] == "HELLO"
        assert result.context["final_val"] == "OLLEH"
        assert len(result.steps) == 2

class TestChainOfThought:
    """Tests for ChainOfThought chain."""

    def test_cot_structure(self):
        """Should have reasoning and answer steps."""
        chain = ChainOfThought()
        assert len(chain.steps) == 2
        assert chain.steps[0].name == "reasoning"
        assert chain.steps[1].name == "answer"

    def test_cot_run(self):
        """Should run CoT steps."""
        chain = ChainOfThought()

        def mock_llm(prompt):
            if "Think through this step-by-step" in prompt:
                return "Reasoning: 1+1 is 2"
            if "Based on this reasoning" in prompt:
                return "Final Answer: 2"
            return "unknown"

        result = chain.run({"question": "1+1?"}, mock_llm)
        assert result.success is True
        assert "Final Answer: 2" in result.output

class TestReActChain:
    """Tests for ReActChain."""

    def test_react_success(self):
        """Should interact with tools and finish."""
        tools = {
            "search": lambda x: f"Found info about {x}"
        }
        chain = ReActChain(tools=tools, max_iterations=3)

        def mock_llm(prompt):
            if "Observation" not in prompt:
                return "Thought: I need to search.\nAction: search[python]"
            return "Thought: I have info.\nAction: Finish[Python is great]"

        result = chain.run({"question": "What is python?"}, mock_llm)

        assert result.success is True
        assert result.output == "Python is great"
        assert len(result.steps) == 1
        assert result.steps[0]["action"] == "search"
        assert "Found info about python" in result.steps[0]["observation"]

    def test_react_max_iterations(self):
        """Should stop after max iterations."""
        chain = ReActChain(tools={}, max_iterations=2)

        def infinite_llm(prompt):
            return "Thought: keep going.\nAction: unknown[test]"

        result = chain.run({"question": "test"}, infinite_llm)
        assert result.success is False
        assert "Max iterations reached" in (result.error or "")

class TestFactory:
    """Tests for create_chain factory."""

    def test_create_simple(self):
        chain = create_chain(ChainType.SIMPLE, prompt_template="test")
        assert isinstance(chain, SimpleChain)

    def test_create_sequential(self):
        chain = create_chain(ChainType.SEQUENTIAL)
        assert isinstance(chain, SequentialChain)

    def test_create_invalid(self):
        with pytest.raises(ValueError):
            create_chain("invalid_type")

class TestParsers:
    """Tests for output parsers."""

    def test_json_parser(self):
        assert json_parser('{"a": 1}') == {"a": 1}
        assert json_parser('```json\n{"a": 1}\n```') == {"a": 1}
        with pytest.raises(json.JSONDecodeError):
            json_parser("invalid")

    def test_list_parser(self):
        output = "1. Item one\n2. Item two\n- Item three"
        items = list_parser(output)
        assert items == ["Item one", "Item two", "Item three"]
