"""
Test Inter-Module Workflows for Codomyrmex Project Orchestration

This module demonstrates and tests workflows that integrate multiple
Codomyrmex modules together to create comprehensive analysis pipelines.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# Add src to path for testing
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))  # Removed sys.path manipulation

# Import Codomyrmex modules (with graceful fallback for testing)
try:
    from codomyrmex.ai_code_editing import AICodeHelper
    from codomyrmex.build_synthesis import BuildManager
    from codomyrmex.data_visualization import DataVisualizer
    from codomyrmex.documentation import DocumentationGenerator
    from codomyrmex.git_operations import GitOperationsManager
    from codomyrmex.logging_monitoring import LoggingManager
    from codomyrmex.static_analysis import StaticAnalyzer

    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available for testing: {e}")
    MODULES_AVAILABLE = False


class InterModuleWorkflowsTest(unittest.TestCase):
    """Test comprehensive inter-module workflows."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.test_project_dir = os.path.join(self.test_dir, "test_project")
        os.makedirs(self.test_project_dir, exist_ok=True)

        # Create sample Python files for testing
        self.create_sample_python_project()

        # Initialize mock modules
        self.setup_mock_modules()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_sample_python_project(self):
        """Create a sample Python project structure for testing."""
        # Create main module
        main_content = '''"""
Sample Python project for testing Codomyrmex workflows.
"""
import os
import sys
from typing import List, Dict


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()


def process_data(data: Dict) -> Dict:
    """Process input data."""
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    result = {}
    for key, value in data.items():
        if isinstance(value, (int, float)):
            result[key] = value * 2
        else:
            result[key] = str(value).upper()

    return result


if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.divide(10, 2))
'''

        with open(os.path.join(self.test_project_dir, "main.py"), "w") as f:
            f.write(main_content)

        # Create utils module
        utils_content = '''"""
Utility functions for the test project.
"""
import json
from pathlib import Path


def read_config(config_path: str) -> dict:
    """Read configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_results(results: dict, output_path: str) -> None:
    """Save results to JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)


# Security issue: Using eval (should be detected by static analysis)
def unsafe_eval(expression: str):
    """Unsafe function using eval - should trigger security warnings."""
    return eval(expression)  # nosec - intentional for testing
'''

        with open(os.path.join(self.test_project_dir, "utils.py"), "w") as f:
            f.write(utils_content)

        # Create test file
        test_content = '''"""
Tests for the sample project.
"""
import unittest
from main import Calculator, process_data


class TestCalculator(unittest.TestCase):
    """Test the Calculator class."""

    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        """Test addition."""
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)

    def test_divide(self):
        """Test division."""
        result = self.calc.divide(10, 2)
        self.assertEqual(result, 5)

    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)


class TestProcessData(unittest.TestCase):
    """Test the process_data function."""

    def test_process_data_valid(self):
        """Test processing valid data."""
        data = {"count": 5, "name": "test"}
        result = process_data(data)
        expected = {"count": 10, "name": "TEST"}
        self.assertEqual(result, expected)

    def test_process_data_invalid_type(self):
        """Test processing invalid data type."""
        with self.assertRaises(TypeError):
            process_data("not a dict")


if __name__ == "__main__":
    unittest.main()
'''

        with open(os.path.join(self.test_project_dir, "test_main.py"), "w") as f:
            f.write(test_content)

        # Create requirements.txt
        requirements_content = """pytest>=6.0.0
requests>=2.25.0
pandas>=1.3.0
numpy>=1.20.0
"""

        with open(os.path.join(self.test_project_dir, "requirements.txt"), "w") as f:
            f.write(requirements_content)

        # Create README.md
        readme_content = """# Test Project

This is a sample Python project for testing Codomyrmex workflows.

## Features

- Calculator class with basic operations
- Data processing utilities
- Configuration management
- Unit tests

## Usage

```python
from main import Calculator

calc = Calculator()
result = calc.add(5, 3)
print(result)  # 8
```

## Testing

Run tests with:

```bash
python -m pytest test_main.py
```
"""

        with open(os.path.join(self.test_project_dir, "README.md"), "w") as f:
            f.write(readme_content)

    def setup_mock_modules(self):
        """Set up mock modules for testing workflows."""
        # Mock Static Analyzer
        self.mock_static_analyzer = Mock()
        self.mock_static_analyzer.analyze_code_quality.return_value = {
            "overall_score": 8.5,
            "security_score": 7.8,
            "maintainability_score": 9.2,
            "complexity_score": 8.0,
            "issues": [
                {
                    "type": "security",
                    "severity": "high",
                    "message": "Use of eval() detected in utils.py:25",
                    "file": "utils.py",
                    "line": 25,
                },
                {
                    "type": "style",
                    "severity": "low",
                    "message": "Line too long in main.py:15",
                    "file": "main.py",
                    "line": 15,
                },
            ],
            "metrics": {
                "lines_of_code": 150,
                "cyclomatic_complexity": 3.2,
                "maintainability_index": 85.4,
            },
        }

        # Mock Data Visualizer
        self.mock_data_visualizer = Mock()
        self.mock_data_visualizer.create_bar_chart.return_value = {
            "success": True,
            "output_path": os.path.join(self.test_dir, "code_quality_chart.png"),
            "chart_data": {
                "categories": ["Security", "Maintainability", "Complexity"],
                "values": [7.8, 9.2, 8.0],
            },
        }

        # Mock Git Operations
        self.mock_git_ops = Mock()
        self.mock_git_ops.analyze_repository.return_value = {
            "commit_count": 45,
            "contributor_count": 3,
            "branch_count": 5,
            "recent_activity": {
                "last_commit_date": "2024-01-15",
                "commits_last_month": 12,
            },
            "file_changes": {"added": 25, "modified": 18, "deleted": 2},
        }

        # Mock AI Code Helper
        self.mock_ai_helper = Mock()
        self.mock_ai_helper.generate_code_snippet.return_value = {
            "success": True,
            "generated_code": """# Code Improvement Recommendations

## Security Issues
- Replace eval() usage in utils.py with safer alternatives
- Implement input validation for all public functions

## Performance Optimizations
- Add caching to configuration reading
- Use list comprehensions where applicable

## Code Quality
- Add type hints to all function signatures
- Improve error handling with specific exception types
""",
            "confidence": 0.92,
        }

        # Mock Documentation Generator
        self.mock_doc_generator = Mock()
        self.mock_doc_generator.generate_api_docs.return_value = {
            "success": True,
            "output_path": os.path.join(self.test_dir, "api_docs.html"),
            "pages_generated": 5,
            "coverage": 0.87,
        }

        # Mock Build Manager
        self.mock_build_manager = Mock()
        self.mock_build_manager.build_project.return_value = {
            "success": True,
            "build_time": 45.6,
            "artifacts": [
                os.path.join(self.test_dir, "dist", "package.tar.gz"),
                os.path.join(self.test_dir, "dist", "package.whl"),
            ],
            "test_results": {
                "tests_run": 8,
                "tests_passed": 8,
                "tests_failed": 0,
                "coverage": 0.92,
            },
        }

    def test_comprehensive_code_analysis_workflow(self):
        """Test a comprehensive code analysis workflow integrating multiple modules."""
        print("\n🔍 Testing Comprehensive Code Analysis Workflow")

        # Workflow steps:
        # 1. Static analysis
        # 2. Git repository analysis
        # 3. Data visualization of results
        # 4. AI-generated recommendations
        # 5. Documentation generation

        workflow_results = {}

        # Step 1: Static Code Analysis
        print("   📊 Step 1: Static Code Analysis")
        analysis_result = self.mock_static_analyzer.analyze_code_quality(
            code_path=self.test_project_dir,
            include_security=True,
            include_complexity=True,
        )
        workflow_results["static_analysis"] = analysis_result

        self.assertIsInstance(analysis_result, dict)
        self.assertIn("overall_score", analysis_result)
        self.assertIn("issues", analysis_result)
        self.assertEqual(len(analysis_result["issues"]), 2)
        print(f"      ✅ Code quality score: {analysis_result['overall_score']}")
        print(f"      ⚠️ Issues found: {len(analysis_result['issues'])}")

        # Step 2: Git Repository Analysis
        print("   📈 Step 2: Git Repository Analysis")
        git_result = self.mock_git_ops.analyze_repository(
            repo_path=self.test_project_dir
        )
        workflow_results["git_analysis"] = git_result

        self.assertIsInstance(git_result, dict)
        self.assertIn("commit_count", git_result)
        self.assertIn("contributor_count", git_result)
        print(f"      ✅ Commits: {git_result['commit_count']}")
        print(f"      👥 Contributors: {git_result['contributor_count']}")

        # Step 3: Create Visualizations
        print("   📊 Step 3: Data Visualization")
        viz_data = {
            "categories": ["Security", "Maintainability", "Complexity"],
            "values": [
                analysis_result["security_score"],
                analysis_result["maintainability_score"],
                analysis_result["complexity_score"],
            ],
        }

        chart_result = self.mock_data_visualizer.create_bar_chart(
            categories=viz_data["categories"],
            values=viz_data["values"],
            title="Code Quality Metrics",
            output_path=os.path.join(self.test_dir, "quality_metrics.png"),
        )
        workflow_results["visualization"] = chart_result

        self.assertTrue(chart_result["success"])
        print(
            f"      ✅ Chart created: {os.path.basename(chart_result['output_path'])}"
        )

        # Step 4: AI-Generated Recommendations
        print("   🤖 Step 4: AI Code Recommendations")
        ai_prompt = f"""
        Based on the following code analysis results, provide specific improvement recommendations:

        Code Quality Score: {analysis_result['overall_score']}/10
        Issues Found: {len(analysis_result['issues'])}
        Security Score: {analysis_result['security_score']}/10

        Key Issues:
        {chr(10).join([f"- {issue['message']}" for issue in analysis_result['issues']])}
        """

        ai_result = self.mock_ai_helper.generate_code_snippet(
            prompt=ai_prompt, language="markdown", provider="openai"
        )
        workflow_results["ai_recommendations"] = ai_result

        self.assertTrue(ai_result["success"])
        self.assertIn("generated_code", ai_result)
        print(
            f"      ✅ AI recommendations generated (confidence: {ai_result['confidence']:.2%})"
        )

        # Step 5: Generate Documentation
        print("   📚 Step 5: Documentation Generation")
        doc_result = self.mock_doc_generator.generate_api_docs(
            source_path=self.test_project_dir,
            output_path=os.path.join(self.test_dir, "docs"),
            include_analysis_results=True,
            analysis_data=analysis_result,
        )
        workflow_results["documentation"] = doc_result

        self.assertTrue(doc_result["success"])
        self.assertGreater(doc_result["coverage"], 0.8)
        print(
            f"      ✅ Documentation generated (coverage: {doc_result['coverage']:.1%})"
        )

        # Verify workflow completion
        successful_steps = sum(
            1
            for result in workflow_results.values()
            if isinstance(result, dict) and result.get("success", True)
        )

        print(
            f"\n   🎉 Workflow completed: {successful_steps}/{len(workflow_results)} steps successful"
        )

        # Assertions for workflow success
        self.assertEqual(successful_steps, len(workflow_results))
        self.assertIn("static_analysis", workflow_results)
        self.assertIn("git_analysis", workflow_results)
        self.assertIn("visualization", workflow_results)
        self.assertIn("ai_recommendations", workflow_results)
        self.assertIn("documentation", workflow_results)

    def test_ci_cd_pipeline_workflow(self):
        """Test a CI/CD pipeline workflow integrating build, test, and deployment steps."""
        print("\n🚀 Testing CI/CD Pipeline Workflow")

        # Workflow steps:
        # 1. Code quality check
        # 2. Build project
        # 3. Run tests
        # 4. Generate documentation
        # 5. Create deployment artifacts

        workflow_results = {}
        pipeline_success = True

        try:
            # Step 1: Pre-build Code Quality Check
            print("   🔍 Step 1: Pre-build Quality Check")
            quality_check = self.mock_static_analyzer.analyze_code_quality(
                code_path=self.test_project_dir,
                include_security=True,
                quality_gate_threshold=7.0,
            )
            workflow_results["quality_check"] = quality_check

            # Quality gate - fail pipeline if quality is too low
            if quality_check["overall_score"] < 7.0:
                pipeline_success = False
                print(
                    f"      ❌ Quality gate failed: {quality_check['overall_score']} < 7.0"
                )
            else:
                print(
                    f"      ✅ Quality gate passed: {quality_check['overall_score']} >= 7.0"
                )

            # Step 2: Build Project
            print("   🔨 Step 2: Build Project")
            build_result = self.mock_build_manager.build_project(
                project_path=self.test_project_dir,
                build_type="production",
                run_tests=True,
                generate_coverage=True,
            )
            workflow_results["build"] = build_result

            if not build_result["success"]:
                pipeline_success = False
                print("      ❌ Build failed")
            else:
                print(f"      ✅ Build completed in {build_result['build_time']:.1f}s")
                print(f"      📦 Artifacts: {len(build_result['artifacts'])} files")
                print(
                    f"      🧪 Tests: {build_result['test_results']['tests_passed']}/{build_result['test_results']['tests_run']} passed"
                )
                print(
                    f"      📊 Coverage: {build_result['test_results']['coverage']:.1%}"
                )

            # Step 3: Generate Release Documentation
            print("   📝 Step 3: Generate Release Documentation")
            release_notes_prompt = f"""
            Generate release notes based on the following build information:

            Build Status: {'Success' if build_result['success'] else 'Failed'}
            Test Results: {build_result['test_results']['tests_passed']}/{build_result['test_results']['tests_run']} tests passed
            Code Coverage: {build_result['test_results']['coverage']:.1%}
            Build Time: {build_result['build_time']:.1f} seconds
            Quality Score: {quality_check['overall_score']}/10

            Include:
            - Summary of changes
            - Test results
            - Known issues (if any)
            - Installation instructions
            """

            release_notes = self.mock_ai_helper.generate_code_snippet(
                prompt=release_notes_prompt, language="markdown", provider="openai"
            )
            workflow_results["release_notes"] = release_notes

            if release_notes["success"]:
                print("      ✅ Release notes generated")
            else:
                print("      ⚠️ Release notes generation failed (non-critical)")

            # Step 4: Create Deployment Package
            print("   📦 Step 4: Create Deployment Package")

            # Simulate package creation
            deployment_package = {
                "success": pipeline_success,
                "package_path": os.path.join(
                    self.test_dir, "deployment_package.tar.gz"
                ),
                "version": "1.0.0",
                "size_mb": 15.3,
                "checksum": "sha256:abcd1234...",
                "contents": [
                    "application binaries",
                    "configuration files",
                    "documentation",
                    "deployment scripts",
                ],
            }
            workflow_results["deployment_package"] = deployment_package

            if deployment_package["success"]:
                print(
                    f"      ✅ Deployment package created: {deployment_package['size_mb']} MB"
                )
                print(f"      🔐 Checksum: {deployment_package['checksum'][:20]}...")
            else:
                print("      ❌ Deployment package creation failed")

            # Step 5: Pipeline Summary
            print("   📋 Step 5: Pipeline Summary")

            pipeline_summary = {
                "overall_success": pipeline_success,
                "steps_completed": len(
                    [r for r in workflow_results.values() if r.get("success", True)]
                ),
                "total_steps": len(workflow_results),
                "quality_score": quality_check["overall_score"],
                "test_coverage": build_result["test_results"]["coverage"],
                "build_time": build_result["build_time"],
                "ready_for_deployment": pipeline_success and build_result["success"],
            }

            workflow_results["pipeline_summary"] = pipeline_summary

            # Print final summary
            status_emoji = "✅" if pipeline_summary["overall_success"] else "❌"
            print(f"\n   {status_emoji} Pipeline Summary:")
            print(f"      Success: {pipeline_summary['overall_success']}")
            print(
                f"      Steps: {pipeline_summary['steps_completed']}/{pipeline_summary['total_steps']}"
            )
            print(f"      Quality: {pipeline_summary['quality_score']}/10")
            print(f"      Coverage: {pipeline_summary['test_coverage']:.1%}")
            print(f"      Build Time: {pipeline_summary['build_time']:.1f}s")
            print(f"      Deployment Ready: {pipeline_summary['ready_for_deployment']}")

        except Exception as e:
            print(f"   ❌ Pipeline failed with exception: {str(e)}")
            pipeline_success = False
            workflow_results["error"] = str(e)

        # Assertions
        self.assertIn("quality_check", workflow_results)
        self.assertIn("build", workflow_results)
        self.assertIn("pipeline_summary", workflow_results)

        # For testing purposes, we expect success since we're using mocks
        self.assertTrue(pipeline_success)

    def test_ai_driven_code_improvement_workflow(self):
        """Test an AI-driven code improvement workflow."""
        print("\n🤖 Testing AI-Driven Code Improvement Workflow")

        # Workflow steps:
        # 1. Analyze code for improvement opportunities
        # 2. Generate AI recommendations
        # 3. Apply automated improvements (simulated)
        # 4. Re-analyze improved code
        # 5. Generate improvement report

        workflow_results = {}

        # Step 1: Initial Code Analysis
        print("   🔍 Step 1: Initial Code Analysis")
        initial_analysis = self.mock_static_analyzer.analyze_code_quality(
            code_path=self.test_project_dir,
            include_security=True,
            include_complexity=True,
            include_suggestions=True,
        )
        workflow_results["initial_analysis"] = initial_analysis

        print(f"      📊 Initial quality score: {initial_analysis['overall_score']}")
        print(f"      🐛 Issues found: {len(initial_analysis['issues'])}")

        # Step 2: Generate AI-Powered Improvement Suggestions
        print("   🧠 Step 2: AI Improvement Suggestions")
        improvement_prompt = f"""
        Analyze this Python codebase and suggest specific improvements:

        Current Quality Score: {initial_analysis['overall_score']}/10
        Security Score: {initial_analysis['security_score']}/10

        Issues Found:
        {chr(10).join([f"- {issue['severity'].upper()}: {issue['message']}" for issue in initial_analysis['issues']])}

        Code Metrics:
        - Lines of Code: {initial_analysis['metrics']['lines_of_code']}
        - Cyclomatic Complexity: {initial_analysis['metrics']['cyclomatic_complexity']}
        - Maintainability Index: {initial_analysis['metrics']['maintainability_index']}

        Provide:
        1. Specific code improvements
        2. Security enhancements
        3. Performance optimizations
        4. Code refactoring suggestions

        Format as actionable Python code changes.
        """

        ai_improvements = self.mock_ai_helper.generate_code_snippet(
            prompt=improvement_prompt,
            language="python",
            provider="openai",
            context="code_improvement",
        )
        workflow_results["ai_improvements"] = ai_improvements

        print(
            f"      ✅ AI improvements generated (confidence: {ai_improvements['confidence']:.1%})"
        )

        # Step 3: Simulate Code Improvements Applied
        print("   ⚡ Step 3: Apply Automated Improvements")

        # Simulate applying improvements (in reality, this would modify files)
        improvements_applied = {
            "security_fixes": [
                "Replaced eval() with ast.literal_eval() in utils.py",
                "Added input validation to process_data() function",
            ],
            "performance_optimizations": [
                "Added caching to read_config() function",
                "Optimized list operations in Calculator class",
            ],
            "code_quality_improvements": [
                "Added type hints to all function signatures",
                "Improved error handling with specific exceptions",
                "Added docstring documentation",
            ],
            "files_modified": 3,
            "lines_changed": 47,
        }
        workflow_results["improvements_applied"] = improvements_applied

        print(f"      🔧 Files modified: {improvements_applied['files_modified']}")
        print(f"      📝 Lines changed: {improvements_applied['lines_changed']}")
        print(f"      🔒 Security fixes: {len(improvements_applied['security_fixes'])}")
        print(
            f"      ⚡ Performance improvements: {len(improvements_applied['performance_optimizations'])}"
        )

        # Step 4: Re-analyze Improved Code
        print("   🔄 Step 4: Re-analyze Improved Code")

        # Simulate improved scores
        improved_analysis = {
            "overall_score": min(10.0, initial_analysis["overall_score"] + 1.5),
            "security_score": min(10.0, initial_analysis["security_score"] + 2.2),
            "maintainability_score": min(
                10.0, initial_analysis["maintainability_score"] + 0.8
            ),
            "complexity_score": initial_analysis["complexity_score"] + 0.5,
            "issues": [
                issue
                for issue in initial_analysis["issues"]
                if issue["type"] != "security"  # Security issues resolved
            ],
            "metrics": {
                "lines_of_code": initial_analysis["metrics"]["lines_of_code"]
                + 20,  # Documentation added
                "cyclomatic_complexity": max(
                    1.0, initial_analysis["metrics"]["cyclomatic_complexity"] - 0.3
                ),
                "maintainability_index": min(
                    100.0, initial_analysis["metrics"]["maintainability_index"] + 5.2
                ),
            },
        }
        workflow_results["improved_analysis"] = improved_analysis

        print(
            f"      📈 New quality score: {improved_analysis['overall_score']} (+{improved_analysis['overall_score'] - initial_analysis['overall_score']:.1f})"
        )
        print(
            f"      🔒 Security score: {improved_analysis['security_score']} (+{improved_analysis['security_score'] - initial_analysis['security_score']:.1f})"
        )
        print(
            f"      🐛 Issues remaining: {len(improved_analysis['issues'])} (-{len(initial_analysis['issues']) - len(improved_analysis['issues'])})"
        )

        # Step 5: Generate Improvement Report
        print("   📊 Step 5: Generate Improvement Report")

        improvement_report = {
            "success": True,
            "improvements": {
                "quality_score_improvement": improved_analysis["overall_score"]
                - initial_analysis["overall_score"],
                "security_score_improvement": improved_analysis["security_score"]
                - initial_analysis["security_score"],
                "issues_resolved": len(initial_analysis["issues"])
                - len(improved_analysis["issues"]),
                "maintainability_improvement": improved_analysis["metrics"][
                    "maintainability_index"
                ]
                - initial_analysis["metrics"]["maintainability_index"],
            },
            "summary": {
                "total_improvements": len(improvements_applied["security_fixes"])
                + len(improvements_applied["performance_optimizations"])
                + len(improvements_applied["code_quality_improvements"]),
                "files_touched": improvements_applied["files_modified"],
                "estimated_time_saved": "2.5 hours",
                "ai_confidence": ai_improvements["confidence"],
            },
            "recommendations": [
                "Continue monitoring code quality with regular analysis",
                "Set up automated code quality checks in CI/CD pipeline",
                "Consider additional security scanning for production deployment",
            ],
        }
        workflow_results["improvement_report"] = improvement_report

        print("      ✅ Improvement report generated")
        print(
            f"      📈 Quality improvement: +{improvement_report['improvements']['quality_score_improvement']:.1f}"
        )
        print(
            f"      🔒 Security improvement: +{improvement_report['improvements']['security_score_improvement']:.1f}"
        )
        print(
            f"      ⏰ Estimated time saved: {improvement_report['summary']['estimated_time_saved']}"
        )

        # Final Summary
        print("\n   🎉 AI-Driven Improvement Workflow Completed!")
        print(f"      Original Score: {initial_analysis['overall_score']:.1f}/10")
        print(f"      Improved Score: {improved_analysis['overall_score']:.1f}/10")
        print(
            f"      Net Improvement: +{improvement_report['improvements']['quality_score_improvement']:.1f}"
        )

        # Assertions
        self.assertIn("initial_analysis", workflow_results)
        self.assertIn("ai_improvements", workflow_results)
        self.assertIn("improvements_applied", workflow_results)
        self.assertIn("improved_analysis", workflow_results)
        self.assertIn("improvement_report", workflow_results)

        # Verify improvements were made
        self.assertGreater(
            improved_analysis["overall_score"], initial_analysis["overall_score"]
        )
        self.assertGreater(
            improved_analysis["security_score"], initial_analysis["security_score"]
        )
        self.assertLess(
            len(improved_analysis["issues"]), len(initial_analysis["issues"])
        )
        self.assertTrue(improvement_report["success"])

    def test_data_driven_project_analysis_workflow(self):
        """Test a data-driven project analysis workflow with visualization."""
        print("\n📊 Testing Data-Driven Project Analysis Workflow")

        # Workflow steps:
        # 1. Collect project metrics
        # 2. Analyze development patterns
        # 3. Create data visualizations
        # 4. Generate insights report
        # 5. Create project dashboard

        workflow_results = {}

        # Step 1: Collect Project Metrics
        print("   📈 Step 1: Collect Project Metrics")

        # Combine multiple data sources
        code_metrics = self.mock_static_analyzer.analyze_code_quality(
            code_path=self.test_project_dir, include_metrics=True
        )

        git_metrics = self.mock_git_ops.analyze_repository(
            repo_path=self.test_project_dir
        )

        project_metrics = {
            "code_quality": {
                "overall_score": code_metrics["overall_score"],
                "lines_of_code": code_metrics["metrics"]["lines_of_code"],
                "complexity": code_metrics["metrics"]["cyclomatic_complexity"],
                "maintainability": code_metrics["metrics"]["maintainability_index"],
            },
            "development_activity": {
                "total_commits": git_metrics["commit_count"],
                "active_contributors": git_metrics["contributor_count"],
                "branch_count": git_metrics["branch_count"],
                "recent_commits": git_metrics["recent_activity"]["commits_last_month"],
            },
            "project_health": {
                "test_coverage": 0.85,  # Simulated
                "documentation_coverage": 0.75,  # Simulated
                "dependency_freshness": 0.90,  # Simulated
                "security_vulnerabilities": len(
                    [i for i in code_metrics["issues"] if i["type"] == "security"]
                ),
            },
        }
        workflow_results["project_metrics"] = project_metrics

        print(
            f"      📊 Code Quality: {project_metrics['code_quality']['overall_score']:.1f}/10"
        )
        print(
            f"      📝 Lines of Code: {project_metrics['code_quality']['lines_of_code']:,}"
        )
        print(
            f"      👥 Contributors: {project_metrics['development_activity']['active_contributors']}"
        )
        print(
            f"      🧪 Test Coverage: {project_metrics['project_health']['test_coverage']:.1%}"
        )

        # Step 2: Analyze Development Patterns
        print("   🔍 Step 2: Analyze Development Patterns")

        # Simulate pattern analysis
        development_patterns = {
            "commit_frequency": {
                "daily_average": 2.3,
                "weekly_average": 16.1,
                "trend": "increasing",
            },
            "code_growth": {
                "monthly_lines_added": 450,
                "monthly_lines_removed": 120,
                "net_growth": 330,
                "growth_rate": 0.12,  # 12% per month
            },
            "quality_trends": {
                "quality_score_trend": "stable",
                "complexity_trend": "decreasing",
                "test_coverage_trend": "increasing",
            },
            "hotspots": [
                {"file": "main.py", "changes": 15, "complexity": 3.2},
                {"file": "utils.py", "changes": 8, "complexity": 2.1},
            ],
        }
        workflow_results["development_patterns"] = development_patterns

        print(
            f"      📈 Commit frequency: {development_patterns['commit_frequency']['daily_average']:.1f}/day"
        )
        print(
            f"      📏 Growth rate: {development_patterns['code_growth']['growth_rate']:.1%}/month"
        )
        print(
            f"      🎯 Quality trend: {development_patterns['quality_trends']['quality_score_trend']}"
        )

        # Step 3: Create Data Visualizations
        print("   🎨 Step 3: Create Data Visualizations")

        # Quality metrics chart
        quality_chart = self.mock_data_visualizer.create_bar_chart(
            categories=["Quality", "Security", "Maintainability", "Complexity"],
            values=[
                project_metrics["code_quality"]["overall_score"],
                code_metrics["security_score"],
                code_metrics["maintainability_score"],
                code_metrics["complexity_score"],
            ],
            title="Project Quality Metrics",
            output_path=os.path.join(self.test_dir, "quality_metrics.png"),
        )

        # Development activity chart (simulated)
        activity_chart = {
            "success": True,
            "output_path": os.path.join(self.test_dir, "activity_chart.png"),
            "chart_data": {
                "type": "line_chart",
                "title": "Development Activity Over Time",
                "datasets": [
                    {
                        "name": "Commits",
                        "data": [12, 15, 18, 22, 16, 19, 25],  # Last 7 weeks
                    },
                    {
                        "name": "Quality Score",
                        "data": [8.1, 8.2, 8.3, 8.5, 8.4, 8.5, 8.5],
                    },
                ],
            },
        }

        # Project health dashboard (simulated)
        health_dashboard = {
            "success": True,
            "output_path": os.path.join(self.test_dir, "health_dashboard.png"),
            "dashboard_data": {
                "widgets": [
                    {
                        "type": "gauge",
                        "title": "Code Quality",
                        "value": project_metrics["code_quality"]["overall_score"],
                        "max": 10,
                    },
                    {
                        "type": "gauge",
                        "title": "Test Coverage",
                        "value": project_metrics["project_health"]["test_coverage"]
                        * 10,
                        "max": 10,
                    },
                    {
                        "type": "badge",
                        "title": "Security Issues",
                        "value": project_metrics["project_health"][
                            "security_vulnerabilities"
                        ],
                    },
                    {
                        "type": "trend",
                        "title": "Growth Rate",
                        "value": development_patterns["code_growth"]["growth_rate"],
                    },
                ]
            },
        }

        visualizations = {
            "quality_chart": quality_chart,
            "activity_chart": activity_chart,
            "health_dashboard": health_dashboard,
        }
        workflow_results["visualizations"] = visualizations

        print(
            f"      📊 Quality chart: {os.path.basename(quality_chart['output_path'])}"
        )
        print(
            f"      📈 Activity chart: {os.path.basename(activity_chart['output_path'])}"
        )
        print(
            f"      🏥 Health dashboard: {os.path.basename(health_dashboard['output_path'])}"
        )

        # Step 4: Generate Insights Report
        print("   🧠 Step 4: Generate Insights Report")

        insights_prompt = f"""
        Generate data-driven insights based on this project analysis:

        Project Metrics:
        - Code Quality Score: {project_metrics['code_quality']['overall_score']}/10
        - Lines of Code: {project_metrics['code_quality']['lines_of_code']:,}
        - Test Coverage: {project_metrics['project_health']['test_coverage']:.1%}
        - Active Contributors: {project_metrics['development_activity']['active_contributors']}

        Development Patterns:
        - Daily Commit Rate: {development_patterns['commit_frequency']['daily_average']:.1f}
        - Growth Rate: {development_patterns['code_growth']['growth_rate']:.1%}/month
        - Quality Trend: {development_patterns['quality_trends']['quality_score_trend']}

        Provide:
        1. Key strengths of the project
        2. Areas for improvement
        3. Risk assessment
        4. Actionable recommendations
        5. Future outlook
        """

        insights_report = self.mock_ai_helper.generate_code_snippet(
            prompt=insights_prompt,
            language="markdown",
            provider="openai",
            context="data_analysis",
        )
        workflow_results["insights_report"] = insights_report

        print(
            f"      ✅ Insights report generated (confidence: {insights_report['confidence']:.1%})"
        )

        # Step 5: Create Executive Summary
        print("   📋 Step 5: Create Executive Summary")

        executive_summary = {
            "project_overview": {
                "name": "Test Project Analysis",
                "analysis_date": "2024-01-15",
                "total_metrics_analyzed": len(project_metrics)
                + len(development_patterns),
                "visualizations_created": len(visualizations),
            },
            "key_findings": {
                "overall_health": (
                    "Good"
                    if project_metrics["code_quality"]["overall_score"] >= 7.5
                    else "Needs Attention"
                ),
                "development_velocity": (
                    "High"
                    if development_patterns["commit_frequency"]["daily_average"] >= 2.0
                    else "Moderate"
                ),
                "quality_stability": development_patterns["quality_trends"][
                    "quality_score_trend"
                ],
                "risk_level": (
                    "Low"
                    if project_metrics["project_health"]["security_vulnerabilities"]
                    <= 2
                    else "Moderate"
                ),
            },
            "recommendations": [
                "Maintain current development velocity",
                "Focus on improving test coverage",
                "Address remaining security issues",
                "Consider setting up automated quality gates",
            ],
            "next_steps": [
                "Schedule monthly analysis reviews",
                "Implement dashboard monitoring",
                "Set up alerting for quality degradation",
            ],
        }
        workflow_results["executive_summary"] = executive_summary

        print(
            f"      📊 Overall Health: {executive_summary['key_findings']['overall_health']}"
        )
        print(
            f"      🚀 Development Velocity: {executive_summary['key_findings']['development_velocity']}"
        )
        print(f"      ⚠️ Risk Level: {executive_summary['key_findings']['risk_level']}")

        # Final Summary
        print("\n   🎉 Data-Driven Analysis Completed!")
        print("      Metrics Collected: ✅")
        print("      Patterns Analyzed: ✅")
        print(f"      Visualizations Created: {len(visualizations)}")
        print("      Insights Generated: ✅")
        print("      Executive Summary: ✅")

        # Assertions
        self.assertIn("project_metrics", workflow_results)
        self.assertIn("development_patterns", workflow_results)
        self.assertIn("visualizations", workflow_results)
        self.assertIn("insights_report", workflow_results)
        self.assertIn("executive_summary", workflow_results)

        # Verify data quality
        self.assertIsInstance(
            project_metrics["code_quality"]["overall_score"], (int, float)
        )
        self.assertGreater(project_metrics["development_activity"]["total_commits"], 0)
        self.assertTrue(all(viz["success"] for viz in visualizations.values()))
        self.assertTrue(insights_report["success"])


