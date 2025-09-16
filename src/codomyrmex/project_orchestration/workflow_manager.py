"""
Workflow Manager for Codomyrmex Project Orchestration

Handles the creation, listing, execution, and management of workflows
that coordinate multiple Codomyrmex modules with performance monitoring.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import performance monitoring
try:
    from ..performance import monitor_performance, performance_context, PerformanceMonitor
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logging.warning("Performance monitoring not available")
    PERFORMANCE_MONITORING_AVAILABLE = False
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class performance_context:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowExecution:
    """Tracks workflow execution state."""
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """Manages workflow definitions and executions with performance monitoring."""
    
    def __init__(self, config_dir: Optional[Path] = None, enable_performance_monitoring: bool = True):
        """Initialize the WorkflowManager."""
        self.config_dir = config_dir or Path.cwd() / ".codomyrmex" / "workflows"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Workflow storage
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        
        # Performance monitoring
        self.enable_performance_monitoring = enable_performance_monitoring and PERFORMANCE_MONITORING_AVAILABLE
        self.performance_monitor = PerformanceMonitor() if self.enable_performance_monitoring else None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing workflows
        self._load_workflows()
    
    @monitor_performance("workflow_create")
    def create_workflow(self, name: str, steps: List[WorkflowStep], save: bool = True) -> bool:
        """Create a new workflow."""
        try:
            self.workflows[name] = steps
            if save:
                self._save_workflow(name, steps)
            self.logger.info(f"Created workflow: {name} ({len(steps)} steps)")
            return True
        except Exception as e:
            self.logger.error(f"Error creating workflow {name}: {e}")
            return False
    
    @monitor_performance("workflow_list")
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all available workflows with metadata."""
        workflow_info = {}
        for name, steps in self.workflows.items():
            workflow_info[name] = {
                'steps': len(steps),
                'modules': list(set(step.module for step in steps)),
                'estimated_duration': sum(step.timeout or 60 for step in steps)
            }
        return workflow_info
    
    @monitor_performance("workflow_execute")
    async def execute_workflow(self, name: str, parameters: Optional[Dict[str, Any]] = None, 
                             timeout: Optional[int] = None) -> WorkflowExecution:
        """Execute a workflow asynchronously with performance monitoring."""
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found")
        
        # Create execution tracker
        execution = WorkflowExecution(workflow_name=name)
        execution.start_time = datetime.now()
        execution.status = WorkflowStatus.RUNNING
        self.executions[f"{name}_{int(time.time())}"] = execution
        
        try:
            steps = self.workflows[name]
            completed_steps = set()
            
            for step in steps:
                # Execute step with monitoring
                step_result = await self._execute_step(step, parameters or {}, execution)
                execution.results[step.name] = step_result
                
                if step_result.get('success', False):
                    completed_steps.add(step.name)
                    self.logger.info(f"Step {step.name} completed successfully")
                else:
                    error_msg = f"Step {step.name} failed: {step_result.get('error', 'Unknown error')}"
                    execution.errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Update execution status
            execution.end_time = datetime.now()
            execution.status = WorkflowStatus.COMPLETED if not execution.errors else WorkflowStatus.FAILED
            
            self.logger.info(f"Workflow {name} completed with status: {execution.status}")
            return execution
                
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(f"Workflow execution failed: {str(e)}")
            self.logger.error(f"Workflow {name} failed: {e}")
            return execution
    
    @monitor_performance("workflow_step_execution")
    async def _execute_step(self, step: WorkflowStep, parameters: Dict[str, Any], 
                          execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            self.logger.info(f"Executing step: {step.name} ({step.module}.{step.action})")
            
            # Simulate module execution
            start_time = time.time()
            await asyncio.sleep(0.5)  # Simulate processing time
            execution_time = time.time() - start_time
            
            # Record step performance
            if self.enable_performance_monitoring and self.performance_monitor:
                self.performance_monitor.record_metrics(
                    function_name=f"{step.module}_{step.action}",
                    execution_time=execution_time,
                    metadata={
                        'workflow': execution.workflow_name,
                        'step_name': step.name
                    }
                )
            
            return {
                'success': True,
                'execution_time': execution_time,
                'message': f'Step {step.name} completed'
            }
            
        except Exception as e:
            self.logger.error(f"Step {step.name} execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0
            }
    
    @monitor_performance("workflow_get_performance_summary")
    def get_performance_summary(self, workflow_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for workflows."""
        if not self.enable_performance_monitoring or not self.performance_monitor:
            return {"error": "Performance monitoring not enabled"}
        
        stats = self.performance_monitor.get_stats(workflow_name)
        
        summary = {
            'performance_stats': stats,
            'total_workflows_executed': len(self.executions),
            'successful_executions': len([e for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED]),
            'failed_executions': len([e for e in self.executions.values() if e.status == WorkflowStatus.FAILED])
        }
        
        return summary
    
    def _save_workflow(self, name: str, steps: List[WorkflowStep]):
        """Save a workflow to disk."""
        try:
            workflow_file = self.config_dir / f"{name}.json"
            workflow_data = {
                'name': name,
                'steps': [
                    {
                        'name': step.name,
                        'module': step.module,
                        'action': step.action,
                        'parameters': step.parameters,
                        'dependencies': step.dependencies,
                        'timeout': step.timeout,
                        'retry_count': step.retry_count,
                        'max_retries': step.max_retries
                    }
                    for step in steps
                ]
            }
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            self.logger.debug(f"Saved workflow: {name}")
        except Exception as e:
            self.logger.error(f"Failed to save workflow {name}: {e}")
    
    def _load_workflows(self):
        """Load workflows from disk."""
        try:
            if not self.config_dir.exists():
                return
            
            for workflow_file in self.config_dir.glob("*.json"):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_data = json.load(f)
                    
                    steps = [
                        WorkflowStep(
                            name=step_data['name'],
                            module=step_data['module'],
                            action=step_data['action'],
                            parameters=step_data.get('parameters', {}),
                            dependencies=step_data.get('dependencies', []),
                            timeout=step_data.get('timeout'),
                            retry_count=step_data.get('retry_count', 0),
                            max_retries=step_data.get('max_retries', 3)
                        )
                        for step_data in workflow_data.get('steps', [])
                    ]
                    
                    self.workflows[workflow_data['name']] = steps
                    self.logger.debug(f"Loaded workflow: {workflow_data['name']}")
                except Exception as e:
                    self.logger.error(f"Failed to load workflow from {workflow_file}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to load workflows: {e}")


# Global workflow manager instance
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager