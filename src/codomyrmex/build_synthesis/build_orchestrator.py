from pathlib import Path
import os
import shutil
import subprocess
import sys


from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging



#!/usr/bin/env python3
"""
"""Core functionality module

This module provides build_orchestrator functionality including:
- 8 functions: check_build_environment, run_build_command, synthesize_build_artifact...
- 0 classes: 

Usage:
    # Example usage here
"""
Build Orchestrator for Codomyrmex Build Synthesis.

This module provides build orchestration and synthesis capabilities for
automating build processes and artifact generation.
"""



# Add project root for sibling module imports if run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation


logger = get_logger(__name__)


def check_build_environment():
    """Check if the build environment is properly configured."""
    logger.info("Checking build environment...")

    # Check for common build tools
    tools = ["make", "cmake", "ninja", "gcc", "python3"]
    available_tools = []

    for tool in tools:
        try:
            result = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                available_tools.append(tool)
                logger.info(f"  ✅ {tool} is available")
            else:
                logger.warning(f"  ⚠️  {tool} returned non-zero exit code")
        except FileNotFoundError:
            logger.warning(f"  ❌ {tool} not found")

    # Build result dictionary
    result = {
        "python_available": "python3" in available_tools,
        "make_available": "make" in available_tools,
        "cmake_available": "cmake" in available_tools,
        "ninja_available": "ninja" in available_tools,
        "gcc_available": "gcc" in available_tools,
        "available_tools": available_tools,
        "all_required_available": len(available_tools) >= 1,  # At least Python should be available
    }

    if available_tools:
        logger.info(
            f"Build environment check passed. Available tools: {', '.join(available_tools)}"
        )
        return result
    else:
        logger.error(
            "No build tools found. Please install build tools for your platform."
        )
        return result


def run_build_command(command: list[str], cwd: str = None) -> tuple[bool, str, str]:
    """
    Run a build command and return the result.

    Args:
        command: List of command arguments
        cwd: Working directory for the command

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        logger.info(f"Running build command: {' '.join(command)}")
        if cwd:
            logger.info(f"Working directory: {cwd}")

        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        success = result.returncode == 0
        if success:
            logger.info("Build command completed successfully")
        else:
            logger.error(f"Build command failed with exit code {result.returncode}")

        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        error_msg = "Build command timed out after 5 minutes"
        logger.error(error_msg)
        return False, "", error_msg
    except Exception as e:
        error_msg = f"Build command failed: {e}"
        logger.error(error_msg)
        return False, "", error_msg


def synthesize_build_artifact(
    source_path: str, output_path: str, artifact_type: str = "executable"
) -> bool:
    """
    Synthesize a build artifact from source code.

    Args:
        source_path: Path to source file or directory
        output_path: Path where artifact should be created
        artifact_type: Type of artifact to create ('executable', 'library', 'package')

    Returns:
        True if synthesis was successful, False otherwise
    """
    logger.info(f"Synthesizing {artifact_type} from {source_path} to {output_path}")

    source_path = Path(source_path)
    output_path = Path(output_path)

    if not source_path.exists():
        logger.error(f"Source path does not exist: {source_path}")
        return False

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if artifact_type == "executable" and source_path.suffix == ".py":
        # For Python scripts, create executable wrapper
        success = _create_python_executable(source_path, output_path)
    elif artifact_type == "package":
        # For Python packages, create distributable package
        success = _create_python_package(source_path, output_path)
    else:
        logger.warning(f"Unsupported artifact type: {artifact_type}")
        success = False

    if success:
        logger.info(f"Successfully synthesized {artifact_type}: {output_path}")
    else:
        logger.error(f"Failed to synthesize {artifact_type}")

    return success


def _create_python_executable(source_path: Path, output_path: Path) -> bool:
    """Create a Python executable wrapper."""
    try:
        # Create a simple wrapper script
        wrapper_content = f"""#!/usr/bin/env python3
# sys.path.insert(0, os.path.dirname(__file__))  # Removed sys.path manipulation
if __name__ == "__main__":
    main()
"""
        with open(output_path, "w") as f:
            f.write(wrapper_content)

        # Make executable on Unix-like systems
        if os.name != "nt":
            os.chmod(output_path, 0o755)

        return True
    except Exception as e:
        logger.error(f"Failed to create Python executable: {e}")
        return False


def _create_python_package(source_path: Path, output_path: Path) -> bool:
    """Create a Python package distributable."""
    try:
        # This would typically use setuptools or similar
        # For now, just copy the source
        if source_path.is_dir():

            if output_path.exists():
                shutil.rmtree(output_path)
            shutil.copytree(source_path, output_path)
        else:

            shutil.copy2(source_path, output_path)

        return True
    except Exception as e:
        logger.error(f"Failed to create Python package: {e}")
        return False


def validate_build_output(output_path: str) -> dict[str, any]:
    """
    Validate that build output meets expectations.

    Args:
        output_path: Path to the build output

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Validating build output: {output_path}")

    output_path = Path(output_path)
    validation_results = {
        "exists": output_path.exists(),
        "is_file": output_path.is_file(),
        "is_executable": False,
        "size_bytes": 0,
        "errors": [],
    }

    if not output_path.exists():
        validation_results["errors"].append("Output file does not exist")
        return validation_results

    validation_results["size_bytes"] = output_path.stat().st_size

    if output_path.is_file():
        # Check if executable
        if os.name != "nt":  # Unix-like systems
            validation_results["is_executable"] = os.access(output_path, os.X_OK)
        else:  # Windows
            validation_results["is_executable"] = output_path.suffix in [
                ".exe",
                ".bat",
                ".cmd",
            ]

        # Basic validation for Python files
        if output_path.suffix == ".py":
            try:
                with open(output_path) as f:
                    content = f.read()
                    if "import" not in content and "def " not in content:
                        validation_results["errors"].append(
                            "File appears to be empty or malformed"
                        )
            except Exception as e:
                validation_results["errors"].append(f"Cannot read file: {e}")

    logger.info(f"Validation completed. Errors: {len(validation_results['errors'])}")
    return validation_results


