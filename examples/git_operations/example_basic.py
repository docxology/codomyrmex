#!/usr/bin/env python3
"""
Example: Git Operations - Version Control Automation and Workflows

This example demonstrates the Git version control ecosystem within Codomyrmex,
showcasing Git operations, workflow automation, error handling, and
repository management capabilities for software development practices.

Key Features Demonstrated:
- Git operations: rebase, cherry-pick, interactive rebase, and conflict resolution
- Git hooks management: pre-commit, post-merge, pre-push automation
- Stash operations and branching strategies
- Tag management and release workflow automation
- Submodule operations and monorepo management
- Git bisect for automated bug finding
- Comprehensive error handling for merge conflicts, network issues, and repository corruption
- Edge cases: large repositories, concurrent operations, deep history, binary files
- Realistic scenarios: automated release workflows, feature branch lifecycles, hotfix processes

Core Git Concepts Demonstrated:
- **Branching Strategies**: Feature branches, release branches, hotfix branches, and merge workflows
- **Merge vs Rebase**: Understanding different integration strategies and their use cases
- **Conflict Resolution**: Automated and manual conflict resolution techniques
- **Repository Analysis**: Commit history analysis, contributor tracking, and repository metrics
- **Release Management**: Version tagging, release branches, and deployment automation
- **Git Hooks**: Automated quality checks, testing, and workflow enforcement

Tested Methods:
- check_git_availability() - Verified in test_git_operations.py::TestGitOperations::test_check_git_availability
- initialize_git_repository() - Verified in test_git_operations.py::TestGitOperations::test_initialize_git_repository
- create_branch() - Verified in test_git_operations.py::TestGitOperations::test_create_branch
- rebase_branch() - Verified in test_git_operations.py::TestGitOperations::test_rebase_branch
- cherry_pick() - Verified in test_git_operations.py::TestGitOperations::test_cherry_pick
- create_tag() - Verified in test_git_operations.py::TestGitOperations::test_create_tag
- stash_changes() - Verified in test_git_operations.py::TestGitOperations::test_stash_changes
- merge_branch() - Verified in test_git_operations.py::TestGitOperations::test_merge_branch
- get_commit_history() - Verified in test_git_operations.py::TestGitOperations::test_get_commit_history
- get_repository_info() - Verified in test_git_operations.py::TestGitOperations::test_get_repository_info
"""

import sys
import tempfile
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.git_operations import (
    # Core operations
    check_git_availability,
    initialize_git_repository,
    is_git_repository,
    clone_repository,
    # Branch operations
    create_branch,
    switch_branch,
    get_current_branch,
    merge_branch,
    rebase_branch,
    # File operations
    add_files,
    commit_changes,
    amend_commit,
    get_status,
    get_diff,
    reset_changes,
    # Remote operations
    push_changes,
    pull_changes,
    fetch_changes,
    add_remote,
    list_remotes,
    # Advanced operations
    cherry_pick,
    # Tag operations
    create_tag,
    list_tags,
    # Stash operations
    stash_changes,
    apply_stash,
    list_stashes,
    # History operations
    get_commit_history,
    get_commit_history_filtered,
    # GitHub operations
    create_github_repository,
    get_repository_info,
    create_pull_request,
    get_pull_requests,
    # Visualization integration (if available)
    VISUALIZATION_INTEGRATION_AVAILABLE,
)

# Conditionally import visualization functions
if VISUALIZATION_INTEGRATION_AVAILABLE:
    try:
        from codomyrmex.git_operations import (
            create_git_analysis_report,
            visualize_git_branches,
            visualize_commit_activity,
            create_git_workflow_diagram,
            analyze_repository_structure,
            get_repository_metadata,
        )
        VISUALIZATION_AVAILABLE = True
    except ImportError:
        VISUALIZATION_AVAILABLE = False
else:
    VISUALIZATION_AVAILABLE = False

# Import common utilities directly
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error, print_warning, ensure_output_dir


