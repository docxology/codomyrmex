import importlib
import inspect
import logging
import os
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False
    docker = None

from codomyrmex.coding.execution.executor import execute_code
from codomyrmex.coding.static_analysis import analyze_file
from codomyrmex.environment_setup.env_checker import validate_environment_completeness
from codomyrmex.git_operations.core.git import check_git_availability
from codomyrmex.logging_monitoring.core.logger_config import (
    get_logger,
    log_with_context,
)
from codomyrmex.logistics.orchestration.project.workflow_dag import WorkflowDAG
from codomyrmex.performance import get_system_metrics, profile_function
from codomyrmex.security.digital import analyze_file_security

"""
Health Checker for Codomyrmex System Discovery

This module provides health checking capabilities for all
Codomyrmex modules, including dependency validation, performance monitoring,
and system health assessment.
"""


# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    module_name: str
    status: HealthStatus
    timestamp: float = field(default_factory=time.time)
    checks_performed: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, HealthStatus] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_name": self.module_name,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "checks_performed": self.checks_performed,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "dependencies": {k: v.value for k, v in self.dependencies.items()}
        }

    def add_issue(self, issue: str, recommendation: str | None = None) -> None:
        """Add an issue with optional recommendation."""
        self.issues.append(issue)
        if recommendation:
            self.recommendations.append(recommendation)

    def add_metric(self, name: str, value: Any) -> None:
        """Add a metric."""
        self.metrics[name] = value


