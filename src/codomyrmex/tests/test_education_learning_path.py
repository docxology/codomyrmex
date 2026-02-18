"""Property-based tests for EducationDataProvider learning path operations.

# Feature: local-web-viewer
# Tests Properties 6–7 from the design document.

Uses Hypothesis to verify universal correctness properties of
learning path prerequisite ordering and level filtering.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.website.education_provider import EducationDataProvider

# ── Strategies ─────────────────────────────────────────────────────

VALID_LEVELS = ["beginner", "intermediate", "advanced", "expert"]

CURRICULUM_NAMES = (
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "Zs"), whitelist_characters="-_"
        ),
        min_size=1,
        max_size=40,
    )
    .map(str.strip)
    .filter(lambda s: len(s) > 0)
)

MODULE_NAMES = (
    st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N", "Zs"), whitelist_characters="-_"
        ),
        min_size=1,
        max_size=30,
    )
    .map(str.strip)
    .filter(lambda s: len(s) > 0)
)


# ── Property 6: Learning path respects prerequisites ──────────────
# Feature: local-web-viewer, Property 6: Learning path respects prerequisites
# Validates: Requirements 3.1


@given(
    cur_name=CURRICULUM_NAMES,
    mod_names=st.lists(MODULE_NAMES, min_size=2, max_size=5, unique=True),
)
@settings(max_examples=100)
def test_property6_learning_path_respects_prerequisites(
    cur_name: str, mod_names: list[str]
) -> None:
    """The learning path SHALL be a topological ordering where every module
    appears after all of its prerequisites."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, "beginner")

    # First module has no prerequisites; each subsequent depends on the previous
    for i, mod_name in enumerate(mod_names):
        prereqs = [mod_names[i - 1]] if i > 0 else []
        provider.add_module(
            cur_name,
            {
                "name": mod_name,
                "content": f"Content for {mod_name}",
                "duration_minutes": 30,
                "prerequisites": prereqs,
            },
        )

    result = provider.get_learning_path(cur_name, level="beginner")
    path = result["path"]

    # Every module in the chain should appear in the path
    assert set(path) == set(mod_names)

    # Verify topological order: each module appears after its prerequisites
    position = {name: idx for idx, name in enumerate(path)}
    for i, mod_name in enumerate(mod_names):
        if i > 0:
            prereq = mod_names[i - 1]
            msg = f"Prerequisite '{prereq}' should appear before '{mod_name}'"
            assert position[prereq] < position[mod_name], msg


# ── Property 7: Learning path level filtering reduces or preserves path length ──
# Feature: local-web-viewer, Property 7: Learning path level filtering reduces or preserves path length
# Validates: Requirements 3.2


@given(
    cur_name=CURRICULUM_NAMES,
    mod_names=st.lists(MODULE_NAMES, min_size=2, max_size=6, unique=True),
    level_a_idx=st.integers(min_value=0, max_value=2),
)
@settings(max_examples=100)
def test_property7_level_filtering_reduces_or_preserves_length(
    cur_name: str, mod_names: list[str], level_a_idx: int
) -> None:
    """For level A < level B, the path for B SHALL have length <= path for A."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, "beginner")

    for i, mod_name in enumerate(mod_names):
        prereqs = [mod_names[i - 1]] if i > 0 else []
        provider.add_module(
            cur_name,
            {
                "name": mod_name,
                "content": f"Content for {mod_name}",
                "duration_minutes": 30,
                "prerequisites": prereqs,
            },
        )

    level_a = VALID_LEVELS[level_a_idx]
    level_b = VALID_LEVELS[level_a_idx + 1]

    path_a = provider.get_learning_path(cur_name, level=level_a)["path"]
    path_b = provider.get_learning_path(cur_name, level=level_b)["path"]

    msg = (
        f"Path for '{level_b}' ({len(path_b)}) "
        f"should be <= path for '{level_a}' ({len(path_a)})"
    )
    assert len(path_b) <= len(path_a), msg