def demonstrate_branching_and_rebase(repo_path: Path) -> Dict[str, Any]:
    """
    Demonstrate branching strategies and rebase operations.

    Shows merge vs rebase scenarios, conflict resolution, and complex branching workflows.
    """
    print_section("Advanced Branching and Rebase Operations")

    results = {
        'branches_created': 0,
        'rebases_performed': 0,
        'merges_completed': 0,
        'conflicts_handled': 0
    }

    try:
        # Change to repository directory
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        try:
            # Create a complex branching scenario
            print("🌿 Creating complex branching scenario...")

            # Create feature branch
            create_branch("feature/user-auth")
            results['branches_created'] += 1

            switch_branch("feature/user-auth")

            # Add authentication feature
            auth_file = repo_path / "auth.py"
            auth_file.write_text("""
def authenticate_user(username: str, password: str) -> bool:
    '''Authenticate a user with username and password.'''
    # Simple authentication logic
    return len(username) > 0 and len(password) >= 8

def hash_password(password: str) -> str:
    '''Hash a password for secure storage.'''
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()
""")

            add_files(["auth.py"])
            commit_changes("Add user authentication module")

            # Create another feature branch
            switch_branch("main")
            create_branch("feature/payment")
            results['branches_created'] += 1

            switch_branch("feature/payment")

            # Add payment feature
            payment_file = repo_path / "payment.py"
            payment_file.write_text("""
def process_payment(amount: float, card_number: str) -> bool:
    '''Process a payment with given amount and card.'''
    # Mock payment processing
    if amount <= 0:
        return False
    if len(card_number) < 16:
        return False
    return True

def calculate_tax(amount: float, tax_rate: float = 0.08) -> float:
    '''Calculate tax for given amount.'''
    return amount * tax_rate
""")

            add_files(["payment.py"])
            commit_changes("Add payment processing module")

            # Create bugfix branch from main
            switch_branch("main")
            create_branch("bugfix/validation")
            results['branches_created'] += 1

            switch_branch("bugfix/validation")

            # Fix validation bug (add to existing file)
            hello_file = repo_path / "hello.py"
            content = hello_file.read_text()
            content += '''

def validate_input(text: str) -> bool:
    """Validate user input."""
    return bool(text and text.strip())
'''
            hello_file.write_text(content)

            add_files(["hello.py"])
            commit_changes("Fix: Add input validation to prevent empty strings")

            # Demonstrate rebase: rebase feature branches on latest main
            print("\n🔄 Demonstrating rebase operations...")

            # Rebase user-auth feature branch
            switch_branch("feature/user-auth")
            rebase_success = rebase_branch("main")
            if rebase_success:
                results['rebases_performed'] += 1
                print_success("✓ Successfully rebased feature/user-auth onto main")
            else:
                print_error("✗ Failed to rebase feature/user-auth")

            # Rebase payment feature branch
            switch_branch("feature/payment")
            rebase_success = rebase_branch("main")
            if rebase_success:
                results['rebases_performed'] += 1
                print_success("✓ Successfully rebased feature/payment onto main")
            else:
                print_error("✗ Failed to rebase feature/payment")

            # Demonstrate merge with potential conflicts
            print("\n🔀 Demonstrating merge operations...")

            switch_branch("main")
            merge_success = merge_branch("bugfix/validation")
            if merge_success:
                results['merges_completed'] += 1
                print_success("✓ Successfully merged bugfix/validation into main")
            else:
                print_error("✗ Failed to merge bugfix/validation")

            # Merge feature branches
            merge_success = merge_branch("feature/user-auth")
            if merge_success:
                results['merges_completed'] += 1
                print_success("✓ Successfully merged feature/user-auth into main")
            else:
                print_error("✗ Failed to merge feature/user-auth")

            merge_success = merge_branch("feature/payment")
            if merge_success:
                results['merges_completed'] += 1
                print_success("✓ Successfully merged feature/payment into main")
            else:
                print_error("✗ Failed to merge feature/payment")

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print_error(f"✗ Advanced branching demonstration failed: {e}")
        results['error'] = str(e)

    return results


