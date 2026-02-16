"""Assessment and certification engine.

Generates exams from curriculum modules, grades submissions, and
produces certificates for students who pass.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Certificate:
    """A completion certificate issued to a student.

    Attributes:
        certificate_id: Unique identifier.
        student: Student name.
        curriculum_name: Name of the curriculum completed.
        score: Final score as a percentage (0-100).
        passed: Whether the student met the passing threshold.
        issued_at: ISO-format timestamp.
        verification_hash: SHA-256 hash for certificate authenticity.
    """

    certificate_id: str
    student: str
    curriculum_name: str
    score: float
    passed: bool
    issued_at: str
    verification_hash: str


class Assessment:
    """Exam generation and grading tied to a Curriculum.

    Creates exams from the curriculum's modules, grades student
    submissions, and generates certificates for passing scores.

    Attributes:
        curriculum: The Curriculum instance this assessment covers.
        passing_score: Minimum percentage score to pass (default 70).
    """

    def __init__(self, curriculum: Any, passing_score: float = 70.0) -> None:
        """Initialize an assessment for the given curriculum.

        Args:
            curriculum: A Curriculum instance (from curriculum subpackage).
            passing_score: Minimum score (0-100) required to pass.
        """
        self.curriculum = curriculum
        self.passing_score = passing_score
        self._exams: dict[str, dict[str, Any]] = {}
        self._certificates: list[Certificate] = []

    def create_exam(self, module_names: list[str] | None = None) -> dict[str, Any]:
        """Generate an exam from the curriculum's modules.

        Each module contributes one question based on its content and
        objectives.  If module_names is None, all modules are included.

        Args:
            module_names: Optional subset of module names to include.

        Returns:
            Exam dict with 'exam_id', 'questions', 'total_points'.
        """
        modules = self.curriculum.get_modules()

        if module_names is not None:
            name_set = set(module_names)
            modules = [m for m in modules if m["title"] in name_set]

        questions: list[dict[str, Any]] = []
        for mod in modules:
            # Build a question from each module's objectives
            objectives = mod.get("objectives", [])
            objective_text = objectives[0] if objectives else mod["title"]

            question = {
                "id": str(uuid4()),
                "module": mod["title"],
                "prompt": f"Explain the following concept: {objective_text}",
                "points": 10,
                "type": "open_ended",
            }

            # If the module has exercises, also include the first one
            exercises = mod.get("exercises", [])
            if exercises:
                ex = exercises[0]
                question["bonus_prompt"] = ex.get("prompt", "")
                question["points"] += 5

            questions.append(question)

        exam_id = str(uuid4())
        exam = {
            "exam_id": exam_id,
            "curriculum": self.curriculum.name,
            "created_at": datetime.utcnow().isoformat(),
            "questions": questions,
            "total_points": sum(q["points"] for q in questions),
        }
        self._exams[exam_id] = exam
        return exam

    def grade_submission(self, exam_id: str, answers: dict[str, str]) -> dict[str, Any]:
        """Grade a student's exam submission.

        Grading uses a simplified heuristic: answers that are non-empty
        and contain at least 10 characters receive full points.  Shorter
        answers receive partial credit proportional to length.

        Args:
            exam_id: The exam identifier.
            answers: Mapping of question ID -> answer text.

        Returns:
            Dict with 'exam_id', 'total_points', 'earned_points',
            'score_percent', 'passed', and per-question 'breakdown'.

        Raises:
            KeyError: If the exam_id is not found.
        """
        exam = self._exams.get(exam_id)
        if exam is None:
            raise KeyError(f"Exam '{exam_id}' not found")

        total = exam["total_points"]
        earned = 0.0
        breakdown: list[dict[str, Any]] = []

        for question in exam["questions"]:
            qid = question["id"]
            answer = answers.get(qid, "")
            max_pts = question["points"]

            # Simple length-based heuristic grading
            if len(answer.strip()) >= 10:
                pts = max_pts
            elif len(answer.strip()) > 0:
                pts = max_pts * (len(answer.strip()) / 10.0)
            else:
                pts = 0.0

            pts = min(pts, max_pts)
            earned += pts
            breakdown.append({
                "question_id": qid,
                "module": question["module"],
                "points_possible": max_pts,
                "points_earned": round(pts, 2),
            })

        score_pct = (earned / total * 100) if total > 0 else 0.0

        return {
            "exam_id": exam_id,
            "total_points": total,
            "earned_points": round(earned, 2),
            "score_percent": round(score_pct, 2),
            "passed": score_pct >= self.passing_score,
            "breakdown": breakdown,
        }

    def generate_certificate(self, student: str, score: float) -> dict[str, Any]:
        """Generate a certificate for a student.

        Args:
            student: Student's name.
            score: The student's final score percentage.

        Returns:
            Certificate data dict.
        """
        cert_id = str(uuid4())
        issued_at = datetime.utcnow().isoformat()
        passed = score >= self.passing_score

        # Create a verification hash
        payload = f"{cert_id}:{student}:{self.curriculum.name}:{score}:{issued_at}"
        verification_hash = hashlib.sha256(payload.encode()).hexdigest()

        cert = Certificate(
            certificate_id=cert_id,
            student=student,
            curriculum_name=self.curriculum.name,
            score=round(score, 2),
            passed=passed,
            issued_at=issued_at,
            verification_hash=verification_hash,
        )
        self._certificates.append(cert)

        return {
            "certificate_id": cert.certificate_id,
            "student": cert.student,
            "curriculum": cert.curriculum_name,
            "score": cert.score,
            "passed": cert.passed,
            "issued_at": cert.issued_at,
            "verification_hash": cert.verification_hash,
            "message": "Congratulations!" if passed else "Below passing threshold.",
        }

    @property
    def certificates(self) -> list[Certificate]:
        """All certificates issued by this assessment."""
        return list(self._certificates)
