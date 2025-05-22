# Git Operations - Tutorial: Creating a Feature Branch

This tutorial guides you through using a conceptual `create_feature_branch` function from the Git Operations module to start new development work in a Codomyrmex project, adhering to typical project conventions.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Git Operations module's (future) Python API available in your environment.
- A local clone of a Codomyrmex Git repository.
- Git command-line tool installed and configured (user name, email).
- Familiarity with basic Git concepts (branch, commit) and the Codomyrmex branching strategy (feature branches from `main` - see `git_operations/README.md` or main `CONTRIBUTING.md`).

## 2. Goal

By the end of this tutorial, you will understand how to conceptually use a `create_feature_branch` function to:

- Create a new local branch based on the latest `main` (or other specified base branch).
- Name the branch according to a common convention (e.g., `feature/my-new-idea`).
- Automatically check out the new branch.

## 3. Conceptual API Function

Let's assume the Git Operations module will provide a function like this (details in `API_SPECIFICATION.md`):

```python
# Hypothetical function signature
# def create_feature_branch(repo_path: str, branch_name: str, base_branch: str = "main", checkout: bool = True) -> bool:
#     """
#     Creates a new branch from base_branch and optionally checks it out.
#     Returns True on success, False on failure.
#     """
#     # ... implementation using GitPython or subprocess ...
#     pass
```

## 4. Steps

### Step 1: Identify Your Task and Choose a Branch Name

Suppose you are about to work on a new feature to add a "user profile display". 
According to common conventions, a good branch name might be:
- `feature/user-profile-display`
- `feat/user-profile`

Let's choose `feature/user-profile-display`.

### Step 2: Using the (Conceptual) `create_feature_branch` Function

Here's how you might use the function in a Python script:

```python
# Assuming the function is imported, e.g.:
# from git_operations.git_wrapper import create_feature_branch, pull_changes, get_current_branch

# Placeholder for actual function call
def create_feature_branch(repo_path: str, branch_name: str, base_branch: str = "main", checkout: bool = True):
    print(f"Simulating: Creating branch '{branch_name}' from '{base_branch}' in '{repo_path}'. Checkout: {checkout}")
    # In a real scenario, this would pull base_branch first to ensure it's up-to-date
    # pull_changes(repo_path, branch_name=base_branch) 
    # Then create and checkout the new branch
    print(f"Branch '{branch_name}' created and checked out.")
    return True

def get_current_branch(repo_path: str):
    # This is a mock, assumes create_feature_branch changed mock state
    global MOCK_CURRENT_BRANCH
    return MOCK_CURRENT_BRANCH 

# --- Script --- 
REPO_PATH = "/path/to/your/codomyrmex-clone" # Replace with your actual repo path
NEW_BRANCH_NAME = "feature/user-profile-display"
BASE_BRANCH = "main"

# For mock purposes
MOCK_CURRENT_BRANCH = BASE_BRANCH 

print(f"Preparing to create feature branch: {NEW_BRANCH_NAME}")

# It's good practice to ensure the base branch (main) is up-to-date first.
# A real script might call a conceptual `pull_changes(REPO_PATH, branch_name=BASE_BRANCH)` here.
# print(f"Ensuring '{BASE_BRANCH}' is up-to-date...")
# if not pull_changes(REPO_PATH, branch_name=BASE_BRANCH):
#     print(f"Could not update '{BASE_BRANCH}'. Aborting branch creation.")
#     exit()

if create_feature_branch(REPO_PATH, NEW_BRANCH_NAME, base_branch=BASE_BRANCH, checkout=True):
    MOCK_CURRENT_BRANCH = NEW_BRANCH_NAME # Update mock state
    print(f"Successfully created and checked out branch: {NEW_BRANCH_NAME}")
    # current_actual_branch = get_current_branch(REPO_PATH) # Call to verify
    # print(f"Current active branch is now: {current_actual_branch}")
    print(f"Current active branch is now (mocked): {get_current_branch(REPO_PATH)}")
    print("You can now start working on your feature.")
else:
    print(f"Failed to create feature branch: {NEW_BRANCH_NAME}")

```

### Step 3: Verify (Manual Git Commands)

After running such a script (once the `create_feature_branch` function is implemented), you would typically verify with `git` commands in your terminal:

```bash
cd /path/to/your/codomyrmex-clone
git branch
# Expected output should show * feature/user-profile-display

git status
# Expected output should show "On branch feature/user-profile-display"
# and that it's up to date with 'origin/main' if main was just pulled.
```

## 5. Understanding the Benefits

Using a dedicated function from the `git_operations` module (once implemented) would:
- Ensure consistency in branch naming if the function incorporates validation or templating.
- Potentially automate pre-checks (like ensuring `main` is up-to-date before branching).
- Integrate with project logging via `logging_monitoring`.
- Provide a scriptable way to manage branches, useful for more complex automation or CI/CD integration in the future.

## 6. Troubleshooting (Conceptual)

- **Error: `Base branch 'main' not found or not up-to-date.`**
  - **Cause (Conceptual)**: The `create_feature_branch` function might internally try to pull `main` and fail, or `main` doesn't exist locally.
  - **Solution**: Manually run `git checkout main` and `git pull origin main` in your repository before running the script. Ensure `main` exists and is current.
- **Error: `Branch 'feature/user-profile-display' already exists.`**
  - **Cause**: A branch with that name is already present.
  - **Solution**: Choose a different name, or delete the existing branch if it's no longer needed (`git branch -d feature/user-profile-display`). The API function might also have a `force` option or different error handling for this.

## 7. Next Steps

Once your feature branch is created:
- Start developing your feature, making regular commits.
- Refer to `CONTRIBUTING.md` for guidelines on commit messages and the Pull Request process.
- Explore other (future) tools from the `git_operations` module for tasks like validating commit messages or automating PR creation. 