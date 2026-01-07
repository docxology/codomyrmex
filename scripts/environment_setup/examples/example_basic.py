#!/usr/bin/env python3
"""
Example: Environment Setup - Comprehensive Environment Validation

This example demonstrates comprehensive environment setup and validation for Codomyrmex,
including dependency checking, environment validation, package manager integration, and
error handling for various edge cases. It shows how to ensure a complete development
environment for new developers and handle common setup issues.

Key Features Demonstrated:
- UV package manager detection and validation
- Python version compatibility checking
- Core dependency validation (kit, python-dotenv)
- Environment variable setup and .env file management
- Comprehensive environment completeness validation
- Package version checking and reporting
- Error handling for missing dependencies, invalid environments
- Edge cases: empty requirements, version conflicts, missing config files
- Realistic scenario: complete new developer onboarding workflow

Tested Methods:
- is_uv_available() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_is_uv_available
- is_uv_environment() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_is_uv_environment
- check_and_setup_env_vars() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_check_and_setup_env_vars
- validate_python_version() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_validate_python_version
- check_package_versions() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_check_package_versions
- validate_environment_completeness() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_validate_environment_completeness
- generate_environment_report() - Verified in test_environment_setup.py::TestEnvironmentSetup::test_generate_environment_report
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.environment_setup.env_checker import (
    is_uv_available,
    is_uv_environment,
    check_and_setup_env_vars,
    validate_python_version,
    check_package_versions,
    validate_environment_completeness,
    generate_environment_report,
    ensure_dependencies_installed
)
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, print_error, print_success


def demonstrate_basic_environment_checks():
    """
    Demonstrate basic environment checks including UV availability and environment type.

    This section shows the fundamental environment validation that should be performed
    at the start of any Codomyrmex workflow.
    """
    print_section("Basic Environment Checks")

    # Check UV package manager availability
    print("🔍 Checking UV package manager availability...")
    uv_available = is_uv_available()
    if uv_available:
        print_success("✓ UV package manager is available")
    else:
        print_error("✗ UV package manager not found - consider installing for faster dependency management")
        print("   Visit: https://github.com/astral-sh/uv")

    # Check environment type
    print("\n🏠 Checking environment type...")
    in_uv_env = is_uv_environment()
    if in_uv_env:
        print_success("✓ Running in UV-managed environment")
    elif "VIRTUAL_ENV" in sys.environ:
        print("⚠️  Running in virtual environment (not UV-managed)")
    else:
        print_error("✗ Running in system Python environment - consider using a virtual environment")

    return uv_available, in_uv_env


def demonstrate_python_version_validation():
    """
    Demonstrate Python version validation with different requirement scenarios.

    Shows how to validate Python version compatibility for different use cases.
    """
    print_section("Python Version Validation")

    # Test different version requirements
    test_cases = [
        (">=3.8", "Minimum Codomyrmex requirement"),
        (">=3.10", "Recommended for full feature support"),
        ("==3.11.0", "Specific version requirement"),
        (">=3.12", "Future compatibility check")
    ]

    results = {}
    for requirement, description in test_cases:
        print(f"🔍 Testing {description}: {requirement}")
        try:
            is_valid = validate_python_version(requirement)
            if is_valid:
                print_success(f"✓ Python {sys.version.split()[0]} meets requirement {requirement}")
            else:
                print_error(f"✗ Python {sys.version.split()[0]} does not meet requirement {requirement}")
            results[requirement] = is_valid
        except Exception as e:
            print_error(f"✗ Error validating version requirement {requirement}: {e}")
            results[requirement] = False

    return results


def demonstrate_dependency_validation():
    """
    Demonstrate comprehensive dependency validation with error handling.

    Shows how to check for core dependencies and handle various failure scenarios.
    """
    print_section("Dependency Validation")

    # Test core dependency imports with detailed error handling
    dependencies = [
        ("kit", "cased/kit", "Core utility library"),
        ("dotenv", "python-dotenv", "Environment variable management"),
        ("packaging", "packaging", "Version parsing and comparison")
    ]

    dependency_status = {}

    for module_name, package_name, description in dependencies:
        print(f"🔍 Checking {description} ({package_name})...")
        try:
            __import__(module_name)
            print_success(f"✓ {package_name} is available")
            dependency_status[module_name] = True
        except ImportError:
            print_error(f"✗ {package_name} is not installed")
            print(f"   Install with: uv pip install {package_name}")
            dependency_status[module_name] = False
        except Exception as e:
            print_error(f"✗ Unexpected error checking {package_name}: {e}")
            dependency_status[module_name] = False

    # Run the comprehensive dependency check
    print("\n🔍 Running comprehensive dependency validation...")
    try:
        # This will print detailed status and guidance
        ensure_dependencies_installed()
        print_success("✓ Comprehensive dependency check completed")
    except SystemExit:
        print_error("✗ Dependency validation failed - see guidance above")
    except Exception as e:
        print_error(f"✗ Unexpected error in dependency validation: {e}")

    return dependency_status


def demonstrate_environment_variable_setup():
    """
    Demonstrate environment variable setup and .env file management.

    Shows how to check for and set up environment variables, including API keys.
    """
    print_section("Environment Variable Setup")

    # Get repository root
    repo_root = str(Path(__file__).parent.parent.parent)
    print(f"📁 Repository root: {repo_root}")

    # Check and setup environment variables
    print("\n🔍 Checking environment variable configuration...")
    try:
        check_and_setup_env_vars(repo_root)
        print_success("✓ Environment variable check completed")
    except Exception as e:
        print_error(f"✗ Error checking environment variables: {e}")
        print("   This may indicate issues with .env file or environment setup")


def demonstrate_package_version_checking():
    """
    Demonstrate package version checking and analysis.

    Shows how to get information about installed packages and their versions.
    """
    print_section("Package Version Analysis")

    print("🔍 Analyzing installed package versions...")
    try:
        package_versions = check_package_versions()

        if package_versions:
            print_success(f"✓ Found {len(package_versions)} installed packages")

            # Show some key packages
            key_packages = ["pip", "setuptools", "wheel", "requests", "click"]
            found_key_packages = {k: v for k, v in package_versions.items()
                                if k.lower() in key_packages}

            if found_key_packages:
                print("\n📦 Key package versions:")
                for package, version in sorted(found_key_packages.items()):
                    print(f"   {package}: {version}")

            # Show total count
            print(f"\n📊 Total installed packages: {len(package_versions)}")
        else:
            print_error("✗ No package version information available")
            print("   This may indicate issues with package introspection")

        return package_versions

    except Exception as e:
        print_error(f"✗ Error analyzing package versions: {e}")
        return {}


def demonstrate_environment_completeness_validation():
    """
    Demonstrate comprehensive environment completeness validation.

    Shows how to perform a complete environment health check.
    """
    print_section("Environment Completeness Validation")

    print("🔍 Performing comprehensive environment validation...")
    try:
        validation_results = validate_environment_completeness()

        print("\n📋 Validation Results:")
        checks_passed = 0
        total_checks = len(validation_results)

        for check_name, passed in validation_results.items():
            status_icon = "✓" if passed else "✗"
            status_color = print_success if passed else print_error
            status_color(f"{status_icon} {check_name.replace('_', ' ').title()}")
            if passed:
                checks_passed += 1

        print(f"\n📊 Summary: {checks_passed}/{total_checks} checks passed")

        if checks_passed == total_checks:
            print_success("🎉 Environment is fully configured and ready!")
        elif checks_passed >= total_checks * 0.8:
            print("⚠️  Environment is mostly configured but has minor issues")
        else:
            print_error("❌ Environment requires attention - several issues detected")

        return validation_results

    except Exception as e:
        print_error(f"✗ Error during environment validation: {e}")
        return {}


def demonstrate_environment_report_generation():
    """
    Demonstrate environment report generation for documentation and debugging.

    Shows how to generate comprehensive environment status reports.
    """
    print_section("Environment Report Generation")

    print("📄 Generating comprehensive environment report...")
    try:
        report = generate_environment_report()
        print("\n" + "="*80)
        print(report)
        print("="*80)

        print_success("✓ Environment report generated successfully")
        return report

    except Exception as e:
        print_error(f"✗ Error generating environment report: {e}")
        return ""


def demonstrate_error_handling_scenarios():
    """
    Demonstrate error handling for various edge cases and failure scenarios.

    Shows how the environment setup handles different types of errors gracefully.
    """
    print_section("Error Handling Scenarios")

    # Test invalid version requirements
    print("🔍 Testing invalid version requirement handling...")
    try:
        result = validate_python_version("invalid-specifier")
        print_error(f"✗ Should have failed with invalid specifier, got: {result}")
    except Exception as e:
        print_success(f"✓ Correctly handled invalid version specifier: {e}")

    # Test missing repository root
    print("\n🔍 Testing missing repository root handling...")
    try:
        check_and_setup_env_vars("/nonexistent/path")
        print_error("✗ Should have handled missing repository gracefully")
    except Exception as e:
        print_success(f"✓ Correctly handled missing repository: {e}")


def demonstrate_new_developer_onboarding():
    """
    Demonstrate a realistic scenario: complete new developer onboarding workflow.

    This shows how a new developer would set up their environment from scratch.
    """
    print_section("New Developer Onboarding Scenario")

    print("👋 Welcome to Codomyrmex! Let's set up your development environment...")
    print("This simulates the complete onboarding process for a new developer.\n")

    onboarding_steps = [
        ("Environment Check", "Checking your development environment..."),
        ("Dependencies", "Ensuring all required dependencies are installed..."),
        ("Configuration", "Setting up environment variables and configuration..."),
        ("Validation", "Running final validation checks..."),
        ("Ready", "Your environment is ready for development!")
    ]

    for step_name, description in onboarding_steps:
        print(f"📋 Step: {step_name}")
        print(f"   {description}")

        # Simulate some processing time
        time.sleep(0.5)

        if step_name == "Environment Check":
            uv_available, in_uv_env = demonstrate_basic_environment_checks()
            print(f"   UV Available: {uv_available}, In UV Env: {in_uv_env}")

        elif step_name == "Dependencies":
            dependency_status = demonstrate_dependency_validation()
            installed_deps = sum(dependency_status.values())
            total_deps = len(dependency_status)
            print(f"   Dependencies: {installed_deps}/{total_deps} installed")

        elif step_name == "Configuration":
            demonstrate_environment_variable_setup()
            print("   Configuration files checked and guidance provided")

        elif step_name == "Validation":
            validation_results = demonstrate_environment_completeness_validation()
            passed_checks = sum(validation_results.values())
            total_checks = len(validation_results)
            print(f"   Validation: {passed_checks}/{total_checks} checks passed")

        elif step_name == "Ready":
            if sum(demonstrate_environment_completeness_validation().values()) >= 4:
                print_success("🎉 Welcome aboard! Your Codomyrmex environment is ready!")
            else:
                print_error("⚠️  Environment setup incomplete - please review the guidance above")

        print()  # Empty line between steps


def main():
    """
    Run the comprehensive environment setup example.

    This example demonstrates all aspects of environment validation and setup,
    including error handling, edge cases, and realistic onboarding scenarios.
    """
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Codomyrmex Environment Setup - Comprehensive Example")
        print("This example demonstrates complete environment validation and setup")
        print("including error handling, edge cases, and new developer onboarding.\n")

        # Execute all demonstration sections
        basic_results = demonstrate_basic_environment_checks()
        version_results = demonstrate_python_version_validation()
        dependency_results = demonstrate_dependency_validation()
        demonstrate_environment_variable_setup()
        package_results = demonstrate_package_version_checking()
        validation_results = demonstrate_environment_completeness_validation()
        report = demonstrate_environment_report_generation()
        demonstrate_error_handling_scenarios()
        demonstrate_new_developer_onboarding()

        # Collect comprehensive results
        results = {
            'status': 'success',
            'uv_available': basic_results[0],
            'in_uv_environment': basic_results[1],
            'python_version': sys.version,
            'python_version_validations': version_results,
            'dependency_status': dependency_results,
            'package_count': len(package_results),
            'validation_results': validation_results,
            'validation_score': f"{sum(validation_results.values())}/{len(validation_results)}",
            'report_length': len(report),
            'timestamp': time.time()
        }

        print_results(results, "Comprehensive Environment Setup Results")

        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

    except Exception as e:
        runner.error("Comprehensive environment setup example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