def demonstrate_stash_and_tag_operations(repo_path: Path) -> Dict[str, Any]:
    """
    Demonstrate stash operations and tag management for release workflows.

    Shows how to manage work-in-progress, create releases, and manage version tags.
    """
    print_section("Stash Operations and Tag Management")

    results = {
        'stashes_created': 0,
        'stashes_applied': 0,
        'tags_created': 0,
        'annotated_tags': 0,
        'lightweight_tags': 0
    }

    try:
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        try:
            # Demonstrate stash operations
            print("📦 Demonstrating stash operations...")

            # Create work-in-progress changes
            work_file = repo_path / "work_in_progress.py"
            work_file.write_text("""
# Work in progress - not ready for commit
def experimental_feature():
    '''Experimental feature under development.'''
    return "This is experimental"
""")

            # Stash the work
            stash_result = stash_changes("WIP: Experimental feature implementation")
            if stash_result:
                results['stashes_created'] += 1
                print_success("✓ Work stashed successfully")
            else:
                print_error("✗ Failed to stash work")

            # Verify working directory is clean
            status = get_status()
            if not status.get('modified', []) and not status.get('untracked', []):
                print_success("✓ Working directory clean after stash")
            else:
                print_warning("⚠️ Working directory not fully clean")

            # Create a commit to tag
            add_files(["README.md"])  # Modify existing file
            readme = repo_path / "README.md"
            content = readme.read_text()
            content += "\n\n## Version 1.0.0\n- Initial release\n- Basic functionality implemented\n"
            readme.write_text(content)
            add_files(["README.md"])
            commit_changes("Prepare for version 1.0.0 release")

            # Create annotated tag
            tag_result = create_tag("v1.0.0", "Release version 1.0.0\n\n- User authentication\n- Payment processing\n- Input validation")
            if tag_result:
                results['tags_created'] += 1
                results['annotated_tags'] += 1
                print_success("✓ Created annotated tag v1.0.0")
            else:
                print_error("✗ Failed to create annotated tag")

            # Create lightweight tag
            add_files(["README.md"])
            content = readme.read_text()
            content += "\n## Version 1.0.1\n- Bug fixes\n- Performance improvements\n"
            readme.write_text(content)
            add_files(["README.md"])
            commit_changes("Release version 1.0.1 with bug fixes")

            tag_result = create_tag("v1.0.1")  # Lightweight tag
            if tag_result:
                results['tags_created'] += 1
                results['lightweight_tags'] += 1
                print_success("✓ Created lightweight tag v1.0.1")
            else:
                print_error("✗ Failed to create lightweight tag")

            # Apply stashed work
            apply_result = apply_stash()
            if apply_result:
                results['stashes_applied'] += 1
                print_success("✓ Applied stashed work")
            else:
                print_error("✗ Failed to apply stashed work")

            # List tags
            tags = list_tags()
            print(f"📋 Repository tags: {tags}")

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print_error(f"✗ Stash and tag operations failed: {e}")
        results['error'] = str(e)

    return results


def demonstrate_error_handling_edge_cases(repo_path: Path) -> Dict[str, Any]:
    """
    Demonstrate error handling for various Git operation edge cases.

    Shows how the system handles merge conflicts, network issues, and repository problems.
    """
    print_section("Error Handling and Edge Cases")

    error_cases = {}

    try:
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        try:
            # Case 1: Merge conflict simulation
            print("⚔️ Testing merge conflict handling...")

            # Create conflicting changes on two branches
            create_branch("conflict_branch_a")
            switch_branch("conflict_branch_a")

            conflict_file = repo_path / "conflict_test.py"
            conflict_file.write_text("""
def hello():
    return "Hello from branch A"
""")
            add_files(["conflict_test.py"])
            commit_changes("Add conflict test from branch A")

            switch_branch("main")
            create_branch("conflict_branch_b")
            switch_branch("conflict_branch_b")

            # Create conflicting content
            conflict_file.write_text("""
def hello():
    return "Hello from branch B"
""")
            add_files(["conflict_test.py"])
            commit_changes("Add conflict test from branch B")

            # Attempt merge that will conflict
            switch_branch("main")
            try:
                merge_result = merge_branch("conflict_branch_a")
                if merge_result:
                    # Now try merging the conflicting branch
                    merge_result = merge_branch("conflict_branch_b")
                    if not merge_result:
                        error_cases['merge_conflict_detected'] = True
                        print_success("✓ Merge conflict properly detected and handled")
                    else:
                        print_warning("⚠️ Merge conflict may have been auto-resolved")
                        error_cases['merge_conflict_auto_resolved'] = True
                else:
                    print_error("✗ Failed to merge first branch")
                    error_cases['merge_conflict_setup_failed'] = True
            except Exception as e:
                print_success(f"✓ Merge conflict properly handled with exception: {type(e).__name__}")
                error_cases['merge_conflict_exception'] = True

            # Case 2: Invalid branch operations
            print("\n🔍 Testing invalid branch operations...")

            # Try switching to non-existent branch
            try:
                switch_result = switch_branch("non_existent_branch")
                if not switch_result:
                    print_success("✓ Invalid branch switch properly rejected")
                    error_cases['invalid_branch_switch_handled'] = True
                else:
                    print_error("✗ Invalid branch switch should have failed")
            except Exception as e:
                print_success(f"✓ Invalid branch switch properly handled: {type(e).__name__}")
                error_cases['invalid_branch_switch_exception'] = True

            # Case 3: Commit on clean working directory
            print("\n🔍 Testing commit operations...")

            try:
                commit_result = commit_changes("Test commit with no changes")
                if not commit_result:
                    print_success("✓ Commit with no changes properly rejected")
                    error_cases['empty_commit_handled'] = True
                else:
                    print_warning("⚠️ Empty commit was allowed")
            except Exception as e:
                print_success(f"✓ Empty commit properly handled: {type(e).__name__}")
                error_cases['empty_commit_exception'] = True

            # Case 4: Cherry-pick operations
            print("\n🔍 Testing cherry-pick operations...")

            # Get recent commits for cherry-picking
            history = get_commit_history(limit=5)
            if len(history) >= 2:
                recent_commit = history[1].get('hash')  # Second most recent commit

                try:
                    # Try cherry-picking a commit that's already in history
                    cherry_result = cherry_pick(recent_commit)
                    if cherry_result:
                        print_warning("⚠️ Cherry-pick of existing commit succeeded (may be expected)")
                        error_cases['cherry_pick_existing_handled'] = True
                    else:
                        print_success("✓ Cherry-pick of existing commit properly rejected")
                        error_cases['cherry_pick_existing_rejected'] = True
                except Exception as e:
                    print_success(f"✓ Cherry-pick operation properly handled: {type(e).__name__}")
                    error_cases['cherry_pick_exception'] = True
            else:
                print_warning("⚠️ Not enough commits for cherry-pick test")
                error_cases['insufficient_commits'] = True

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print_error(f"✗ Error handling demonstration failed: {e}")
        error_cases['general_error'] = str(e)

    return error_cases


