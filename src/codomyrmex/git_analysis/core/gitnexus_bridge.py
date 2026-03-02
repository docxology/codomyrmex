"""Python bridge to the GitNexus Node.js codebase-analysis tool.

GitNexus indexes a repository using Tree-sitter AST parsing and KuzuDB graph
storage, then exposes structural query tools via its CLI and MCP server.

This bridge invokes GitNexus via subprocess, preferring:
  1. npx gitnexus  (if npm/npx available on PATH)
  2. node vendor/gitnexus/dist/index.js  (if vendor built locally)

GitNexus analyzes CODE STRUCTURE (symbol dependencies, call chains, blast
radius) rather than git commit history — complementing GitHistoryAnalyzer.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class GitNexusNotAvailableError(RuntimeError):
    """Raised when neither npx nor built vendor gitnexus is found."""


class GitNexusBridge:
    """Subprocess bridge to the GitNexus CLI tool.

    Provides structural code analysis via knowledge graph queries.
    Requires Node.js/npx or a built vendor distribution.
    """

    def __init__(self, repo_path: str, vendor_dir: str | None = None) -> None:
        self.repo_path = str(Path(repo_path).resolve())
        self._vendor_dir = vendor_dir or str(
            Path(__file__).parent.parent / "vendor" / "gitnexus"
        )
        self._node_cmd: list[str] | None = None  # resolved lazily

    def check_availability(self) -> bool:
        """Return True if gitnexus is runnable (npx or vendor build)."""
        try:
            self._resolve_cmd()
            return True
        except GitNexusNotAvailableError as e:
            logger.warning("GitNexus is not available: %s", e)
            return False

    def _resolve_cmd(self) -> list[str]:
        """Resolve the command to invoke gitnexus."""
        if self._node_cmd is not None:
            return self._node_cmd
        # Prefer npx (zero-install, downloads if not cached)
        if shutil.which("npx"):
            self._node_cmd = ["npx", "--yes", "gitnexus"]
            return self._node_cmd
        # Fall back to vendored build
        vendor_entry = Path(self._vendor_dir) / "dist" / "index.js"
        if vendor_entry.exists() and shutil.which("node"):
            self._node_cmd = ["node", str(vendor_entry)]
            return self._node_cmd
        raise GitNexusNotAvailableError(
            "GitNexus requires Node.js/npx or a built vendor dist. "
            "Install Node.js or run `npm install && npm run build` in "
            f"{self._vendor_dir}"
        )

    def _run(
        self,
        *args: str,
        timeout: int = 60,
        json_output: bool = True,
    ) -> dict[str, Any]:
        """Run a gitnexus CLI command and return parsed JSON output.

        Args:
            *args: Positional arguments for the gitnexus CLI.
            timeout: Subprocess timeout in seconds.
            json_output: If True, append ``--json`` flag and parse stdout as
                JSON. If False, return stdout/stderr as plain strings in a dict
                (used for commands like ``analyze`` that emit status messages).
        """
        cmd = self._resolve_cmd() + list(args)
        if json_output:
            cmd += ["--json"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.repo_path,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"gitnexus {args[0]} failed (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )
        if json_output:
            return json.loads(result.stdout)
        return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}

    def analyze(self) -> dict[str, Any]:
        """Index the repository. Creates .gitnexus/ directory in repo root.

        This must be run before query/context/impact operations.
        May take several minutes for large repositories.

        Returns:
            Dict with "stdout" and "stderr" from the analyze process, plus
            "indexed": True to confirm completion.
        """
        result = self._run(
            "analyze", self.repo_path, timeout=300, json_output=False
        )
        result["indexed"] = True
        return result

    def query(self, query_text: str, limit: int = 10) -> dict[str, Any]:
        """Hybrid BM25 + semantic search over the knowledge graph.

        Args:
            query_text: Natural language or symbol name to search for.
            limit: Maximum number of results to return.
        """
        return self._run("query", query_text, "--limit", str(limit))

    def get_context(self, symbol: str) -> dict[str, Any]:
        """360-degree analysis: incoming + outgoing deps for a symbol.

        Args:
            symbol: Fully-qualified symbol name (e.g., "MyClass.my_method").
        """
        return self._run("context", symbol)

    def assess_impact(self, symbol: str) -> dict[str, Any]:
        """Blast-radius assessment with confidence scoring.

        Returns all symbols that would be affected if the given symbol changes.

        Args:
            symbol: Fully-qualified symbol name to assess.
        """
        return self._run("impact", symbol)

    def detect_changes(self, diff: str | None = None) -> dict[str, Any]:
        """Map a git diff to architectural impact.

        Args:
            diff: Unified diff string. Uses HEAD diff if None.
        """
        if diff:
            return self._run("detect-changes", "--diff", diff)
        return self._run("detect-changes")

    def run_cypher(self, cypher_query: str) -> dict[str, Any]:
        """Execute a raw Cypher query against the KuzuDB graph.

        Args:
            cypher_query: Cypher query string (KuzuDB dialect).
        """
        return self._run("cypher", cypher_query)

    def list_repos(self) -> list[dict[str, Any]]:
        """List all repos indexed in the global ~/.gitnexus registry."""
        result = self._run("list-repos")
        return result.get("repos", result) if isinstance(result, dict) else result
