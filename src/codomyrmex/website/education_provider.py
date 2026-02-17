"""Education data provider for the Local Web Viewer.

Bridges the API layer with the education module classes (Curriculum,
Tutor, Assessment), managing in-memory state for curricula, tutoring
sessions, assessments, and certificates.

All data is stored in Python dictionaries and lost on server restart.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codomyrmex.education import Assessment, Curriculum, Tutor
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Difficulty levels ordered from lowest to highest
_DIFFICULTY_ORDER = ["beginner", "intermediate", "advanced", "expert"]


class EducationDataProvider:
    """Manages education state and provides a clean interface for the API layer.

    Stores curricula, tutoring sessions, assessments, and certificates
    in memory. Each curriculum gets its own Assessment instance.
    """

    def __init__(self, content_root: Path | None = None) -> None:
        self._curricula: dict[str, Curriculum] = {}
        self._tutor = Tutor(subject="general")
        self._assessments: dict[str, Assessment] = {}
        self._sessions: dict[str, dict[str, Any]] = {}
        # Map session_id -> list of quiz questions (with _answer) for grading
        self._session_questions: dict[str, list[dict[str, Any]]] = {}
        self._content_root = content_root or Path("output")

    # ── Curriculum operations ──────────────────────────────────────

    def create_curriculum(self, name: str, level: str) -> dict[str, Any]:
        """Create a new curriculum.

        Returns:
            Dict with curriculum summary.

        Raises:
            ValueError: If a curriculum with the same name exists.
        """
        if name in self._curricula:
            raise ValueError(f"Curriculum '{name}' already exists")
        if level not in _DIFFICULTY_ORDER:
            raise ValueError(f"Invalid difficulty level: {level}")

        cur = Curriculum(name=name, level=level)
        self._curricula[name] = cur
        self._assessments[name] = Assessment(curriculum=cur)
        return {
            "name": cur.name,
            "level": cur.level,
            "total_duration_minutes": 0,
            "modules": [],
        }

    def list_curricula(self) -> list[dict[str, Any]]:
        """List all curricula with summary info."""
        result = []
        for cur in self._curricula.values():
            result.append(
                {
                    "name": cur.name,
                    "level": cur.level,
                    "module_count": len(cur),
                    "total_duration_minutes": cur.total_duration(),
                }
            )
        return result

    def get_curriculum(self, name: str) -> dict[str, Any] | None:
        """Get full curriculum details including modules.

        Returns None if not found.
        """
        cur = self._curricula.get(name)
        if cur is None:
            return None
        return {
            "name": cur.name,
            "level": cur.level,
            "total_duration_minutes": cur.total_duration(),
            "modules": cur.get_modules(),
        }

    def add_module(
        self, curriculum_name: str, module_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a module to a curriculum.

        Args:
            curriculum_name: Name of the target curriculum.
            module_data: Dict with keys: name, content, objectives, exercises,
                         duration_minutes, prerequisites.

        Returns:
            The added module as a dict.

        Raises:
            KeyError: If curriculum not found.
            ValueError: If module name is duplicate.
        """
        cur = self._curricula.get(curriculum_name)
        if cur is None:
            raise KeyError(f"Curriculum '{curriculum_name}' not found")

        lesson = cur.add_module(
            name=module_data.get("name", "Untitled"),
            content=module_data.get("content", ""),
            objectives=module_data.get("objectives"),
            exercises=module_data.get("exercises"),
            duration_minutes=module_data.get("duration_minutes", 30),
            prerequisites=module_data.get("prerequisites"),
        )
        return lesson.to_dict()

    def update_module(
        self, curriculum_name: str, module_name: str, module_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing module in a curriculum.

        Raises:
            KeyError: If curriculum or module not found.
        """
        cur = self._curricula.get(curriculum_name)
        if cur is None:
            raise KeyError(f"Curriculum '{curriculum_name}' not found")

        lesson = cur.get_module(module_name)
        if lesson is None:
            raise KeyError(
                f"Module '{module_name}' not found in curriculum '{curriculum_name}'"
            )

        if "content" in module_data:
            lesson.content = module_data["content"]
        if "objectives" in module_data:
            lesson.objectives = module_data["objectives"]
        if "exercises" in module_data:
            lesson.exercises = module_data["exercises"]
        if "duration_minutes" in module_data:
            lesson.duration_minutes = module_data["duration_minutes"]
        if "prerequisites" in module_data:
            lesson.prerequisites = module_data["prerequisites"]

        return lesson.to_dict()

    def export_curriculum(self, name: str, fmt: str = "json") -> str:
        """Export a curriculum in the given format.

        Raises:
            KeyError: If curriculum not found.
            ValueError: If format is unsupported.
        """
        cur = self._curricula.get(name)
        if cur is None:
            raise KeyError(f"Curriculum '{name}' not found")
        return cur.export(format=fmt)

    def get_learning_path(self, name: str, level: str = "beginner") -> dict[str, Any]:
        """Get the learning path for a curriculum at a given student level.

        Raises:
            KeyError: If curriculum not found.
        """
        cur = self._curricula.get(name)
        if cur is None:
            raise KeyError(f"Curriculum '{name}' not found")
        if level not in _DIFFICULTY_ORDER:
            raise ValueError(f"Invalid student level: {level}")

        path = cur.generate_learning_path(student_level=level)
        return {
            "curriculum_name": cur.name,
            "student_level": level,
            "path": path,
        }

    # ── Tutoring operations ────────────────────────────────────────

    def list_topics(self) -> list[str]:
        """List available tutoring topics."""
        return self._tutor.available_topics

    def create_session(self, student_name: str, topic: str) -> dict[str, Any]:
        """Create a new tutoring session.

        Returns:
            Session metadata dict.
        """
        result = self._tutor.create_session(student_name=student_name, topic=topic)
        sid = result["session_id"]
        self._sessions[sid] = {"tutor_key": "general", "session_id": sid}
        self._session_questions[sid] = []
        return result

    def generate_quiz(
        self, topic: str, difficulty: str = "easy", count: int = 5
    ) -> list[dict[str, Any]]:
        """Generate quiz questions, stripping _answer before returning.

        The full questions (with _answer) are stored internally for grading.
        """
        raw_questions = self._tutor.generate_quiz(
            topic=topic, difficulty=difficulty, count=count
        )
        # Store full questions for later grading
        self._last_generated_quiz = raw_questions

        # Strip _answer from each question before returning
        safe_questions = []
        for q in raw_questions:
            safe_q = {k: v for k, v in q.items() if k != "_answer"}
            safe_questions.append(safe_q)
        return safe_questions

    def evaluate_answer(self, question_id: str, answer: str) -> dict[str, Any]:
        """Evaluate an answer given a question ID.

        Looks up the full question (with _answer) from the last generated quiz.

        Raises:
            KeyError: If question_id not found.
        """
        full_question = self._find_question_by_id(question_id)
        if full_question is None:
            raise KeyError(f"Question '{question_id}' not found")
        return self._tutor.evaluate_answer(full_question, answer)

    def record_answer(
        self, session_id: str, question_id: str, answer: str
    ) -> dict[str, Any]:
        """Evaluate and record an answer within a session.

        Raises:
            KeyError: If session or question not found.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found")

        full_question = self._find_question_by_id(question_id)
        if full_question is None:
            raise KeyError(f"Question '{question_id}' not found")

        return self._tutor.record_answer(session_id, full_question, answer)

    def get_session_progress(self, session_id: str) -> dict[str, Any]:
        """Get progress for a tutoring session.

        Raises:
            KeyError: If session not found.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found")
        result = self._tutor.get_session_progress(session_id)
        if "error" in result:
            raise KeyError(result["error"])
        return result

    def _find_question_by_id(self, question_id: str) -> dict[str, Any] | None:
        """Find a full question (with _answer) by its ID from the last quiz."""
        if not hasattr(self, "_last_generated_quiz"):
            return None
        for q in self._last_generated_quiz:
            if q.get("id") == question_id:
                return q
        return None

    # ── Assessment operations ──────────────────────────────────────

    def create_exam(
        self, curriculum_name: str, module_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Create an exam for a curriculum.

        Raises:
            KeyError: If curriculum not found.
        """
        assessment = self._assessments.get(curriculum_name)
        if assessment is None:
            raise KeyError(f"Curriculum '{curriculum_name}' not found")
        return assessment.create_exam(module_names=module_names)

    def grade_submission(
        self, curriculum_name: str, exam_id: str, answers: dict[str, str]
    ) -> dict[str, Any]:
        """Grade an exam submission.

        Raises:
            KeyError: If curriculum or exam not found.
        """
        assessment = self._assessments.get(curriculum_name)
        if assessment is None:
            raise KeyError(f"Curriculum '{curriculum_name}' not found")
        return assessment.grade_submission(exam_id=exam_id, answers=answers)

    def generate_certificate(
        self, student: str, curriculum_name: str, score: float
    ) -> dict[str, Any]:
        """Generate a certificate for a student.

        Raises:
            KeyError: If curriculum not found.
        """
        assessment = self._assessments.get(curriculum_name)
        if assessment is None:
            raise KeyError(f"Curriculum '{curriculum_name}' not found")
        return assessment.generate_certificate(student=student, score=score)

    def list_certificates(self) -> list[dict[str, Any]]:
        """List all certificates across all curricula."""
        certs = []
        for assessment in self._assessments.values():
            for cert in assessment.certificates:
                certs.append(
                    {
                        "certificate_id": cert.certificate_id,
                        "student": cert.student,
                        "curriculum": cert.curriculum_name,
                        "score": cert.score,
                        "passed": cert.passed,
                        "issued_at": cert.issued_at,
                        "verification_hash": cert.verification_hash,
                    }
                )
        return certs

    # ── Content browsing ───────────────────────────────────────────

    def list_output_files(self, subpath: str = "") -> dict[str, Any]:
        """List files and directories in the content root.

        Args:
            subpath: Relative path within the content root.

        Returns:
            Dict with 'path' and 'entries' list.

        Raises:
            FileNotFoundError: If the path doesn't exist.
            PermissionError: If path traversal is attempted.
        """
        base = self._content_root.resolve()
        target = (self._content_root / subpath).resolve()

        # Security: prevent directory traversal
        if not target.is_relative_to(base):
            raise PermissionError("Access denied")

        if not target.exists():
            raise FileNotFoundError(f"Path not found: {subpath}")

        if not target.is_dir():
            raise ValueError(f"Not a directory: {subpath}")

        entries = []
        for item in sorted(target.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_file():
                entries.append(
                    {
                        "name": item.name,
                        "type": "file",
                        "extension": item.suffix,
                        "size": item.stat().st_size,
                    }
                )
            elif item.is_dir():
                children = [c for c in item.iterdir() if not c.name.startswith(".")]
                entries.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "children_count": len(children),
                    }
                )

        return {
            "path": str(target.relative_to(base)) if subpath else "",
            "entries": entries,
        }

    def get_file_content(self, filepath: str) -> dict[str, Any]:
        """Get the content of a file in the content root.

        Returns:
            Dict with 'path', 'content' or 'url', 'type'.

        Raises:
            FileNotFoundError: If file doesn't exist.
            PermissionError: If path traversal is attempted.
        """
        base = self._content_root.resolve()
        target = (self._content_root / filepath).resolve()

        # Security: prevent directory traversal
        if not target.is_relative_to(base):
            raise PermissionError("Access denied")

        if not target.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if not target.is_file():
            raise ValueError(f"Not a file: {filepath}")

        # Don't serve sensitive files
        sensitive_names = {".env", ".credentials", ".secret", ".key"}
        if target.name.lower() in sensitive_names:
            raise PermissionError("Access denied")

        ext = target.suffix.lower()
        text_extensions = {
            ".txt",
            ".md",
            ".json",
            ".yaml",
            ".yml",
            ".py",
            ".js",
            ".css",
            ".html",
            ".xml",
            ".csv",
            ".toml",
            ".cfg",
            ".ini",
            ".log",
            ".sh",
            ".bat",
        }
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}

        if ext in text_extensions:
            content = target.read_text(encoding="utf-8", errors="replace")
            return {
                "path": filepath,
                "type": "text",
                "extension": ext,
                "content": content,
            }
        elif ext in image_extensions:
            return {
                "path": filepath,
                "type": "image",
                "extension": ext,
                "url": f"/content/files/{filepath}",
            }
        elif ext == ".html":
            return {
                "path": filepath,
                "type": "html",
                "extension": ext,
                "url": f"/content/files/{filepath}",
            }
        else:
            return {
                "path": filepath,
                "type": "binary",
                "extension": ext,
                "size": target.stat().st_size,
            }
