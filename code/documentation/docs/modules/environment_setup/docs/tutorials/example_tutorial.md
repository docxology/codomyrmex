---
sidebar_label: 'Verifying Setup'
title: 'Tutorial: Verifying Your Environment Setup'
---

# Environment Setup - Tutorial: Verifying Your Setup with `env_checker.py`

This tutorial will guide you through using the conceptual `env_checker.py` script (if implemented and available at `environment_setup/env_checker.py`) to verify your Codomyrmex development environment.

## 1. Prerequisites

Before you begin, ensure you have the following:

- A local clone of the Codomyrmex repository.
- Python 3.9+ installed and accessible in your PATH.
- The Codomyrmex Python virtual environment (`.venv`) should be created and activated as per the main [Environment Setup instructions](../../index.md).
- (Optional, but recommended for full check) Node.js (v18+) and npm/yarn installed.
- (Optional) Git installed.
- (Optional) Graphviz installed if you intend to use features requiring it.

## 2. Goal

By the end of this tutorial, you will be able to:

- Run the `env_checker.py` script.
- Understand its output, identifying any potential issues with your environment setup.
- Know what areas the script checks (e.g., Python version, Node.js, critical dependencies).

## 3. Steps

### Step 1: Navigate to the Project Root

Open your terminal and ensure you are in the root directory of your Codomyrmex project clone.

```bash
cd path/to/your/codomyrmex-repository
```

### Step 2: Activate Your Python Virtual Environment

If not already active, activate your `.venv`:

```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows (Git Bash or similar):
# source .venv/Scripts/activate

# On Windows (Command Prompt / PowerShell):
# .venv\Scripts\activate
```
Your terminal prompt should change to indicate the active virtual environment (e.g., `(.venv) user@host:...$`).

### Step 3: Run the `env_checker.py` Script

Execute the script using Python:

```bash
python environment_setup/env_checker.py
```

(Note: The actual path to `env_checker.py` might be just `env_checker.py` if it's added to PATH or if you are in the `environment_setup` directory, but running from project root as `environment_setup/env_checker.py` is a safe assumption for a project script.)

### Step 4: Interpret the Output

The script will print a series of checks to your console. Look for:
- **[OK]** messages indicating a successful check.
- **[WARNING]** messages for optional components that are missing but not critical for all functionality.
- **[ERROR]** or **[FAILED]** messages for critical components that are missing or incorrectly configured.
- A summary at the end, often with recommendations if issues were found.

**Example Output Snippet:**
```
Checking Codomyrmex Environment...
[OK] Python version: 3.9.10 (Expected: >=3.9)
[OK] pip is available.
[OK] Git version: 2.34.1 (Expected: any version)
[INFO] Node.js version: 18.15.0 (Expected: >=18.0)
[INFO] npm version: 9.5.0
[OK] Docusaurus dependencies seem to be installed in ./documentation.
[WARNING] Graphviz: Not found. Some visualization features might be unavailable.
---
Environment Status: PARTIAL_SUCCESS (Some optional tools missing)
Recommendations:
 - Consider installing Graphviz if you need dependency graph visualizations.
```

## 4. Understanding the Results

- A `Status: SUCCESS` or `PARTIAL_SUCCESS` (if only optional items are missing) means your core environment is likely ready for most development tasks.
- `Status: FAILURE` indicates a problem with a critical component (like an incorrect Python version) that needs to be addressed before proceeding.
- The `Recommendations` section should guide you on fixing any detected issues.

## 5. Troubleshooting

- **Error: `python: command not found` or `env_checker.py: No such file or directory`**
  - **Solution**: Ensure Python is installed and in your PATH. Verify you are in the correct project root directory and the path to `env_checker.py` is correct. Make sure your virtual environment is active.
- **Script reports a tool as missing, but you believe it's installed**:
  - **Cause**: The tool might not be in the PATH recognized by the script or the active virtual environment. System-wide installations vs. user-specific installations can sometimes cause this.
  - **Solution**: Ensure the tool is correctly installed and its executable is in your system PATH. For Python packages, ensure they were installed in the active virtual environment.

## 6. Next Steps

Congratulations! You've learned how to use the (conceptual) `env_checker.py` to verify your setup.

- Address any critical errors reported by the script by following its recommendations or the main [Environment Setup instructions](../../index.md).
- You can now proceed with other development tasks, confident that your environment meets the basic requirements. 