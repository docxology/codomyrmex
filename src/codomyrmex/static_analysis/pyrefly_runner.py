import subprocess
import json
import re
import os
import sys

# Add project root for sibling module imports if run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..')) # static_analysis -> codomyrmex
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
except ImportError:
    # Fallback for environments where logging_monitoring might not be discoverable
    # This is less ideal but provides a basic operational mode.
    import logging
    print("Warning: Could not import Codomyrmex logging. Using standard Python logging.", file=sys.stderr)
    def setup_logging(): # Dummy setup_logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    def get_logger(name):
        _logger = logging.getLogger(name)
        if not _logger.handlers: # Avoid adding handlers multiple times if already configured
            _handler = logging.StreamHandler(sys.stdout)
            _formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
            _handler.setFormatter(_formatter)
            _logger.addHandler(_handler)
            _logger.setLevel(logging.INFO)
        return _logger

logger = get_logger(__name__)

# Regex to attempt to parse Pyrefly errors, this is a guess and might need refinement
# Example: <path>:<line>:<col> <Error Code> <description>
# or path:line:col: <message type>: <message>
PYREFLY_ERROR_PATTERN = re.compile(r"([^:]+):(\d+):(\d+):\s*(.*)") # Adjusted to be more flexible with error codes/types

def parse_pyrefly_output(output: str, project_root: str) -> list:
    """
    Parses the raw output from Pyrefly to extract structured error information.
    This is a basic parser and might need significant improvement based on actual Pyrefly output.
    """
    issues = []
    logger.debug(f"Attempting to parse Pyrefly output. Project root: {project_root}")
    logger.debug(f"Raw output for parsing:\\n{output}")

    for line in output.splitlines():
        match = PYREFLY_ERROR_PATTERN.match(line.strip()) # Ensure leading/trailing whitespace is removed
        if match:
            raw_file_path, line_num, col_num, message = match.groups()
            # Attempt to make file path relative to project_root
            try:
                # If raw_file_path is already absolute and within project_root, relpath is fine.
                # If raw_file_path is relative (to where pyrefly ran, i.e., project_root), os.path.join might be redundant
                # but os.path.relpath should correctly simplify it.
                abs_raw_path = os.path.join(project_root, raw_file_path.strip())
                if not os.path.exists(abs_raw_path) and os.path.exists(raw_file_path.strip()):
                    # If joining with project_root doesn't make sense (e.g. path is already absolute)
                    # and original path exists, use original path.
                    # This can happen if Pyrefly outputs absolute paths.
                    file_path = os.path.relpath(raw_file_path.strip(), project_root) \
                                  if os.path.isabs(raw_file_path.strip()) and raw_file_path.strip().startswith(project_root) \
                                  else raw_file_path.strip()
                else:
                    file_path = os.path.relpath(abs_raw_path, project_root)

            except ValueError:
                logger.warning(f"Could not create relative path for {raw_file_path.strip()} against {project_root}. Using original path.")
                file_path = raw_file_path.strip() # Keep original if relpath fails

            issue = {
                "file_path": file_path,
                "line_number": int(line_num),
                "column_number": int(col_num),
                "code": "PYREFLY_ERROR", # Generic code for now, actual error codes might be in message
                "message": message.strip(),
                "severity": "error" # Pyrefly errors are typically type errors
            }
            issues.append(issue)
            logger.debug(f"Parsed issue: {issue}")
        elif line.strip(): # Log lines that don't match, if they are not empty
            logger.debug(f"Non-matching line in Pyrefly output: '{line.strip()}'")
    logger.info(f"Parsed {len(issues)} issues from Pyrefly output.")
    return issues

