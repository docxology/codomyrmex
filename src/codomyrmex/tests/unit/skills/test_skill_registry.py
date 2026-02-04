"""Tests for SkillRegistry."""

import tempfile
from pathlib import Path

import pytest
import yaml

from codomyrmex.skills.skill_loader import SkillLoader
from codomyrmex.skills.skill_registry import SkillRegistry


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        upstream_dir = Path(tmpdir) / "upstream"
        custom_dir = Path(tmpdir) / "custom"
        cache_dir = Path(tmpdir) / "cache"

        upstream_dir.mkdir(parents=True)
        custom_dir.mkdir(parents=True)
        cache_dir.mkdir(parents=True)

        yield upstream_dir, custom_dir, cache_dir


@pytest.fixture
def populated_registry(temp_dirs):
    """Create a registry with some test skills."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Create test skills
    skills = [
        ("backend", "api-design", {
            "description": "API design patterns",
            "patterns": [{"name": "REST", "description": "RESTful API design"}],
        }),
        ("backend", "database", {
            "description": "Database management patterns",
            "patterns": [{"name": "ORM", "description": "Object relational mapping"}],
            "anti_patterns": [{"name": "N+1", "why_bad": "Performance"}],
        }),
        ("frontend", "react", {
            "description": "React development patterns",
            "patterns": [{"name": "Hooks", "description": "React hooks"}],
        }),
    ]

    for category, name, data in skills:
        skill_dir = upstream_dir / category / name
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "skill.yaml"
        with open(skill_file, "w") as f:
            yaml.dump(data, f)

    registry = SkillRegistry(loader)
    return registry


@pytest.mark.unit
def test_build_index(populated_registry):
    """Test that index builds from loaded skills."""
    index = populated_registry.build_index()
    assert "backend" in index
    assert "frontend" in index
    assert "api-design" in index["backend"]
    assert "database" in index["backend"]
    assert "react" in index["frontend"]


@pytest.mark.unit
def test_get_categories(populated_registry):
    """Test that get_categories returns sorted list."""
    categories = populated_registry.get_categories()
    assert categories == ["backend", "frontend"]


@pytest.mark.unit
def test_get_skill_metadata(populated_registry):
    """Test getting metadata for a specific skill."""
    metadata = populated_registry.get_skill_metadata("backend", "api-design")
    assert metadata is not None
    assert metadata["category"] == "backend"
    assert metadata["name"] == "api-design"
    assert metadata["has_patterns"] is True


@pytest.mark.unit
def test_search_by_pattern(populated_registry):
    """Test pattern-based search."""
    results = populated_registry.search_by_pattern("api")
    assert len(results) >= 1
    names = [r["name"] for r in results]
    assert "api-design" in names


@pytest.mark.unit
def test_search_by_pattern_regex(populated_registry):
    """Test regex pattern search."""
    results = populated_registry.search_by_pattern(r"react|database")
    assert len(results) >= 2
    names = [r["name"] for r in results]
    assert "react" in names
    assert "database" in names


@pytest.mark.unit
def test_search_skills(populated_registry):
    """Test full text search returns data."""
    results = populated_registry.search_skills("REST")
    assert len(results) >= 1
    assert "data" in results[0]
    assert "metadata" in results[0]


@pytest.mark.unit
def test_get_index(populated_registry):
    """Test get_index auto-builds on first access."""
    # Registry hasn't been built yet, get_index should trigger build
    index = populated_registry.get_index()
    assert len(index) > 0
    assert "backend" in index


@pytest.mark.unit
def test_refresh_index(populated_registry):
    """Test refresh_index clears cache and rebuilds."""
    # Build index first
    populated_registry.build_index()
    assert len(populated_registry._index) > 0

    # Refresh should rebuild
    populated_registry.refresh_index()
    assert len(populated_registry._index) > 0
    assert "backend" in populated_registry._index
