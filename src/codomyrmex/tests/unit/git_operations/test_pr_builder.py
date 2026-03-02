"""Tests for git_operations.pr_builder — PR specification and branch naming.

Pure Python tests — no git, no network, no optional dependencies.
"""

import pytest

from codomyrmex.git_operations.pr_builder import FileChange, PRBuilder, PRSpec

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# FileChange dataclass
# ---------------------------------------------------------------------------

class TestFileChange:

    def test_default_action_is_add(self):
        fc = FileChange("path.py")
        assert fc.action == "add"

    def test_custom_action(self):
        fc = FileChange("path.py", action="modify")
        assert fc.action == "modify"

    def test_empty_content_default(self):
        fc = FileChange("path.py")
        assert fc.content == ""


# ---------------------------------------------------------------------------
# PRSpec dataclass
# ---------------------------------------------------------------------------

class TestPRSpec:

    def test_file_count_empty(self):
        spec = PRSpec()
        assert spec.file_count == 0

    def test_file_count_with_changes(self):
        spec = PRSpec(changes=[FileChange("a.py"), FileChange("b.py")])
        assert spec.file_count == 2

    def test_to_dict_contains_required_keys(self):
        spec = PRSpec(title="Test PR", branch="auto/test", base="main")
        d = spec.to_dict()
        required = {"title", "branch", "base", "files_changed", "labels", "test_results"}
        assert required.issubset(d.keys())

    def test_to_dict_files_changed_matches_file_count(self):
        spec = PRSpec(changes=[FileChange("x.py")])
        d = spec.to_dict()
        assert d["files_changed"] == spec.file_count

    def test_default_base_is_main(self):
        spec = PRSpec()
        assert spec.base == "main"


# ---------------------------------------------------------------------------
# PRBuilder.create
# ---------------------------------------------------------------------------

class TestPRBuilderCreate:

    def setup_method(self):
        self.builder = PRBuilder()

    def test_create_with_explicit_title(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            title="My Custom Title",
        )
        assert pr.title == "My Custom Title"

    def test_create_auto_title_from_changes(self):
        pr = self.builder.create(
            changes=[FileChange("utils.py"), FileChange("helpers.py")],
        )
        # Auto-title should mention the file names
        assert "utils.py" in pr.title
        assert "helpers.py" in pr.title

    def test_create_empty_changeset_title(self):
        pr = self.builder.create(changes=[])
        assert pr.title == "Empty changeset"

    def test_create_default_labels(self):
        pr = self.builder.create(changes=[FileChange("a.py")])
        assert "auto-generated" in pr.labels

    def test_create_custom_labels(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            labels=["bugfix", "urgent"],
        )
        assert "bugfix" in pr.labels
        assert "urgent" in pr.labels

    def test_create_auto_description(self):
        pr = self.builder.create(changes=[FileChange("a.py")])
        assert pr.description != ""
        assert "Auto-generated" in pr.description

    def test_create_custom_description(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            description="This fixes the login bug.",
        )
        assert pr.description == "This fixes the login bug."

    def test_create_test_results_stored(self):
        results = {"passed": 10, "failed": 0}
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            test_results=results,
        )
        assert pr.test_results == results


# ---------------------------------------------------------------------------
# PRBuilder branch name generation
# ---------------------------------------------------------------------------

class TestPRBuilderBranchName:

    def setup_method(self):
        self.builder = PRBuilder()

    def test_branch_name_has_auto_prefix(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            title="Fix the login flow",
        )
        assert pr.branch.startswith("auto/")

    def test_branch_name_slugifies_title(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            title="Fix Login Flow",
        )
        # Should be lowercased with hyphens
        slug_part = pr.branch.removeprefix("auto/")
        assert " " not in slug_part
        assert slug_part == slug_part.lower()

    def test_branch_name_removes_special_chars(self):
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            title="Fix: login (v2) flow!",
        )
        slug_part = pr.branch.removeprefix("auto/")
        # Only alphanumeric and hyphens allowed
        assert all(c.isalnum() or c == "-" for c in slug_part)

    def test_branch_name_truncated_at_40_chars(self):
        long_title = "A" * 100
        pr = self.builder.create(
            changes=[FileChange("a.py")],
            title=long_title,
        )
        slug_part = pr.branch.removeprefix("auto/")
        assert len(slug_part) <= 40

    def test_branch_name_from_add_action(self):
        pr = self.builder.create(
            changes=[FileChange("new_module.py", action="add")],
        )
        assert "add" in pr.title.lower() or "Add" in pr.title

    def test_branch_name_from_modify_action(self):
        pr = self.builder.create(
            changes=[FileChange("existing.py", action="modify")],
        )
        assert "update" in pr.title.lower() or "Update" in pr.title
