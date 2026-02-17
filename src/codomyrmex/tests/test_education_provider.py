"""Property-based tests for EducationDataProvider curriculum operations.

# Feature: local-web-viewer
# Tests Properties 2–5 from the design document.

Uses Hypothesis to verify universal correctness properties of
curriculum create, list, add_module, update_module, and export.
"""

from __future__ import annotations

import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.website.education_provider import EducationDataProvider

# ── Strategies ─────────────────────────────────────────────────────

VALID_LEVELS = st.sampled_from(["beginner", "intermediate", "advanced", "expert"])

# Curriculum names: non-empty printable strings without leading/trailing whitespace
CURRICULUM_NAMES = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs"), whitelist_characters="-_"),
    min_size=1,
    max_size=40,
).map(str.strip).filter(lambda s: len(s) > 0)

MODULE_NAMES = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs"), whitelist_characters="-_"),
    min_size=1,
    max_size=40,
).map(str.strip).filter(lambda s: len(s) > 0)

MODULE_CONTENT = st.text(min_size=0, max_size=200)

OBJECTIVES = st.lists(st.text(min_size=1, max_size=60), min_size=0, max_size=5)

EXERCISES = st.lists(
    st.fixed_dictionaries({"prompt": st.text(min_size=1, max_size=80), "solution": st.text(min_size=0, max_size=80)}),
    min_size=0,
    max_size=3,
)

DURATION = st.integers(min_value=1, max_value=600)


# ── Property 2: Curriculum create-then-list round trip ─────────────
# Feature: local-web-viewer, Property 2: Curriculum create-then-list round trip
# Validates: Requirements 2.1, 2.2


@given(name=CURRICULUM_NAMES, level=VALID_LEVELS)
@settings(max_examples=100)
def test_property2_curriculum_create_then_list(name: str, level: str) -> None:
    """After creating a curriculum, listing SHALL return it with correct fields."""
    provider = EducationDataProvider()
    provider.create_curriculum(name, level)

    curricula = provider.list_curricula()
    matching = [c for c in curricula if c["name"] == name]

    assert len(matching) == 1, f"Expected exactly 1 curriculum named '{name}'"
    entry = matching[0]
    assert entry["level"] == level
    assert entry["module_count"] == 0
    assert entry["total_duration_minutes"] == 0


# ── Property 3: Module add-then-read round trip ───────────────────
# Feature: local-web-viewer, Property 3: Module add-then-read round trip
# Validates: Requirements 2.3, 2.4


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    mod_name=MODULE_NAMES,
    content=MODULE_CONTENT,
    objectives=OBJECTIVES,
    exercises=EXERCISES,
    duration=DURATION,
)
@settings(max_examples=100)
def test_property3_module_add_then_read(
    cur_name: str,
    level: str,
    mod_name: str,
    content: str,
    objectives: list[str],
    exercises: list[dict[str, str]],
    duration: int,
) -> None:
    """After adding a module, the curriculum detail SHALL include it."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, level)

    module_data = {
        "name": mod_name,
        "content": content,
        "objectives": objectives if objectives else None,
        "exercises": exercises if exercises else None,
        "duration_minutes": duration,
        "prerequisites": None,
    }
    provider.add_module(cur_name, module_data)

    detail = provider.get_curriculum(cur_name)
    assert detail is not None
    modules = detail["modules"]
    assert len(modules) == 1

    mod = modules[0]
    assert mod["title"] == mod_name
    assert mod["content"] == content
    assert mod["duration_minutes"] == duration
    # Objectives default to [f"Understand {name}"] when None/empty
    if objectives:
        assert mod["objectives"] == objectives
    else:
        assert mod["objectives"] == [f"Understand {mod_name}"]
    # Exercises default to [] when None/empty
    if exercises:
        assert mod["exercises"] == exercises
    else:
        assert mod["exercises"] == []


# ── Property 4: Curriculum export JSON round trip ─────────────────
# Feature: local-web-viewer, Property 4: Curriculum export JSON round trip
# Validates: Requirements 2.5


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    mod_names=st.lists(MODULE_NAMES, min_size=1, max_size=5, unique=True),
)
@settings(max_examples=100)
def test_property4_curriculum_export_json_round_trip(
    cur_name: str,
    level: str,
    mod_names: list[str],
) -> None:
    """Exporting to JSON and parsing SHALL produce matching structure."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, level)

    for mod_name in mod_names:
        provider.add_module(cur_name, {
            "name": mod_name,
            "content": "some content",
            "duration_minutes": 30,
        })

    exported = provider.export_curriculum(cur_name, fmt="json")
    parsed = json.loads(exported)

    assert parsed["name"] == cur_name
    assert parsed["level"] == level
    assert isinstance(parsed["total_duration_minutes"], int)
    assert len(parsed["modules"]) == len(mod_names)


# ── Property 5: Module update-then-read round trip ────────────────
# Feature: local-web-viewer, Property 5: Module update-then-read round trip
# Validates: Requirements 2.7


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    mod_name=MODULE_NAMES,
    new_content=MODULE_CONTENT,
    new_objectives=OBJECTIVES,
    new_exercises=EXERCISES,
    new_duration=DURATION,
)
@settings(max_examples=100)
def test_property5_module_update_then_read(
    cur_name: str,
    level: str,
    mod_name: str,
    new_content: str,
    new_objectives: list[str],
    new_exercises: list[dict[str, str]],
    new_duration: int,
) -> None:
    """After updating a module, the curriculum SHALL show updated values."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, level)
    provider.add_module(cur_name, {
        "name": mod_name,
        "content": "original",
        "duration_minutes": 10,
    })

    update_data = {
        "content": new_content,
        "objectives": new_objectives,
        "exercises": new_exercises,
        "duration_minutes": new_duration,
    }
    provider.update_module(cur_name, mod_name, update_data)

    detail = provider.get_curriculum(cur_name)
    assert detail is not None
    mod = detail["modules"][0]

    assert mod["content"] == new_content
    assert mod["objectives"] == new_objectives
    assert mod["exercises"] == new_exercises
    assert mod["duration_minutes"] == new_duration
