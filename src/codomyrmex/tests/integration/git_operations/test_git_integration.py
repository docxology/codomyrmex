
import os
import shutil
import pytest
from codomyrmex.git_operations.core.git import (
    initialize_git_repository,
    create_branch,
    switch_branch,
    add_files,
    commit_changes,
    get_current_branch,
    create_tag,
    list_tags,
    get_status
)

@pytest.mark.integration
def test_git_workflow_real_repo(real_git_repo):
    """Test a full git workflow on a real repository."""
    repo_path = str(real_git_repo)
    
    # Verify initial state
    assert get_current_branch(repo_path) == "feature/test"
    
    # 1. Create a new file
    new_file = real_git_repo / "new_feature.py"
    new_file.write_text("print('New feature')")
    
    # 2. Check status
    status = get_status(repo_path)
    # The file is untracked
    assert "new_feature.py" in status["untracked"]
    
    # 3. Add file
    assert add_files(["new_feature.py"], repo_path) is True
    
    # 4. Commit
    commit_sha = commit_changes("Add new feature", repo_path)
    assert commit_sha is not None
    
    # 5. Create tag
    assert create_tag("v0.1.0", "Release 0.1.0", repo_path) is True
    tags = list_tags(repo_path)
    assert "v0.1.0" in tags
    
    # 6. Create another branch and switch
    assert create_branch("release/v0.1.0", repo_path) is True
    assert get_current_branch(repo_path) == "release/v0.1.0"
    
    # 7. Clean repository (create untracked file and clean it)
    junk_file = real_git_repo / "junk.tmp"
    junk_file.write_text("junk")
    from codomyrmex.git_operations.core.git import clean_repository
    clean_repository(force=True, repository_path=repo_path)
    assert not junk_file.exists()

@pytest.mark.integration
def test_git_init_real(tmp_path):
    """Test git initialization on a real path."""
    repo_path = tmp_path / "new_repo"
    repo_path.mkdir()
    
    assert initialize_git_repository(str(repo_path), initial_commit=True) is True
    assert (repo_path / ".git").exists()
    assert (repo_path / "README.md").exists()
    
    # Check commit history to verify initial commit
    from codomyrmex.git_operations.core.git import get_commit_history
    commits = get_commit_history(repository_path=str(repo_path))
    assert len(commits) == 1
    assert commits[0]["message"] == "Initial commit"