class WorkflowIntegrationTest(unittest.TestCase):
    """Test workflow integration scenarios."""

    def test_workflow_chaining(self):
        """Test chaining multiple workflows together."""
        print("\n🔗 Testing Workflow Chaining")

        # Simulate a chain of workflows where output of one feeds into the next
        workflow_chain = [
            ("static_analysis", {"code_path": "./src"}),
            ("ai_recommendations", {"analysis_results": "${static_analysis.output}"}),
            ("code_improvements", {"recommendations": "${ai_recommendations.output}"}),
            (
                "quality_verification",
                {"improved_code_path": "${code_improvements.output}"},
            ),
        ]

        chain_results = {}

        for i, (workflow_name, params) in enumerate(workflow_chain):
            print(f"   🔄 Step {i+1}: {workflow_name}")

            # Simulate workflow execution with parameter substitution
            resolved_params = params.copy()
            for key, value in resolved_params.items():
                if isinstance(value, str) and value.startswith("${"):
                    # Simple parameter substitution simulation
                    ref = value[2:-1]  # Remove ${ and }
                    if "." in ref:
                        workflow_ref, output_ref = ref.split(".", 1)
                        if workflow_ref in chain_results:
                            resolved_params[key] = (
                                f"output_from_{workflow_ref}_{output_ref}"
                            )

            # Simulate successful workflow execution
            result = {
                "success": True,
                "execution_time": 15.5 + i * 5,  # Increasing execution time
                "output": f"result_from_{workflow_name}",
                "parameters_used": resolved_params,
            }

            chain_results[workflow_name] = result
            print(f"      ✅ Completed in {result['execution_time']:.1f}s")

        print(f"\n   🎉 Workflow chain completed: {len(chain_results)} workflows")

        # Assertions
        self.assertEqual(len(chain_results), len(workflow_chain))
        self.assertTrue(all(result["success"] for result in chain_results.values()))

        # Verify parameter substitution worked
        ai_params = chain_results["ai_recommendations"]["parameters_used"]
        self.assertIn("analysis_results", ai_params)
        self.assertEqual(
            ai_params["analysis_results"], "output_from_static_analysis_output"
        )

    def test_parallel_workflow_execution(self):
        """Test executing multiple workflows in parallel."""
        print("\n⚡ Testing Parallel Workflow Execution")

        import threading
        import time

        # Define workflows to run in parallel
        parallel_workflows = [
            ("code_analysis", {"path": "./src"}),
            ("documentation_scan", {"path": "./docs"}),
            ("dependency_check", {"path": "./requirements.txt"}),
            ("security_scan", {"path": "./src"}),
        ]

        results = {}
        threads = []

        def execute_workflow(workflow_name, params):
            """Simulate workflow execution in a separate thread."""
            start_time = time.time()

            # Simulate variable execution time
            import random

            execution_time = random.uniform(1.0, 3.0)
            time.sleep(execution_time)

            end_time = time.time()

            results[workflow_name] = {
                "success": True,
                "execution_time": end_time - start_time,
                "thread_id": threading.current_thread().name,
                "parameters": params,
                "output": f"result_from_{workflow_name}",
            }

            print(
                f"      ✅ {workflow_name} completed in {results[workflow_name]['execution_time']:.2f}s"
            )

        print(f"   🚀 Starting {len(parallel_workflows)} workflows in parallel...")
        start_time = time.time()

        # Create and start threads
        for workflow_name, params in parallel_workflows:
            thread = threading.Thread(
                target=execute_workflow,
                args=(workflow_name, params),
                name=f"Workflow-{workflow_name}",
            )
            threads.append(thread)
            thread.start()
            print(f"      🔄 Started {workflow_name}")

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        print(f"\n   🎉 All parallel workflows completed in {total_time:.2f}s")
        print(
            f"      Sequential time would be: ~{sum(r['execution_time'] for r in results.values()):.2f}s"
        )
        print(
            f"      Time savings: ~{(sum(r['execution_time'] for r in results.values()) - total_time):.2f}s"
        )

        # Assertions
        self.assertEqual(len(results), len(parallel_workflows))
        self.assertTrue(all(result["success"] for result in results.values()))

        # Verify parallel execution was faster than sequential
        sequential_time = sum(result["execution_time"] for result in results.values())
        self.assertLess(total_time, sequential_time)

    def test_workflow_error_handling(self):
        """Test error handling and recovery in workflows."""
        print("\n🛠️ Testing Workflow Error Handling")

        # Simulate a workflow with some failing steps
        workflow_steps = [
            ("step_1", True),  # Success
            ("step_2", False),  # Failure
            ("step_3", True),  # Success (with error recovery)
            ("step_4", True),  # Success
        ]

        results = []
        workflow_failed = False

        for step_name, should_succeed in workflow_steps:
            print(f"   🔄 Executing {step_name}...")

            if should_succeed:
                result = {
                    "step": step_name,
                    "success": True,
                    "execution_time": 2.5,
                    "output": f"success_output_from_{step_name}",
                }
                print(f"      ✅ {step_name} completed successfully")
            else:
                result = {
                    "step": step_name,
                    "success": False,
                    "error": f"Simulated failure in {step_name}",
                    "retry_attempts": 2,
                    "recovery_action": "used_fallback_data",
                }
                print(f"      ❌ {step_name} failed: {result['error']}")
                print(f"      🔄 Attempted {result['retry_attempts']} retries")
                print(f"      🛠️ Recovery action: {result['recovery_action']}")

                # Simulate recovery - continue with next steps
                if step_name == "step_2":
                    print("      ✅ Workflow continuing with recovered data")
                    workflow_failed = False
                else:
                    workflow_failed = True

            results.append(result)

        # Workflow summary
        successful_steps = len([r for r in results if r["success"]])
        total_steps = len(results)

        print("\n   📊 Workflow Summary:")
        print(f"      Total steps: {total_steps}")
        print(f"      Successful: {successful_steps}")
        print(f"      Failed: {total_steps - successful_steps}")
        print(f"      Workflow completed: {'✅' if not workflow_failed else '❌'}")

        # Assertions
        self.assertEqual(len(results), len(workflow_steps))
        self.assertGreater(successful_steps, 0)
        self.assertIn("step_2", [r["step"] for r in results if not r["success"]])

        # Verify error recovery
        failed_step = next(r for r in results if r["step"] == "step_2")
        self.assertIn("recovery_action", failed_step)
        self.assertEqual(failed_step["retry_attempts"], 2)


def run_comprehensive_workflow_tests():
    """Run all inter-module workflow tests."""
    print("🚀 Starting Comprehensive Inter-Module Workflow Tests")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add inter-module workflow tests
    test_suite.addTest(
        InterModuleWorkflowsTest("test_comprehensive_code_analysis_workflow")
    )
    test_suite.addTest(InterModuleWorkflowsTest("test_ci_cd_pipeline_workflow"))
    test_suite.addTest(
        InterModuleWorkflowsTest("test_ai_driven_code_improvement_workflow")
    )
    test_suite.addTest(
        InterModuleWorkflowsTest("test_data_driven_project_analysis_workflow")
    )

    # Add workflow integration tests
    test_suite.addTest(WorkflowIntegrationTest("test_workflow_chaining"))
    test_suite.addTest(WorkflowIntegrationTest("test_parallel_workflow_execution"))
    test_suite.addTest(WorkflowIntegrationTest("test_workflow_error_handling"))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(
        f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split(chr(10))[-2]}")

    if result.errors:
        print("\n🚫 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split(chr(10))[-2]}")

    if not result.failures and not result.errors:
        print("\n🎉 All workflow tests passed successfully!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_workflow_tests()
    sys.exit(0 if success else 1)