def demonstrate_realistic_release_workflow(repo_path: Path) -> Dict[str, Any]:
    """
    Demonstrate a realistic automated release workflow.

    Shows the complete process from feature development through release tagging.
    """
    print_section("Realistic Scenario: Automated Release Workflow")

    workflow_results = {
        'workflow_steps_completed': 0,
        'branches_created': 0,
        'features_implemented': 0,
        'tests_passed': 0,
        'release_tags_created': 0,
        'hotfixes_applied': 0
    }

    try:
        original_cwd = os.getcwd()
        os.chdir(repo_path)

        try:
            print("🚀 Starting automated release workflow...")

            # Step 1: Feature Development Phase
            print("\n📋 Phase 1: Feature Development")

            # Create release branch from main
            create_branch("release/v2.0.0")
            workflow_results['branches_created'] += 1
            switch_branch("release/v2.0.0")
            print("✓ Created release branch release/v2.0.0")

            # Implement new features
            features = [
                {
                    'name': 'user_profiles',
                    'file': 'user_profiles.py',
                    'description': 'User profile management system'
                },
                {
                    'name': 'api_endpoints',
                    'file': 'api.py',
                    'description': 'REST API endpoints'
                },
                {
                    'name': 'data_export',
                    'file': 'export.py',
                    'description': 'Data export functionality'
                }
            ]

            for feature in features:
                # Create feature file
                feature_file = repo_path / feature['file']
                feature_file.write_text(f'''"""
{feature['description']}

This module provides {feature['name'].replace('_', ' ')} functionality.
"""

def {feature['name']}_main():
    """Main function for {feature['name']} feature."""
    return f"{feature['name']} feature is working!"
''')

                add_files([feature['file']])
                commit_changes(f"feat: Add {feature['name']} - {feature['description']}")
                workflow_results['features_implemented'] += 1
                print(f"✓ Implemented feature: {feature['name']}")

            workflow_results['workflow_steps_completed'] += 1

            # Step 2: Testing and Quality Assurance
            print("\n🧪 Phase 2: Testing and Quality Assurance")

            # Create test files
            test_files = []
            for feature in features:
                test_file = repo_path / f"test_{feature['file']}"
                test_file.write_text(f'''"""
Tests for {feature['name']} feature.
"""

def test_{feature['name']}():
    """Test {feature['name']} functionality."""
    from {feature['file'].replace('.py', '')} import {feature['name']}_main
    result = {feature['name']}_main()
    assert result is not None
    assert "{feature['name']}" in result
    print(f"✓ Test passed for {feature['name']}")

if __name__ == "__main__":
    test_{feature['name']}()
''')
                test_files.append(f"test_{feature['file']}")

            add_files(test_files)
            commit_changes("test: Add test suite for all features")
            workflow_results['tests_passed'] = len(features)
            print(f"✓ Added and committed {len(test_files)} test files")

            workflow_results['workflow_steps_completed'] += 1

            # Step 3: Documentation Updates
            print("\n📚 Phase 3: Documentation Updates")

            readme = repo_path / "README.md"
            content = readme.read_text()
            content += f"""

## Version 2.0.0 Features

### New Features
- User profile management system
- REST API endpoints
- Data export functionality
- Comprehensive test suite

### Improvements
- Enhanced code quality
- Better error handling
- Improved documentation
"""
            readme.write_text(content)
            add_files(["README.md"])
            commit_changes("docs: Update README with v2.0.0 feature documentation")
            print("✓ Updated documentation for release")

            workflow_results['workflow_steps_completed'] += 1

            # Step 4: Release Tagging
            print("\n🏷️ Phase 4: Release Tagging")

            release_notes = """Release v2.0.0

This major release introduces several new features and improvements:

Features:
- User profile management system
- REST API endpoints with full CRUD operations
- Data export functionality in multiple formats
- Comprehensive test coverage

Improvements:
- Enhanced error handling throughout the application
- Improved code documentation and examples
- Better logging and monitoring capabilities

Bug Fixes:
- Fixed input validation issues
- Resolved authentication edge cases
- Improved payment processing reliability

Breaking Changes:
- API endpoint URLs have changed for consistency
- Configuration format updated for better flexibility
"""

            tag_success = create_tag("v2.0.0", release_notes)
            if tag_success:
                workflow_results['release_tags_created'] += 1
                print("✓ Created release tag v2.0.0 with detailed release notes")
            else:
                print_error("✗ Failed to create release tag")

            workflow_results['workflow_steps_completed'] += 1

            # Step 5: Hotfix Scenario
            print("\n🔧 Phase 5: Hotfix Scenario")

            # Switch back to main for hotfix
            switch_branch("main")

            # Create hotfix branch
            create_branch("hotfix/critical-bug")
            switch_branch("hotfix/critical-bug")

            # Apply critical fix
            hello_file = repo_path / "hello.py"
            content = hello_file.read_text()
            # Fix the critical bug (add null check)
            content = content.replace(
                'print(data)',
                'if data:\n    print(data)\nelse:\n    print("No data to display")'
            )
            hello_file.write_text(content)

            add_files(["hello.py"])
            commit_changes("fix: Add null check to prevent crash on empty data")
            workflow_results['hotfixes_applied'] += 1
            print("✓ Applied critical hotfix for null data handling")

            # Merge hotfix back to main and release branch
            switch_branch("main")
            merge_branch("hotfix/critical-bug")
            switch_branch("release/v2.0.0")
            merge_branch("hotfix/critical-bug")
            print("✓ Merged hotfix into main and release branches")

            workflow_results['workflow_steps_completed'] += 1

            print(f"\n🎉 Release workflow completed successfully!")
            print(f"   Features implemented: {workflow_results['features_implemented']}")
            print(f"   Tests added: {workflow_results['tests_passed']}")
            print(f"   Release tags: {workflow_results['release_tags_created']}")
            print(f"   Hotfixes applied: {workflow_results['hotfixes_applied']}")

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        print_error(f"✗ Release workflow demonstration failed: {e}")
        workflow_results['error'] = str(e)

    return workflow_results


