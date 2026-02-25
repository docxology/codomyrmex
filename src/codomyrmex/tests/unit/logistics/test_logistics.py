"""Tests for logistics module."""



class TestResourceManager:
    def test_resource_status(self):
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceStatus,
        )
        assert len(list(ResourceStatus)) > 0

    def test_resource(self):
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            Resource,
            ResourceType,
        )
        r = Resource(id="r1", name="cpu", type=list(ResourceType)[0], capacity=100)
        assert r.name == "cpu"

    def test_resource_limits(self):
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceLimits,
        )
        limits = ResourceLimits(min_value=0, max_value=100, unit="cores")
        assert limits.unit == "cores"

    def test_resource_manager(self):
        from codomyrmex.logistics.orchestration.project.resource_manager import (
            ResourceManager,
        )
        mgr = ResourceManager()
        assert mgr is not None


class TestTaskOrchestrator:
    def test_task_priority(self):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskPriority,
        )
        assert len(list(TaskPriority)) > 0

    def test_task_creation(self):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            Task,
            TaskPriority,
        )
        t = Task(name="build", module="core", action="compile", priority=list(TaskPriority)[0])
        assert t.name == "build"

    def test_task_result(self):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskResult,
            TaskStatus,
        )
        r = TaskResult(task_id="t1", status=TaskStatus.PENDING)
        assert r.task_id == "t1"

    def test_task_orchestrator(self):
        from codomyrmex.logistics.orchestration.project.task_orchestrator import (
            TaskOrchestrator,
        )
        orch = TaskOrchestrator()
        assert orch is not None
