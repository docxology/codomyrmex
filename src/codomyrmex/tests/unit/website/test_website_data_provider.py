import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from codomyrmex.website.data_provider import DataProvider

@pytest.fixture
def mock_root(tmp_path):
    # Create a fake project structure
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)
    
    # Create a fake agent
    agent_dir = src / "fake_agent"
    agent_dir.mkdir()
    (agent_dir / "__init__.py").touch()
    (agent_dir / "AGENTS.md").write_text("Test Description")
    
    return tmp_path

@pytest.mark.unit
def test_get_system_summary(mock_root):
    provider = DataProvider(mock_root)
    summary = provider.get_system_summary()
    assert summary["status"] == "Operational"
    assert "agent_count" in summary

@pytest.mark.unit
def test_get_agents_status(mock_root):
    provider = DataProvider(mock_root)
    agents = provider.get_agents_status()
    
    assert len(agents) == 1
    assert agents[0]["name"] == "fake_agent"
    assert agents[0]["description"] == "Test Description"
    assert agents[0]["status"] == "Active"

@pytest.mark.unit
def test_get_description_fallback(mock_root):
    # Create agent without description
    agent_dir = mock_root / "src" / "codomyrmex" / "mystery_agent"
    agent_dir.mkdir()
    (agent_dir / "__init__.py").touch()
    
    provider = DataProvider(mock_root)
    agents = provider.get_agents_status()
    
    # Sort to find the mystery one or check by name
    mystery = next(a for a in agents if a["name"] == "mystery_agent")
    assert mystery["description"] == "No description available"
