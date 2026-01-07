"""Tests for SkillLoader."""

import tempfile
from pathlib import Path

import pytest
import yaml

from codomyrmex.skills.skill_loader import SkillLoader


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
def sample_skill():
    """Sample skill data."""
    return {
        "description": "Test skill",
        "patterns": [
            {
                "name": "Test Pattern",
                "description": "A test pattern",
            }
        ],
    }


def test_load_skill_file(temp_dirs, sample_skill):
    """Test loading a skill file."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Create a skill file
    skill_file = upstream_dir / "test-category" / "test-skill" / "skill.yaml"
    skill_file.parent.mkdir(parents=True)
    with open(skill_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_skill, f)

    # Load it
    result = loader.load_skill_file(skill_file)
    assert result is not None
    assert result["description"] == "Test skill"
    assert len(result["patterns"]) == 1


def test_get_merged_skill_upstream_only(temp_dirs, sample_skill):
    """Test getting a skill from upstream only."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Create upstream skill
    skill_file = upstream_dir / "test-category" / "test-skill" / "skill.yaml"
    skill_file.parent.mkdir(parents=True)
    with open(skill_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_skill, f)

    # Get merged skill
    result = loader.get_merged_skill("test-category", "test-skill")
    assert result is not None
    assert result["description"] == "Test skill"
    assert result["_source"] == "upstream"


def test_get_merged_skill_custom_override(temp_dirs, sample_skill):
    """Test custom skill overriding upstream."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Create upstream skill
    upstream_file = upstream_dir / "test-category" / "test-skill" / "skill.yaml"
    upstream_file.parent.mkdir(parents=True)
    with open(upstream_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_skill, f)

    # Create custom skill (overrides upstream)
    custom_skill = sample_skill.copy()
    custom_skill["description"] = "Custom skill"
    custom_file = custom_dir / "test-category" / "test-skill" / "skill.yaml"
    custom_file.parent.mkdir(parents=True)
    with open(custom_file, "w", encoding="utf-8") as f:
        yaml.dump(custom_skill, f)

    # Get merged skill (should be custom)
    result = loader.get_merged_skill("test-category", "test-skill")
    assert result is not None
    assert result["description"] == "Custom skill"
    assert result["_source"] == "custom"


def test_get_merged_skill_not_found(temp_dirs):
    """Test getting a non-existent skill."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    result = loader.get_merged_skill("nonexistent", "skill")
    assert result is None


def test_load_all_skills(temp_dirs, sample_skill):
    """Test loading all skills."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Create multiple skills
    for i in range(3):
        skill_file = upstream_dir / "category1" / f"skill{i}" / "skill.yaml"
        skill_file.parent.mkdir(parents=True)
        skill_data = sample_skill.copy()
        skill_data["description"] = f"Skill {i}"
        with open(skill_file, "w", encoding="utf-8") as f:
            yaml.dump(skill_data, f)

    # Load all
    all_skills = loader.load_all_skills()
    assert "category1" in all_skills
    assert len(all_skills["category1"]) == 3


def test_clear_cache(temp_dirs, sample_skill):
    """Test clearing the cache."""
    upstream_dir, custom_dir, cache_dir = temp_dirs
    loader = SkillLoader(upstream_dir, custom_dir, cache_dir)

    # Load a skill to populate cache
    skill_file = upstream_dir / "test-category" / "test-skill" / "skill.yaml"
    skill_file.parent.mkdir(parents=True)
    with open(skill_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_skill, f)

    loader.get_merged_skill("test-category", "test-skill")
    assert "test-category/test-skill" in loader._cache

    # Clear cache
    loader.clear_cache()
    assert len(loader._cache) == 0

