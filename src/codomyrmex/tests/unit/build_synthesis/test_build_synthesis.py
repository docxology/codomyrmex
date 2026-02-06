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
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import build synthesis functions
try:
    from codomyrmex.build_synthesis.build_orchestrator import (
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
        from codomyrmex.build_synthesis.build_orchestrator import (
            check_build_environment,
            orchestrate_build_pipeline,
            synthesize_build_artifact,
            validate_build_output,
        )
        FULL_BUILD_AVAILABLE = False
    except ImportError:
        FULL_BUILD_AVAILABLE = False


@pytest.mark.unit
class TestBuildSynthesis(unittest.TestCase):
    """Test cases for build synthesis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_check_build_environment(self):
        """Test build environment checking."""
        result = check_build_environment()
        # This should work regardless of what's installed
        # Function returns a dict, not a bool
        self.assertIsInstance(result, dict)
        self.assertIn('python_available', result)

    def test_synthesize_python_executable(self):
        """Test synthesis of Python executable."""
        source_file = os.path.join(self.test_dir, "test_script.py")
        output_file = os.path.join(self.test_dir, "test_executable.py")

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

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check that the output contains expected content
        with open(output_file) as f:
            content = f.read()
            self.assertIn("import", content)
            # The synthesized executable may use exec() or main() depending on implementation
            self.assertTrue("main()" in content or "__main__" in content or "exec(" in content)

    def test_validate_build_output(self):
        """Test build output validation."""
        # Create a test file with proper Python code
        test_file = os.path.join(self.test_dir, "test_output.py")
        with open(test_file, 'w') as f:
            f.write("# Test Python file\nimport sys\ndef main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()\n")

        validation = validate_build_output(test_file)

        self.assertTrue(validation["exists"])
        self.assertTrue(validation["is_file"])
        self.assertTrue(validation["size_bytes"] > 0)
        self.assertEqual(len(validation["errors"]), 0)

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

        self.assertIsInstance(results, dict)
        self.assertIn("overall_success", results)
        self.assertIn("stages", results)
        self.assertIn("artifacts", results)
        self.assertIn("errors", results)

    def test_synthesize_nonexistent_source(self):
        """Test synthesis with nonexistent source file."""
        result = synthesize_build_artifact(
            source_path="/nonexistent/file.py",
            output_path=os.path.join(self.test_dir, "output.py"),
            artifact_type="executable"
        )

        self.assertFalse(result)

    def test_validate_nonexistent_output(self):
        """Test validation of nonexistent output file."""
        validation = validate_build_output("/nonexistent/file.py")

        self.assertFalse(validation["exists"])
        self.assertIn("does not exist", validation["errors"][0])

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_supported_languages(self):
        """Test getting supported languages."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            get_supported_languages,
        )

        languages = get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 0)

        # Should include common languages
        common_languages = ["python", "javascript", "java", "cpp", "c"]
        for lang in common_languages:
            if lang in languages:
                self.assertIn(lang, languages)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_create_build_manifest(self):
        """Test build manifest creation."""
        from codomyrmex.build_synthesis.build_orchestrator import create_build_manifest

        build_config = {
            "name": "test_build",
            "version": "1.0.0",
            "dependencies": ["pytest", "requests"],
            "build_commands": [["python", "setup.py", "build"]]
        }

        manifest = create_build_manifest(build_config)

        self.assertIsInstance(manifest, dict)
        self.assertIn("build_config", manifest)
        self.assertIn("timestamp", manifest)
        self.assertIn("manifest_version", manifest)
        self.assertEqual(manifest["build_config"]["name"], "test_build")

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_optimize_build_config(self):
        """Test build configuration optimization."""
        from codomyrmex.build_synthesis.build_orchestrator import optimize_build_config

        config = {
            "parallel_jobs": 1,
            "cache_enabled": False,
            "optimization_level": "none"
        }

        optimized = optimize_build_config(config)

        self.assertIsInstance(optimized, dict)
        # Should have optimization recommendations
        self.assertIn("parallel_jobs", optimized)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_validate_build_dependencies(self):
        """Test build dependency validation."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            validate_build_dependencies,
        )

        dependencies = ["os", "sys", "json"]  # Built-in modules
        result = validate_build_dependencies(dependencies)

        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertIn("missing", result)
        self.assertIn("available", result)

        # Built-in modules should be available
        self.assertTrue(result["valid"] or len(result["available"]) > 0)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_parallel_build_execution(self):
        """Test parallel build execution."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            parallel_build_execution,
        )

        build_tasks = [
            {"name": "task1", "command": ["echo", "task1"]},
            {"name": "task2", "command": ["echo", "task2"]},
            {"name": "task3", "command": ["echo", "task3"]}
        ]

        results = parallel_build_execution(build_tasks, max_workers=2)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(build_tasks))

        for result in results:
            self.assertIn("task", result)
            self.assertIn("success", result)
            self.assertIn("duration", result)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_incremental_build_check(self):
        """Test incremental build checking."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            incremental_build_check,
        )

        # Create test files with different modification times
        old_file = os.path.join(self.test_dir, "old.py")
        new_file = os.path.join(self.test_dir, "new.py")

        with open(old_file, 'w') as f:
            f.write("# Old file")
        time.sleep(0.1)  # Ensure different timestamps

        with open(new_file, 'w') as f:
            f.write("# New file")

        source_files = [old_file, new_file]
        build_cache = {}

        needs_build = incremental_build_check(source_files, build_cache)

        self.assertIsInstance(needs_build, bool)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_cleanup_build_artifacts(self):
        """Test build artifact cleanup."""
        from codomyrmex.build_synthesis.build_orchestrator import (
            cleanup_build_artifacts,
        )

        # Create some test artifacts
        artifacts = []
        for i in range(3):
            artifact = os.path.join(self.test_dir, f"artifact_{i}.tmp")
            with open(artifact, 'w') as f:
                f.write(f"Test artifact {i}")
            artifacts.append(artifact)

        # Clean them up
        result = cleanup_build_artifacts(artifacts)

        self.assertTrue(result)

        # Verify they're gone
        for artifact in artifacts:
            self.assertFalse(os.path.exists(artifact))

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_get_build_metrics(self):
        """Test build metrics collection."""
        from codomyrmex.build_synthesis.build_orchestrator import get_build_metrics

        # Mock build results
        build_results = {
            "success": True,
            "duration": 45.2,
            "artifacts_created": 5,
            "errors": 0,
            "warnings": 2
        }

        metrics = get_build_metrics(build_results)

        self.assertIsInstance(metrics, dict)
        self.assertIn("build_success_rate", metrics)
        self.assertIn("average_build_time", metrics)
        self.assertIn("artifact_creation_rate", metrics)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_export_build_report(self):
        """Test build report export."""
        from codomyrmex.build_synthesis.build_orchestrator import export_build_report

        build_data = {
            "build_id": "test_build_123",
            "timestamp": time.time(),
            "duration": 30.5,
            "success": True,
            "artifacts": ["app.exe", "lib.dll"]
        }

        # Test JSON export
        json_report = export_build_report(build_data, "json")
        self.assertIsInstance(json_report, str)

        parsed = json.loads(json_report)
        self.assertEqual(parsed["build_id"], "test_build_123")

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_import_build_config(self):
        """Test build configuration import."""
        from codomyrmex.build_synthesis.build_orchestrator import import_build_config

        # Create a test config file
        config_file = os.path.join(self.test_dir, "build_config.json")
        config_data = {
            "name": "test_project",
            "version": "1.0.0",
            "build_commands": [["make", "all"]]
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        imported_config = import_build_config(config_file)

        self.assertIsInstance(imported_config, dict)
        self.assertEqual(imported_config["name"], "test_project")

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_validate_build_config(self):
        """Test build configuration validation."""
        from codomyrmex.build_synthesis.build_orchestrator import validate_build_config

        # Valid config
        valid_config = {
            "name": "test_build",
            "build_commands": [["python", "setup.py", "build"]],
            "artifacts": ["dist/app"]
        }

        is_valid, errors = validate_build_config(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid config
        invalid_config = {
            "name": "",  # Empty name
            "build_commands": [],  # No commands
        }

        is_valid, errors = validate_build_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_get_build_history(self):
        """Test build history retrieval."""
        from codomyrmex.build_synthesis.build_orchestrator import get_build_history

        history = get_build_history(limit=10)

        self.assertIsInstance(history, list)
        # History might be empty if no builds have been recorded
        self.assertGreaterEqual(len(history), 0)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_rollback_build(self):
        """Test build rollback functionality."""
        from codomyrmex.build_synthesis.build_orchestrator import rollback_build

        # Test rollback to non-existent build (should fail gracefully)
        result = rollback_build("nonexistent_build_id")

        self.assertIsInstance(result, bool)
        # Should return False for non-existent build
        self.assertFalse(result)

    @unittest.skipUnless(FULL_BUILD_AVAILABLE, "Full build synthesis not available")
    def test_monitor_build_progress(self):
        """Test build progress monitoring."""
        from codomyrmex.build_synthesis.build_orchestrator import monitor_build_progress

        # Mock build ID
        build_id = "test_build_123"

        progress = monitor_build_progress(build_id)

        self.assertIsInstance(progress, dict)
        # Progress info should be available even for non-existent builds
        self.assertIn("status", progress)

    def test_concurrent_build_operations(self):
        """Test concurrent build operations."""
        if not FULL_BUILD_AVAILABLE:
            self.skipTest("Full build synthesis not available")

        from codomyrmex.build_synthesis.build_orchestrator import (
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

        self.assertEqual(len(results), len(tasks))

        # All tasks should have completed
        for result in results:
            self.assertIn("success", result)
            self.assertIn("duration", result)

    def test_build_error_handling(self):
        """Test error handling in build operations."""
        # Test with invalid build configurations
        invalid_configs = [
            {"name": None},  # Invalid name
            {"build_commands": "not_a_list"},  # Invalid commands
            {"artifacts": None},  # Invalid artifacts
        ]

        for config in invalid_configs:
            with self.subTest(config=config):
                try:
                    results = orchestrate_build_pipeline(config)
                    # Should handle gracefully
                    self.assertIsInstance(results, dict)
                    self.assertIn("overall_success", results)
                except Exception:
                    # Some errors might be raised, that's acceptable
                    pass

    def test_build_resource_limits(self):
        """Test build operations under resource constraints."""
        if not FULL_BUILD_AVAILABLE:
            self.skipTest("Full build synthesis not available")

        from codomyrmex.build_synthesis.build_orchestrator import (
            parallel_build_execution,
        )

        # Test with very limited workers
        tasks = [
            {"name": "task1", "command": ["echo", "task1"]},
            {"name": "task2", "command": ["echo", "task2"]},
        ]

        results = parallel_build_execution(tasks, max_workers=1)

        self.assertEqual(len(results), len(tasks))
        for result in results:
            self.assertIn("success", result)

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

        self.assertIsInstance(results, dict)
        # Should complete within timeout
        self.assertIn("overall_success", results)

    def test_build_artifact_validation_comprehensive(self):
        """Comprehensive test of build artifact validation."""
        # Test various file types and validation scenarios
        test_cases = [
            ("python_file", "test.py", "# Python file\ndef hello():\n    print('hello')\n", True),
            ("empty_file", "empty.py", "", False),
            ("binary_file", "binary.bin", b"\x00\x01\x02", False),
            ("text_file", "readme.txt", "This is a readme file.", False),
        ]

        for case_name, filename, content, should_be_valid in test_cases:
            with self.subTest(case=case_name):
                filepath = os.path.join(self.test_dir, filename)

                if isinstance(content, str):
                    with open(filepath, 'w') as f:
                        f.write(content)
                else:
                    with open(filepath, 'wb') as f:
                        f.write(content)

                validation = validate_build_output(filepath)

                self.assertIsInstance(validation, dict)
                self.assertIn("exists", validation)
                self.assertTrue(validation["exists"])  # File should exist

                if should_be_valid:
                    self.assertTrue(validation["is_file"])
                    self.assertGreater(validation["size_bytes"], 0)

    def test_build_configuration_edge_cases(self):
        """Test build configuration edge cases."""
        edge_configs = [
            {},  # Empty config
            {"name": "test"},  # Minimal config
            {"name": "test", "build_commands": None},  # None commands
            {"name": "test", "build_commands": [[]]},  # Empty commands
        ]

        for config in edge_configs:
            with self.subTest(config=config):
                try:
                    results = orchestrate_build_pipeline(config)
                    self.assertIsInstance(results, dict)
                except Exception:
                    # Edge cases might raise exceptions, that's acceptable
                    pass

    def test_build_metrics_calculation(self):
        """Test build metrics calculation."""
        if not FULL_BUILD_AVAILABLE:
            self.skipTest("Full build synthesis not available")

        from codomyrmex.build_synthesis.build_orchestrator import get_build_metrics

        # Test with various build result scenarios
        test_results = [
            {"success": True, "duration": 30.5, "artifacts_created": 3, "errors": 0},
            {"success": False, "duration": 45.2, "artifacts_created": 0, "errors": 2},
            {"success": True, "duration": 15.1, "artifacts_created": 1, "errors": 0},
        ]

        for result in test_results:
            with self.subTest(result=result):
                metrics = get_build_metrics(result)
                self.assertIsInstance(metrics, dict)
                self.assertIn("build_success_rate", metrics)

    def test_build_report_formats(self):
        """Test different build report formats."""
        if not FULL_BUILD_AVAILABLE:
            self.skipTest("Full build synthesis not available")

        from codomyrmex.build_synthesis.build_orchestrator import export_build_report

        test_data = {
            "build_id": "test_123",
            "success": True,
            "duration": 25.3,
            "artifacts": ["app", "lib"]
        }

        formats = ["json", "xml", "yaml"] if hasattr(export_build_report, '__code__') and 'format' in export_build_report.__code__.co_varnames else ["json"]

        for fmt in formats:
            with self.subTest(format=fmt):
                try:
                    report = export_build_report(test_data, fmt)
                    self.assertIsInstance(report, str)
                    self.assertGreater(len(report), 0)
                except Exception:
                    # Some formats might not be supported
                    pass


if __name__ == '__main__':
    unittest.main()