def run_pyrefly_analysis(target_paths: list[str], project_root: str) -> dict:
    """
    Runs Pyrefly static type checker on the given paths and returns the analysis results.

    Args:
        target_paths: A list of file or directory paths to analyze.
        project_root: The root directory of the project, used for resolving paths
                      and for Pyrefly to find its configuration.

    Returns:
        A dictionary containing the analysis results from Pyrefly, conforming to
        the MCP_TOOL_SPECIFICATION for 'tool_results'.
    """
    tool_name = "pyrefly"
    results = {
        "tool_name": tool_name,
        "issue_count": 0,
        "issues": [],
        "raw_output": "",
        "error": None,
        "report_path": None # Pyrefly might not generate separate report files by default
    }
    logger.info(f"Starting Pyrefly analysis for targets: {target_paths} in project root: {project_root}")

    if not target_paths:
        results["error"] = "No target paths provided for Pyrefly analysis."
        logger.error(results["error"])
        return results

    try:
        # Pyrefly typically operates on the current working directory to find its config
        # and interpret paths.
        command = ["pyrefly", "check"] + target_paths
        logger.info(f"Executing Pyrefly command: {' '.join(command)} in {project_root}")

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=project_root, # Run Pyrefly from the project root
            check=False # Do not raise exception for non-zero exit codes, handle it manually
        )

        stdout_output = process.stdout.strip()
        stderr_output = process.stderr.strip()
        combined_output_parts = []
        if stdout_output:
            combined_output_parts.append("--- Pyrefly STDOUT ---")
            combined_output_parts.append(stdout_output)
        if stderr_output:
            combined_output_parts.append("--- Pyrefly STDERR ---")
            combined_output_parts.append(stderr_output)
        
        results["raw_output"] = "\n".join(combined_output_parts)
        logger.debug(f"Pyrefly raw stdout:\\n{stdout_output}")
        logger.debug(f"Pyrefly raw stderr:\\n{stderr_output}")
        
        # Pyrefly documentation suggests errors might go to stdout or stderr.
        # Let's prioritize parsing stdout as it's more common for findings,
        # but include stderr content for parsing as well if stdout is empty or has no issues.
        # Some tools output to stderr for errors AND findings.
        output_to_parse = stdout_output
        if not output_to_parse and stderr_output: # If stdout is empty, try stderr
            output_to_parse = stderr_output
        elif stdout_output and stderr_output: # If both have content, combine them for parsing
            # This might be noisy but ensures we don't miss errors if they are split.
            # Or, Pyrefly might clearly delineate. For now, let's assume errors could be in either/both.
            output_to_parse = stdout_output + "\n" + stderr_output
            
        parsed_issues = parse_pyrefly_output(output_to_parse, project_root)
        results["issues"] = parsed_issues
        results["issue_count"] = len(parsed_issues)

        if process.returncode != 0:
            logger.warning(f"Pyrefly exited with code {process.returncode}.")
            if not parsed_issues: # If exit code is non-zero AND we found no specific issues
                error_summary = f"Pyrefly exited with code {process.returncode}."
                # Prefer stderr for general error messages if no issues parsed
                if stderr_output:
                    error_summary += f" Stderr: {stderr_output}"
                elif stdout_output:
                    error_summary += f" Stdout: {stdout_output}"
                results["error"] = error_summary
                logger.error(error_summary)
                if not results["raw_output"]: # Ensure raw_output is populated if it wasn't
                    results["raw_output"] = error_summary
        else:
            logger.info("Pyrefly completed successfully (exit code 0).")


    except FileNotFoundError:
        results["error"] = "Pyrefly command not found. Please ensure it is installed and in PATH."
        logger.error(results["error"], exc_info=True)
    except Exception as e:
        results["error"] = f"An unexpected error occurred while running Pyrefly: {str(e)}"
        logger.error(results["error"], exc_info=True)
        if not results["raw_output"]: # Ensure raw_output is populated
            results["raw_output"] = str(e)
            
    logger.info(f"Pyrefly analysis finished. Issues found: {results['issue_count']}. Error: {results['error']}")
    return results

