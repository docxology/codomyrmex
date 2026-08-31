"""Test PersistentScheduler args/kwargs persistence across simulated restart."""

import json
import tempfile
from pathlib import Path

from codomyrmex.orchestrator.scheduler.advanced import PersistentScheduler


def _dummy_func(a=1, b=2):
    """Test function with args."""
    return a + b


def test_save_load_preserves_args_kwargs():
    """Test that _save_state persists args/kwargs and _load_state restores them."""
    state_path = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)

    # First scheduler instance: register, schedule, let it save
    sched1 = PersistentScheduler(state_path=str(state_path), auto_save=True)
    sched1.register_function("dummy", _dummy_func)
    sched1.schedule(
        _dummy_func,
        function_name="dummy",
        name="test_job",
        args=(3, 4),
        kwargs={"extra": "value"},
    )

    # Verify the state file was written with args/kwargs
    with open(state_path) as f:
        data = json.load(f)
    assert len(data["jobs"]) == 1
    saved_job = data["jobs"][0]
    assert saved_job["args"] == [3, 4]
    assert saved_job["kwargs"] == {"extra": "value"}

    # Simulate restart: register function before _load_state sees the file
    sched2 = PersistentScheduler(state_path=str(state_path), auto_save=False)
    sched2.register_function("dummy", _dummy_func)
    # _load_state already ran in __init__ but found no matching function.
    # Re-run it manually now that the function is registered.
    sched2._load_state()

    jobs = list(sched2._jobs.values())
    assert len(jobs) == 1, f"Expected 1 job loaded, got {len(jobs)}"
    loaded_job = jobs[0]
    assert loaded_job.args == (3, 4), f"Expected args (3,4), got {loaded_job.args}"
    assert loaded_job.kwargs == {"extra": "value"}, (
        f"Expected kwargs {{'extra': 'value'}}, got {loaded_job.kwargs}"
    )

    # Cleanup
    state_path.unlink(missing_ok=True)


def test_save_load_with_empty_args_kwargs():
    """Test that jobs with no explicit args/kwargs survive restart."""
    state_path = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)

    sched1 = PersistentScheduler(state_path=str(state_path), auto_save=True)
    sched1.register_function("dummy", _dummy_func)
    sched1.schedule(
        _dummy_func,
        function_name="dummy",
        name="no_args_job",
    )

    # Verify saved
    with open(state_path) as f:
        data = json.load(f)
    saved_job = data["jobs"][0]
    assert saved_job["args"] == []
    assert saved_job["kwargs"] == {}

    sched2 = PersistentScheduler(state_path=str(state_path), auto_save=False)
    sched2.register_function("dummy", _dummy_func)
    sched2._load_state()
    jobs = list(sched2._jobs.values())
    assert len(jobs) >= 1

    state_path.unlink(missing_ok=True)