def orchestrate_build_pipeline(build_config: dict[str, any]) -> dict[str, any]:
    """
    Orchestrate a complete build pipeline.

    Args:
        build_config: Dictionary containing build configuration

    Returns:
        Dictionary with build results
    """
    logger.info("Starting build pipeline orchestration")

    results = {"stages": [], "overall_success": False, "artifacts": [], "errors": []}

    try:
        # Stage 1: Environment check
        logger.info("Stage 1: Environment validation")
        env_ok = check_build_environment()
        results["stages"].append({"name": "environment_check", "success": env_ok})

        if not env_ok:
            results["errors"].append("Build environment validation failed")
            return results

        # Stage 2: Dependency installation
        if "dependencies" in build_config:
            logger.info("Stage 2: Dependency installation")
            dep_success = _install_build_dependencies(build_config["dependencies"])
            results["stages"].append(
                {"name": "dependency_installation", "success": dep_success}
            )
        else:
            results["stages"].append(
                {"name": "dependency_installation", "success": True, "skipped": True}
            )

        # Stage 3: Build execution
        if "build_commands" in build_config:
            logger.info("Stage 3: Build execution")
            build_success = True
            for i, cmd in enumerate(build_config["build_commands"]):
                cmd_success, stdout, stderr = run_build_command(
                    cmd, build_config.get("working_directory")
                )
                results["stages"].append(
                    {
                        "name": f"build_command_{i}",
                        "success": cmd_success,
                        "command": cmd,
                        "stdout": stdout,
                        "stderr": stderr,
                    }
                )
                if not cmd_success:
                    build_success = False
                    results["errors"].append(f"Build command {i} failed: {stderr}")
            results["stages"].append(
                {"name": "build_execution", "success": build_success}
            )
        else:
            results["stages"].append(
                {"name": "build_execution", "success": True, "skipped": True}
            )

        # Stage 4: Artifact synthesis
        if "artifacts" in build_config:
            logger.info("Stage 4: Artifact synthesis")
            artifact_success = True
            for artifact in build_config["artifacts"]:
                art_success = synthesize_build_artifact(
                    artifact["source"],
                    artifact["output"],
                    artifact.get("type", "executable"),
                )
                results["artifacts"].append(
                    {
                        "source": artifact["source"],
                        "output": artifact["output"],
                        "success": art_success,
                    }
                )
                if not art_success:
                    artifact_success = False
            results["stages"].append(
                {"name": "artifact_synthesis", "success": artifact_success}
            )

        # Stage 5: Validation
        if results["artifacts"]:
            logger.info("Stage 5: Output validation")
            validation_success = True
            for artifact in results["artifacts"]:
                if artifact["success"]:
                    validation = validate_build_output(artifact["output"])
                    artifact["validation"] = validation
                    if validation["errors"]:
                        validation_success = False
                        results["errors"].extend(validation["errors"])
            results["stages"].append(
                {"name": "validation", "success": validation_success}
            )

        # Determine overall success
        results["overall_success"] = all(
            stage["success"]
            for stage in results["stages"]
            if not stage.get("skipped", False)
        )

        if results["overall_success"]:
            logger.info("Build pipeline completed successfully")
        else:
            logger.error("Build pipeline failed")

    except Exception as e:
        results["errors"].append(f"Build pipeline orchestration failed: {e}")
        logger.error(f"Build pipeline orchestration error: {e}")

    return results


def _install_build_dependencies(dependencies: list[str]) -> bool:
    """Install build dependencies."""
    logger.info(f"Installing {len(dependencies)} build dependencies")

    # This is a simplified implementation
    # In a real scenario, you might use pip, npm, or other package managers
    try:
        for dep in dependencies:
            logger.info(f"Installing dependency: {dep}")
            # Simulate installation
            success, stdout, stderr = run_build_command(["pip", "install", dep])
            if not success:
                logger.error(f"Failed to install {dep}: {stderr}")
                return False
        return True
    except Exception as e:
        logger.error(f"Dependency installation failed: {e}")
        return False


if __name__ == "__main__":
    # Ensure logging is set up when script is run directly
    setup_logging()
    logger.info("Executing build_orchestrator.py directly for testing example.")

    # Example usage
    example_config = {
        "dependencies": ["setuptools"],
        "build_commands": [["python", "-c", "print('Building...')"]],
        "artifacts": [
            {
                "source": "example.py",
                "output": "example_executable.py",
                "type": "executable",
            }
        ],
    }

    results = orchestrate_build_pipeline(example_config)
    print(f"Build pipeline results: {results['overall_success']}")
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f"  - {error}")
