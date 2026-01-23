"""Analysis pipeline using codomyrmex orchestration capabilities.

Demonstrates integration with:
- codomyrmex.orchestrator for DAG-based workflow execution
- codomyrmex.events for event-driven architecture
- codomyrmex.serialization for data persistence

Example:
    >>> from pathlib import Path
    >>> from src.pipeline import AnalysisPipeline
    >>> 
    >>> pipeline = AnalysisPipeline()
    >>> result = pipeline.execute(Path("src"))
    >>> print(f"Status: {result.status.value}")
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

# Try to import codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger
except ImportError:
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

logger = get_logger(__name__)


class PipelineStatus(Enum):
    """Status of pipeline execution.
    
    Values:
        PENDING: Pipeline has not started.
        RUNNING: Pipeline is currently executing.
        COMPLETED: Pipeline finished successfully.
        FAILED: Pipeline encountered an error.
        CANCELLED: Pipeline was cancelled.
    """
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineStep:
    """A single step in the analysis pipeline.
    
    Represents an atomic unit of work in the pipeline with:
    - A handler function that performs the work
    - Optional dependencies on other steps
    - Status tracking and error handling
    
    Attributes:
        name: Unique identifier for the step.
        handler: Callable that executes the step.
        dependencies: List of step names that must complete first.
        status: Current execution status.
        result: Output from successful execution.
        error: Error message if step failed.
        started_at: When execution began.
        completed_at: When execution finished.
    """
    
    name: str
    handler: Callable[[Dict[str, Any]], Any]
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def duration_seconds(self) -> float:
        """Get step execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute this pipeline step.
        
        Args:
            context: Shared pipeline context dictionary.
            
        Returns:
            Result from the handler function.
            
        Raises:
            Exception: Any exception from the handler.
        """
        self.started_at = datetime.now()
        self.status = PipelineStatus.RUNNING
        logger.debug(f"Step '{self.name}' started")
        
        try:
            self.result = self.handler(context)
            self.status = PipelineStatus.COMPLETED
            self.completed_at = datetime.now()
            logger.debug(f"Step '{self.name}' completed in {self.duration_seconds:.2f}s")
            return self.result
        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.now()
            logger.error(f"Step '{self.name}' failed: {e}")
            raise


@dataclass
class PipelineResult:
    """Result of pipeline execution.
    
    Contains comprehensive information about the pipeline run including:
    - Overall status and timing
    - Results from each step
    - Any errors encountered
    
    Attributes:
        status: Final pipeline status.
        started_at: When pipeline began.
        completed_at: When pipeline finished.
        steps_completed: Number of steps that completed.
        total_steps: Total number of steps in pipeline.
        results: Dictionary of step name to result.
        errors: List of error messages.
        step_durations: Timing for each step.
    """
    
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: int = 0
    total_steps: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    step_durations: Dict[str, float] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        """Get total pipeline duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    @property
    def is_success(self) -> bool:
        """Check if pipeline completed successfully."""
        return self.status == PipelineStatus.COMPLETED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "step_durations": self.step_durations,
            "errors": self.errors,
        }


