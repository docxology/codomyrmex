"""
PAI Chat Simulator.

A test harness that mimics Claude Code's skill and workflow execution engine.
It allows verification of PAI slash commands and workflows without needing
the full Claude Code environment.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class WorkflowTrigger:
    name: str
    description: str
    workflow_file: str


class PAISimulator:
    """Simulator for PAI skill loading and workflow execution."""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path).expanduser().resolve()
        self.triggers: dict[str, WorkflowTrigger] = {}
        self.skill_name = self.skill_path.name

        # Load skill definition
        self._load_skill()

    def _load_skill(self) -> None:
        """Parse SKILL.md to find slash commands."""
        skill_file = self.skill_path / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found at {skill_file}")

        content = skill_file.read_text()

        # Extract workflow routing table (quick regex approach)
        # Format: | **name** | "trigger", "trigger" | `Workflows/file.md` |

        # Look for the table section
        table_match = re.search(r"## Workflow Routing.*?\n(.*?)(?:\n##|\Z)", content, re.DOTALL)
        if not table_match:
            logger.warning("No Workflow Routing table found in SKILL.md")
            return

        rows = table_match.group(1).strip().split('\n')
        for row in rows:
            if "|" not in row or "---" in row:
                continue

            parts = [p.strip() for p in row.split('|') if p.strip()]
            if len(parts) >= 3:
                name_raw = parts[0].replace('*', '')
                triggers_raw = parts[1]
                path_raw = parts[2].replace('`', '')

                # Parse triggers
                triggers = [t.strip(' "') for t in triggers_raw.split(',')]

                trigger_obj = WorkflowTrigger(
                    name=name_raw,
                    description=f"Simulated workflow for {name_raw}",
                    workflow_file=path_raw
                )

                for t in triggers:
                    cmd = t.strip()
                    if cmd.startswith('/'):
                        self.triggers[cmd] = trigger_obj
                        logger.info(f"Registered command: {cmd} -> {path_raw}")

    def execute_command(self, command: str) -> bool:
        """Simulate a user typing a slash command."""
        logger.info(f"USER: {command}")

        if command not in self.triggers:
            logger.error(f"Command not found: {command}")
            logger.info(f"Available commands: {list(self.triggers.keys())}")
            return False

        trigger = self.triggers[command]
        logger.info(f"PAI: Recognized command '{command}'. Executing workflow '{trigger.workflow_file}'...")

        return self._run_workflow(trigger.workflow_file)

    def _run_workflow(self, relative_path: str) -> bool:
        """Parse and run a workflow markdown file."""
        workflow_path = self.skill_path / relative_path
        if not workflow_path.exists():
            logger.error(f"Workflow file not found: {workflow_path}")
            return False

        content = workflow_path.read_text()

        # Extract code blocks
        blocks = re.findall(r"```(bash|python)\n(.*?)```", content, re.DOTALL)

        if not blocks:
            logger.warning("No executable blocks found in workflow.")
            return True

        logger.info(f"Found {len(blocks)} executable blocks.")

        success = True
        for i, (lang, code) in enumerate(blocks, 1):
            logger.info(f"\n--- Block {i} ({lang}) ---")

            if lang == "bash":
                success = self._run_bash(code)
            elif lang == "python":
                success = self._run_python(code)

            if not success:
                logger.error(f"Block {i} failed. Stopping workflow.")
                return False

        return True

    def _run_bash(self, code: str) -> bool:
        """Execute bash code block."""
        # Simple extraction of commands (naive, single line primarily)
        # Claude Code runs these in the terminal. We'll use subprocess.

        # Be careful with multi-line commands.
        # We'll execute the whole block as a script for fidelity.
        try:
            # Print for visibility
            print(f"Executing Bash:\n{code.strip()}\n")

            result = subprocess.run(
                code,
                shell=True,
                check=False,
                executable="/bin/bash",
                text=True,
                capture_output=True
            )

            print("--- Output ---")
            print(result.stdout)

            if result.stderr:
                print("--- Stderr ---")
                print(result.stderr)

            if result.returncode != 0:
                print(f"Exit Code: {result.returncode}")
                return False

            return True

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return False

    def _run_python(self, code: str) -> bool:
        """Execute python code block."""
        try:
            print(f"Executing Python:\n{code.strip()}\n")

            # Since the workflows often assume they are in the python environment context
            # or running via `python -c`, but here they are often just snippets.
            # However, Codomyrmex workflows use `uv run python -c "..."` inside bash blocks!

            # If the block is raw python (not inside a bash command), we run it securely.
            # But wait, looking at the workflows:
            # They are MOSTLY bash blocks that invoke `uv run python -c ...`
            # If there is a raw python block, Claude Code would try to run it?
            # Actually Claude Code creates artifacts or runs commands.
            # PAI workflows mostly use bash to run python one-liners.

            # If we do encounter a raw python block:
            exec_globals = {}
            exec(code, exec_globals)
            return True

        except Exception as e:
            logger.error(f"Python execution failed: {e}")
            return False
