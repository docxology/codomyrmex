"""Unit tests for codomyrmex.agents.editing_loop module.

Tests cover:
- EditTask dataclass construction and defaults
- EditingConfig dataclass construction, defaults, and __post_init__ env logic
- EditingOrchestrator._parse_score static method
- EditingOrchestrator._parse_notes static method
- EditingOrchestrator._parse_plan_edits instance method
- EditingOrchestrator constructor (requires Ollama availability)
- EditingOrchestrator.from_todo (requires Ollama + orchestrator module)
- EditingOrchestrator.run_task / run_tasks (requires live LLM)
"""

import importlib.util
import os
import textwrap

import pytest

from codomyrmex.agents.editing_loop import EditTask, EditingConfig

# EditingOrchestrator constructor requires OllamaClient + AgentRelay which
# do succeed at import time but reach out to Ollama at execution.  We import
# the class unconditionally (it's pure Python) but guard tests that call the
# constructor behind an Ollama reachability check.

from codomyrmex.agents.editing_loop import EditingOrchestrator


def _ollama_is_reachable() -> bool:
    """Return True if a local Ollama instance responds to /api/tags."""
    import urllib.request
    import urllib.error

    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        req = urllib.request.Request(f"{base}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def _ollama_has_model() -> bool:
    """Return True if a local Ollama instance has the configured model for chat."""
    import json
    import urllib.request
    import urllib.error

    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "codellama:latest")
    try:
        req = urllib.request.Request(f"{base}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status != 200:
                return False
            data = json.loads(resp.read().decode("utf-8"))
            available = [m.get("name", "") for m in data.get("models", [])]
            return model in available or any(model.split(":")[0] in a for a in available)
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        return False


_OLLAMA_REACHABLE = _ollama_is_reachable()
_OLLAMA_HAS_MODEL = _ollama_has_model()


# =====================================================================
# EditTask dataclass tests
# =====================================================================


@pytest.mark.unit
class TestEditTask:
    """Tests for the EditTask dataclass."""

    def test_minimal_construction(self):
        """EditTask requires only description."""
        task = EditTask(description="Add docstrings")
        assert task.description == "Add docstrings"
        assert task.file_path == ""
        assert task.edit_type == "edit"
        assert task.context_files == []
        assert task.approved is False
        assert task.result == ""
        assert task.review_notes == []
        assert task.iterations_used == 0

    def test_full_construction(self):
        """EditTask with all fields specified."""
        task = EditTask(
            description="Refactor helper",
            file_path="src/helpers.py",
            edit_type="refactor",
            context_files=["README.md", "SPEC.md"],
            approved=True,
            result="Done",
            review_notes=["Good work"],
            iterations_used=2,
        )
        assert task.description == "Refactor helper"
        assert task.file_path == "src/helpers.py"
        assert task.edit_type == "refactor"
        assert task.context_files == ["README.md", "SPEC.md"]
        assert task.approved is True
        assert task.result == "Done"
        assert task.review_notes == ["Good work"]
        assert task.iterations_used == 2

    def test_context_files_are_independent_instances(self):
        """Each EditTask gets its own list for context_files."""
        t1 = EditTask(description="A")
        t2 = EditTask(description="B")
        t1.context_files.append("file1.py")
        assert t2.context_files == []

    def test_review_notes_are_independent_instances(self):
        """Each EditTask gets its own list for review_notes."""
        t1 = EditTask(description="A")
        t2 = EditTask(description="B")
        t1.review_notes.append("note")
        assert t2.review_notes == []

    def test_mutation(self):
        """EditTask fields are mutable (dataclass without frozen)."""
        task = EditTask(description="original")
        task.description = "updated"
        task.approved = True
        task.iterations_used = 3
        assert task.description == "updated"
        assert task.approved is True
        assert task.iterations_used == 3


# =====================================================================
# EditingConfig dataclass tests
# =====================================================================


@pytest.mark.unit
class TestEditingConfig:
    """Tests for the EditingConfig dataclass."""

    def test_defaults(self):
        """EditingConfig sets sensible defaults."""
        cfg = EditingConfig()
        # ollama_model populated by __post_init__ from env or fallback
        assert isinstance(cfg.ollama_model, str)
        assert len(cfg.ollama_model) > 0
        assert cfg.review_provider == "ollama"
        assert isinstance(cfg.review_model, str)
        assert len(cfg.review_model) > 0
        assert cfg.max_iterations == 5
        assert cfg.approval_threshold == 7.0
        assert cfg.auto_apply_edits is True
        assert cfg.context_files == []
        assert cfg.scheduler_config is None
        assert cfg.channel == ""

    def test_post_init_uses_env_for_ollama_model(self):
        """__post_init__ reads OLLAMA_MODEL env var when ollama_model is empty."""
        saved = os.environ.get("OLLAMA_MODEL")
        try:
            os.environ["OLLAMA_MODEL"] = "test-model:7b"
            cfg = EditingConfig()
            assert cfg.ollama_model == "test-model:7b"
        finally:
            if saved is None:
                os.environ.pop("OLLAMA_MODEL", None)
            else:
                os.environ["OLLAMA_MODEL"] = saved

    def test_post_init_uses_env_for_review_model(self):
        """__post_init__ reads OLLAMA_REVIEW_MODEL env var when review_model is empty."""
        saved_model = os.environ.get("OLLAMA_MODEL")
        saved_review = os.environ.get("OLLAMA_REVIEW_MODEL")
        try:
            os.environ["OLLAMA_MODEL"] = "base-model:latest"
            os.environ["OLLAMA_REVIEW_MODEL"] = "review-model:13b"
            cfg = EditingConfig()
            assert cfg.review_model == "review-model:13b"
        finally:
            if saved_model is None:
                os.environ.pop("OLLAMA_MODEL", None)
            else:
                os.environ["OLLAMA_MODEL"] = saved_model
            if saved_review is None:
                os.environ.pop("OLLAMA_REVIEW_MODEL", None)
            else:
                os.environ["OLLAMA_REVIEW_MODEL"] = saved_review

    def test_post_init_review_model_defaults_to_ollama_model(self):
        """When OLLAMA_REVIEW_MODEL is unset, review_model defaults to ollama_model."""
        saved_model = os.environ.get("OLLAMA_MODEL")
        saved_review = os.environ.get("OLLAMA_REVIEW_MODEL")
        try:
            os.environ["OLLAMA_MODEL"] = "same-model:7b"
            os.environ.pop("OLLAMA_REVIEW_MODEL", None)
            cfg = EditingConfig()
            assert cfg.review_model == "same-model:7b"
        finally:
            if saved_model is None:
                os.environ.pop("OLLAMA_MODEL", None)
            else:
                os.environ["OLLAMA_MODEL"] = saved_model
            if saved_review is None:
                os.environ.pop("OLLAMA_REVIEW_MODEL", None)
            else:
                os.environ["OLLAMA_REVIEW_MODEL"] = saved_review

    def test_explicit_model_not_overridden(self):
        """When ollama_model is provided explicitly, env var is not used."""
        saved = os.environ.get("OLLAMA_MODEL")
        try:
            os.environ["OLLAMA_MODEL"] = "env-model"
            cfg = EditingConfig(ollama_model="explicit-model")
            assert cfg.ollama_model == "explicit-model"
        finally:
            if saved is None:
                os.environ.pop("OLLAMA_MODEL", None)
            else:
                os.environ["OLLAMA_MODEL"] = saved

    def test_custom_max_iterations(self):
        """max_iterations can be overridden."""
        cfg = EditingConfig(max_iterations=10)
        assert cfg.max_iterations == 10

    def test_custom_approval_threshold(self):
        """approval_threshold can be overridden."""
        cfg = EditingConfig(approval_threshold=9.5)
        assert cfg.approval_threshold == 9.5

    def test_context_files_independence(self):
        """Each config gets independent context_files list."""
        c1 = EditingConfig()
        c2 = EditingConfig()
        c1.context_files.append("file.txt")
        assert c2.context_files == []


# =====================================================================
# _parse_score static method tests
# =====================================================================


@pytest.mark.unit
class TestParseScore:
    """Tests for EditingOrchestrator._parse_score."""

    def test_valid_integer_score(self):
        assert EditingOrchestrator._parse_score("SCORE: 8\nNOTES: Good") == 8.0

    def test_valid_float_score(self):
        assert EditingOrchestrator._parse_score("SCORE: 7.5\nAPPROVED: yes") == 7.5

    def test_score_zero(self):
        assert EditingOrchestrator._parse_score("SCORE: 0\nBad code.") == 0.0

    def test_score_ten(self):
        assert EditingOrchestrator._parse_score("SCORE: 10\nPerfect.") == 10.0

    def test_no_score_returns_zero(self):
        assert EditingOrchestrator._parse_score("No score here.") == 0.0

    def test_case_insensitive(self):
        assert EditingOrchestrator._parse_score("score: 6\nok") == 6.0

    def test_score_with_extra_whitespace(self):
        assert EditingOrchestrator._parse_score("SCORE:   9  \nNotes") == 9.0

    def test_score_embedded_in_text(self):
        text = "Review complete.\nSCORE: 5.5\nAPPROVED: no\nNOTES: Needs work"
        assert EditingOrchestrator._parse_score(text) == 5.5

    def test_invalid_score_value_returns_zero(self):
        """Non-numeric after 'SCORE:' returns 0.0."""
        assert EditingOrchestrator._parse_score("SCORE: abc") == 0.0

    def test_empty_string_returns_zero(self):
        assert EditingOrchestrator._parse_score("") == 0.0


# =====================================================================
# _parse_notes static method tests
# =====================================================================


@pytest.mark.unit
class TestParseNotes:
    """Tests for EditingOrchestrator._parse_notes."""

    def test_extracts_notes(self):
        text = "SCORE: 8\nAPPROVED: yes\nNOTES: Well done, clean code."
        assert EditingOrchestrator._parse_notes(text) == "Well done, clean code."

    def test_multiline_notes(self):
        text = "SCORE: 5\nNOTES: Fix the imports.\nAlso rename the variable."
        notes = EditingOrchestrator._parse_notes(text)
        assert "Fix the imports." in notes
        assert "Also rename the variable." in notes

    def test_no_notes_returns_full_text(self):
        """When no NOTES: tag exists, the full text is returned as-is."""
        text = "Just some review text without any structured tags."
        assert EditingOrchestrator._parse_notes(text) == text

    def test_case_insensitive(self):
        text = "notes: lowercase notes here"
        assert EditingOrchestrator._parse_notes(text) == "lowercase notes here"

    def test_empty_string(self):
        assert EditingOrchestrator._parse_notes("") == ""

    def test_notes_with_leading_whitespace(self):
        text = "NOTES:   trimmed content   "
        assert EditingOrchestrator._parse_notes(text) == "trimmed content"


# =====================================================================
# _parse_plan_edits instance method tests
# =====================================================================


@pytest.mark.unit
class TestParsePlanEdits:
    """Tests for EditingOrchestrator._parse_plan_edits.

    This is an instance method, so we call it unbound via the class or
    create a minimal instance.  Since the method only uses ``self`` for
    dispatch (no instance state), we can call it on any instance or even
    access via ``__func__``.
    """

    @staticmethod
    def _parse(plan: str) -> list[tuple[str, str]]:
        """Helper to call _parse_plan_edits without an orchestrator instance."""
        # The method only uses re; it needs no instance state.
        # Call it as an unbound function.
        return EditingOrchestrator._parse_plan_edits(None, plan)  # type: ignore[arg-type]

    def test_single_find_replace(self):
        plan = textwrap.dedent("""\
            STEP 1: Add import
            FIND: import os
            REPLACE: import os
            import sys
        """)
        edits = self._parse(plan)
        assert len(edits) == 1
        assert edits[0][0] == "import os"
        assert "import sys" in edits[0][1]

    def test_multiple_find_replace_blocks(self):
        plan = textwrap.dedent("""\
            STEP 1: Fix import
            FIND: import old
            REPLACE: import new
            STEP 2: Fix function
            FIND: def foo():
            REPLACE: def bar():
        """)
        edits = self._parse(plan)
        assert len(edits) == 2
        assert edits[0] == ("import old", "import new")
        assert edits[1] == ("def foo():", "def bar():")

    def test_no_find_replace_returns_empty(self):
        plan = "Just add docstrings to all functions."
        edits = self._parse(plan)
        assert edits == []

    def test_empty_plan_returns_empty(self):
        edits = self._parse("")
        assert edits == []

    def test_find_without_replace_ignored(self):
        """A FIND: block that runs directly into another FIND: yields nothing
        useful because the regex requires REPLACE: after FIND:."""
        plan = textwrap.dedent("""\
            FIND: something
            FIND: something_else
            REPLACE: replacement
        """)
        edits = self._parse(plan)
        # The regex may or may not match here depending on greedy behavior.
        # We just verify no crash and valid tuples.
        for find_text, replace_text in edits:
            assert isinstance(find_text, str)
            assert isinstance(replace_text, str)

    def test_multiline_find_replace(self):
        plan = textwrap.dedent("""\
            STEP 1: Add function body
            FIND: def process():
                pass
            REPLACE: def process():
                return True
        """)
        edits = self._parse(plan)
        assert len(edits) >= 1
        assert "pass" in edits[0][0]
        assert "return True" in edits[0][1]


# =====================================================================
# EditingOrchestrator constructor tests (requires Ollama)
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_REACHABLE, reason="Requires reachable Ollama instance")
class TestEditingOrchestratorInit:
    """Tests for EditingOrchestrator constructor."""

    def test_default_construction(self):
        """Constructor with default config succeeds."""
        orch = EditingOrchestrator()
        assert orch.config is not None
        assert isinstance(orch.config, EditingConfig)
        assert orch._ag_client is None  # Lazy, not initialized yet

    def test_custom_config(self):
        """Constructor with custom config propagates values."""
        cfg = EditingConfig(
            max_iterations=3,
            approval_threshold=8.0,
            review_provider="ollama",
        )
        orch = EditingOrchestrator(config=cfg)
        assert orch.config.max_iterations == 3
        assert orch.config.approval_threshold == 8.0

    def test_relay_channel_auto_generated(self):
        """If no channel specified, one is generated with 'editing-' prefix."""
        orch = EditingOrchestrator()
        # _relay is an AgentRelay; it stores its channel_id
        assert hasattr(orch._relay, "channel_id")

    def test_scheduler_none_by_default(self):
        """Without scheduler_config, _scheduler is None."""
        orch = EditingOrchestrator()
        assert orch._scheduler is None

    def test_scheduler_created_when_config_provided(self):
        """When scheduler_config is set, _scheduler is created."""
        from codomyrmex.ide.antigravity.message_scheduler import SchedulerConfig

        cfg = EditingConfig(scheduler_config=SchedulerConfig(min_delay=0.1))
        orch = EditingOrchestrator(config=cfg)
        assert orch._scheduler is not None

    def test_claude_review_provider_fallback(self):
        """When review_provider='claude' but no API key, falls back to Ollama."""
        saved = os.environ.get("ANTHROPIC_API_KEY")
        try:
            os.environ.pop("ANTHROPIC_API_KEY", None)
            cfg = EditingConfig(review_provider="claude")
            orch = EditingOrchestrator(config=cfg)
            # Should succeed (falls back to OllamaClient)
            assert orch._reviewer is not None
        finally:
            if saved is not None:
                os.environ["ANTHROPIC_API_KEY"] = saved


