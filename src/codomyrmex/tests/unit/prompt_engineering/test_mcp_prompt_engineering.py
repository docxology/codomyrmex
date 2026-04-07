from codomyrmex.prompt_engineering.mcp_tools import (
    prompt_evaluate,
    prompt_list_strategies,
    prompt_list_templates,
)
from codomyrmex.prompt_engineering.templates import PromptTemplate, get_default_registry


def test_prompt_list_templates():
    """Test prompt_list_templates MCP tool without mocks."""
    registry = get_default_registry()

    # Store existing to restore later
    original_templates = registry._templates.copy()

    try:
        # Clear default registry and add test templates
        registry._templates.clear()

        template1 = PromptTemplate(name="test_tool_t1", template_str="Hello {name}")
        template2 = PromptTemplate(name="test_tool_t2", template_str="Goodbye {name}")

        registry.add(template1)
        registry.add(template2)

        result = prompt_list_templates()

        assert isinstance(result, list)
        assert len(result) == 2
        assert "test_tool_t1" in result
        assert "test_tool_t2" in result

    finally:
        # Restore original templates
        registry._templates.clear()
        registry._templates.update(original_templates)


def test_prompt_list_strategies():
    """Test prompt_list_strategies MCP tool without mocks."""
    result = prompt_list_strategies()

    assert isinstance(result, list)
    assert len(result) >= 0
    # Even if empty, it should be a list of strings
    if result:
        assert isinstance(result[0], str)


def test_prompt_evaluate():
    """Test prompt_evaluate MCP tool without mocks."""
    prompt = "What is the capital of France?"
    response = "The capital of France is Paris."

    result = prompt_evaluate(prompt, response)

    assert isinstance(result, dict)
    assert "weighted_score" in result
    assert isinstance(result["weighted_score"], (int, float))
    assert "scores" in result
    assert isinstance(result["scores"], dict)