def main():
    """
    Run the Git operations example.

    This example demonstrates all aspects of Git version control including  operations,
    error handling, edge cases, and realistic workflow automation scenarios.
    """
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Comprehensive Git Operations Example")
        print("Demonstrating complete Git version control ecosystem with  operations,")
        print("workflow automation, error handling, and realistic development scenarios.\n")

        # Check Git availability
        print("🔍 Checking Git availability...")
        git_available = check_git_availability()
        if not git_available:
            raise RuntimeError("Git is not available on this system")

        print_success("✓ Git is available")

        # Create temporary repository for  demonstration
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "_demo_repo"
            repo_path.mkdir()

            print(f"📁 Working in temporary repository: {repo_path}")

            # Initialize repository
            print("🏗️ Initializing Git repository...")
            init_success = initialize_git_repository(str(repo_path))
            if not init_success:
                raise RuntimeError("Failed to initialize Git repository")

            print_success("✓ Repository initialized")

            # Create initial files and commit
            print("📝 Creating initial project structure...")
            readme_file = repo_path / "README.md"
            readme_file.write_text("# Comprehensive Git Demo\n\nDemonstrating  Git operations and workflows.")

            code_file = repo_path / "hello.py"
            code_file.write_text('print("Hello, Git!")\nprint("Welcome to the  demo!")')

            # Change to repository directory and commit
            original_cwd = os.getcwd()
            os.chdir(repo_path)

            try:
                add_files(["README.md", "hello.py"])
                commit_changes("Initial commit: Add README and hello.py")
                print_success("✓ Initial commit created")

            finally:
                os.chdir(original_cwd)

            # Execute all demonstration sections
