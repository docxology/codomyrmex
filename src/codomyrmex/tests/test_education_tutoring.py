"""Property-based tests for EducationDataProvider tutoring operations.

# Feature: local-web-viewer
# Tests Properties 8–11 from the design document.

Uses Hypothesis to verify universal correctness properties of
session creation, quiz generation, answer evaluation, and session progress.
"""

from __future__ import annotations

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from codomyrmex.website.education_provider import EducationDataProvider

# ── Strategies ─────────────────────────────────────────────────────

AVAILABLE_TOPICS = st.sampled_from(["python_basics", "data_structures"])
QUIZ_DIFFICULTIES = st.sampled_from(["easy", "medium", "hard"])
DIFFICULTY_ORDER = ["easy", "medium", "hard"]

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

ANSWER_STRINGS = st.text(min_size=0, max_size=100)


# ── Property 8: Session creation returns correct data ──────────────
# Feature: local-web-viewer, Property 8: Session creation returns correct data
# Validates: Requirements 4.1


@given(student_name=STUDENT_NAMES, topic=AVAILABLE_TOPICS)
@settings(max_examples=100)
def test_property8_session_creation_returns_correct_data(
    student_name: str, topic: str
) -> None:
    """Creating a session SHALL return non-empty session_id, exact student_name, and exact topic."""
    provider = EducationDataProvider()
    result = provider.create_session(student_name, topic)

    assert "session_id" in result
    assert isinstance(result["session_id"], str)
    assert len(result["session_id"]) > 0
    assert result["student_name"] == student_name
    assert result["topic"] == topic


# ── Property 9: Quiz questions respect difficulty filter and contain required fields ──
# Feature: local-web-viewer, Property 9: Quiz questions respect difficulty filter and contain required fields
# Validates: Requirements 4.2, 4.6


@given(topic=AVAILABLE_TOPICS, difficulty=QUIZ_DIFFICULTIES)
@settings(max_examples=100)
def test_property9_quiz_questions_respect_difficulty_and_fields(
    topic: str, difficulty: str
) -> None:
    """All returned questions SHALL have difficulty >= requested, required fields, and no _answer."""
    provider = EducationDataProvider()
    questions = provider.generate_quiz(topic=topic, difficulty=difficulty, count=10)

    min_idx = DIFFICULTY_ORDER.index(difficulty)

    for q in questions:
        # Required fields present
        assert "id" in q
        assert "question" in q
        assert "choices" in q
        assert isinstance(q["choices"], list)
        assert len(q["choices"]) > 0
        assert "difficulty" in q

        # No _answer exposed
        assert "_answer" not in q

        # Difficulty at or above requested level
        q_idx = DIFFICULTY_ORDER.index(q["difficulty"])
        msg = f"Question difficulty '{q['difficulty']}' below requested '{difficulty}'"
        assert q_idx >= min_idx, msg


# ── Property 10: Answer evaluation consistency ────────────────────
# Feature: local-web-viewer, Property 10: Answer evaluation consistency
# Validates: Requirements 4.3


@given(topic=AVAILABLE_TOPICS, answer=ANSWER_STRINGS)
@settings(max_examples=100)
def test_property10_answer_evaluation_consistency(topic: str, answer: str) -> None:
    """Evaluating an answer SHALL return correct=True iff answer matches expected (case-insensitive, trimmed),
    and feedback SHALL be non-empty."""
    provider = EducationDataProvider()
    questions = provider.generate_quiz(topic=topic, difficulty="easy", count=5)
    assume(len(questions) > 0)

    q = questions[0]
    result = provider.evaluate_answer(q["id"], answer)

    assert "correct" in result
    assert "feedback" in result
    assert isinstance(result["correct"], bool)
    assert isinstance(result["feedback"], str)
    assert len(result["feedback"]) > 0

    # Verify correctness matches expected answer
    expected = result.get("expected", "")
    should_be_correct = answer.strip().lower() == expected.strip().lower()
    assert result["correct"] == should_be_correct


# ── Property 11: Session progress internal consistency ─────────────
# Feature: local-web-viewer, Property 11: Session progress internal consistency
# Validates: Requirements 4.4


@given(
    student_name=STUDENT_NAMES,
    topic=AVAILABLE_TOPICS,
    answers=st.lists(ANSWER_STRINGS, min_size=0, max_size=5),
)
@settings(max_examples=100)
def test_property11_session_progress_internal_consistency(
    student_name: str, topic: str, answers: list[str]
) -> None:
    """After N recorded answers, progress SHALL report questions_asked=N,
    correct_answers = count of correct in history, accuracy = correct/asked (or 0),
    and history length = N."""
    provider = EducationDataProvider()
    session = provider.create_session(student_name, topic)
    sid = session["session_id"]

    # Generate enough questions
    questions = provider.generate_quiz(
        topic=topic, difficulty="easy", count=max(len(answers), 1)
    )
    assume(len(questions) >= len(answers))

    # Record each answer
    for i, ans in enumerate(answers):
        provider.record_answer(sid, questions[i]["id"], ans)

    progress = provider.get_session_progress(sid)

    n = len(answers)
    assert progress["questions_asked"] == n
    assert progress["history"] is not None
    assert len(progress["history"]) == n

    # Count correct from history
    correct_count = sum(1 for h in progress["history"] if h["correct"])
    assert progress["correct_answers"] == correct_count

    # Accuracy check
    if n == 0:
        assert progress["accuracy"] == 0.0
    else:
        expected_accuracy = round(correct_count / n, 3)
        assert progress["accuracy"] == expected_accuracy
