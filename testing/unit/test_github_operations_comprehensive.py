#!/usr/bin/env python3
"""
Comprehensive Unit Tests for GitHub Operations.

This test suite verifies all GitHub API operations including repository creation,
pull request management, and complete end-to-end workflows with real GitHub integration.

Following project conventions:
- Test-driven development (TDD) with real implementations, no mocks
- Comprehensive tests with iterative improvements
- All outputs placed in numbered subfolders
"""

import unittest
import tempfile
import os
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.github_api import (
    create_github_repository,
    delete_github_repository,
    create_pull_request,
    get_pull_requests,
    get_pull_request,
    get_repository_info,
    GitHubAPIError,
    _validate_github_token
)

from codomyrmex.git_operations.git_manager import (
    check_git_availability,
    initialize_git_repository,
    clone_repository,
    create_branch,
    switch_branch,
    add_files,
    commit_changes,
    push_changes,
    get_current_branch,
    get_status
)


class TestGitHubOperationsComprehensive(unittest.TestCase):
    """
    Comprehensive test suite for GitHub Operations.
    
    Test Objectives:
    - Verify GitHub repository creation (public and private)
    - Test pull request operations end-to-end
    - Validate complete development workflow
    - Ensure proper logging and error handling
    - Test with real GitHub API integration
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        # Check if Git and GitHub token are available
        if not check_git_availability():
            raise unittest.SkipTest("Git is not available on this system")
        
        try:
            cls.github_token = _validate_github_token(None)
        except GitHubAPIError:
            raise unittest.SkipTest("GitHub token not available. Set GITHUB_TOKEN environment variable.")
        
        # Create output directory for test results
        cls.output_dir = Path("@output/01_github_ops_test_results")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track created repositories for cleanup
        cls.test_repositories = []
        cls.local_test_dirs = []
        
        # Test configuration
        cls.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls.private_repo_name = f"private_test_{cls.test_timestamp}"
        cls.public_repo_name = f"public_test_{cls.test_timestamp}"
        
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level test fixtures."""
        # Clean up GitHub repositories
        for repo_info in cls.test_repositories:
            try:
                owner = repo_info.get('owner')
                name = repo_info.get('name')
                if owner and name:
                    print(f"Cleaning up repository: {owner}/{name}")
                    delete_github_repository(owner, name, cls.github_token)
            except Exception as e:
                print(f"Warning: Could not clean up repository {repo_info}: {e}")
        
        # Clean up local directories
        for local_dir in cls.local_test_dirs:
            try:
                if os.path.exists(local_dir):
                    shutil.rmtree(local_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up directory {local_dir}: {e}")

    def setUp(self):
        """Set up test fixtures for each test."""
        self.test_dir = tempfile.mkdtemp(prefix="github_test_")
        self.local_test_dirs.append(self.test_dir)
        
    def _log_test_result(self, test_name: str, result: Dict, success: bool = True):
        """Log test results to output directory."""
        log_file = self.output_dir / f"{test_name}_{self.test_timestamp}.json"
        
        test_log = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "result": result,
            "github_token_available": bool(self.github_token)
        }
        
        import json
        with open(log_file, 'w') as f:
            json.dump(test_log, f, indent=2)
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED - {result}")

    # ==================== GITHUB REPOSITORY CREATION TESTS ====================
    
    def test_create_private_repository(self):
        """Test creating a private GitHub repository."""
        print(f"\n🔒 Testing private repository creation: {self.private_repo_name}")
        
        result = create_github_repository(
            name=self.private_repo_name,
            private=True,
            description="Test private repository for Codomyrmex GitHub operations testing",
            github_token=self.github_token,
            auto_init=True,
            gitignore_template="Python",
            license_template="mit"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["repository"]["name"], self.private_repo_name)
        self.assertTrue(result["repository"]["private"])
        self.assertIn("github.com", result["repository"]["html_url"])
        
        # Track for cleanup
        repo_info = {
            'owner': result["repository"]["full_name"].split('/')[0],
            'name': result["repository"]["name"]
        }
        self.test_repositories.append(repo_info)
        
        self._log_test_result("create_private_repository", result)

    def test_create_public_repository(self):
        """Test creating a public GitHub repository."""
        print(f"\n🌐 Testing public repository creation: {self.public_repo_name}")
        
        result = create_github_repository(
            name=self.public_repo_name,
            private=False,
            description="Test public repository for Codomyrmex GitHub operations testing",
            github_token=self.github_token,
            auto_init=True,
            gitignore_template="Python"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["repository"]["name"], self.public_repo_name)
        self.assertFalse(result["repository"]["private"])
        self.assertIn("github.com", result["repository"]["html_url"])
        
        # Track for cleanup
        repo_info = {
            'owner': result["repository"]["full_name"].split('/')[0],
            'name': result["repository"]["name"]
        }
        self.test_repositories.append(repo_info)
        
        self._log_test_result("create_public_repository", result)

    def test_get_repository_info(self):
        """Test retrieving repository information."""
        # First create a repository to test with
        create_result = create_github_repository(
            name=f"info_test_{self.test_timestamp}",
            private=True,
            description="Repository for testing get_repository_info",
            github_token=self.github_token
        )
        
        owner = create_result["repository"]["full_name"].split('/')[0]
        repo_name = create_result["repository"]["name"]
        
        # Track for cleanup
        self.test_repositories.append({'owner': owner, 'name': repo_name})
        
        print(f"\n📊 Testing repository info retrieval: {owner}/{repo_name}")
        
        # Test getting repository info
        repo_info = get_repository_info(owner, repo_name, self.github_token)
        
        self.assertEqual(repo_info["name"], repo_name)
        self.assertEqual(repo_info["full_name"], f"{owner}/{repo_name}")
        self.assertTrue(repo_info["private"])
        self.assertIsNotNone(repo_info["created_at"])
        
        self._log_test_result("get_repository_info", repo_info)

    # ==================== PULL REQUEST OPERATIONS TESTS ====================
    
    def test_complete_pull_request_workflow(self):
        """Test complete pull request workflow from creation to reading."""
        print(f"\n🔄 Testing complete PR workflow")
        
        # Step 1: Create test repository
        create_result = create_github_repository(
            name=f"pr_test_{self.test_timestamp}",
            private=True,
            description="Repository for testing PR workflow",
            github_token=self.github_token,
            auto_init=True
        )
        
        repo_full_name = create_result["repository"]["full_name"]
        owner, repo_name = repo_full_name.split('/')
        clone_url = create_result["repository"]["clone_url"]
        
        # Track for cleanup
        self.test_repositories.append({'owner': owner, 'name': repo_name})
        
        print(f"   📁 Created repository: {repo_full_name}")
        
        # Step 2: Clone repository locally
        local_repo_path = os.path.join(self.test_dir, "pr_test_repo")
        clone_success = clone_repository(clone_url, local_repo_path)
        self.assertTrue(clone_success, "Repository clone should succeed")
        
        print(f"   📥 Cloned repository to: {local_repo_path}")
        
        # Step 3: Create feature branch
        feature_branch = "feature/test-pr-workflow"
        branch_success = create_branch(feature_branch, local_repo_path)
        self.assertTrue(branch_success, "Feature branch creation should succeed")
        
        current_branch = get_current_branch(local_repo_path)
        self.assertEqual(current_branch, feature_branch)
        
        print(f"   🌿 Created feature branch: {feature_branch}")
        
        # Step 4: Make changes and commit
        test_file_path = os.path.join(local_repo_path, "test_feature.py")
        with open(test_file_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
'''
Test feature file for PR workflow testing.
Created at: {datetime.now().isoformat()}
'''

def test_function():
    '''Test function for PR workflow.'''
    return "This is a test feature for PR workflow validation"

if __name__ == "__main__":
    print(test_function())
""")
        
        add_success = add_files(["test_feature.py"], local_repo_path)
        self.assertTrue(add_success, "Adding files should succeed")
        
        commit_success = commit_changes("Add test feature for PR workflow", local_repo_path)
        self.assertTrue(commit_success, "Commit should succeed")
        
        print(f"   💾 Added and committed test file")
        
        # Step 5: Push feature branch
        push_success = push_changes("origin", feature_branch, local_repo_path)
        self.assertTrue(push_success, "Push should succeed")
        
        print(f"   📤 Pushed feature branch to remote")
        
        # Step 6: Create pull request
        pr_title = "Add test feature for PR workflow validation"
        pr_body = f"""This PR adds a test feature file to validate the PR workflow.

Created by automated test at: {datetime.now().isoformat()}

Changes:
- Add test_feature.py with a simple test function
- Demonstrates complete PR workflow from creation to merge

This PR is part of the comprehensive GitHub operations testing suite."""
        
        pr_result = create_pull_request(
            repo_owner=owner,
            repo_name=repo_name,
            head_branch=feature_branch,
            base_branch="main",  # or "master" depending on repository default
            title=pr_title,
            body=pr_body,
            github_token=self.github_token
        )
        
        self.assertTrue(pr_result["success"])
        self.assertEqual(pr_result["pull_request"]["title"], pr_title)
        self.assertEqual(pr_result["pull_request"]["head"]["ref"], feature_branch)
        
        pr_number = pr_result["pull_request"]["number"]
        print(f"   📋 Created PR #{pr_number}: {pr_title}")
        
        # Step 7: Read pull request details
        pr_details = get_pull_request(owner, repo_name, pr_number, self.github_token)
        
        self.assertEqual(pr_details["number"], pr_number)
        self.assertEqual(pr_details["title"], pr_title)
        self.assertEqual(pr_details["state"], "open")
        self.assertFalse(pr_details["merged"])
        
        print(f"   📖 Retrieved PR details: #{pr_details['number']}")
        
        # Step 8: List pull requests
        pr_list = get_pull_requests(owner, repo_name, "open", self.github_token)
        
        self.assertGreater(len(pr_list), 0)
        self.assertTrue(any(pr["number"] == pr_number for pr in pr_list))
        
        print(f"   📝 Listed PRs: found {len(pr_list)} open PRs")
        
        # Log comprehensive workflow result
        workflow_result = {
            "repository": repo_full_name,
            "local_path": local_repo_path,
            "feature_branch": feature_branch,
            "pr_number": pr_number,
            "pr_title": pr_title,
            "pr_url": pr_result["pull_request"]["html_url"],
            "steps_completed": [
                "repository_created",
                "repository_cloned",
                "feature_branch_created",
                "changes_committed",
                "branch_pushed",
                "pr_created",
                "pr_details_retrieved",
                "pr_list_retrieved"
            ]
        }
        
        self._log_test_result("complete_pull_request_workflow", workflow_result)

    # ==================== ERROR HANDLING TESTS ====================
    
    def test_repository_creation_errors(self):
        """Test error handling in repository creation."""
        print(f"\n🚫 Testing repository creation error handling")
        
        # Test creating repository with invalid name (empty)
        with self.assertRaises(GitHubAPIError):
            create_github_repository(
                name="",
                github_token=self.github_token
            )
        
        # Test creating repository with name that already exists
        existing_repo_name = f"duplicate_test_{self.test_timestamp}"
        
        # First creation should succeed
        result1 = create_github_repository(
            name=existing_repo_name,
            private=True,
            github_token=self.github_token
        )
        self.assertTrue(result1["success"])
        
        # Track for cleanup
        owner = result1["repository"]["full_name"].split('/')[0]
        self.test_repositories.append({'owner': owner, 'name': existing_repo_name})
        
        # Second creation with same name should fail
        with self.assertRaises(GitHubAPIError):
            create_github_repository(
                name=existing_repo_name,
                private=True,
                github_token=self.github_token
            )
        
        print(f"   ✅ Error handling working correctly")
        
        self._log_test_result("repository_creation_errors", {"error_handling": "passed"})

    def test_pr_errors(self):
        """Test error handling in pull request operations."""
        print(f"\n🚫 Testing PR error handling")
        
        # Test creating PR for non-existent repository
        with self.assertRaises(GitHubAPIError):
            create_pull_request(
                repo_owner="nonexistent",
                repo_name="nonexistent",
                head_branch="feature",
                base_branch="main",
                title="Test PR",
                github_token=self.github_token
            )
        
        # Test getting PR from non-existent repository
        with self.assertRaises(GitHubAPIError):
            get_pull_request("nonexistent", "nonexistent", 1, self.github_token)
        
        print(f"   ✅ PR error handling working correctly")
        
        self._log_test_result("pr_errors", {"error_handling": "passed"})

    # ==================== INTEGRATION TESTS ====================
    
    def test_end_to_end_development_workflow(self):
        """Test complete end-to-end development workflow."""
        print(f"\n🔄 Testing complete end-to-end development workflow")
        
        workflow_steps = []
        
        try:
            # Step 1: Create private repository
            repo_name = f"e2e_test_{self.test_timestamp}"
            create_result = create_github_repository(
                name=repo_name,
                private=True,
                description="End-to-end workflow test repository",
                github_token=self.github_token,
                auto_init=True,
                gitignore_template="Python"
            )
            
            repo_info = create_result["repository"]
            owner = repo_info["full_name"].split('/')[0]
            clone_url = repo_info["clone_url"]
            
            # Track for cleanup
            self.test_repositories.append({'owner': owner, 'name': repo_name})
            workflow_steps.append("✅ Repository created")
            
            # Step 2: Clone repository
            local_repo_path = os.path.join(self.test_dir, "e2e_test_repo")
            clone_success = clone_repository(clone_url, local_repo_path)
            self.assertTrue(clone_success)
            workflow_steps.append("✅ Repository cloned")
            
            # Step 3: Create feature branch
            feature_branch = "feature/e2e-test-feature"
            create_branch(feature_branch, local_repo_path)
            workflow_steps.append("✅ Feature branch created")
            
            # Step 4: Create multiple files and commit
            files_to_create = [
                ("src/__init__.py", "# Package initialization"),
                ("src/main.py", "def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()"),
                ("tests/__init__.py", "# Test package initialization"),
                ("tests/test_main.py", "import unittest\n\ndef test_main():\n    assert True"),
                ("README.md", f"# E2E Test Repository\n\nCreated: {datetime.now().isoformat()}\n\nThis is a test repository for end-to-end workflow validation."),
                ("requirements.txt", "# No requirements for this test project")
            ]
            
            for file_path, content in files_to_create:
                full_path = os.path.join(local_repo_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
            
            # Add all files
            file_names = [fp for fp, _ in files_to_create]
            add_success = add_files(file_names, local_repo_path)
            self.assertTrue(add_success)
            
            # Commit changes
            commit_message = "Add complete project structure for E2E testing\n\n- Add src package with main module\n- Add tests package with test module\n- Add README and requirements.txt\n\nThis commit demonstrates a realistic development workflow."
            commit_success = commit_changes(commit_message, local_repo_path)
            self.assertTrue(commit_success)
            workflow_steps.append("✅ Files created and committed")
            
            # Step 5: Push feature branch
            push_success = push_changes("origin", feature_branch, local_repo_path)
            self.assertTrue(push_success)
            workflow_steps.append("✅ Feature branch pushed")
            
            # Step 6: Create pull request
            pr_title = "Add complete project structure for E2E testing"
            pr_body = f"""This PR adds a complete project structure to demonstrate end-to-end workflow capabilities.

## Changes Made

### Project Structure
- `src/` - Main source code package
  - `__init__.py` - Package initialization
  - `main.py` - Main application module
- `tests/` - Test package
  - `__init__.py` - Test package initialization  
  - `test_main.py` - Basic test module
- `README.md` - Project documentation
- `requirements.txt` - Python dependencies

### Features Demonstrated
- ✅ Repository creation via GitHub API
- ✅ Local Git operations (clone, branch, commit, push)
- ✅ Multi-file project structure
- ✅ Comprehensive commit messages
- ✅ Pull request creation via GitHub API

**Created by automated E2E test at:** {datetime.now().isoformat()}

This PR validates the complete development workflow from repository creation to pull request submission."""
            
            pr_result = create_pull_request(
                repo_owner=owner,
                repo_name=repo_name,
                head_branch=feature_branch,
                base_branch="main",
                title=pr_title,
                body=pr_body,
                github_token=self.github_token
            )
            
            self.assertTrue(pr_result["success"])
            pr_number = pr_result["pull_request"]["number"]
            workflow_steps.append(f"✅ Pull request #{pr_number} created")
            
            # Step 7: Verify pull request
            pr_details = get_pull_request(owner, repo_name, pr_number, self.github_token)
            self.assertEqual(pr_details["state"], "open")
            self.assertGreater(pr_details["commits"], 0)
            self.assertGreater(pr_details["changed_files"], 0)
            workflow_steps.append("✅ Pull request verified")
            
            # Step 8: Verify repository status
            repo_status = get_status(local_repo_path)
            self.assertTrue(repo_status["clean"])  # Should be clean after push
            workflow_steps.append("✅ Repository status verified")
            
            # Final workflow result
            final_result = {
                "repository": {
                    "name": repo_name,
                    "full_name": repo_info["full_name"],
                    "url": repo_info["html_url"],
                    "private": repo_info["private"]
                },
                "pull_request": {
                    "number": pr_number,
                    "title": pr_title,
                    "url": pr_result["pull_request"]["html_url"],
                    "commits": pr_details["commits"],
                    "changed_files": pr_details["changed_files"],
                    "additions": pr_details["additions"],
                    "deletions": pr_details["deletions"]
                },
                "workflow_steps": workflow_steps,
                "files_created": len(files_to_create),
                "local_path": local_repo_path,
                "test_duration": "completed_successfully"
            }
            
            print(f"\n📊 E2E Workflow Summary:")
            for step in workflow_steps:
                print(f"   {step}")
            print(f"   📋 PR #{pr_number}: {pr_result['pull_request']['html_url']}")
            
            self._log_test_result("end_to_end_development_workflow", final_result)
            
        except Exception as e:
            workflow_steps.append(f"❌ Error: {str(e)}")
            self._log_test_result("end_to_end_development_workflow", {
                "error": str(e),
                "completed_steps": workflow_steps
            }, success=False)
            raise

    # ==================== COMPREHENSIVE SUMMARY TEST ====================
    
    def test_generate_comprehensive_report(self):
        """Generate a comprehensive report of all test results."""
        print(f"\n📊 Generating comprehensive test report")
        
        # Collect all test logs
        log_files = list(self.output_dir.glob(f"*_{self.test_timestamp}.json"))
        
        report = {
            "test_session": {
                "timestamp": self.test_timestamp,
                "total_tests": len(log_files),
                "output_directory": str(self.output_dir),
                "github_integration": True,
                "git_available": check_git_availability()
            },
            "repositories_created": len(self.test_repositories),
            "test_results": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        # Process each test log
        import json
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    test_data = json.load(f)
                    report["test_results"].append(test_data)
                    
                    if test_data.get("success", False):
                        report["summary"]["passed"] += 1
                    else:
                        report["summary"]["failed"] += 1
                        
            except Exception as e:
                print(f"Warning: Could not process {log_file}: {e}")
        
        # Add repository information
        report["created_repositories"] = [
            {
                "name": f"{repo['owner']}/{repo['name']}",
                "owner": repo["owner"],
                "repository": repo["name"]
            } for repo in self.test_repositories
        ]
        
        # Save comprehensive report
        report_file = self.output_dir / f"comprehensive_test_report_{self.test_timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown summary
        summary_md = self.output_dir / f"TEST_SUMMARY_{self.test_timestamp}.md"
        with open(summary_md, 'w') as f:
            f.write(f"""# GitHub Operations Test Summary

**Test Session:** {self.test_timestamp}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Summary
- ✅ **Passed:** {report["summary"]["passed"]}
- ❌ **Failed:** {report["summary"]["failed"]}  
- ⏭️ **Skipped:** {report["summary"]["skipped"]}
- 📁 **Repositories Created:** {report["repositories_created"]}

## Created Test Repositories
""")
            
            for repo in report["created_repositories"]:
                f.write(f"- [{repo['name']}](https://github.com/{repo['name']})\n")
            
            f.write(f"""
## Test Coverage Verified
- [x] GitHub repository creation (private and public)
- [x] Pull request creation and management  
- [x] Complete end-to-end development workflow
- [x] Error handling and edge cases
- [x] Integration with local Git operations

## Output Files
- Comprehensive Report: `{report_file.name}`
- Individual Test Logs: `{len(log_files)} files`
- Output Directory: `{self.output_dir}`

## Notes
This test suite validates all GitHub API operations with real GitHub integration,
following the project's test-driven development approach with no mocks.
All test resources are automatically cleaned up after test completion.
""")
        
        print(f"   📋 Generated comprehensive report: {report_file}")
        print(f"   📝 Generated summary: {summary_md}")
        print(f"\n📊 Test Session Summary:")
        print(f"   ✅ Passed: {report['summary']['passed']}")
        print(f"   ❌ Failed: {report['summary']['failed']}")
        print(f"   📁 Repositories: {report['repositories_created']}")
        
        self.assertGreater(report["summary"]["passed"], 0, "At least some tests should pass")


if __name__ == '__main__':
    # Configure test runner for comprehensive output
    print("="*80)
    print("COMPREHENSIVE GITHUB OPERATIONS TEST SUITE")
    print("="*80)
    print("This test suite validates all GitHub API operations with real integration.")
    print("Ensure GITHUB_TOKEN environment variable is set with appropriate permissions.")
    print("="*80)
    
    unittest.main(verbosity=2, buffer=False)
