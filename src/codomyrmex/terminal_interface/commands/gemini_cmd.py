"""Gemini CLI command wrapper for the terminal interface."""

import shutil
import subprocess
import sys

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def run_gemini_cli(*args: str) -> int:
    """Run the Gemini CLI natively.
    
    Args:
        args: Command line arguments to pass to the gemini executable.
        
    Returns:
        Exit code from the gemini CLI execution.
    """
    cli_path = shutil.which("gemini")
    
    if not cli_path:
        sys.stderr.write(
            "gemini CLI not found. Please install with `npm install -g @google/gemini-cli`\n"
        )
        return 1

    cmd = [cli_path] + list(args)
    
    try:
        logger.debug("Executing gemini terminal command: %s", " ".join(cmd))
        result = subprocess.run(cmd)
        return result.returncode
    except KeyboardInterrupt:
        # Standard interrupt handling
        return 130
    except subprocess.SubprocessError as e:
        logger.error("Failed to execute gemini command: %s", e)
        sys.stderr.write(f"Error executing gemini CLI: {e}\n")
        return 1
    except Exception as e:
        logger.error("Unexpected error executing gemini command: %s", e)
        sys.stderr.write(f"Unexpected error: {e}\n")
        return 1
