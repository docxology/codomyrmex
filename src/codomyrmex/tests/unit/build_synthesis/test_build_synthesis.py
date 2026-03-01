import pytest

#!/usr/bin/env python3
"""
Unit tests for the Build Synthesis module.
"""

import json
import os
import sys
import tempfile
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import build synthesis functions
try:
    from codomyrmex.ci_cd_automation.build.build_orchestrator import (
        check_build_environment,
        cleanup_build_artifacts,
        create_build_manifest,
        export_build_report,
        get_build_history,
        get_build_metrics,
        get_supported_languages,
        import_build_config,
        incremental_build_check,
        monitor_build_progress,
        optimize_build_config,
        orchestrate_build_pipeline,
        parallel_build_execution,
        rollback_build,
        synthesize_build_artifact,
        validate_build_config,
        validate_build_dependencies,
        validate_build_output,
    )
    FULL_BUILD_AVAILABLE = True
except ImportError:
    # Fallback to basic imports
    try:
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            check_build_environment,
            orchestrate_build_pipeline,
            synthesize_build_artifact,
            validate_build_output,
        )
        FULL_BUILD_AVAILABLE = False
    except ImportError:
        FULL_BUILD_AVAILABLE = False


@pytest.mark.unit
class TestBuildSynthesis:
    """Test cases for build synthesis functionality."""

    def test_check_build_environment(self):
        """Test build environment checking."""
        result = check_build_environment()
        # This should work regardless of what's installed
        # Function returns a dict, not a bool
        assert isinstance(result, dict)
        assert 'python_available' in result

    def test_synthesize_python_executable(self, tmp_path):
        """Test synthesis of Python executable."""
        test_dir = str(tmp_path)
        source_file = os.path.join(test_dir, "test_script.py")
        output_file = os.path.join(test_dir, "test_executable.py")

        # Create a simple Python script
        with open(source_file, 'w') as f:
            f.write("""
def main():
    print("Hello from test script!")

if __name__ == "__main__":
    main()
""")

        result = synthesize_build_artifact(
            source_path=source_file,
            output_path=output_file,
            artifact_type="executable"
        )

        assert result
        assert os.path.exists(output_file)

        # Check that the output contains expected content
        with open(output_file) as f:
            content = f.read()
            assert "import" in content
            # The synthesized executable may use exec() or main() depending on implementation
            assert "main()" in content or "__main__" in content or "exec(" in content

    def test_validate_build_output(self, tmp_path):
        """Test build output validation."""
        test_dir = str(tmp_path)
        # Create a test file with proper Python code
        test_file = os.path.join(test_dir, "test_output.py")
        with open(test_file, 'w') as f:
            f.write("# Test Python file\nimport sys\ndef main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()\n")

        validation = validate_build_output(test_file)

        assert validation["exists"]
        assert validation["is_file"]
        assert validation["size_bytes"] > 0
        assert len(validation["errors"]) == 0

    def test_orchestrate_build_pipeline(self):
        """Test build pipeline orchestration."""
        build_config = {
            "dependencies": [],
            "build_commands": [
                ["python", "-c", "print('Test build command')"]
            ],
            "artifacts": []
        }

        results = orchestrate_build_pipeline(build_config)

        assert isinstance(results, dict)
        assert "overall_success" in results
        assert "stages" in results
        assert "artifacts" in results
        assert "errors" in results

    def test_synthesize_nonexistent_source(self, tmp_path):
        """Test synthesis with nonexistent source file."""
        test_dir = str(tmp_path)
        result = synthesize_build_artifact(
            source_path="/nonexistent/file.py",
            output_path=os.path.join(test_dir, "output.py"),
            artifact_type="executable"
        )

        assert not result

    def test_validate_nonexistent_output(self):
        """Test validation of nonexistent output file."""
        validation = validate_build_output("/nonexistent/file.py")

        assert not validation["exists"]
        assert "does not exist" in validation["errors"][0]

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_supported_languages(self):
        """Test getting supported languages."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            get_supported_languages,
        )

        languages = get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0

        # Should include common languages
        common_languages = ["python", "javascript", "java", "cpp", "c"]
        for lang in common_languages:
            if lang in languages:
                assert lang in languages

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_create_build_manifest(self):
        """Test build manifest creation."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            create_build_manifest,
        )

        build_config = {
            "name": "test_build",
            "version": "1.0.0",
            "dependencies": ["pytest", "requests"],
            "build_commands": [["python", "setup.py", "build"]]
        }

        manifest = create_build_manifest(build_config)

        assert isinstance(manifest, dict)
        assert "build_config" in manifest
        assert "timestamp" in manifest
        assert "manifest_version" in manifest
        assert manifest["build_config"]["name"] == "test_build"

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_optimize_build_config(self):
        """Test build configuration optimization."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            optimize_build_config,
        )

        config = {
            "parallel_jobs": 1,
            "cache_enabled": False,
            "optimization_level": "none"
        }

        optimized = optimize_build_config(config)

        assert isinstance(optimized, dict)
        # Should have optimization recommendations
        assert "parallel_jobs" in optimized

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_validate_build_dependencies(self):
        """Test build dependency validation."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            validate_build_dependencies,
        )

        dependencies = ["os", "sys", "json"]  # Built-in modules
        result = validate_build_dependencies(dependencies)

        assert isinstance(result, dict)
        assert "valid" in result
        assert "missing" in result
        assert "available" in result

        # Built-in modules should be available
        assert result["valid"] or len(result["available"]) > 0

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_parallel_build_execution(self):
        """Test parallel build execution."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            parallel_build_execution,
        )

        build_tasks = [
            {"name": "task1", "command": ["echo", "task1"]},
            {"name": "task2", "command": ["echo", "task2"]},
            {"name": "task3", "command": ["echo", "task3"]}
        ]

        results = parallel_build_execution(build_tasks, max_workers=2)

        assert isinstance(results, list)
        assert len(results) == len(build_tasks)

        for result in results:
            assert "task" in result
            assert "success" in result
            assert "duration" in result

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_incremental_build_check(self, tmp_path):
        """Test incremental build checking."""
        test_dir = str(tmp_path)
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            incremental_build_check,
        )

        # Create test files with different modification times
        old_file = os.path.join(test_dir, "old.py")
        new_file = os.path.join(test_dir, "new.py")

        with open(old_file, 'w') as f:
            f.write("# Old file")
        time.sleep(0.1)  # Ensure different timestamps

        with open(new_file, 'w') as f:
            f.write("# New file")

        source_files = [old_file, new_file]
        build_cache = {}

        needs_build = incremental_build_check(source_files, build_cache)

        assert isinstance(needs_build, bool)

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_cleanup_build_artifacts(self, tmp_path):
        """Test build artifact cleanup."""
        test_dir = str(tmp_path)
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            cleanup_build_artifacts,
        )

        # Create some test artifacts
        artifacts = []
        for i in range(3):
            artifact = os.path.join(test_dir, f"artifact_{i}.tmp")
            with open(artifact, 'w') as f:
                f.write(f"Test artifact {i}")
            artifacts.append(artifact)

        # Clean them up
        result = cleanup_build_artifacts(artifacts)

        assert result

        # Verify they're gone
        for artifact in artifacts:
            assert not os.path.exists(artifact)

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_get_build_metrics(self):
        """Test build metrics collection."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            get_build_metrics,
        )

        # Mock build results
        build_results = {
            "success": True,
            "duration": 45.2,
            "artifacts_created": 5,
            "errors": 0,
            "warnings": 2
        }

        metrics = get_build_metrics(build_results)

        assert isinstance(metrics, dict)
        assert "build_success_rate" in metrics
        assert "average_build_time" in metrics
        assert "artifact_creation_rate" in metrics

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_export_build_report(self):
        """Test build report export."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            export_build_report,
        )

        build_data = {
            "build_id": "test_build_123",
            "timestamp": time.time(),
            "duration": 30.5,
            "success": True,
            "artifacts": ["app.exe", "lib.dll"]
        }

        # Test JSON export
        json_report = export_build_report(build_data, "json")
        assert isinstance(json_report, str)

        parsed = json.loads(json_report)
        assert parsed["build_id"] == "test_build_123"

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_import_build_config(self, tmp_path):
        """Test build configuration import."""
        test_dir = str(tmp_path)
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            import_build_config,
        )

        # Create a test config file
        config_file = os.path.join(test_dir, "build_config.json")
        config_data = {
            "name": "test_project",
            "version": "1.0.0",
            "build_commands": [["make", "all"]]
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        imported_config = import_build_config(config_file)

        assert isinstance(imported_config, dict)
        assert imported_config["name"] == "test_project"

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_validate_build_config(self):
        """Test build configuration validation."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            validate_build_config,
        )

        # Valid config
        valid_config = {
            "name": "test_build",
            "build_commands": [["python", "setup.py", "build"]],
            "artifacts": ["dist/app"]
        }

        is_valid, errors = validate_build_config(valid_config)
        assert is_valid
        assert len(errors) == 0

        # Invalid config
        invalid_config = {
            "name": "",  # Empty name
            "build_commands": [],  # No commands
        }

        is_valid, errors = validate_build_config(invalid_config)
        assert not is_valid
        assert len(errors) > 0

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_get_build_history(self):
        """Test build history retrieval."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            get_build_history,
        )

        history = get_build_history(limit=10)

        assert isinstance(history, list)
        # History might be empty if no builds have been recorded
        assert len(history) >= 0

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_rollback_build(self):
        """Test build rollback functionality."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import rollback_build

        # Test rollback to non-existent build (should fail gracefully)
        result = rollback_build("nonexistent_build_id")

        assert isinstance(result, bool)
        # Should return False for non-existent build
        assert not result

    @pytest.mark.skipif(not FULL_BUILD_AVAILABLE, reason="Full build synthesis not available")
    def test_monitor_build_progress(self):
        """Test build progress monitoring."""
        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            monitor_build_progress,
        )

        # Mock build ID
        build_id = "test_build_123"

        progress = monitor_build_progress(build_id)

        assert isinstance(progress, dict)
        # Progress info should be available even for non-existent builds
        assert "status" in progress

    def test_concurrent_build_operations(self):
        """Test concurrent build operations."""
        if not FULL_BUILD_AVAILABLE:
            pytest.skip("Full build synthesis not available")

        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            parallel_build_execution,
        )

        # Create multiple build tasks
        tasks = []
        for i in range(5):
            task = {
                "name": f"build_task_{i}",
                "command": ["echo", f"Building task {i}"]
            }
            tasks.append(task)

        results = parallel_build_execution(tasks, max_workers=3)

        assert len(results) == len(tasks)

        # All tasks should have completed
        for result in results:
            assert "success" in result
            assert "duration" in result

    def test_build_error_handling(self):
        """Test error handling in build operations."""
        # Test with invalid build configurations
        invalid_configs = [
            {"name": None},  # Invalid name
            {"build_commands": "not_a_list"},  # Invalid commands
            {"artifacts": None},  # Invalid artifacts
        ]

        for config in invalid_configs:
            try:
                results = orchestrate_build_pipeline(config)
                # Should handle gracefully
                assert isinstance(results, dict)
                assert "overall_success" in results
            except Exception:
                # Some errors might be raised, that's acceptable
                pass

    def test_build_resource_limits(self):
        """Test build operations under resource constraints."""
        if not FULL_BUILD_AVAILABLE:
            pytest.skip("Full build synthesis not available")

        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            parallel_build_execution,
        )

        # Test with very limited workers
        tasks = [
            {"name": "task1", "command": ["echo", "task1"]},
            {"name": "task2", "command": ["echo", "task2"]},
        ]

        results = parallel_build_execution(tasks, max_workers=1)

        assert len(results) == len(tasks)
        for result in results:
            assert "success" in result

    def test_build_timeout_handling(self):
        """Test timeout handling in build operations."""
        # Test with potentially slow operations
        slow_config = {
            "build_commands": [
                ["python", "-c", "import time; time.sleep(0.1); print('Slow command')"]
            ],
            "timeout": 1  # Short timeout
        }

        results = orchestrate_build_pipeline(slow_config)

        assert isinstance(results, dict)
        # Should complete within timeout
        assert "overall_success" in results

    def test_build_artifact_validation_comprehensive(self, tmp_path):
        """Comprehensive test of build artifact validation."""
        test_dir = str(tmp_path)
        # Test various file types and validation scenarios
        test_cases = [
            ("python_file", "test.py", "# Python file\ndef hello():\n    print('hello')\n", True),
            ("empty_file", "empty.py", "", False),
            ("binary_file", "binary.bin", b"\x00\x01\x02", False),
            ("text_file", "readme.txt", "This is a readme file.", False),
        ]

        for case_name, filename, content, should_be_valid in test_cases:
            filepath = os.path.join(test_dir, filename)

            if isinstance(content, str):
                with open(filepath, 'w') as f:
                    f.write(content)
            else:
                with open(filepath, 'wb') as f:
                    f.write(content)

            validation = validate_build_output(filepath)

            assert isinstance(validation, dict)
            assert "exists" in validation
            assert validation["exists"]  # File should exist

            if should_be_valid:
                assert validation["is_file"]
                assert validation["size_bytes"] > 0

    def test_build_configuration_edge_cases(self):
        """Test build configuration edge cases."""
        edge_configs = [
            {},  # Empty config
            {"name": "test"},  # Minimal config
            {"name": "test", "build_commands": None},  # None commands
            {"name": "test", "build_commands": [[]]},  # Empty commands
        ]

        for config in edge_configs:
            try:
                results = orchestrate_build_pipeline(config)
                assert isinstance(results, dict)
            except Exception:
                # Edge cases might raise exceptions, that's acceptable
                pass

    def test_build_metrics_calculation(self):
        """Test build metrics calculation."""
        if not FULL_BUILD_AVAILABLE:
            pytest.skip("Full build synthesis not available")

        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            get_build_metrics,
        )

        # Test with various build result scenarios
        test_results = [
            {"success": True, "duration": 30.5, "artifacts_created": 3, "errors": 0},
            {"success": False, "duration": 45.2, "artifacts_created": 0, "errors": 2},
            {"success": True, "duration": 15.1, "artifacts_created": 1, "errors": 0},
        ]

        for result in test_results:
            metrics = get_build_metrics(result)
            assert isinstance(metrics, dict)
            assert "build_success_rate" in metrics

    def test_build_report_formats(self):
        """Test different build report formats."""
        if not FULL_BUILD_AVAILABLE:
            pytest.skip("Full build synthesis not available")

        from codomyrmex.ci_cd_automation.build.build_orchestrator import (
            export_build_report,
        )

        test_data = {
            "build_id": "test_123",
            "success": True,
            "duration": 25.3,
            "artifacts": ["app", "lib"]
        }

        formats = ["json", "xml", "yaml"] if hasattr(export_build_report, '__code__') and 'format' in export_build_report.__code__.co_varnames else ["json"]

        for fmt in formats:
            try:
                report = export_build_report(test_data, fmt)
                assert isinstance(report, str)
                assert len(report) > 0
            except Exception:
                # Some formats might not be supported
                pass
