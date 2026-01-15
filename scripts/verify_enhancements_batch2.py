"""Verification script for batch 2 module enhancements."""

import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_module_template_scaffold():
    """Test module template scaffolding."""
    print("\nTesting Module Template Scaffold...")
    from codomyrmex.module_template.scaffold import scaffold_new_module, list_template_files
    
    # List template files
    files = list_template_files()
    print(f"Template files: {len(files)} available")
    assert len(files) > 0, "No template files found"
    
    # Scaffold to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        new_module = scaffold_new_module(
            "test_module",
            target_path=Path(tmpdir),
            description="A test module"
        )
        print(f"Created module at: {new_module}")
        
        # Verify files exist
        assert new_module.exists()
        assert (new_module / "__init__.py").exists()
        assert (new_module / "README.md").exists()
        assert (new_module / "test_module.py").exists()
        print("✅ Module Template Scaffold: PASSED")

def test_mcp_registry():
    """Test MCP Tool Registry."""
    print("\nTesting MCP Tool Registry...")
    from codomyrmex.model_context_protocol import MCPToolRegistry, MCPToolCall, MCPMessage
    
    registry = MCPToolRegistry()
    
    # Register a tool
    registry.register("test.add", {"type": "object"}, handler=lambda x, y: x + y)
    assert "test.add" in registry.list_tools()
    
    # Execute tool
    call = MCPToolCall(tool_name="test.add", arguments={"x": 2, "y": 3})
    result = registry.execute(call)
    assert result.status == "success"
    assert result.data["result"] == 5
    
    # Test MCPMessage
    msg = MCPMessage(role="user", content="Hello")
    assert msg.role == "user"
    
    print("✅ MCP Tool Registry: PASSED")

def test_logistics_scheduler():
    """Test Logistics JobScheduler enhancements."""
    print("\nTesting Logistics JobScheduler...")
    from codomyrmex.logistics.task import Queue, Job, JobScheduler
    
    queue = Queue()
    scheduler = JobScheduler(queue)
    
    # Add jobs
    job1 = Job(task="task1")
    job2 = Job(task="task2")
    queue.enqueue(job1)
    queue.enqueue(job2)
    
    # Test get_all_job_statuses
    statuses = scheduler.get_all_job_statuses()
    assert len(statuses) == 2
    assert all(s == "pending" for s in statuses.values())
    
    # Test cancel_job
    result = scheduler.cancel_job(job1.job_id)
    assert result == True
    assert scheduler.get_job(job1.job_id).status.value == "cancelled"
    
    print("✅ Logistics JobScheduler: PASSED")

def test_logging_json_formatter():
    """Test JsonFormatter and AuditLogger."""
    print("\nTesting Logging Enhancements...")
    import json
    import logging
    from io import StringIO
    from codomyrmex.logging_monitoring.logger_config import JsonFormatter, AuditLogger
    
    # Test JsonFormatter
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert "timestamp" in parsed
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Test message"
    
    # Test AuditLogger
    audit = AuditLogger()
    audit.log(actor="test_user", action="create", resource="file:/test")
    print("✅ Logging Enhancements: PASSED")

if __name__ == "__main__":
    test_module_template_scaffold()
    test_mcp_registry()
    test_logistics_scheduler()
    test_logging_json_formatter()
    print("\n" + "="*50)
    print("ALL BATCH 2 TESTS PASSED ✅")
