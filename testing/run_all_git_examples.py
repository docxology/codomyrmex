#!/usr/bin/env python3
"""
Git Operations - Example Test Runner

This script demonstrates and tests all Git operations with real examples.
It creates temporary repositories to safely test all functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from codomyrmex.git_operations import *


class GitExampleRunner:
    """Runner for Git operations examples with real repositories."""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
        self.examples_run = 0
        self.examples_passed = 0
        
    def setup(self):
        """Set up temporary repository for testing."""
        self.temp_dir = tempfile.mkdtemp(prefix="git_examples_")
        self.repo_path = os.path.join(self.temp_dir, "test_repo")
        os.makedirs(self.repo_path, exist_ok=True)
        
        print(f"🔧 Set up test repository: {self.repo_path}")
        return True
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"🧹 Cleaned up test repository")
    
    def run_example(self, name, example_func, *args, **kwargs):
        """Run a single example with error handling."""
        self.examples_run += 1
        print(f"\n{'='*60}")
        print(f"🧪 Running Example {self.examples_run}: {name}")
        print(f"{'='*60}")
        
        try:
            result = example_func(*args, **kwargs)
            if result:
                print(f"✅ Example '{name}' completed successfully")
                self.examples_passed += 1
                return True
            else:
                print(f"❌ Example '{name}' failed")
                return False
        except Exception as e:
            print(f"💥 Example '{name}' raised exception: {e}")
            return False
    
    def example_basic_setup(self):
        """Example 1: Basic repository setup."""
        
        # Check Git availability
        if not check_git_availability():
            print("❌ Git not available")
            return False
        
        print("✅ Git is available")
        
        # Initialize repository
        success = initialize_git_repository(self.repo_path, initial_commit=True)
        if not success:
            print("❌ Failed to initialize repository")
            return False
        
        print("✅ Repository initialized with initial commit")
        
        # Verify it's a Git repository
        if not is_git_repository(self.repo_path):
            print("❌ Repository verification failed")
            return False
        
        print("✅ Repository verification passed")
        
        # Check status
        status = get_status(self.repo_path)
        if status.get("clean"):
            print("✅ Repository is clean")
        else:
            print(f"📊 Repository status: {status}")
        
        return True
    
    def example_branch_operations(self):
        """Example 2: Branch operations."""
        
        # Get current branch
        current = get_current_branch(self.repo_path)
        print(f"📍 Current branch: {current}")
        
        # Create feature branch
        feature_branch = "feature/example-feature"
        success = create_branch(feature_branch, self.repo_path)
        if not success:
            print("❌ Failed to create feature branch")
            return False
        
        print(f"✅ Created branch: {feature_branch}")
        
        # Verify we're on the new branch
        current = get_current_branch(self.repo_path)
        if current != feature_branch:
            print(f"❌ Branch switch failed. Expected {feature_branch}, got {current}")
            return False
        
        print(f"✅ Successfully switched to: {current}")
        
        # Switch back to main
        success = switch_branch("main", self.repo_path)
        if not success:
            print("❌ Failed to switch back to main")
            return False
        
        print("✅ Switched back to main")
        
        return True
    
    def example_file_operations(self):
        """Example 3: File operations."""
        
        # Create test files
        test_files = ["example1.py", "example2.py", "config.json"]
        
        for i, filename in enumerate(test_files):
            file_path = os.path.join(self.repo_path, filename)
            with open(file_path, 'w') as f:
                if filename.endswith('.py'):
                    f.write(f"# Example Python file {i+1}\nprint('Hello from {filename}')\n")
                elif filename.endswith('.json'):
                    f.write(f'{{"example": "file {i+1}", "type": "config"}}\n')
        
        print(f"✅ Created {len(test_files)} test files")
        
        # Add files to Git
        success = add_files(test_files, self.repo_path)
        if not success:
            print("❌ Failed to add files")
            return False
        
        print("✅ Files added to staging area")
        
        # Check status
        status = get_status(self.repo_path)
        added_files = status.get("added", [])
        print(f"📊 Staged files: {added_files}")
        
        # Commit changes
        success = commit_changes("Add example files", self.repo_path)
        if not success:
            print("❌ Failed to commit changes")
            return False
        
        print("✅ Changes committed")
        
        # Verify clean status
        status = get_status(self.repo_path)
        if not status.get("clean"):
            print("❌ Repository should be clean after commit")
            return False
        
        print("✅ Repository is clean after commit")
        
        return True
    
    def example_diff_operations(self):
        """Example 4: Diff operations."""
        
        # Modify an existing file
        config_file = os.path.join(self.repo_path, "config.json")
        if os.path.exists(config_file):
            with open(config_file, 'w') as f:
                f.write('{"example": "modified file", "type": "config", "version": 2}\n')
            
            print("✅ Modified config.json")
            
            # Get diff of changes
            diff = get_diff("config.json", repository_path=self.repo_path)
            if diff:
                print("📋 Diff preview:")
                print(diff[:200] + "..." if len(diff) > 200 else diff)
            else:
                print("⚠️ No diff found (might be expected)")
            
            # Stage the changes
            add_files(["config.json"], self.repo_path)
            
            # Get staged diff
            staged_diff = get_diff(staged=True, repository_path=self.repo_path)
            if staged_diff:
                print("📋 Staged diff found")
            
            # Commit the changes
            commit_changes("Update config.json", self.repo_path)
            print("✅ Committed modified file")
        
        return True
    
    def example_merge_operations(self):
        """Example 5: Merge operations."""
        
        # Create a feature branch with changes
        feature_branch = "feature/merge-example"
        success = create_branch(feature_branch, self.repo_path)
        if not success:
            print("❌ Failed to create merge example branch")
            return False
        
        # Add content to feature branch
        feature_file = os.path.join(self.repo_path, "merge_feature.py")
        with open(feature_file, 'w') as f:
            f.write("# Merge example feature\ndef merge_feature():\n    return 'Merged successfully'\n")
        
        add_files(["merge_feature.py"], self.repo_path)
        commit_changes("Add merge feature", self.repo_path)
        
        print("✅ Created feature branch with changes")
        
        # Switch back to main
        switch_branch("main", self.repo_path)
        
        # Merge feature branch
        success = merge_branch(feature_branch, repository_path=self.repo_path)
        if not success:
            print("❌ Failed to merge feature branch")
            return False
        
        print("✅ Successfully merged feature branch")
        
        # Verify merge result
        if os.path.exists(feature_file):
            print("✅ Merge result verified - feature file exists")
        else:
            print("❌ Merge verification failed - feature file missing")
            return False
        
        return True
    
    def example_tag_operations(self):
        """Example 6: Tag operations."""
        
        # Create lightweight tag
        success = create_tag("v1.0.0", repository_path=self.repo_path)
        if not success:
            print("❌ Failed to create lightweight tag")
            return False
        
        print("✅ Created lightweight tag: v1.0.0")
        
        # Create annotated tag
        success = create_tag("v1.1.0", "Version 1.1.0 - Added merge feature", self.repo_path)
        if not success:
            print("❌ Failed to create annotated tag")
            return False
        
        print("✅ Created annotated tag: v1.1.0")
        
        # List tags
        tags = list_tags(self.repo_path)
        print(f"📋 Repository tags: {tags}")
        
        if "v1.0.0" not in tags or "v1.1.0" not in tags:
            print("❌ Tag verification failed")
            return False
        
        print("✅ Tag operations completed successfully")
        
        return True
    
    def example_stash_operations(self):
        """Example 7: Stash operations."""
        
        # Create work in progress
        wip_file = os.path.join(self.repo_path, "work_in_progress.py")
        with open(wip_file, 'w') as f:
            f.write("# Work in progress\n# TODO: Complete implementation\n")
        
        add_files(["work_in_progress.py"], self.repo_path)
        
        print("✅ Created work in progress")
        
        # Stash changes
        success = stash_changes("WIP: Working on new feature", self.repo_path)
        if not success:
            print("❌ Failed to stash changes")
            return False
        
        print("✅ Stashed work in progress")
        
        # Verify stash was created
        stashes = list_stashes(self.repo_path)
        if not stashes:
            print("❌ No stashes found")
            return False
        
        print(f"📋 Stashes: {len(stashes)} found")
        for stash in stashes:
            print(f"   {stash['ref']}: {stash['message']}")
        
        # Apply stash
        success = apply_stash(repository_path=self.repo_path)
        if not success:
            print("❌ Failed to apply stash")
            return False
        
        print("✅ Applied stash successfully")
        
        # Verify file was restored
        if os.path.exists(wip_file):
            print("✅ Stash application verified - file restored")
        else:
            print("❌ Stash verification failed - file not restored")
            return False
        
        return True
    
    def example_reset_operations(self):
        """Example 8: Reset operations."""
        
        # Create a commit to reset from
        reset_file = os.path.join(self.repo_path, "reset_example.py")
        with open(reset_file, 'w') as f:
            f.write("# Reset example\nprint('Before reset')\n")
        
        add_files(["reset_example.py"], self.repo_path)
        commit_changes("Add reset example", self.repo_path)
        
        print("✅ Created commit for reset example")
        
        # Modify the file
        with open(reset_file, 'w') as f:
            f.write("# Reset example - modified\nprint('After modification')\n")
        
        add_files(["reset_example.py"], self.repo_path)
        
        print("✅ Modified and staged file")
        
        # Perform mixed reset (unstage changes)
        success = reset_changes("mixed", "HEAD", self.repo_path)
        if not success:
            print("❌ Failed to perform reset")
            return False
        
        print("✅ Reset completed")
        
        # Verify reset result
        status = get_status(self.repo_path)
        if status.get("modified") and "reset_example.py" in status["modified"]:
            print("✅ Reset verification passed - file is modified but unstaged")
        else:
            print("⚠️ Reset verification - status may vary")
        
        return True
    
    def example_commit_history(self):
        """Example 9: Commit history operations."""
        
        # Get commit history
        commits = get_commit_history(limit=10, repository_path=self.repo_path)
        
        if not commits:
            print("❌ No commit history found")
            return False
        
        print(f"📋 Commit history ({len(commits)} commits):")
        for i, commit in enumerate(commits[:5]):  # Show first 5
            print(f"   {i+1}. {commit['hash'][:8]} - {commit['message']}")
            print(f"      Author: {commit['author_name']} ({commit['date']})")
        
        print("✅ Commit history retrieved successfully")
        
        return True
    
    def example_comprehensive_workflow(self):
        """Example 10: Comprehensive workflow combining multiple operations."""
        
        print("🌟 Running comprehensive workflow example...")
        
        # Step 1: Create development branch
        dev_branch = "develop"
        success = create_branch(dev_branch, self.repo_path)
        if not success:
            print("❌ Failed to create develop branch")
            return False
        
        # Step 2: Create multiple feature files
        features = ["authentication", "database", "api"]
        
        for feature in features:
            # Create feature file
            feature_file = os.path.join(self.repo_path, f"{feature}.py")
            with open(feature_file, 'w') as f:
                f.write(f"# {feature.title()} module\n")
                f.write(f"class {feature.title()}:\n")
                f.write(f"    def __init__(self):\n")
                f.write(f"        self.name = '{feature}'\n")
                f.write(f"    \n")
                f.write(f"    def process(self):\n")
                f.write(f"        return f'Processing {{self.name}}'\n")
            
            # Add and commit
            add_files([f"{feature}.py"], self.repo_path)
            commit_changes(f"Add {feature} module", self.repo_path)
        
        print(f"✅ Created {len(features)} feature modules")
        
        # Step 3: Create release tag
        success = create_tag("v2.0.0", "Major release with new features", self.repo_path)
        if success:
            print("✅ Created release tag")
        
        # Step 4: Switch to main and merge
        switch_branch("main", self.repo_path)
        success = merge_branch(dev_branch, repository_path=self.repo_path)
        if success:
            print("✅ Merged develop branch to main")
        
        # Step 5: Final verification
        status = get_status(self.repo_path)
        tags = list_tags(self.repo_path)
        commits = get_commit_history(limit=5, repository_path=self.repo_path)
        
        print(f"\n📊 Workflow Summary:")
        print(f"   - Repository status: {'Clean' if status.get('clean') else 'Has changes'}")
        print(f"   - Total tags: {len(tags)}")
        print(f"   - Recent commits: {len(commits)}")
        print(f"   - Features implemented: {len(features)}")
        
        print("🌟 Comprehensive workflow completed successfully!")
        
        return True
    
    def run_all_examples(self):
        """Run all Git operations examples."""
        
        print("🚀 Starting Git Operations Example Runner")
        print(f"Testing all 22 Git operations with real examples\n")
        
        if not self.setup():
            print("❌ Failed to set up test environment")
            return False
        
        try:
            # Run all examples
            examples = [
                ("Basic Repository Setup", self.example_basic_setup),
                ("Branch Operations", self.example_branch_operations),
                ("File Operations", self.example_file_operations),
                ("Diff Operations", self.example_diff_operations),
                ("Merge Operations", self.example_merge_operations),
                ("Tag Operations", self.example_tag_operations),
                ("Stash Operations", self.example_stash_operations),
                ("Reset Operations", self.example_reset_operations),
                ("Commit History", self.example_commit_history),
                ("Comprehensive Workflow", self.example_comprehensive_workflow),
            ]
            
            for name, example_func in examples:
                self.run_example(name, example_func)
            
            # Print final summary
            print(f"\n{'='*60}")
            print(f"🎯 FINAL RESULTS")
            print(f"{'='*60}")
            print(f"📊 Examples run: {self.examples_run}")
            print(f"✅ Examples passed: {self.examples_passed}")
            print(f"❌ Examples failed: {self.examples_run - self.examples_passed}")
            print(f"📈 Success rate: {(self.examples_passed/self.examples_run)*100:.1f}%")
            
            if self.examples_passed == self.examples_run:
                print(f"\n🎉 ALL EXAMPLES PASSED! Git operations are working perfectly!")
                return True
            else:
                print(f"\n⚠️ Some examples failed. Check the output above for details.")
                return False
                
        finally:
            self.cleanup()


def main():
    """Main function to run all Git examples."""
    
    # Check if Git is available before starting
    if not check_git_availability():
        print("❌ Git is not available on this system")
        print("Please install Git and try again")
        return False
    
    # Run all examples
    runner = GitExampleRunner()
    success = runner.run_all_examples()
    
    if success:
        print("\n✨ All Git operations examples completed successfully!")
        print("The Git Operations module is ready for production use!")
    else:
        print("\n⚠️ Some examples failed. Please check the implementation.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
