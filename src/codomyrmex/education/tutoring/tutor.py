"""Interactive tutoring engine.

Provides quiz generation, answer evaluation, and session tracking
for one-on-one tutoring workflows.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TutoringSession:
    """Record of a tutoring session between a tutor and a student.

    Attributes:
        session_id: Unique identifier.
        student_name: Name of the student.
        topic: Subject area being studied.
        started_at: Timestamp when the session began.
        questions_asked: Number of questions posed so far.
        correct_answers: Number of correct answers.
        history: Chronological log of question/answer events.
    """

    session_id: str = field(default_factory=lambda: str(uuid4()))
    student_name: str = ""
    topic: str = ""
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    questions_asked: int = 0
    correct_answers: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Proportion of correct answers (0.0 to 1.0)."""
        if self.questions_asked == 0:
            return 0.0
        return self.correct_answers / self.questions_asked


class Tutor:
    """Subject-matter tutor that generates quizzes and evaluates answers.

    The tutor maintains a bank of question templates per topic and can
    create quizzes of varying difficulty.

    Attributes:
        subject: The broad subject area this tutor covers.
    """

    # Built-in question bank keyed by (topic, difficulty)
    _QUESTION_BANK: dict[str, list[dict[str, Any]]] = {
        "python_basics": [
            {
                "question": "What keyword is used to define a function in Python?",
                "choices": ["func", "def", "function", "lambda"],
                "answer": "def",
                "difficulty": "easy",
            },
            {
                "question": "Which data structure uses key-value pairs?",
                "choices": ["list", "tuple", "dict", "set"],
                "answer": "dict",
                "difficulty": "easy",
            },
            {
                "question": "What does 'len([1,2,3])' return?",
                "choices": ["2", "3", "4", "Error"],
                "answer": "3",
                "difficulty": "easy",
            },
            {
                "question": "What is the output of 'bool([])'?",
                "choices": ["True", "False", "None", "Error"],
                "answer": "False",
                "difficulty": "medium",
            },
            {
                "question": "Which decorator makes a method a class method?",
                "choices": ["@staticmethod", "@classmethod", "@property", "@abstractmethod"],
                "answer": "@classmethod",
                "difficulty": "medium",
            },
            {
                "question": "What does a generator yield?",
                "choices": ["A list", "A value lazily", "An exception", "A class"],
                "answer": "A value lazily",
                "difficulty": "hard",
            },
        ],
        "data_structures": [
            {
                "question": "What is the time complexity of accessing an element in a hash map?",
                "choices": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
                "answer": "O(1)",
                "difficulty": "easy",
            },
            {
                "question": "Which data structure follows LIFO ordering?",
                "choices": ["Queue", "Stack", "Heap", "Deque"],
                "answer": "Stack",
                "difficulty": "easy",
            },
            {
                "question": "What is the worst-case time complexity of quicksort?",
                "choices": ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"],
                "answer": "O(n^2)",
                "difficulty": "medium",
            },
            {
                "question": "A balanced BST has what height relative to n nodes?",
                "choices": ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
                "answer": "O(log n)",
                "difficulty": "hard",
            },
        ],
    }

    _DIFFICULTY_ORDER = ["easy", "medium", "hard"]

    def __init__(self, subject: str) -> None:
        """Create a tutor for the given subject.

        Args:
            subject: Broad subject area (e.g., 'programming', 'math').
        """
        self.subject = subject
        self._sessions: dict[str, TutoringSession] = {}

    def create_session(self, student_name: str, topic: str) -> dict[str, Any]:
        """Start a new tutoring session.

        Args:
            student_name: Name of the student.
            topic: Specific topic within the subject.

        Returns:
            Session metadata dict with session_id and start time.
        """
        session = TutoringSession(student_name=student_name, topic=topic)
        self._sessions[session.session_id] = session
        return {
            "session_id": session.session_id,
            "student_name": student_name,
            "topic": topic,
            "started_at": session.started_at,
        }

    def generate_quiz(
        self,
        topic: str,
        difficulty: str = "easy",
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate a multiple-choice quiz for the given topic.

        Questions are drawn from the built-in bank and filtered by
        difficulty.  If fewer questions are available than requested,
        all matching questions are returned.

        Args:
            topic: Topic key (e.g., 'python_basics', 'data_structures').
            difficulty: Minimum difficulty level ('easy', 'medium', 'hard').
            count: Number of questions to include.

        Returns:
            List of question dicts, each with 'id', 'question', 'choices'.
        """
        bank = self._QUESTION_BANK.get(topic, [])
        min_idx = self._DIFFICULTY_ORDER.index(difficulty) if difficulty in self._DIFFICULTY_ORDER else 0

        eligible = [
            q for q in bank
            if self._DIFFICULTY_ORDER.index(q.get("difficulty", "easy")) >= min_idx
        ]

        selected = random.sample(eligible, min(count, len(eligible)))

        quiz: list[dict[str, Any]] = []
        for q in selected:
            quiz.append({
                "id": str(uuid4()),
                "question": q["question"],
                "choices": q["choices"],
                "difficulty": q["difficulty"],
                # Answer is NOT included -- used internally for grading
                "_answer": q["answer"],
            })
        return quiz

    def evaluate_answer(self, question: dict[str, Any], answer: str) -> dict[str, Any]:
        """Evaluate a student's answer to a quiz question.

        Args:
            question: The question dict (must include '_answer').
            answer: The student's chosen answer string.

        Returns:
            Dict with 'correct' (bool), 'expected', and 'feedback'.
        """
        expected = question.get("_answer", "")
        is_correct = answer.strip().lower() == expected.strip().lower()

        feedback = "Correct!" if is_correct else f"Incorrect. The correct answer is: {expected}"

        return {
            "correct": is_correct,
            "expected": expected,
            "given": answer,
            "feedback": feedback,
        }

    def get_session_progress(self, session_id: str) -> dict[str, Any]:
        """Retrieve progress information for a session.

        Args:
            session_id: The session identifier.

        Returns:
            Dict with session stats or an error message if not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return {"error": f"Session '{session_id}' not found"}

        return {
            "session_id": session.session_id,
            "student_name": session.student_name,
            "topic": session.topic,
            "started_at": session.started_at,
            "questions_asked": session.questions_asked,
            "correct_answers": session.correct_answers,
            "accuracy": round(session.accuracy, 3),
            "history": session.history,
        }

    def record_answer(
        self,
        session_id: str,
        question: dict[str, Any],
        answer: str,
    ) -> dict[str, Any]:
        """Evaluate and record an answer within a session.

        Combines evaluation with session bookkeeping.

        Args:
            session_id: Session to record against.
            question: The question dict.
            answer: Student's answer.

        Returns:
            Evaluation result dict.
        """
        result = self.evaluate_answer(question, answer)
        session = self._sessions.get(session_id)
        if session is not None:
            session.questions_asked += 1
            if result["correct"]:
                session.correct_answers += 1
            session.history.append({
                "question": question.get("question", ""),
                "answer": answer,
                "correct": result["correct"],
            })
        return result

    @property
    def available_topics(self) -> list[str]:
        """List of topics that have questions in the bank."""
        return list(self._QUESTION_BANK.keys())
