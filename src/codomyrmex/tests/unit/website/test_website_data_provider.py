
import pytest

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
    """Test functionality: get system summary."""
    provider = DataProvider(mock_root)
    summary = provider.get_system_summary()
    assert summary["status"] == "Operational"
    assert "agent_count" in summary

@pytest.mark.unit
def test_get_modules(mock_root):
    """Test functionality: get modules."""
    provider = DataProvider(mock_root)
    modules = provider.get_modules()

    assert len(modules) == 1
    assert modules[0]["name"] == "fake_agent"
    assert modules[0]["description"] == "Test Description"
    assert modules[0]["status"] == "Active"

@pytest.mark.unit
def test_get_description_fallback(mock_root):
    """Test functionality: get description fallback."""
    # Create module without description
    agent_dir = mock_root / "src" / "codomyrmex" / "mystery_agent"
    agent_dir.mkdir()
    (agent_dir / "__init__.py").touch()

    provider = DataProvider(mock_root)
    modules = provider.get_modules()

    # Sort to find the mystery one or check by name
    mystery = next(a for a in modules if a["name"] == "mystery_agent")
    assert mystery["description"] == "No description available"
