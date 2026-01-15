
import pytest
import asyncio
from codomyrmex.orchestrator.workflow import Workflow, TaskStatus, CycleError, WorkflowError

@pytest.mark.asyncio
async def test_workflow_linear_execution():
    """Test simple linear dependency A -> B -> C."""
    execution_order = []

    async def task_a():
        execution_order.append("A")
        return "result_a"

    async def task_b():
        execution_order.append("B")
        return "result_b"
        
    async def task_c():
        execution_order.append("C")
        return "result_c"

    wf = Workflow("test_linear")
    wf.add_task("A", task_a)
    wf.add_task("B", task_b, dependencies=["A"])
    wf.add_task("C", task_c, dependencies=["B"])

    results = await wf.run()

    assert execution_order == ["A", "B", "C"]
    assert results == {"A": "result_a", "B": "result_b", "C": "result_c"}

@pytest.mark.asyncio
async def test_workflow_parallel_execution():
    """Test parallel execution: A -> (B, C) -> D."""
    results_list = []

    async def task_common(name, delay=0.1):
        await asyncio.sleep(delay)
        results_list.append(name)
        return name

    wf = Workflow("test_parallel")
    wf.add_task("A", task_common, args=["A", 0])
    wf.add_task("B", task_common, args=["B", 0.05], dependencies=["A"]) # Slower
    wf.add_task("C", task_common, args=["C", 0], dependencies=["A"])    # Faster
    wf.add_task("D", task_common, args=["D", 0], dependencies=["B", "C"])

    await wf.run()

    # Sort results by the order they were appended to check relative ordering where deterministic
    # A MUST come before B and C
    assert results_list.index("A") < results_list.index("B")
    assert results_list.index("A") < results_list.index("C")
    
    # B and C MUST come before D
    assert results_list.index("B") < results_list.index("D")
    assert results_list.index("C") < results_list.index("D")
    
    # We cannot guarantee B vs C order due to small sleep diffs and scheduler, 
    # but we know they are in between A and D.
    
    assert len(results_list) == 4
    assert set(results_list) == {"A", "B", "C", "D"}

@pytest.mark.asyncio
async def test_cycle_detection():
    """Test detection of circular dependencies."""
    wf = Workflow("test_cycle")
    wf.add_task("A", lambda: None, dependencies=["B"])
    wf.add_task("B", lambda: None, dependencies=["A"])

    with pytest.raises(CycleError):
        await wf.run()

@pytest.mark.asyncio
async def test_missing_dependency():
    """Test missing dependency validation."""
    wf = Workflow("test_missing")
    wf.add_task("A", lambda: None, dependencies=["NON_EXISTENT"])

    with pytest.raises(WorkflowError):
        await wf.run()

@pytest.mark.asyncio
async def test_task_failure_handling():
    """Test that downstream tasks are skipped/marked failed if dependency fails."""
    
    async def failing_task():
        raise ValueError("Boom")
    
    success_run = False
    async def downstream_task():
        nonlocal success_run
        success_run = True

    wf = Workflow("test_failure")
    wf.add_task("Fail", failing_task)
    wf.add_task("Downstream", downstream_task, dependencies=["Fail"])

    results = await wf.run()
    
    # Downstream should not have run or should be skipped/failed in a specific way.
    # Implementation treats raising Exception as FAILED status.
    # Current implementation does NOT execute tasks with pending/failed dependencies.
    
    task_fail = wf.tasks["Fail"]
    task_down = wf.tasks["Downstream"]
    
    assert task_fail.status == TaskStatus.FAILED
    assert success_run is False
    # Check if downstream was marked skipped (logic was: if pending and deps disjoint failed -> blocked)
    # The logic in run() loop is:
    # 1. blocks on failed deps -> marks SKIPPED
    assert task_down.status == TaskStatus.SKIPPED