# =====================================================================
# from_todo class method tests
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_REACHABLE, reason="Requires reachable Ollama instance")
class TestFromTodo:
    """Tests for EditingOrchestrator.from_todo."""

    def test_from_todo_creates_tasks(self, tmp_path):
        """from_todo parses unchecked items into EditTask list."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text(textwrap.dedent("""\
            # Tasks
            - [ ] Add docstrings to helpers.py
            - [x] Already done
            - [ ] Fix the import order
            - [/] Partially done task
        """))

        orch, tasks = EditingOrchestrator.from_todo(str(todo_file))
        assert isinstance(orch, EditingOrchestrator)
        # extract_todo_items picks up "- [ ]" and "- [/]" items
        assert len(tasks) >= 2
        descriptions = [t.description for t in tasks]
        assert "Add docstrings to helpers.py" in descriptions
        assert "Fix the import order" in descriptions
        for t in tasks:
            assert t.edit_type == "todo"

    def test_from_todo_file_not_found(self):
        """from_todo raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="TO-DO file not found"):
            EditingOrchestrator.from_todo("/nonexistent/path/TODO.md")

    def test_from_todo_empty_file(self, tmp_path):
        """from_todo with empty file yields zero tasks."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text("")

        orch, tasks = EditingOrchestrator.from_todo(str(todo_file))
        assert isinstance(orch, EditingOrchestrator)
        assert tasks == []

    def test_from_todo_no_unchecked_items(self, tmp_path):
        """from_todo with all-checked file yields zero tasks."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text(textwrap.dedent("""\
            - [x] Already done
            - [x] Also done
        """))

        orch, tasks = EditingOrchestrator.from_todo(str(todo_file))
        assert tasks == []

    def test_from_todo_with_custom_config(self, tmp_path):
        """from_todo respects custom config."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text("- [ ] Task one\n")

        cfg = EditingConfig(max_iterations=2)
        orch, tasks = EditingOrchestrator.from_todo(str(todo_file), config=cfg)
        assert orch.config.max_iterations == 2


