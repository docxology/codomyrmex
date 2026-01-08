from datetime import datetime
from typing import Any, Optional
import json
import os
import shutil
import subprocess
import sys
import time

from build_manager import FunctionName, ClassName
from dataclasses import dataclass, field
from enum import Enum
import shlex
import tarfile
import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.performance import monitor_performance, performance_context







































































































"""
"""Core business logic and data management

This module provides build_manager functionality including:
- 27 functions: create_python_build_target, create_docker_build_target, create_static_build_target...
- 10 classes: BuildType, BuildStatus, BuildEnvironment...

Usage:
    # Example usage here
"""
Advanced build management functionality for Codomyrmex.

This module provides comprehensive build orchestration, dependency management,
artifact synthesis, and deployment automation capabilities.
"""



# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation

# Import logger setup

# Get module logger
logger = get_logger(__name__)

# Import performance monitoring
try:
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
    """Brief description of decorator.

Args:
    func : Description of func

    Returns: Description of return value
"""
            return func

        return decorator

    class performance_context:
        """
        A class for handling performance_context operations.
        """
        def __init__(self, context_name: str = "unknown_context", *args, **kwargs):
            """Initialize performance context (fallback)."""
            self.context_name = context_name
            self.start_time = 0

        def __enter__(self):
    """Brief description of __enter__.

Args:
    self : Description of self

    Returns: Description of return value
"""
            self.start_time = time.time()
            logger.debug(f"Entering performance context: {self.context_name}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
    """Brief description of __exit__.

Args:
    self : Description of self
    exc_type : Description of exc_type
    exc_val : Description of exc_val
    exc_tb : Description of exc_tb

    Returns: Description of return value
"""
            duration = time.time() - self.start_time
            logger.debug(f"Exiting performance context: {self.context_name} (Duration: {duration:.4f}s)")


# Enums for build types and status
class BuildType(Enum):
    """Types of builds supported."""

    PYTHON = "python"
    NODEJS = "nodejs"
    DOCKER = "docker"
    STATIC = "static"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PACKAGING = "packaging"
    DEPLOYMENT = "deployment"


class BuildStatus(Enum):
    """Build status states."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class BuildEnvironment(Enum):
    """Build environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DependencyType(Enum):
    """Types of dependencies."""

    RUNTIME = "runtime"
    DEVELOPMENT = "development"
    BUILD = "build"
    OPTIONAL = "optional"


@dataclass
class BuildStep:
    """Individual build step definition."""

    name: str
    command: str
    working_dir: Optional[str] = None
    environment: dict[str, str] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 300  # seconds
    retry_count: int = 0
    required: bool = True
    parallel: bool = False
    condition: Optional[str] = None  # Command to check if step should run


@dataclass
class BuildTarget:
    """Build target definition."""

    name: str
    build_type: BuildType
    source_path: str
    output_path: str
    dependencies: list[str] = field(default_factory=list)
    environment: BuildEnvironment = BuildEnvironment.DEVELOPMENT
    config: dict[str, Any] = field(default_factory=dict)
    steps: list[BuildStep] = field(default_factory=list)


@dataclass
class BuildResult:
    """Result of a build operation."""

    target_name: str
    status: BuildStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    output: str = ""
    error: str = ""
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Dependency:
    """Dependency definition."""

    name: str
    version: str
    dep_type: DependencyType
    source: str = "pypi"  # pypi, npm, git, local, etc.
    install_command: Optional[str] = None
    check_command: Optional[str] = None


class BuildManager:
    """Main build management class."""

    def __init__(self, project_root: str = None, config_path: str = None):
        """
        Initialize the build manager.

        Args:
            project_root: Root directory of the project
            config_path: Path to build configuration file
        """
        self.project_root = project_root or os.getcwd()
        self.config_path = config_path or os.path.join(self.project_root, "build.yaml")
        self.targets: dict[str, BuildTarget] = {}
        self.dependencies: dict[str, Dependency] = {}
        self.results: list[BuildResult] = []
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load build configuration from file."""
        if not os.path.exists(self.config_path):
            logger.warning(
                f"Build config not found at {self.config_path}, using defaults"
            )
            return self._get_default_config()

        try:
            with open(self.config_path) as f:
                if self.config_path.endswith(".yaml") or self.config_path.endswith(
                    ".yml"
                ):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error accessing build config file: {e}")
            return self._get_default_config()
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing build config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default build configuration."""
        return {
            "build_dir": "build",
            "cache_dir": ".build_cache",
            "parallel_jobs": 4,
            "timeout": 1800,  # 30 minutes
            "retry_count": 3,
            "clean_before_build": True,
            "environments": {
                "development": {"debug": True, "optimize": False},
                "production": {"debug": False, "optimize": True},
            },
        }

    @monitor_performance("add_build_target")
    def add_build_target(self, target: BuildTarget) -> bool:
        """
        Add a build target to the manager.

        Args:
            target: Build target to add

        Returns:
            True if successful, False otherwise
        """
        try:
            self.targets[target.name] = target
            logger.info(f"Added build target: {target.name}")
            return True
        except (TypeError, AttributeError, KeyError) as e:
            logger.error(f"Error adding build target {target.name}: {e}")
            return False

    @monitor_performance("add_dependency")
    def add_dependency(self, dependency: Dependency) -> bool:
        """
        Add a dependency to the manager.

        Args:
            dependency: Dependency to add

        Returns:
            True if successful, False otherwise
        """
        try:
            self.dependencies[dependency.name] = dependency
            logger.info(f"Added dependency: {dependency.name}")
            return True
        except (TypeError, AttributeError, KeyError) as e:
            logger.error(f"Error adding dependency {dependency.name}: {e}")
            return False

    @monitor_performance("check_dependencies")
    def check_dependencies(self) -> dict[str, bool]:
        """
        Check if all dependencies are available.

        Returns:
            Dictionary mapping dependency names to availability status
        """
        results = {}

        for name, dep in self.dependencies.items():
            try:
                if dep.check_command:
                    # Use shlex.split to safely parse command string without shell=True
                    cmd_parts = shlex.split(dep.check_command) if isinstance(dep.check_command, str) else dep.check_command
                    result = subprocess.run(
                        cmd_parts,
                        shell=False,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    results[name] = result.returncode == 0
                else:
                    # Default check based on dependency type
                    if dep.source == "pypi":
                        result = subprocess.run(
                            [sys.executable, "-c", f"import {dep.name}"],
                            capture_output=True,
                            timeout=30,
                        )
                        results[name] = result.returncode == 0
                    elif dep.source == "npm":
                        result = subprocess.run(
                            ["npm", "list", dep.name], capture_output=True, timeout=30
                        )
                        results[name] = result.returncode == 0
                    else:
                        results[name] = True  # Assume available for other sources

            except (subprocess.SubprocessError, FileNotFoundError, ValueError, OSError) as e:
                logger.error(f"Error checking dependency {name}: {e}")
                results[name] = False

        return results

    @monitor_performance("install_dependencies")
    def install_dependencies(self, force: bool = False) -> dict[str, bool]:
        """
        Install missing dependencies.

        Args:
            force: Whether to reinstall all dependencies

        Returns:
            Dictionary mapping dependency names to installation status
        """
        results = {}

        for name, dep in self.dependencies.items():
            try:
                if not force and self._is_dependency_installed(dep):
                    results[name] = True
                    continue

                if dep.install_command:
                    # Use shlex.split to safely parse command string without shell=True
                    cmd_parts = shlex.split(dep.install_command) if isinstance(dep.install_command, str) else dep.install_command
                    result = subprocess.run(
                        cmd_parts,
                        shell=False,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes
                    )
                    results[name] = result.returncode == 0
                else:
                    # Default installation based on source
                    if dep.source == "pypi":
                        result = subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                f"{dep.name}=={dep.version}",
                            ],
                            capture_output=True,
                            text=True,
                            timeout=300,
                        )
                        results[name] = result.returncode == 0
                    elif dep.source == "npm":
                        result = subprocess.run(
                            ["npm", "install", f"{dep.name}@{dep.version}"],
                            capture_output=True,
                            text=True,
                            timeout=300,
                        )
                        results[name] = result.returncode == 0
                    else:
                        results[name] = True  # Assume installed for other sources

            except (subprocess.SubprocessError, FileNotFoundError, ValueError, OSError) as e:
                logger.error(f"Error installing dependency {name}: {e}")
                results[name] = False

        return results

    def _is_dependency_installed(self, dep: Dependency) -> bool:
        """Check if a dependency is already installed."""
        try:
            if dep.check_command:
                # Use shlex.split to safely parse command string without shell=True
                cmd_parts = shlex.split(dep.check_command) if isinstance(dep.check_command, str) else dep.check_command
                result = subprocess.run(
                    cmd_parts, shell=False, capture_output=True, timeout=30
                )
                return result.returncode == 0
            return True
        except (subprocess.SubprocessError, FileNotFoundError, ValueError, OSError):
            return False

    @monitor_performance("build_target")
    def build_target(
        self, target_name: str, environment: BuildEnvironment = None
    ) -> BuildResult:
        """
        Build a specific target.

        Args:
            target_name: Name of the target to build
            environment: Build environment to use

        Returns:
            Build result
        """
        if target_name not in self.targets:
            raise ValueError(f"Build target '{target_name}' not found")

        target = self.targets[target_name]
        environment = environment or target.environment

        start_time = datetime.now()
        result = BuildResult(
            target_name=target_name, status=BuildStatus.RUNNING, start_time=start_time
        )

        try:
            logger.info(f"Starting build for target: {target_name}")

            # Check dependencies
            dep_status = self.check_dependencies()
            missing_deps = [
                name for name, available in dep_status.items() if not available
            ]
            if missing_deps:
                logger.warning(f"Missing dependencies: {missing_deps}")
                # Try to install missing dependencies
                install_results = self.install_dependencies()
                still_missing = [
                    name for name, installed in install_results.items() if not installed
                ]
                if still_missing:
                    result.status = BuildStatus.FAILED
                    result.error = f"Missing dependencies: {still_missing}"
                    return result

            # Create build directory
            build_dir = os.path.join(
                self.project_root, self.config.get("build_dir", "build")
            )
            os.makedirs(build_dir, exist_ok=True)

            # Execute build steps
            for step in target.steps:
                if not self._should_run_step(step, environment):
                    logger.info(f"Skipping step: {step.name}")
                    continue

                step_result = self._execute_build_step(step, target, environment)
                if not step_result and step.required:
                    result.status = BuildStatus.FAILED
                    result.error = f"Required step failed: {step.name}"
                    break
                elif not step_result:
                    logger.warning(f"Optional step failed: {step.name}")

            if result.status == BuildStatus.RUNNING:
                result.status = BuildStatus.SUCCESS

        except (OSError, subprocess.SubprocessError, ValueError, KeyError) as e:
            logger.error(f"Error building target {target_name}: {e}")
            result.status = BuildStatus.FAILED
            result.error = str(e)
        except Exception as e:
            # Final fallback for unexpected errors
            logger.error(f"Unexpected error building target {target_name}: {e}", exc_info=True)
            result.status = BuildStatus.FAILED
            result.error = str(e)

        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            self.results.append(result)

            logger.info(f"Build completed for {target_name}: {result.status.value}")

        return result

    def _should_run_step(self, step: BuildStep, environment: BuildEnvironment) -> bool:
        """Check if a build step should run."""
        if not step.condition:
            return True

        try:
            # Use shlex.split to safely parse command string without shell=True
            cmd_parts = shlex.split(step.condition) if isinstance(step.condition, str) else step.condition
            result = subprocess.run(
                cmd_parts, shell=False, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, ValueError, OSError) as e:
            logger.error(f"Error checking step condition: {e}")
            return True  # Run by default if condition check fails

    def _execute_build_step(
        self, step: BuildStep, target: BuildTarget, environment: BuildEnvironment
    ) -> bool:
        """Execute a single build step."""
        try:
            logger.info(f"Executing step: {step.name}")

            # Set up environment
            env = os.environ.copy()
            env.update(step.environment)

            # Set up working directory
            working_dir = step.working_dir or target.source_path
            if not os.path.isabs(working_dir):
                working_dir = os.path.join(self.project_root, working_dir)

            # Execute command
            # Use shlex.split to safely parse command string without shell=True
            cmd_parts = shlex.split(step.command) if isinstance(step.command, str) else step.command
            result = subprocess.run(
                cmd_parts,
                shell=False,
                cwd=working_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=step.timeout,
            )

            if result.returncode == 0:
                logger.info(f"Step completed successfully: {step.name}")
                return True
            else:
                logger.error(f"Step failed: {step.name}")
                logger.error(f"Error output: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Step timed out: {step.name}")
            return False
        except (subprocess.SubprocessError, FileNotFoundError, ValueError, OSError) as e:
            logger.error(f"Error executing step {step.name}: {e}")
            return False

    @monitor_performance("build_all_targets")
    def build_all_targets(
        self, environment: BuildEnvironment = None
    ) -> list[BuildResult]:
        """
        Build all targets.

        Args:
            environment: Build environment to use

        Returns:
            List of build results
        """
        results = []

        for target_name in self.targets:
            try:
                result = self.build_target(target_name, environment)
                results.append(result)
            except (ValueError, KeyError, OSError) as e:
                logger.error(f"Error building target {target_name}: {e}")
                results.append(
                    BuildResult(
                        target_name=target_name,
                        status=BuildStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error=str(e),
                    )
                )
            except Exception as e:
                # Final fallback for unexpected errors
                logger.error(f"Unexpected error building target {target_name}: {e}", exc_info=True)
                results.append(
                    BuildResult(
                        target_name=target_name,
                        status=BuildStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error=str(e),
                    )
                )

        return results

    @monitor_performance("clean_build")
    def clean_build(self, target_name: str = None) -> bool:
        """
        Clean build artifacts.

        Args:
            target_name: Specific target to clean (None for all)

        Returns:
            True if successful, False otherwise
        """
        try:
            build_dir = os.path.join(
                self.project_root, self.config.get("build_dir", "build")
            )

            if target_name and target_name in self.targets:
                self.targets[target_name]
                target_build_dir = os.path.join(build_dir, target_name)
                if os.path.exists(target_build_dir):
                    shutil.rmtree(target_build_dir)
                    logger.info(f"Cleaned build directory for target: {target_name}")
            else:
                if os.path.exists(build_dir):
                    shutil.rmtree(build_dir)
                    logger.info("Cleaned all build directories")

            return True
        except (OSError, PermissionError, shutil.Error) as e:
            logger.error(f"Error cleaning build: {e}")
            return False

    @monitor_performance("package_artifacts")
    def package_artifacts(self, target_name: str, output_path: str = None) -> str:
        """
        Package build artifacts.

        Args:
            target_name: Target to package
            output_path: Output package path

        Returns:
            Path to the created package
        """
        if target_name not in self.targets:
            raise ValueError(f"Build target '{target_name}' not found")

        self.targets[target_name]

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.project_root, f"{target_name}_{timestamp}.tar.gz"
            )

        try:
            build_dir = os.path.join(
                self.project_root, self.config.get("build_dir", "build")
            )
            target_build_dir = os.path.join(build_dir, target_name)

            if not os.path.exists(target_build_dir):
                raise ValueError(f"Build directory not found: {target_build_dir}")

            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(target_build_dir, arcname=target_name)

            logger.info(f"Packaged artifacts to: {output_path}")
            return output_path

        except (OSError, PermissionError, tarfile.TarError, ValueError) as e:
            logger.error(f"Error packaging artifacts: {e}")
            raise

    def get_build_summary(self) -> dict[str, Any]:
        """Get summary of all builds."""
        if not self.results:
            return {"total_builds": 0, "successful": 0, "failed": 0}

        successful = len([r for r in self.results if r.status == BuildStatus.SUCCESS])
        failed = len([r for r in self.results if r.status == BuildStatus.FAILED])

        return {
            "total_builds": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.results) if self.results else 0,
            "average_duration": (
                sum(r.duration or 0 for r in self.results) / len(self.results)
                if self.results
                else 0
            ),
        }

    def export_config(self, output_path: str) -> bool:
        """Export current configuration to file."""
        try:
            config_data = {
                "targets": {
                    name: {
                        "name": target.name,
                        "build_type": target.build_type.value,
                        "source_path": target.source_path,
                        "output_path": target.output_path,
                        "environment": target.environment.value,
                        "config": target.config,
                        "steps": [
                            {
                                "name": step.name,
                                "command": step.command,
                                "working_dir": step.working_dir,
                                "environment": step.environment,
                                "dependencies": step.dependencies,
                                "timeout": step.timeout,
                                "retry_count": step.retry_count,
                                "required": step.required,
                                "parallel": step.parallel,
                                "condition": step.condition,
                            }
                            for step in target.steps
                        ],
                    }
                    for name, target in self.targets.items()
                },
                "dependencies": {
                    name: {
                        "name": dep.name,
                        "version": dep.version,
                        "dep_type": dep.dep_type.value,
                        "source": dep.source,
                        "install_command": dep.install_command,
                        "check_command": dep.check_command,
                    }
                    for name, dep in self.dependencies.items()
                },
                "config": self.config,
            }

            with open(output_path, "w") as f:
                if output_path.endswith(".yaml") or output_path.endswith(".yml"):
                    yaml.dump(config_data, f, default_flow_style=False)
                else:
                    json.dump(config_data, f, indent=2)

            logger.info(f"Configuration exported to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False


# Convenience functions
def create_python_build_target(
    name: str, source_path: str, output_path: str = None, dependencies: list[str] = None
) -> BuildTarget:
    """Create a Python build target."""
    if output_path is None:
        output_path = f"dist/{name}"

    steps = [
        BuildStep(
            name="install_dependencies",
            command="pip install -r requirements.txt",
            required=True,
        ),
        BuildStep(name="run_tests", command="python -m pytest tests/", required=False),
        BuildStep(name="build_package", command="python -m build", required=True),
        BuildStep(
            name="create_distribution",
            command=f"python -m pip wheel . -w {output_path}",
            required=True,
        ),
    ]

    return BuildTarget(
        name=name,
        build_type=BuildType.PYTHON,
        source_path=source_path,
        output_path=output_path,
        dependencies=dependencies or [],
        steps=steps,
    )


def create_docker_build_target(
    name: str,
    source_path: str,
    dockerfile_path: str = "Dockerfile",
    image_tag: str = None,
) -> BuildTarget:
    """Create a Docker build target."""
    if image_tag is None:
        image_tag = f"{name}:latest"

    steps = [
        BuildStep(
            name="build_docker_image",
            command=f"docker build -t {image_tag} -f {dockerfile_path} .",
            required=True,
        ),
        BuildStep(
            name="test_docker_image",
            command=f"docker run --rm {image_tag} echo 'Docker image test'",
            required=False,
        ),
    ]

    return BuildTarget(
        name=name,
        build_type=BuildType.DOCKER,
        source_path=source_path,
        output_path=image_tag,
        steps=steps,
    )


def create_static_build_target(
    name: str,
    source_path: str,
    output_path: str = None,
    build_command: str = "npm run build",
) -> BuildTarget:
    """Create a static site build target."""
    if output_path is None:
        output_path = f"dist/{name}"

    steps = [
        BuildStep(name="install_dependencies", command="npm install", required=True),
        BuildStep(name="build_static_site", command=build_command, required=True),
        BuildStep(name="optimize_assets", command="npm run optimize", required=False),
    ]

    return BuildTarget(
        name=name,
        build_type=BuildType.STATIC,
        source_path=source_path,
        output_path=output_path,
        steps=steps,
    )


def get_available_build_types() -> list[BuildType]:
    """Get list of available build types."""
    return list(BuildType)


def get_available_environments() -> list[BuildEnvironment]:
    """Get list of available build environments."""
    return list(BuildEnvironment)


def trigger_build(
    target_name: str = None, environment: str = "development", config_path: str = None
) -> bool:
    """
    Trigger a build process for the specified target or all targets.

    Args:
        target_name: Name of the build target to execute (None for all targets)
        environment: Build environment (development, production, staging)
        config_path: Path to build configuration file

    Returns:
        bool: True if build succeeded, False otherwise
    """
    try:
        # Initialize build manager
        manager = BuildManager(config_path=config_path)

        # Convert environment string to enum
        try:
            build_env = BuildEnvironment[environment.upper()]
        except KeyError:
            logger.error(f"Invalid environment: {environment}")
            return False

        # Execute build
        if target_name:
            logger.info(
                f"Triggering build for target: {target_name} in {environment} environment"
            )
            result = manager.build_target(target_name, build_env)
            return result.status == BuildStatus.SUCCESS
        else:
            logger.info(
                f"Triggering build for all targets in {environment} environment"
            )
            results = manager.build_all_targets(build_env)
            return all(result.status == BuildStatus.SUCCESS for result in results)

    except Exception as e:
        logger.error(f"Build failed: {e}")
        return False
