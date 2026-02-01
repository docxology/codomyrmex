"""
Workflow Testing Module

End-to-end workflow validation and testing.
"""

__version__ = "0.1.0"

import time
import threading
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class WorkflowStepType(Enum):
    """Types of workflow steps."""
    HTTP_REQUEST = "http_request"
    ASSERTION = "assertion"
    WAIT = "wait"
    SCRIPT = "script"
    CONDITIONAL = "conditional"


class StepStatus(Enum):
    """Status of a step execution."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class WorkflowStep:
    """A single step in a workflow test."""
    id: str
    name: str
    step_type: WorkflowStepType
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    timeout_seconds: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.step_type.value,
            "config": self.config,
        }


@dataclass
class StepResult:
    """Result of executing a step."""
    step_id: str
    status: StepStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    retries: int = 0
    
    @property
    def passed(self) -> bool:
        """Check if step passed."""
        return self.status == StepStatus.PASSED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "output": str(self.output) if self.output else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class WorkflowResult:
    """Result of running a complete workflow."""
    workflow_id: str
    status: StepStatus
    step_results: List[StepResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    @property
    def total_steps(self) -> int:
        """Get total steps."""
        return len(self.step_results)
    
    @property
    def passed_steps(self) -> int:
        """Get passed steps."""
        return sum(1 for r in self.step_results if r.passed)
    
    @property
    def duration_ms(self) -> float:
        """Get total duration."""
        return sum(r.duration_ms for r in self.step_results)
    
    @property
    def pass_rate(self) -> float:
        """Get pass rate."""
        if self.total_steps == 0:
            return 0.0
        return self.passed_steps / self.total_steps
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "pass_rate": self.pass_rate,
            "duration_ms": self.duration_ms,
        }


class StepExecutor(ABC):
    """Base class for step executors."""
    
    @abstractmethod
    def execute(self, step: WorkflowStep, context: Dict[str, Any]) -> StepResult:
        """Execute a step."""
        pass


class AssertionExecutor(StepExecutor):
    """Executor for assertion steps."""
    
    def execute(self, step: WorkflowStep, context: Dict[str, Any]) -> StepResult:
        """Execute assertion step."""
        start = time.time()
        
        try:
            assertion_type = step.config.get("type", "equals")
            expected = step.config.get("expected")
            actual_key = step.config.get("actual_key")
            actual = context.get(actual_key) if actual_key else step.config.get("actual")
            
            passed = False
            if assertion_type == "equals":
                passed = actual == expected
            elif assertion_type == "contains":
                passed = expected in str(actual)
            elif assertion_type == "not_null":
                passed = actual is not None
            elif assertion_type == "greater_than":
                passed = float(actual) > float(expected)
            elif assertion_type == "less_than":
                passed = float(actual) < float(expected)
            
            duration = (time.time() - start) * 1000
            
            return StepResult(
                step_id=step.id,
                status=StepStatus.PASSED if passed else StepStatus.FAILED,
                output={"actual": actual, "expected": expected},
                duration_ms=duration,
            )
            
        except Exception as e:
            duration = (time.time() - start) * 1000
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=str(e),
                duration_ms=duration,
            )


class WaitExecutor(StepExecutor):
    """Executor for wait steps."""
    
    def execute(self, step: WorkflowStep, context: Dict[str, Any]) -> StepResult:
        """Execute wait step."""
        start = time.time()
        
        seconds = step.config.get("seconds", 1.0)
        time.sleep(seconds)
        
        duration = (time.time() - start) * 1000
        
        return StepResult(
            step_id=step.id,
            status=StepStatus.PASSED,
            output={"waited": seconds},
            duration_ms=duration,
        )


class ScriptExecutor(StepExecutor):
    """Executor for script steps."""
    
    def execute(self, step: WorkflowStep, context: Dict[str, Any]) -> StepResult:
        """Execute script step."""
        start = time.time()
        
        try:
            script_fn = step.config.get("function")
            if callable(script_fn):
                result = script_fn(context)
            else:
                result = eval(step.config.get("expression", "True"), {"ctx": context})
            
            duration = (time.time() - start) * 1000
            
            return StepResult(
                step_id=step.id,
                status=StepStatus.PASSED,
                output=result,
                duration_ms=duration,
            )
            
        except Exception as e:
            duration = (time.time() - start) * 1000
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=str(e),
                duration_ms=duration,
            )


@dataclass
class Workflow:
    """A workflow test definition."""
    id: str
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def add_step(self, step: WorkflowStep) -> "Workflow":
        """Add a step to workflow."""
        self.steps.append(step)
        return self
    
    def add_assertion(
        self,
        id: str,
        name: str,
        assertion_type: str,
        expected: Any,
        actual_key: Optional[str] = None,
    ) -> "Workflow":
        """Add an assertion step."""
        step = WorkflowStep(
            id=id,
            name=name,
            step_type=WorkflowStepType.ASSERTION,
            config={
                "type": assertion_type,
                "expected": expected,
                "actual_key": actual_key,
            },
        )
        return self.add_step(step)
    
    def add_wait(self, id: str, seconds: float) -> "Workflow":
        """Add a wait step."""
        step = WorkflowStep(
            id=id,
            name=f"Wait {seconds}s",
            step_type=WorkflowStepType.WAIT,
            config={"seconds": seconds},
        )
        return self.add_step(step)


class WorkflowRunner:
    """
    Runs workflow tests.
    
    Usage:
        runner = WorkflowRunner()
        
        workflow = Workflow(id="test", name="API Test")
        workflow.add_step(WorkflowStep(
            id="check",
            name="Check response",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 200},
        ))
        
        result = runner.run(workflow)
        print(f"Pass rate: {result.pass_rate:.1%}")
    """
    
    def __init__(self):
        self._executors: Dict[WorkflowStepType, StepExecutor] = {
            WorkflowStepType.ASSERTION: AssertionExecutor(),
            WorkflowStepType.WAIT: WaitExecutor(),
            WorkflowStepType.SCRIPT: ScriptExecutor(),
        }
    
    def register_executor(self, step_type: WorkflowStepType, executor: StepExecutor) -> None:
        """Register a step executor."""
        self._executors[step_type] = executor
    
    def run(
        self,
        workflow: Workflow,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowResult:
        """
        Run a workflow.
        
        Args:
            workflow: The workflow to run
            initial_context: Initial context variables
            
        Returns:
            WorkflowResult with all step results
        """
        context = dict(workflow.variables)
        if initial_context:
            context.update(initial_context)
        
        result = WorkflowResult(
            workflow_id=workflow.id,
            status=StepStatus.RUNNING,
        )
        
        all_passed = True
        
        for step in workflow.steps:
            step_result = self._run_step(step, context)
            result.step_results.append(step_result)
            
            # Store output in context
            if step_result.output:
                context[f"step_{step.id}"] = step_result.output
            
            if not step_result.passed:
                all_passed = False
                if step_result.status == StepStatus.ERROR:
                    break
        
        result.status = StepStatus.PASSED if all_passed else StepStatus.FAILED
        result.completed_at = datetime.now()
        
        return result
    
    def _run_step(self, step: WorkflowStep, context: Dict[str, Any]) -> StepResult:
        """Run a single step with retries."""
        executor = self._executors.get(step.step_type)
        
        if not executor:
            return StepResult(
                step_id=step.id,
                status=StepStatus.ERROR,
                error=f"No executor for step type: {step.step_type}",
            )
        
        last_result = None
        for attempt in range(step.retry_count + 1):
            last_result = executor.execute(step, context)
            last_result.retries = attempt
            
            if last_result.passed:
                break
        
        return last_result


__all__ = [
    # Enums
    "WorkflowStepType",
    "StepStatus",
    # Data classes
    "WorkflowStep",
    "StepResult",
    "WorkflowResult",
    "Workflow",
    # Executors
    "StepExecutor",
    "AssertionExecutor",
    "WaitExecutor",
    "ScriptExecutor",
    # Core
    "WorkflowRunner",
]