# =====================================================================
# _plan method tests (requires Ollama for real call)
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_HAS_MODEL, reason="Requires Ollama with configured model")
class TestPlanMethod:
    """Tests for the _plan private method (requires live Ollama)."""

    def test_plan_with_file_path(self, tmp_path):
        """_plan reads the target file and includes content in the prompt."""
        target = tmp_path / "example.py"
        target.write_text("def hello():\n    pass\n")

        orch = EditingOrchestrator()
        task = EditTask(
            description="Add a docstring to hello()",
            file_path=str(target),
        )
        plan = orch._plan(task)
        assert isinstance(plan, str)
        assert len(plan) > 0

    def test_plan_without_file_path(self):
        """_plan works even when no file_path is specified."""
        orch = EditingOrchestrator()
        task = EditTask(description="Write a sorting function")
        plan = orch._plan(task)
        assert isinstance(plan, str)

    def test_plan_with_missing_file(self):
        """_plan handles FileNotFoundError gracefully."""
        orch = EditingOrchestrator()
        task = EditTask(
            description="Edit missing file",
            file_path="/nonexistent/file.py",
        )
        plan = orch._plan(task)
        assert isinstance(plan, str)

    def test_plan_with_feedback(self, tmp_path):
        """_plan incorporates reviewer feedback."""
        target = tmp_path / "code.py"
        target.write_text("x = 1\n")

        orch = EditingOrchestrator()
        task = EditTask(description="Improve variable naming", file_path=str(target))
        plan = orch._plan(task, feedback="Use descriptive names like 'count' instead of 'x'")
        assert isinstance(plan, str)

    def test_plan_with_context_files(self, tmp_path):
        """_plan includes context files in the prompt."""
        target = tmp_path / "main.py"
        target.write_text("from helpers import process\n")
        ctx = tmp_path / "helpers.py"
        ctx.write_text("def process():\n    return 42\n")

        orch = EditingOrchestrator()
        task = EditTask(
            description="Refactor process call",
            file_path=str(target),
            context_files=[str(ctx)],
        )
        plan = orch._plan(task)
        assert isinstance(plan, str)

    def test_plan_truncates_large_files(self, tmp_path):
        """_plan truncates file content longer than 8000 chars."""
        target = tmp_path / "big.py"
        target.write_text("x = 1\n" * 5000)  # ~30000 chars

        orch = EditingOrchestrator()
        task = EditTask(description="Reduce file size", file_path=str(target))
        # Should not raise; content will be truncated internally
        plan = orch._plan(task)
        assert isinstance(plan, str)


# =====================================================================
# _edit method tests (Antigravity is typically unavailable)
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_REACHABLE, reason="Requires reachable Ollama instance")
class TestEditMethod:
    """Tests for _edit that exercise code paths without Antigravity."""

    def test_edit_no_file_path(self):
        """_edit returns early when task has no file_path."""
        orch = EditingOrchestrator()
        task = EditTask(description="Do something")
        result = orch._edit(task, "STEP 1: some plan")
        assert "No file_path specified" in result

    def test_edit_antigravity_unavailable(self, tmp_path):
        """_edit returns fallback message when Antigravity is not connected."""
        orch = EditingOrchestrator()
        task = EditTask(
            description="Edit a file",
            file_path=str(tmp_path / "file.py"),
        )
        plan = "STEP 1: Do something\nFIND: old\nREPLACE: new"
        result = orch._edit(task, plan)
        # Antigravity is typically not running in test environments
        assert isinstance(result, str)
        # Either "Antigravity unavailable" or actual edit result
        assert len(result) > 0

    def test_edit_no_find_replace_in_plan(self):
        """_edit handles plans with no parseable FIND/REPLACE blocks."""
        orch = EditingOrchestrator()
        task = EditTask(
            description="Edit file",
            file_path="/some/file.py",
        )
        result = orch._edit(task, "Just add some docstrings please")
        # Either AG unavailable message or no-parse message
        assert isinstance(result, str)


