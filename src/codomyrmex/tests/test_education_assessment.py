"""Property-based tests for EducationDataProvider assessment operations.

# Feature: local-web-viewer
# Tests Properties 12–14 from the design document.

Uses Hypothesis to verify universal correctness properties of
exam creation, grading invariants, and certificate round trips.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.website.education_provider import EducationDataProvider

# ── Strategies ─────────────────────────────────────────────────────

VALID_LEVELS = st.sampled_from(["beginner", "intermediate", "advanced", "expert"])

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
        max_size=40,
    )
    .map(str.strip)
    .filter(lambda s: len(s) > 0)
)

STUDENT_NAMES = (
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

ANSWER_STRINGS = st.text(min_size=0, max_size=50)

SCORES = st.floats(
    min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
)


def _build_provider_with_modules(cur_name, level, mod_names):
    """Helper: create a provider with a curriculum and modules."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, level)
    for mod_name in mod_names:
        provider.add_module(
            cur_name,
            {
                "name": mod_name,
                "content": f"Content for {mod_name}",
                "duration_minutes": 30,
            },
        )
    return provider


# ── Property 12: Exam questions derived from curriculum modules ────
# Feature: local-web-viewer, Property 12: Exam questions derived from curriculum modules
# Validates: Requirements 5.1


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    mod_names=st.lists(MODULE_NAMES, min_size=1, max_size=5, unique=True),
)
@settings(max_examples=100)
def test_property12_exam_questions_derived_from_modules(
    cur_name: str, level: str, mod_names: list[str]
) -> None:
    """Creating an exam (no filter) SHALL return exactly M questions referencing distinct modules."""
    provider = _build_provider_with_modules(cur_name, level, mod_names)
    exam = provider.create_exam(cur_name)

    questions = exam["questions"]
    assert len(questions) == len(mod_names)

    referenced_modules = set()
    for q in questions:
        assert "id" in q
        assert "module" in q
        assert "prompt" in q
        assert "points" in q
        assert "type" in q
        referenced_modules.add(q["module"])

    assert referenced_modules == set(mod_names)


# ── Property 13: Grading invariants ───────────────────────────────
# Feature: local-web-viewer, Property 13: Grading invariants
# Validates: Requirements 5.2


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    mod_names=st.lists(MODULE_NAMES, min_size=1, max_size=5, unique=True),
    answer_text=ANSWER_STRINGS,
)
@settings(max_examples=100)
def test_property13_grading_invariants(
    cur_name: str, level: str, mod_names: list[str], answer_text: str
) -> None:
    """Grading SHALL return earned <= total, score in [0,100], passed iff score >= passing."""
    provider = _build_provider_with_modules(cur_name, level, mod_names)
    exam = provider.create_exam(cur_name)

    # Submit the same answer for every question
    answers = {q["id"]: answer_text for q in exam["questions"]}
    result = provider.grade_submission(cur_name, exam["exam_id"], answers)

    assert result["earned_points"] <= result["total_points"]
    assert 0 <= result["score_percent"] <= 100
    assert result["passed"] == (result["score_percent"] >= 70.0)


# ── Property 14: Certificate create-then-list round trip ──────────
# Feature: local-web-viewer, Property 14: Certificate create-then-list round trip
# Validates: Requirements 5.3, 5.4


@given(
    cur_name=CURRICULUM_NAMES,
    level=VALID_LEVELS,
    student=STUDENT_NAMES,
    score=SCORES,
)
@settings(max_examples=100)
def test_property14_certificate_create_then_list(
    cur_name: str, level: str, student: str, score: float
) -> None:
    """After generating a certificate, listing SHALL include it with matching fields."""
    provider = EducationDataProvider()
    provider.create_curriculum(cur_name, level)

    cert = provider.generate_certificate(student, cur_name, score)

    certs = provider.list_certificates()
    matching = [c for c in certs if c["certificate_id"] == cert["certificate_id"]]
    assert len(matching) == 1

    found = matching[0]
    assert found["student"] == student
    assert found["curriculum"] == cur_name
    assert found["score"] == round(score, 2)
    assert found["passed"] == (score >= 70.0)
    assert len(found["verification_hash"]) > 0