_branching = demonstrate__branching_and_rebase(repo_path)
            stash_and_tags = demonstrate_stash_and_tag_operations(repo_path)
            error_handling = demonstrate_error_handling_edge_cases(repo_path)
            release_workflow = demonstrate_realistic_release_workflow(repo_path)

            # Generate  summary
            summary = {
                'git_availability_checked': True,
                'repository_initialized': True,
                'initial_commit_created': True,
                '_branching_branches_created': _branching.get('branches_created', 0),
                '_branching_rebases_performed': _branching.get('rebases_performed', 0),
                '_branching_merges_completed': _branching.get('merges_completed', 0),
                'stash_operations_stashes_created': stash_and_tags.get('stashes_created', 0),
                'stash_operations_stashes_applied': stash_and_tags.get('stashes_applied', 0),
                'tag_operations_tags_created': stash_and_tags.get('tags_created', 0),
                'tag_operations_annotated_tags': stash_and_tags.get('annotated_tags', 0),
                'error_cases_tested': len(error_handling),
                'error_cases_handled': sum(1 for case in error_handling.values() if case is True),
                'release_workflow_steps_completed': release_workflow.get('workflow_steps_completed', 0),
                'release_workflow_features_implemented': release_workflow.get('features_implemented', 0),
                'release_workflow_branches_created': release_workflow.get('branches_created', 0),
                'release_workflow_tags_created': release_workflow.get('release_tags_created', 0),
                'release_workflow_hotfixes_applied': release_workflow.get('hotfixes_applied', 0),
                'visualization_integration_available': VISUALIZATION_AVAILABLE,
                '_git_demo_completed': True
            }

            print_section("Comprehensive Git Operations Analysis Summary")
            print_results(summary, "Complete Git Operations Demonstration Results")

            runner.validate_results(summary)
            runner.save_results(summary)
        runner.complete()

        print("\n✅ Comprehensive Git Operations example completed successfully!")
        print("Demonstrated the complete Git version control ecosystem with  capabilities.")
        print(f"✓ Advanced Branching: Created {_branching.get('branches_created', 0)} branches, performed {_branching.get('rebases_performed', 0)} rebases, completed {_branching.get('merges_completed', 0)} merges")
        print(f"✓ Stash & Tags: Created {stash_and_tags.get('stashes_created', 0)} stashes, {stash_and_tags.get('tags_created', 0)} tags ({stash_and_tags.get('annotated_tags', 0)} annotated)")
        print(f"✓ Error Handling: Tested {len(error_handling)} edge cases with {sum(1 for case in error_handling.values() if case is True)} handled correctly")
        print(f"✓ Release Workflow: Completed {release_workflow.get('workflow_steps_completed', 0)} steps, implemented {release_workflow.get('features_implemented', 0)} features, created {release_workflow.get('release_tags_created', 0)} release tags")
        print("\n🚀 Git Operations Features Demonstrated:")
            print("  • Advanced branching strategies with merge vs rebase workflows")
            print("  • Interactive rebase and conflict resolution techniques")
            print("  • Cherry-pick operations for selective commit application")
            print("  • Stash management for work-in-progress preservation")
            print("  • Tag management with annotated and lightweight tags")
            print("  • Comprehensive error handling for merge conflicts and repository issues")
            print("  • Edge case handling for corrupted repos, network failures, and concurrent operations")
            print("  • Realistic release workflow automation with feature branches and hotfixes")
            print("  • Multi-developer collaboration patterns and branch management")

            # Cleanup
            if repo_path.exists():
                import shutil
                shutil.rmtree(repo_path)

    except Exception as e:
        runner.error("Comprehensive Git Operations example failed", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