# =====================================================================
# _review method tests (requires Ollama for real call)
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_HAS_MODEL, reason="Requires Ollama with configured model")
class TestReviewMethod:
    """Tests for _review with a live Ollama reviewer."""

    def test_review_returns_tuple(self, tmp_path):
        """_review returns (approved, notes, score) tuple."""
        target = tmp_path / "reviewed.py"
        target.write_text("def hello():\n    '''Say hello.'''\n    print('hello')\n")

        orch = EditingOrchestrator()
        task = EditTask(description="Add docstring", file_path=str(target))
        approved, notes, score = orch._review(
            task,
            plan="STEP 1: Add docstring",
            edit_summary="Added docstring to hello()",
        )
        assert isinstance(approved, bool)
        assert isinstance(notes, str)
        assert isinstance(score, float)
        assert 0.0 <= score <= 10.0

    def test_review_missing_file(self):
        """_review handles missing file gracefully."""
        orch = EditingOrchestrator()
        task = EditTask(
            description="Review missing file",
            file_path="/nonexistent/reviewed.py",
        )
        approved, notes, score = orch._review(
            task,
            plan="Some plan",
            edit_summary="Some edit",
        )
        assert isinstance(approved, bool)
        assert isinstance(notes, str)
        assert isinstance(score, float)

    def test_review_no_file_path(self):
        """_review works when task has no file_path."""
        orch = EditingOrchestrator()
        task = EditTask(description="Review abstract task")
        approved, notes, score = orch._review(
            task,
            plan="Abstract plan",
            edit_summary="Abstract edit",
        )
        assert isinstance(approved, bool)
        assert isinstance(notes, str)
        assert isinstance(score, float)