class AnalysisPipeline:
    """DAG-based analysis pipeline.
    
    Orchestrates code analysis workflow with configurable steps
    and dependency management using codomyrmex.orchestrator patterns.
    
    The default pipeline includes these steps:
    1. load_config - Load project configuration
    2. validate - Validate inputs and settings
    3. analyze - Run code analysis
    4. visualize - Generate visualizations
    5. report - Create final reports
    
    Attributes:
        config_path: Optional path to workflow configuration.
        steps: Dictionary of registered pipeline steps.
        context: Shared context passed to all steps.
        
    Example:
        >>> pipeline = AnalysisPipeline()
        >>> result = pipeline.execute(Path("src"))
        >>> if result.is_success:
        ...     print(f"Completed in {result.duration_seconds:.2f}s")
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the pipeline.
        
        Args:
            config_path: Optional path to workflow YAML configuration.
        """
        self.config_path = config_path
        self.steps: Dict[str, PipelineStep] = {}
        self.context: Dict[str, Any] = {}
        self._setup_default_pipeline()
        
    def _setup_default_pipeline(self) -> None:
        """Set up the default analysis pipeline steps."""
        
        # Step 1: Load configuration
        self.add_step(
            name="load_config",
            handler=self._step_load_config,
            description="Load project configuration",
            dependencies=[]
        )
        
        # Step 2: Validate inputs
        self.add_step(
            name="validate",
            handler=self._step_validate,
            description="Validate inputs and configuration",
            dependencies=["load_config"]
        )
        
        # Step 3: Run analysis
        self.add_step(
            name="analyze",
            handler=self._step_analyze,
            description="Run code analysis",
            dependencies=["validate"]
        )
        
        # Step 4: Generate visualizations
        self.add_step(
            name="visualize",
            handler=self._step_visualize,
            description="Generate visualizations",
            dependencies=["analyze"]
        )
        
        # Step 5: Create report
        self.add_step(
            name="report",
            handler=self._step_report,
            description="Create final report",
            dependencies=["analyze", "visualize"]
        )
        
    def add_step(
        self,
        name: str,
        handler: Callable[[Dict[str, Any]], Any],
        description: str = "",
        dependencies: Optional[List[str]] = None
    ) -> None:
        """Add a step to the pipeline.
        
        Args:
            name: Unique identifier for the step.
            handler: Function to execute for this step.
            description: Human-readable description.
            dependencies: List of step names that must complete first.
            
        Raises:
            ValueError: If step name already exists.
        """
        if name in self.steps:
            raise ValueError(f"Step '{name}' already exists")
            
        self.steps[name] = PipelineStep(
            name=name,
            handler=handler,
            description=description,
            dependencies=dependencies or []
        )
        logger.debug(f"Added step '{name}' with dependencies {dependencies}")
        
    def remove_step(self, name: str) -> None:
        """Remove a step from the pipeline.
        
        Args:
            name: Name of step to remove.
        """
        if name in self.steps:
            del self.steps[name]
            
    def execute(self, target_path: Optional[Path] = None) -> PipelineResult:
        """Execute the analysis pipeline.
        
        Runs all pipeline steps in dependency order, tracking
        status and collecting results.
        
        Args:
            target_path: Optional target path to analyze.
            
        Returns:
            PipelineResult with execution details.
            
        Example:
            >>> result = pipeline.execute(Path("src"))
            >>> print(f"Status: {result.status.value}")
            >>> print(f"Steps: {result.steps_completed}/{result.total_steps}")
        """
        result = PipelineResult(
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(),
            total_steps=len(self.steps)
        )
        
        # Initialize context
        self.context = {
            "target_path": target_path or Path("."),
            "results": {},
            "config": {},
        }
        
        logger.info(f"Starting pipeline with {len(self.steps)} steps")
        logger.info(f"Target: {self.context['target_path']}")
        
        # Reset all step statuses
        for step in self.steps.values():
            step.status = PipelineStatus.PENDING
            step.result = None
            step.error = None
        
        # Execute steps in dependency order
        execution_order = self._get_execution_order()
        logger.debug(f"Execution order: {execution_order}")
        
        for step_name in execution_order:
            step = self.steps[step_name]
            
            # Check dependencies
            if not self._dependencies_satisfied(step):
                error_msg = f"Dependencies not satisfied for '{step_name}'"
                logger.error(error_msg)
                result.errors.append(error_msg)
                result.status = PipelineStatus.FAILED
                break
                
            try:
                logger.info(f"Executing step: {step_name}")
                step.execute(self.context)
                
                result.steps_completed += 1
                result.results[step_name] = step.result
                result.step_durations[step_name] = step.duration_seconds
                
            except Exception as e:
                error_msg = f"{step_name}: {e}"
                logger.error(f"Step '{step_name}' failed: {e}")
                result.errors.append(error_msg)
                result.status = PipelineStatus.FAILED
                break
        else:
            # All steps completed successfully
            result.status = PipelineStatus.COMPLETED
            
        result.completed_at = datetime.now()
        
        status_emoji = "✅" if result.is_success else "❌"
        logger.info(
            f"{status_emoji} Pipeline {result.status.value} in {result.duration_seconds:.2f}s "
            f"({result.steps_completed}/{result.total_steps} steps)"
        )
        
        return result
        
    def _get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order.
        
        Returns:
            List of step names in dependency-respecting order.
        """
        visited = set()
        order = []
        
        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            
            step = self.steps.get(name)
            if step:
                for dep in step.dependencies:
                    visit(dep)
                order.append(name)
            
        for name in self.steps:
            visit(name)
            
        return order
        
    def _dependencies_satisfied(self, step: PipelineStep) -> bool:
        """Check if all dependencies are satisfied.
        
        Args:
            step: Step to check dependencies for.
            
        Returns:
            True if all dependencies completed successfully.
        """
        for dep in step.dependencies:
            if dep not in self.steps:
                logger.warning(f"Dependency '{dep}' not found")
                return False
            if self.steps[dep].status != PipelineStatus.COMPLETED:
                return False
        return True
        
    # Pipeline step implementations
    
    def _step_load_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load pipeline configuration.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Loaded configuration dictionary.
        """
        config = {
            "include_patterns": ["*.py"],
            "output_formats": ["html", "json"],
            "max_complexity": 10,
            "generate_dashboard": True,
            "generate_reports": True,
        }
        
        # Try to load from config file
        if self.config_path and self.config_path.exists():
            try:
                import yaml
                with open(self.config_path) as f:
                    loaded = yaml.safe_load(f)
                    config.update(loaded.get("execution", {}))
                    config.update(loaded.get("pipeline", {}))
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                
        context["config"] = config
        return config
        
    def _step_validate(self, context: Dict[str, Any]) -> bool:
        """Validate inputs and configuration.
        
        Args:
            context: Pipeline context.
            
        Returns:
            True if validation passed.
            
        Raises:
            ValueError: If validation fails.
        """
        target = context.get("target_path")
        
        if not target:
            raise ValueError("No target path specified")
            
        target_path = Path(target)
        if not target_path.exists():
            raise ValueError(f"Target path does not exist: {target_path}")
            
        logger.debug(f"Validated target: {target_path}")
        return True
        
    def _step_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run code analysis.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Analysis results dictionary.
        """
        from .analyzer import ProjectAnalyzer
        
        # Get config path for analyzer
        config_dir = Path(__file__).parent.parent / "config"
        settings_path = config_dir / "settings.yaml" if config_dir.exists() else None
        
        analyzer = ProjectAnalyzer(settings_path)
        results = analyzer.analyze(context["target_path"])
        
        # Store in context for later steps
        context["analysis_results"] = results
        
        summary = results.get("summary", {})
        logger.info(
            f"Analysis complete: {summary.get('total_files', 0)} files, "
            f"{summary.get('total_lines', 0)} lines"
        )
        
        return results
        
    def _step_visualize(self, context: Dict[str, Any]) -> Optional[Path]:
        """Generate visualizations.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Path to generated dashboard, or None if skipped.
        """
        from .visualizer import DataVisualizer
        
        config = context.get("config", {})
        if not config.get("generate_dashboard", True):
            logger.info("Dashboard generation skipped per config")
            return None
        
        # Set up output directory
        output_dir = Path(__file__).parent.parent / "reports" / "visualizations"
        
        visualizer = DataVisualizer(output_dir)
        analysis_results = context.get("analysis_results", {})
        
        dashboard_path = visualizer.create_dashboard(analysis_results)
        context["dashboard_path"] = dashboard_path
        
        return dashboard_path
        
    def _step_report(self, context: Dict[str, Any]) -> Optional[Path]:
        """Generate final report.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Path to generated report, or None if skipped.
        """
        from .reporter import ReportGenerator, ReportConfig
        
        config = context.get("config", {})
        if not config.get("generate_reports", True):
            logger.info("Report generation skipped per config")
            return None
        
        # Set up output directory
        output_dir = Path(__file__).parent.parent / "reports" / "output"
        
        generator = ReportGenerator(output_dir)
        analysis_results = context.get("analysis_results", {})
        
        report_config = ReportConfig(
            title="Code Analysis Report",
            format="html",
            include_visualizations=True,
        )
        
        report_path = generator.generate(analysis_results, report_config)
        context["report_path"] = report_path
        
        return report_path