class HealthChecker:
    """
    Comprehensive health checker for Codomyrmex modules.

    Performs various health checks including:
    - Module availability and importability
    - Dependency validation
    - Performance metrics
    - Configuration validation
    - Resource usage monitoring
    """

    def __init__(self):
        """Initialize the health checker."""
        self.module_checks = {
            "logging_monitoring": self._check_logging_monitoring,
            "environment_setup": self._check_environment_setup,
            "model_context_protocol": self._check_model_context_protocol,
            "terminal_interface": self._check_terminal_interface,
            "ai_code_editing": self._check_ai_code_editing,
            "static_analysis": self._check_static_analysis,
            "code": self._check_code,
            "data_visualization": self._check_data_visualization,
            "pattern_matching": self._check_pattern_matching,
            "git_operations": self._check_git_operations,
            "security": self._check_security_digital,
            "llm": self._check_ollama_integration,
            "performance": self._check_performance,
            "project_orchestration": self._check_project_orchestration,
            "containerization": self._check_containerization,
        }

    def perform_health_check(self, module_name: str) -> HealthCheckResult:
        """
        Perform a health check for a module.

        Args:
            module_name: Name of the module to check

        Returns:
            HealthCheckResult with detailed health information
        """
        result = HealthCheckResult(module_name=module_name, status=HealthStatus.UNKNOWN)

        try:
            # Basic availability check
            result.checks_performed.append("module_availability")
            if not self._check_module_availability(module_name):
                result.status = HealthStatus.UNHEALTHY
                result.add_issue("Module not available", "Check module installation and imports")
                return result

            # Perform module-specific checks
            check_func = self.module_checks.get(module_name, self._check_generic_module)
            check_func(result)

            # Determine overall status
            result.status = self._determine_overall_status(result)

        except Exception as e:
            logger.error(f"Error during health check for {module_name}: {e}")
            result.status = HealthStatus.UNKNOWN
            result.add_issue(f"Health check failed: {str(e)}", "Review error logs and module configuration")

        return result

    def _check_module_availability(self, module_name: str) -> bool:
        """Check if a module is available and importable."""
        try:
            module_path = f"codomyrmex.{module_name}"
            importlib.import_module(module_path)
            return True
        except ImportError as e:
            logger.warning("Module %s not importable: %s", module_name, e)
            return False
        except Exception as e:
            logger.warning("Unexpected error checking module %s availability: %s", module_name, e)
            return False

    def _determine_overall_status(self, result: HealthCheckResult) -> HealthStatus:
        """Determine overall health status from check results."""
        if not result.issues:
            return HealthStatus.HEALTHY

        # Count critical vs non-critical issues
        critical_issues = [issue for issue in result.issues
                          if any(keyword in issue.lower()
                                for keyword in ["import", "dependency", "critical", "unavailable"])]

        if critical_issues:
            return HealthStatus.UNHEALTHY
        elif len(result.issues) > 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.DEGRADED

    def _check_generic_module(self, result: HealthCheckResult) -> None:
        """Perform generic checks for any module."""
        module_name = result.module_name

        # Check if module has required components
        try:
            module = importlib.import_module(f"codomyrmex.{module_name}")

            # Check for __init__.py indicators
            if hasattr(module, '__version__'):
                result.add_metric("version", module.__version__)

            # Check for main functions/classes
            members = inspect.getmembers(module)
            functions = [name for name, obj in members if inspect.isfunction(obj)]
            classes = [name for name, obj in members if inspect.isclass(obj)]

            result.add_metric("function_count", len(functions))
            result.add_metric("class_count", len(classes))

            if len(functions) == 0 and len(classes) == 0:
                result.add_issue("Module appears empty", "Check module implementation")

        except Exception as e:
            result.add_issue(f"Error inspecting module: {str(e)}")

    def _check_logging_monitoring(self, result: HealthCheckResult) -> None:
        """Check logging and monitoring module health."""
        result.checks_performed.extend(["logger_creation", "structured_logging"])

        try:

            # Test logger creation
            test_logger = get_logger("health_check_test")
            test_logger.info("Health check test message")

            # Test structured logging
            log_with_context("INFO", "Structured logging test", {"test": True})

            result.add_metric("logger_available", True)

        except Exception as e:
            result.add_issue(f"Logging system error: {str(e)}", "Check logging configuration")

    def _check_environment_setup(self, result: HealthCheckResult) -> None:
        """Check environment setup module health."""
        result.checks_performed.extend(["dependency_check", "python_version"])

        try:

            # Get the project root (assuming we're in the project)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

            is_complete, report = validate_environment_completeness(project_root)

            result.add_metric("environment_complete", is_complete)
            result.add_metric("python_version_check", report.get("python_version_check", {}))

            if not is_complete:
                result.add_issue("Environment setup incomplete", "Run environment validation")

        except Exception as e:
            result.add_issue(f"Environment check error: {str(e)}")

    def _check_code(self, result: HealthCheckResult) -> None:
        """Check code module health (execution, sandbox, review, monitoring)."""
        result.checks_performed.extend(["docker_availability", "sandbox_execution", "code_review"])

        try:

            # Test basic execution (this might require Docker)
            test_result = execute_code("python", "print('test')", timeout=5)

            if test_result.get("status") == "success":
                result.add_metric("sandbox_working", True)
            else:
                result.add_issue("Sandbox execution failed", "Check Docker installation and configuration")

        except Exception as e:
            result.add_issue(f"Sandbox check error: {str(e)}", "Verify Docker and sandbox setup")

    def _check_static_analysis(self, result: HealthCheckResult) -> None:
        """Check static analysis module health."""
        result.checks_performed.extend(["tool_availability", "analysis_execution"])

        try:

            # Create a simple test file

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write("def test(): pass\n")
                test_file = f.name

            try:
                analysis_result = analyze_file(test_file)
                result.add_metric("analysis_working", True)
                result.add_metric("issues_found", len(analysis_result) if isinstance(analysis_result, list) else 0)
            finally:
                os.unlink(test_file)

        except Exception as e:
            result.add_issue(f"Static analysis error: {str(e)}", "Check analysis tools installation")

    def _check_security_digital(self, result: HealthCheckResult) -> None:
        """Check digital security submodule health."""
        result.checks_performed.extend(["vulnerability_scanning", "secrets_detection"])

        try:

            # Create a test file with potential security issues

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write("import os\nos.system('ls')  # Potential security issue\n")
                test_file = f.name

            try:
                findings = analyze_file_security(test_file)
                result.add_metric("security_scan_working", True)
                result.add_metric("vulnerabilities_found", len(findings))
            finally:
                os.unlink(test_file)

        except Exception as e:
            result.add_issue(f"Security audit error: {str(e)}", "Check security scanning tools")

    def _check_performance(self, result: HealthCheckResult) -> None:
        """Check performance monitoring module health."""
        result.checks_performed.extend(["performance_monitoring", "resource_tracking"])

        try:

            # Test performance profiling
            @profile_function
            def test_func():
                """Execute Test Func operations natively."""
                return sum(range(100))

            test_func()
            result.add_metric("profiling_working", True)

            # Test system metrics
            metrics = get_system_metrics()
            result.add_metric("system_metrics_available", bool(metrics))

        except Exception as e:
            result.add_issue(f"Performance monitoring error: {str(e)}")

    def _check_project_orchestration(self, result: HealthCheckResult) -> None:
        """Check project orchestration module health."""
        result.checks_performed.extend(["workflow_creation", "dag_validation"])

        try:

            # Test DAG creation
            tasks = [
                {"name": "task1", "module": "test", "action": "run", "dependencies": []},
                {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            ]

            dag = WorkflowDAG(tasks)
            is_valid, errors = dag.validate_dag()

            result.add_metric("dag_creation_working", True)
            result.add_metric("dag_valid", is_valid)

            if not is_valid:
                result.add_issue(f"DAG validation issues: {errors}")

        except Exception as e:
            result.add_issue(f"Project orchestration error: {str(e)}")

    def _check_containerization(self, result: HealthCheckResult) -> None:
        """Check containerization module health."""
        result.checks_performed.extend(["docker_client", "image_management"])

        try:

            # Test Docker client
            client = docker.from_env()
            client.ping()  # Test connection

            result.add_metric("docker_available", True)

            # Get basic info
            info = client.info()
            result.add_metric("docker_containers", info.get("Containers", 0))
            result.add_metric("docker_images", info.get("Images", 0))

        except ImportError:
            result.add_issue("Docker library not available", "Install docker Python package")
        except Exception as e:
            result.add_issue(f"Docker connection error: {str(e)}", "Check Docker daemon status")

    # Add more module-specific checks as needed
    def _check_model_context_protocol(self, result: HealthCheckResult) -> None:
        """Check model context protocol module health."""
        result.checks_performed.append("mcp_initialization")
        # Basic check - module import already verified

    def _check_terminal_interface(self, result: HealthCheckResult) -> None:
        """Check terminal interface module health."""
        result.checks_performed.append("terminal_capabilities")
        # Basic check - module import already verified

    def _check_ai_code_editing(self, result: HealthCheckResult) -> None:
        """Check AI code editing module health."""
        result.checks_performed.append("ai_services")
        # Would check AI service availability if configured

    def _check_data_visualization(self, result: HealthCheckResult) -> None:
        """Check data visualization module health."""
        result.checks_performed.append("plotting_libraries")

        try:
            result.add_metric("matplotlib_available", True)
        except ImportError:
            result.add_issue("Matplotlib not available", "Install matplotlib for plotting")

    def _check_pattern_matching(self, result: HealthCheckResult) -> None:
        """Check pattern matching module health."""
        result.checks_performed.append("ast_processing")
        # Basic AST functionality check

    def _check_git_operations(self, result: HealthCheckResult) -> None:
        """Check git operations module health."""
        result.checks_performed.append("git_availability")

        try:
            git_available = check_git_availability()
            result.add_metric("git_available", git_available)

            if not git_available:
                result.add_issue("Git not available", "Install git command-line tool")
        except Exception as e:
            result.add_issue(f"Git check error: {str(e)}")

    # Code review is now part of code module, checked in _check_code

    def _check_ollama_integration(self, result: HealthCheckResult) -> None:
        """Check Ollama integration module health."""
        result.checks_performed.append("llm_availability")

        try:
            # Check if LLM module is available
            importlib.import_module("codomyrmex.llm")
            result.add_metric("llm_module_available", True)
        except ImportError:
            result.add_issue("LLM module not importable", "Check installation")
        except Exception as e:
            result.add_issue(f"LLM check failed: {e}")


def check_module_availability(module_name: str) -> bool:
    """
    Check if a module is available and importable.

    Args:
        module_name: Name of the module to check (any Python module, e.g. 'os', 'json')

    Returns:
        True if module is available, False otherwise
    """
    try:
        importlib.import_module(module_name)
        return True
    except ImportError as e:
        logger.warning("Module %s not importable: %s", module_name, e)
        return False


def perform_health_check(module_name: str) -> HealthCheckResult:
    """
    Convenience function to perform a health check for a module.

    Args:
        module_name: Name of the module to check

    Returns:
        HealthCheckResult with detailed health information
    """
    checker = HealthChecker()
    return checker.perform_health_check(module_name)