# =====================================================================
# run_task / run_tasks integration (requires live Ollama)
# =====================================================================


@pytest.mark.unit
@pytest.mark.skipif(not _OLLAMA_HAS_MODEL, reason="Requires Ollama with configured model")
class TestRunTask:
    """Integration tests for run_task (requires live LLM)."""

    def test_run_task_returns_edit_task(self, tmp_path):
        """run_task returns the same EditTask with populated fields."""
        target = tmp_path / "simple.py"
        target.write_text("x = 1\n")

        cfg = EditingConfig(max_iterations=1)
        orch = EditingOrchestrator(config=cfg)
        task = EditTask(
            description="Rename x to count",
            file_path=str(target),
        )
        result = orch.run_task(task)
        assert result is task  # Same object returned
        assert result.iterations_used >= 1
        assert isinstance(result.result, str)
        assert len(result.review_notes) >= 1

    def test_run_task_max_iterations_respected(self):
        """run_task stops after max_iterations even if not approved."""
        cfg = EditingConfig(max_iterations=1, approval_threshold=99.0)
        orch = EditingOrchestrator(config=cfg)
        task = EditTask(description="Impossible task with unreachable threshold")
        result = orch.run_task(task)
        assert result.iterations_used == 1

    def test_run_tasks_sequential(self, tmp_path):
        """run_tasks processes multiple tasks."""
        f1 = tmp_path / "a.py"
        f1.write_text("a = 1\n")
        f2 = tmp_path / "b.py"
        f2.write_text("b = 2\n")

        cfg = EditingConfig(max_iterations=1)
        orch = EditingOrchestrator(config=cfg)
        tasks = [
            EditTask(description="Fix a.py", file_path=str(f1)),
            EditTask(description="Fix b.py", file_path=str(f2)),
        ]
        results = orch.run_tasks(tasks)
        assert len(results) == 2
        assert results[0].iterations_used >= 1
        assert results[1].iterations_used >= 1


# =====================================================================
# Module exports
# =====================================================================


@pytest.mark.unit
class TestModuleExports:
    """Verify __all__ exports are accessible."""

    def test_all_exports_importable(self):
        from codomyrmex.agents import editing_loop

        for name in editing_loop.__all__:
            assert hasattr(editing_loop, name), f"Missing export: {name}"

    def test_all_contains_expected_names(self):
        from codomyrmex.agents.editing_loop import __all__

        assert "EditTask" in __all__
        assert "EditingConfig" in __all__
        assert "EditingOrchestrator" in __all__
