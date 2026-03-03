import pytest

from codomyrmex.agentic_memory import mcp_tools
from codomyrmex.agentic_memory.mcp_tools import memory_get, memory_put, memory_search


@pytest.fixture(autouse=True)
def _reset_store():
    store = mcp_tools._get_store()
    store._data.clear()


@pytest.mark.unit
def test_memory_put_and_get():
    mem_dict = memory_put(
        content="Test memory", memory_type="episodic", importance="high"
    )
    assert mem_dict["content"] == "Test memory"
    assert mem_dict["memory_type"] == "episodic"
    assert mem_dict["importance"] == 3  # HIGH
    mem_id = mem_dict["id"]

    retrieved_dict = memory_get(memory_id=mem_id)
    assert retrieved_dict is not None
    assert retrieved_dict["id"] == mem_id
    assert retrieved_dict["content"] == "Test memory"


@pytest.mark.unit
def test_memory_get_not_found():
    assert memory_get(memory_id="missing-id") is None


@pytest.mark.unit
def test_memory_search():
    memory_put(content="The quick brown fox jumps over the lazy dog", importance="low")
    memory_put(content="Something completely different", importance="medium")

    results = memory_search(query="fox", k=5)
    assert len(results) > 0
    assert "fox" in results[0]["memory"]["content"]
