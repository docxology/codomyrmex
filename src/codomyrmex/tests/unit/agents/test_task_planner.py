"""Zero-mock unit tests for agents/generic/task_planner.py.

Covers TaskStatus enum, Task dataclass, and TaskPlanner public methods:
create_task, decompose_task, get_task, update_task_status, get_ready_tasks,
get_task_execution_order, get_all_tasks.

No mocks, stubs, or monkeypatching used.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.generic.task_planner import Task, TaskPlanner, TaskStatus

# ===========================================================================
# TaskStatus enum
# ===========================================================================


@pytest.mark.unit
class TestTaskStatus:
    """Tests for the TaskStatus enum values and membership."""

    def test_pending_value(self):
        assert TaskStatus.PENDING.value == "pending"

    def test_in_progress_value(self):
        assert TaskStatus.IN_PROGRESS.value == "in_progress"

    def test_completed_value(self):
        assert TaskStatus.COMPLETED.value == "completed"

    def test_failed_value(self):
        assert TaskStatus.FAILED.value == "failed"

    def test_cancelled_value(self):
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_five_members_exist(self):
        assert len(TaskStatus) == 5

    def test_members_are_distinct(self):
        values = [s.value for s in TaskStatus]
        assert len(values) == len(set(values))


# ===========================================================================
# Task dataclass
# ===========================================================================


@pytest.mark.unit
class TestTaskDataclass:
    """Tests for the Task dataclass construction and defaults."""

    def test_construction_minimal(self):
        t = Task(id="t1", description="Do something")
        assert t.id == "t1"
        assert t.description == "Do something"

    def test_default_status_is_pending(self):
        t = Task(id="t1", description="Work")
        assert t.status == TaskStatus.PENDING

    def test_default_dependencies_is_empty_list(self):
        t = Task(id="t1", description="Work")
        assert t.dependencies == []

    def test_default_result_is_none(self):
        t = Task(id="t1", description="Work")
        assert t.result is None

    def test_default_error_is_none(self):
        t = Task(id="t1", description="Work")
        assert t.error is None

    def test_default_metadata_is_empty_dict(self):
        t = Task(id="t1", description="Work")
        assert t.metadata == {}

    def test_custom_status(self):
        t = Task(id="t1", description="Work", status=TaskStatus.COMPLETED)
        assert t.status == TaskStatus.COMPLETED

    def test_custom_dependencies(self):
        t = Task(id="t2", description="Step 2", dependencies=["t1"])
        assert "t1" in t.dependencies

    def test_custom_metadata(self):
        t = Task(id="t1", description="Work", metadata={"priority": "high"})
        assert t.metadata["priority"] == "high"

    def test_dependency_lists_are_independent(self):
        """Different Task instances must not share their dependency lists."""
        t1 = Task(id="a", description="A")
        t2 = Task(id="b", description="B")
        t1.dependencies.append("x")
        assert t2.dependencies == []


# ===========================================================================
# TaskPlanner.create_task
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerCreateTask:
    """Tests for TaskPlanner.create_task."""

    def test_creates_task_with_description(self):
        planner = TaskPlanner()
        task = planner.create_task("Fetch data from API")
        assert task.description == "Fetch data from API"

    def test_returns_task_instance(self):
        planner = TaskPlanner()
        task = planner.create_task("Do work")
        assert isinstance(task, Task)

    def test_task_id_auto_generated(self):
        planner = TaskPlanner()
        task = planner.create_task("First")
        assert task.id.startswith("task_")

    def test_task_ids_are_sequential(self):
        planner = TaskPlanner()
        t1 = planner.create_task("First")
        t2 = planner.create_task("Second")
        assert t1.id != t2.id
        assert t1.id == "task_1"
        assert t2.id == "task_2"

    def test_initial_status_is_pending(self):
        planner = TaskPlanner()
        task = planner.create_task("Step")
        assert task.status == TaskStatus.PENDING

    def test_task_stored_in_planner(self):
        planner = TaskPlanner()
        task = planner.create_task("Stored")
        assert task.id in planner.tasks

    def test_create_with_dependencies(self):
        planner = TaskPlanner()
        t1 = planner.create_task("Base")
        t2 = planner.create_task("Dependent", dependencies=[t1.id])
        assert t1.id in t2.dependencies

    def test_create_with_metadata(self):
        planner = TaskPlanner()
        task = planner.create_task("Meta", metadata={"owner": "alice"})
        assert task.metadata["owner"] == "alice"

    def test_default_dependencies_is_empty(self):
        planner = TaskPlanner()
        task = planner.create_task("No deps")
        assert task.dependencies == []


# ===========================================================================
# TaskPlanner.get_task
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerGetTask:
    """Tests for TaskPlanner.get_task."""

    def test_get_existing_task(self):
        planner = TaskPlanner()
        created = planner.create_task("Find me")
        found = planner.get_task(created.id)
        assert found is created

    def test_get_missing_task_returns_none(self):
        planner = TaskPlanner()
        assert planner.get_task("nonexistent_id") is None

    def test_get_task_after_multiple_creates(self):
        planner = TaskPlanner()
        planner.create_task("First")
        second = planner.create_task("Second")
        planner.create_task("Third")
        assert planner.get_task(second.id).description == "Second"


# ===========================================================================
# TaskPlanner.update_task_status
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerUpdateStatus:
    """Tests for TaskPlanner.update_task_status."""

    def test_update_status_to_completed(self):
        planner = TaskPlanner()
        task = planner.create_task("Work")
        planner.update_task_status(task.id, TaskStatus.COMPLETED)
        assert planner.get_task(task.id).status == TaskStatus.COMPLETED

    def test_update_status_to_failed(self):
        planner = TaskPlanner()
        task = planner.create_task("Fail")
        planner.update_task_status(task.id, TaskStatus.FAILED, error="timeout")
        t = planner.get_task(task.id)
        assert t.status == TaskStatus.FAILED
        assert t.error == "timeout"

    def test_update_with_result(self):
        planner = TaskPlanner()
        task = planner.create_task("Compute")
        planner.update_task_status(task.id, TaskStatus.COMPLETED, result=42)
        assert planner.get_task(task.id).result == 42

    def test_update_nonexistent_task_does_not_raise(self):
        planner = TaskPlanner()
        # Should log a warning but not raise
        planner.update_task_status("ghost_id", TaskStatus.COMPLETED)

    def test_update_to_in_progress(self):
        planner = TaskPlanner()
        task = planner.create_task("Running")
        planner.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        assert planner.get_task(task.id).status == TaskStatus.IN_PROGRESS

    def test_result_none_does_not_overwrite_existing(self):
        planner = TaskPlanner()
        task = planner.create_task("Sticky")
        planner.update_task_status(task.id, TaskStatus.COMPLETED, result="first")
        planner.update_task_status(task.id, TaskStatus.COMPLETED, result=None)
        # result=None should NOT overwrite an existing result
        assert planner.get_task(task.id).result == "first"


# ===========================================================================
# TaskPlanner.get_ready_tasks
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerGetReadyTasks:
    """Tests for TaskPlanner.get_ready_tasks."""

    def test_no_deps_task_is_ready(self):
        planner = TaskPlanner()
        task = planner.create_task("Independent")
        ready = planner.get_ready_tasks()
        assert task in ready

    def test_dependent_task_not_ready_until_dep_complete(self):
        planner = TaskPlanner()
        t1 = planner.create_task("Base")
        t2 = planner.create_task("Needs base", dependencies=[t1.id])
        ready_ids = [t.id for t in planner.get_ready_tasks()]
        assert t2.id not in ready_ids
        assert t1.id in ready_ids

    def test_dependent_task_becomes_ready_after_dep_completes(self):
        planner = TaskPlanner()
        t1 = planner.create_task("Base")
        t2 = planner.create_task("Needs base", dependencies=[t1.id])
        planner.update_task_status(t1.id, TaskStatus.COMPLETED)
        ready_ids = [t.id for t in planner.get_ready_tasks()]
        assert t2.id in ready_ids

    def test_completed_task_not_in_ready_list(self):
        planner = TaskPlanner()
        task = planner.create_task("Done")
        planner.update_task_status(task.id, TaskStatus.COMPLETED)
        ready = planner.get_ready_tasks()
        assert task not in ready

    def test_empty_planner_returns_empty_ready_list(self):
        planner = TaskPlanner()
        assert planner.get_ready_tasks() == []


# ===========================================================================
# TaskPlanner.get_task_execution_order
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerExecutionOrder:
    """Tests for TaskPlanner.get_task_execution_order (topological sort)."""

    def test_linear_chain_order(self):
        planner = TaskPlanner()
        t1 = planner.create_task("Step 1")
        t2 = planner.create_task("Step 2", dependencies=[t1.id])
        t3 = planner.create_task("Step 3", dependencies=[t2.id])
        order = planner.get_task_execution_order()
        ids = [t.id for t in order]
        assert ids.index(t1.id) < ids.index(t2.id)
        assert ids.index(t2.id) < ids.index(t3.id)

    def test_independent_tasks_all_in_order(self):
        planner = TaskPlanner()
        t1 = planner.create_task("A")
        t2 = planner.create_task("B")
        t3 = planner.create_task("C")
        order = planner.get_task_execution_order()
        assert len(order) == 3
        assert {t.id for t in order} == {t1.id, t2.id, t3.id}

    def test_single_task_order(self):
        planner = TaskPlanner()
        task = planner.create_task("Solo")
        order = planner.get_task_execution_order()
        assert len(order) == 1
        assert order[0].id == task.id

    def test_empty_planner_order_is_empty(self):
        planner = TaskPlanner()
        assert planner.get_task_execution_order() == []

    def test_diamond_dependency_order(self):
        """A→B, A→C, B→D, C→D: D must come last."""
        planner = TaskPlanner()
        a = planner.create_task("A")
        b = planner.create_task("B", dependencies=[a.id])
        c = planner.create_task("C", dependencies=[a.id])
        d = planner.create_task("D", dependencies=[b.id, c.id])
        order = planner.get_task_execution_order()
        ids = [t.id for t in order]
        assert ids.index(a.id) < ids.index(b.id)
        assert ids.index(a.id) < ids.index(c.id)
        assert ids.index(b.id) < ids.index(d.id)
        assert ids.index(c.id) < ids.index(d.id)


# ===========================================================================
# TaskPlanner.decompose_task
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerDecomposeTask:
    """Tests for TaskPlanner.decompose_task."""

    def test_decompose_returns_subtasks(self):
        planner = TaskPlanner()
        main = planner.create_task("Big task")
        subtasks = planner.decompose_task(main, ["Sub A", "Sub B", "Sub C"])
        assert len(subtasks) == 3

    def test_subtask_descriptions_match(self):
        planner = TaskPlanner()
        main = planner.create_task("Big task")
        subtasks = planner.decompose_task(main, ["Alpha", "Beta"])
        descs = [t.description for t in subtasks]
        assert "Alpha" in descs
        assert "Beta" in descs

    def test_first_subtask_has_no_parent_dependency(self):
        """The first subtask has no dependencies (it can start immediately)."""
        planner = TaskPlanner()
        main = planner.create_task("Main")
        subtasks = planner.decompose_task(main, ["First", "Second"])
        assert subtasks[0].dependencies == []

    def test_subsequent_subtasks_depend_on_main(self):
        """Subtasks after the first depend on the main task id."""
        planner = TaskPlanner()
        main = planner.create_task("Main")
        subtasks = planner.decompose_task(main, ["First", "Second", "Third"])
        for subtask in subtasks[1:]:
            assert main.id in subtask.dependencies

    def test_subtasks_have_parent_metadata(self):
        planner = TaskPlanner()
        main = planner.create_task("Main")
        subtasks = planner.decompose_task(main, ["Sub"])
        assert subtasks[0].metadata.get("parent_task") == main.id

    def test_subtasks_stored_in_planner(self):
        planner = TaskPlanner()
        main = planner.create_task("Main")
        subtasks = planner.decompose_task(main, ["A", "B"])
        for sub in subtasks:
            assert sub.id in planner.tasks

    def test_decompose_empty_list_returns_empty(self):
        planner = TaskPlanner()
        main = planner.create_task("Main")
        subtasks = planner.decompose_task(main, [])
        assert subtasks == []


# ===========================================================================
# TaskPlanner.get_all_tasks
# ===========================================================================


@pytest.mark.unit
class TestTaskPlannerGetAllTasks:
    """Tests for TaskPlanner.get_all_tasks."""

    def test_returns_all_created_tasks(self):
        planner = TaskPlanner()
        t1 = planner.create_task("First")
        t2 = planner.create_task("Second")
        all_tasks = planner.get_all_tasks()
        assert t1 in all_tasks
        assert t2 in all_tasks

    def test_returns_list(self):
        planner = TaskPlanner()
        planner.create_task("Task")
        assert isinstance(planner.get_all_tasks(), list)

    def test_empty_planner_returns_empty_list(self):
        planner = TaskPlanner()
        assert planner.get_all_tasks() == []

    def test_count_matches_created(self):
        planner = TaskPlanner()
        for i in range(5):
            planner.create_task(f"Task {i}")
        assert len(planner.get_all_tasks()) == 5