if __name__ == "__main__":
    # Ensure logging is set up when script is run directly
    # This will use environment variables or defaults defined in logger_config.py
    setup_logging()
    logger.info("Executing pyrefly_runner.py directly for testing example.")

    # Define a hypothetical project root and target file for the example.
    # For a real test, these paths would need to exist, Pyrefly be installed,
    # and a pyrefly.toml (or pyproject.toml section) be present in the project root.
    example_project_root = "./temp_pyrefly_test_project" # Example path
    analysis_targets = ["test_module.py"]          # Example target

    logger.info(f"Simulating Pyrefly run for: {analysis_targets} in project root {example_project_root}")
    logger.info("To perform a real test run:")
    logger.info(f"1. Create a directory named '{example_project_root}' (relative to where you run this script, or use an absolute path).")
    logger.info(f"2. Inside '{example_project_root}', create a 'pyrefly.toml' with content like:")
    logger.info("   python_version = \"3.10\"\n   project_includes = [\"*.py\"]")
    logger.info(f"3. Inside '{example_project_root}', create a Python file named '{analysis_targets[0]}' with some type errors.")
    logger.info("   Example test_module.py content:")
    logger.info("   def add(a: int, b: str) -> int: return a + b\n   my_var: int = \"text\"")
    logger.info("4. Ensure Pyrefly is installed (`pip install pyrefly`).")
    logger.info("5. Uncomment and run the analysis lines below.")

    # --- To perform an actual run, set up files as described above and uncomment: ---
    logger.info(f"Attempting to create directory {example_project_root} if it doesn't exist for the test.")
    os.makedirs(example_project_root, exist_ok=True)
    pyrefly_toml_path = os.path.join(example_project_root, "pyrefly.toml")
    with open(pyrefly_toml_path, "w") as f:
        f.write("python_version = \"3.10\"\nproject_includes = [\"*.py\"]\n")
    test_file_path_abs = os.path.join(example_project_root, analysis_targets[0])
    with open(test_file_path_abs, "w") as f:
        f.write("def add(a: int, b: str) -> int: return a + b\nmy_var: int = \"text\"\n")
    logger.info(f"Created dummy pyrefly.toml and {analysis_targets[0]} in {example_project_root}")
    
    analysis_result = run_pyrefly_analysis(target_paths=analysis_targets, project_root=example_project_root)
    logger.info("--- Pyrefly Analysis Result (JSON) ---")
    print(json.dumps(analysis_result, indent=2))
    logger.info(f"Test run finished. To clean up, you can remove the directory: {example_project_root}")
    # --- End of actual run block ---

    # Showing a mock result structure for demonstration if not running live
    # if True: # This block will always run to show mock output structure
    #     logger.info("Displaying a MOCK result structure as the actual run is commented out by default.")
    #     mock_result = {
    #         "tool_name": "pyrefly",
    #         "issue_count": 2,
    #         "issues": [
    #             {
    #                 "file_path": "test_module.py",
    #                 "line_number": 1,
    #                 "column_number": 32,
    #                 "code": "PYREFLY_ERROR",
    #                 "message": "Unsupported operand types for + (\"int\" and \"str\")",
    #                 "severity": "error"
    #             },
    #             {
    #                 "file_path": "test_module.py",
    #                 "line_number": 2,
    #                 "column_number": 16,
    #                 "code": "PYREFLY_ERROR",
    #                 "message": "Expression \"text\" is incompatible with declared type \"int\"",
    #                 "severity": "error"
    #             }
    #         ],
    #         "raw_output": "test_module.py:1:32 Unsupported operand types for + (...)\ntest_module.py:2:16 Expression \"text\" is incompatible with declared type \"int\"",
    #         "error": None,
    #         "report_path": None
    #     }
    #     logger.info("--- Mock Pyrefly Analysis Result (JSON) ---")
    #     print(json.dumps(mock_result, indent=2)) 