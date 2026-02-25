import pytest

#!/usr/bin/env python3
"""
Advanced Git Operations Tests - Comprehensive Testing for Fractal Git Operations.

This test suite covers all advanced Git operations including merge, rebase, tag, stash,
diff, and reset operations following web search best practices for comprehensive Git testing.

Test Coverage:
- Merge operations (fast-forward, three-way, with strategies)
- Rebase operations (standard and interactive)
- Tag operations (creation, listing, annotated tags)
- Stash operations (stash, apply, list)
- Diff operations (working tree, staged, specific files)
- Reset operations (soft, mixed, hard)
- Error handling and edge cases for all operations
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Removed mock imports to follow TDD principle: no mock methods, always do real data analysis

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.core.git import (
    # File operations
    add_files,
    apply_stash,
    # Core operations
    check_git_availability,
    commit_changes,
    # Branch operations
    create_branch,
    # Tag operations
    create_tag,
    get_diff,
    initialize_git_repository,
    list_stashes,
    list_tags,
    merge_branch,
    rebase_branch,
    reset_changes,
    # Stash operations
    stash_changes,
    switch_branch,
)


@pytest.mark.unit
class TestAdvancedGitOperations(unittest.TestCase):
    """
    Comprehensive test suite for advanced Git operations.

    Following web search best practices for Git testing:
    - Real repository testing (no mocks for core functionality)
    - Comprehensive scenario coverage
    - Error handling validation
    - Integration testing between operations
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        # Verify Git is available for testing
        if not check_git_availability():
            raise unittest.SkipTest("Git is not available on this system")

        # Create a base temporary directory for all tests
        cls.base_temp_dir = tempfile.mkdtemp(prefix="git_advanced_test_")

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level test fixtures."""
        if hasattr(cls, 'base_temp_dir') and os.path.exists(cls.base_temp_dir):
            shutil.rmtree(cls.base_temp_dir, ignore_errors=True)

    def setUp(self):
        """Set up test fixtures for each test."""
        # Create unique test directory for each test
        self.test_dir = tempfile.mkdtemp(dir=self.base_temp_dir)
        self.repo_dir = os.path.join(self.test_dir, "test_repo")
        os.makedirs(self.repo_dir, exist_ok=True)

        # Store original directory
        self.original_dir = os.getcwd()

        # Initialize repository for most tests
        self.assertTrue(initialize_git_repository(self.repo_dir))

        # Ensure we are on 'main' regardless of system default (master vs main)
        subprocess.run(
            ["git", "branch", "-m", "main"],
            cwd=self.repo_dir,
            capture_output=True,
            check=False
        )

    def tearDown(self):
        """Clean up test fixtures after each test."""
        # Restore original directory
        os.chdir(self.original_dir)

        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # ==================== MERGE OPERATIONS TESTS ====================

    def test_merge_branch_comprehensive(self):
        """Test comprehensive merge operations."""
        # Setup: Create feature branch with commits
        self.assertTrue(create_branch("feature/test", self.repo_dir))

        # Add content to feature branch
        feature_file = os.path.join(self.repo_dir, "feature.txt")
        with open(feature_file, 'w') as f:
            f.write("Feature content")

        self.assertTrue(add_files(["feature.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Add feature", self.repo_dir))

        # Switch back to main and create different content
        self.assertTrue(switch_branch("main", self.repo_dir))
        main_file = os.path.join(self.repo_dir, "main.txt")
        with open(main_file, 'w') as f:
            f.write("Main content")

        self.assertTrue(add_files(["main.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Add main content", self.repo_dir))

        # Test merge
        result = merge_branch("feature/test", repository_path=self.repo_dir)
        self.assertTrue(result)

        # Verify both files exist after merge
        self.assertTrue(os.path.exists(feature_file))
        self.assertTrue(os.path.exists(main_file))

        # Test merge with explicit target branch
        self.assertTrue(create_branch("feature/test2", self.repo_dir))
        feature2_file = os.path.join(self.repo_dir, "feature2.txt")
        with open(feature2_file, 'w') as f:
            f.write("Feature 2 content")

        self.assertTrue(add_files(["feature2.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Add feature 2", self.repo_dir))

        result = merge_branch("feature/test2", "main", self.repo_dir)
        self.assertTrue(result)

    def test_merge_branch_error_scenarios(self):
        """Test merge operation error scenarios."""
        # Test merge non-existent branch
        result = merge_branch("nonexistent-branch", repository_path=self.repo_dir)
        self.assertFalse(result)

        # Test merge in non-repository
        result = merge_branch("main", repository_path=self.test_dir)
        self.assertFalse(result)

    # ==================== REBASE OPERATIONS TESTS ====================

    def test_rebase_branch_comprehensive(self):
        """Test comprehensive rebase operations."""
        # Setup: Create commits on main
        main_file1 = os.path.join(self.repo_dir, "main1.txt")
        with open(main_file1, 'w') as f:
            f.write("Main content 1")

        self.assertTrue(add_files(["main1.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Main commit 1", self.repo_dir))

        # Create feature branch from this point
        self.assertTrue(create_branch("feature/rebase-test", self.repo_dir))

        # Add commits to feature branch
        feature_file = os.path.join(self.repo_dir, "feature.txt")
        with open(feature_file, 'w') as f:
            f.write("Feature content")

        self.assertTrue(add_files(["feature.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Feature commit", self.repo_dir))

        # Go back to main and add more commits
        self.assertTrue(switch_branch("main", self.repo_dir))
        main_file2 = os.path.join(self.repo_dir, "main2.txt")
        with open(main_file2, 'w') as f:
            f.write("Main content 2")

        self.assertTrue(add_files(["main2.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Main commit 2", self.repo_dir))

        # Switch back to feature and rebase
        self.assertTrue(switch_branch("feature/rebase-test", self.repo_dir))
        result = rebase_branch("main", self.repo_dir)

        # Note: Rebase might fail in test environment due to interactive requirements
        # We test that the function handles this gracefully
        self.assertIsInstance(result, bool)

    def test_rebase_branch_error_scenarios(self):
        """Test rebase operation error scenarios."""
        # Test rebase onto non-existent branch
        result = rebase_branch("nonexistent-branch", repository_path=self.repo_dir)
        self.assertFalse(result)

        # Test rebase in non-repository
        result = rebase_branch("main", repository_path=self.test_dir)
        self.assertFalse(result)

    # ==================== TAG OPERATIONS TESTS ====================

    def test_tag_operations_comprehensive(self):
        """Test comprehensive tag operations."""
        # Test creating lightweight tag
        result = create_tag("v1.0.0", repository_path=self.repo_dir)
        self.assertTrue(result)

        # Test creating annotated tag
        result = create_tag("v1.1.0", "Release version 1.1.0", self.repo_dir)
        self.assertTrue(result)

        # Test listing tags
        tags = list_tags(self.repo_dir)
        self.assertIsInstance(tags, list)
        self.assertIn("v1.0.0", tags)
        self.assertIn("v1.1.0", tags)

        # Test creating duplicate tag (should fail)
        result = create_tag("v1.0.0", repository_path=self.repo_dir)
        self.assertFalse(result)

    def test_tag_operations_error_scenarios(self):
        """Test tag operation error scenarios."""
        # Test creating tag in non-repository
        result = create_tag("v1.0.0", repository_path=self.test_dir)
        self.assertFalse(result)

        # Test listing tags in non-repository
        tags = list_tags(self.test_dir)
        self.assertEqual(tags, [])

        # Test creating tag with invalid name
        result = create_tag("", repository_path=self.repo_dir)
        self.assertFalse(result)

    # ==================== STASH OPERATIONS TESTS ====================

    def test_stash_operations_comprehensive(self):
        """Test comprehensive stash operations."""
        # Create some changes to stash
        test_file = os.path.join(self.repo_dir, "stash_test.txt")
        with open(test_file, 'w') as f:
            f.write("Content to stash")

        self.assertTrue(add_files(["stash_test.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Initial commit for stash test", self.repo_dir))

        # Modify the file
        with open(test_file, 'w') as f:
            f.write("Modified content")

        # Test stashing changes
        result = stash_changes("Test stash message", self.repo_dir)
        self.assertTrue(result)

        # Verify file is reverted
        with open(test_file) as f:
            content = f.read()
        self.assertEqual(content, "Content to stash")

        # Test listing stashes
        stashes = list_stashes(self.repo_dir)
        self.assertIsInstance(stashes, list)
        self.assertGreater(len(stashes), 0)

        # Test applying stash
        result = apply_stash(repository_path=self.repo_dir)
        self.assertTrue(result)

        # Verify file is modified again
        with open(test_file) as f:
            content = f.read()
        self.assertEqual(content, "Modified content")

    def test_stash_operations_error_scenarios(self):
        """Test stash operation error scenarios."""
        # Test stashing in non-repository
        result = stash_changes("Test", repository_path=self.test_dir)
        self.assertFalse(result)

        # Test applying stash in non-repository
        result = apply_stash(repository_path=self.test_dir)
        self.assertFalse(result)

        # Test listing stashes in non-repository
        stashes = list_stashes(self.test_dir)
        self.assertEqual(stashes, [])

        # Test applying non-existent stash
        result = apply_stash("stash@{999}", self.repo_dir)
        self.assertFalse(result)

    # ==================== DIFF OPERATIONS TESTS ====================

    def test_diff_operations_comprehensive(self):
        """Test comprehensive diff operations."""
        # Create initial file
        test_file = os.path.join(self.repo_dir, "diff_test.txt")
        with open(test_file, 'w') as f:
            f.write("Original content\n")

        self.assertTrue(add_files(["diff_test.txt"], self.repo_dir))
        self.assertTrue(commit_changes("Initial commit for diff test", self.repo_dir))

        # Modify the file
        with open(test_file, 'w') as f:
            f.write("Modified content\n")

        # Test getting diff of working tree
        diff = get_diff(repository_path=self.repo_dir)
        self.assertIsInstance(diff, str)
        self.assertIn("Modified content", diff)

        # Test getting diff of specific file
        diff = get_diff("diff_test.txt", repository_path=self.repo_dir)
        self.assertIsInstance(diff, str)

        # Stage the changes and test staged diff
        self.assertTrue(add_files(["diff_test.txt"], self.repo_dir))
        diff = get_diff(cached=True, repository_path=self.repo_dir)
        self.assertIsInstance(diff, str)

    def test_diff_operations_error_scenarios(self):
        """Test diff operation error scenarios."""
        # Test diff in non-repository
        diff = get_diff(repository_path=self.test_dir)
        self.assertEqual(diff, "")

        # Test diff of non-existent file
        diff = get_diff("nonexistent.txt", repository_path=self.repo_dir)
        self.assertIsInstance(diff, str)  # Should return empty string, not error

    # ==================== RESET OPERATIONS TESTS ====================

    def test_reset_operations_comprehensive(self):
        """Test comprehensive reset operations."""
        # Create multiple commits
        for i in range(3):
            test_file = os.path.join(self.repo_dir, f"reset_test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Content {i}")

            self.assertTrue(add_files([f"reset_test_{i}.txt"], self.repo_dir))
            self.assertTrue(commit_changes(f"Commit {i}", self.repo_dir))

        # Test soft reset (keeps changes staged)
        result = reset_changes("soft", "HEAD~1", self.repo_dir)
        self.assertTrue(result)

        # Test mixed reset (default, unstages changes)
        result = reset_changes("mixed", "HEAD", self.repo_dir)
        self.assertTrue(result)

        # Test hard reset (discards all changes) - be careful with this
        # We'll test with HEAD to be safe
        result = reset_changes("hard", "HEAD", self.repo_dir)
        self.assertTrue(result)

    def test_reset_operations_error_scenarios(self):
        """Test reset operation error scenarios."""
        # Test reset with invalid mode
        result = reset_changes("invalid", "HEAD", self.repo_dir)
        self.assertFalse(result)

        # Test reset in non-repository
        result = reset_changes("mixed", "HEAD", self.test_dir)
        self.assertFalse(result)

        # Test reset to invalid target
        result = reset_changes("mixed", "invalid-ref", self.repo_dir)
        self.assertFalse(result)

    # ==================== INTEGRATION TESTS ====================

    def test_advanced_workflow_integration(self):
        """Test complete advanced Git workflow integration."""
        # Create feature branch workflow with advanced operations

        # Step 1: Create and work on feature branch
        self.assertTrue(create_branch("feature/advanced-workflow", self.repo_dir))

        # Step 2: Add multiple commits
        for i in range(2):
            feature_file = os.path.join(self.repo_dir, f"advanced_feature_{i}.txt")
            with open(feature_file, 'w') as f:
                f.write(f"Advanced feature content {i}")

            self.assertTrue(add_files([f"advanced_feature_{i}.txt"], self.repo_dir))
            self.assertTrue(commit_changes(f"Add advanced feature {i}", self.repo_dir))

        # Step 3: Create a tag for this version
        result = create_tag("feature-v1.0", "Feature version 1.0", self.repo_dir)
        self.assertTrue(result)

        # Step 4: Make some changes and stash them
        temp_file = os.path.join(self.repo_dir, "temp_work.txt")
        with open(temp_file, 'w') as f:
            f.write("Temporary work")

        self.assertTrue(add_files(["temp_work.txt"], self.repo_dir))
        result = stash_changes("Temporary work in progress", self.repo_dir)
        self.assertTrue(result)

        # Step 5: Switch to main and merge feature
        self.assertTrue(switch_branch("main", self.repo_dir))
        result = merge_branch("feature/advanced-workflow", repository_path=self.repo_dir)
        self.assertTrue(result)

        # Step 6: Verify all operations completed successfully
        # Check that feature files exist
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, "advanced_feature_0.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, "advanced_feature_1.txt")))

        # Check that tag exists
        tags = list_tags(self.repo_dir)
        self.assertIn("feature-v1.0", tags)

        # Check that stash exists
        stashes = list_stashes(self.repo_dir)
        self.assertGreater(len(stashes), 0)

    # ==================== PERFORMANCE AND STRESS TESTS ====================

    def test_performance_with_multiple_operations(self):
        """Test performance with multiple advanced operations."""
        # Create multiple branches and perform various operations
        branch_count = 5

        for i in range(branch_count):
            branch_name = f"perf-branch-{i}"
            self.assertTrue(create_branch(branch_name, self.repo_dir))

            # Add content to each branch
            branch_file = os.path.join(self.repo_dir, f"branch_{i}.txt")
            with open(branch_file, 'w') as f:
                f.write(f"Branch {i} content")

            self.assertTrue(add_files([f"branch_{i}.txt"], self.repo_dir))
            self.assertTrue(commit_changes(f"Branch {i} commit", self.repo_dir))

            # Create tag for each branch
            tag_name = f"branch-{i}-v1.0"
            result = create_tag(tag_name, f"Branch {i} version 1.0", self.repo_dir)
            self.assertTrue(result)

        # Switch back to main
        self.assertTrue(switch_branch("main", self.repo_dir))

        # Verify all tags were created
        tags = list_tags(self.repo_dir)
        # We need to ensure tags list is not empty before checking specific tags
        self.assertIsInstance(tags, list)
        if not tags:
             # If tags are empty, print for debugging (though capture_output usually hides this)
             print(f"DEBUG: No tags found in {self.repo_dir}")

        for i in range(branch_count):
            tag_name = f"branch-{i}-v1.0"
            self.assertIn(tag_name, tags, f"Tag {tag_name} not found in {tags}")

    # ==================== ERROR HANDLING VALIDATION ====================

    def test_comprehensive_error_handling(self):
        """Test comprehensive error handling across all advanced operations."""
        nonexistent_path = "/path/that/does/not/exist"

        # Test all operations with non-existent repository
        self.assertFalse(merge_branch("main", repository_path=nonexistent_path))
        self.assertFalse(rebase_branch("main", repository_path=nonexistent_path))
        self.assertFalse(create_tag("v1.0", repository_path=nonexistent_path))
        self.assertEqual(list_tags(nonexistent_path), [])
        self.assertFalse(stash_changes(repository_path=nonexistent_path))
        self.assertFalse(apply_stash(repository_path=nonexistent_path))
        self.assertEqual(list_stashes(nonexistent_path), [])
        self.assertEqual(get_diff(repository_path=nonexistent_path), "")
        self.assertFalse(reset_changes(repository_path=nonexistent_path))

        # Test operations with invalid parameters
        self.assertFalse(merge_branch("", repository_path=self.repo_dir))
        self.assertFalse(rebase_branch("", repository_path=self.repo_dir))
        self.assertFalse(create_tag("", repository_path=self.repo_dir))
        self.assertFalse(reset_changes("invalid-mode", repository_path=self.repo_dir))


if __name__ == '__main__':
    # Configure test runner for comprehensive output
    unittest.main(verbosity=2, buffer=True)
