"""
MCP Functional Tools

Real, production-ready MCP tools for common development tasks.
These tools are designed to work with Claude Desktop and other MCP clients.
"""

import os
import re
import ast
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def read_file(path: str, encoding: str = "utf-8", max_size: int = 1_000_000) -> Dict[str, Any]:
    """
    Read file contents with metadata.
    
    Args:
        path: File path to read
        encoding: File encoding
        max_size: Maximum file size in bytes
    
    Returns:
        Dict with content, size, encoding, and metadata
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        if not file_path.exists():
            return {"error": f"File not found: {path}", "success": False}
        
        stats = file_path.stat()
        if stats.st_size > max_size:
            return {
                "error": f"File too large ({stats.st_size} bytes, max {max_size})",
                "success": False
            }
        
        content = file_path.read_text(encoding=encoding)
        
        return {
            "success": True,
            "content": content,
            "path": str(file_path),
            "size": stats.st_size,
            "lines": content.count("\n") + 1,
            "encoding": encoding,
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        }
    except Exception as e:
        return {"error": str(e), "success": False}


def write_file(path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        path: File path to write
        content: Content to write
        create_dirs: Create parent directories if needed
    
    Returns:
        Dict with success status and metadata
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content)
        
        return {
            "success": True,
            "path": str(file_path),
            "bytes_written": len(content.encode()),
            "lines": content.count("\n") + 1,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


def list_directory(
    path: str = ".",
    pattern: str = "*",
    recursive: bool = False,
    max_items: int = 200,
) -> Dict[str, Any]:
    """
    List directory contents with filtering.
    
    Args:
        path: Directory path
        pattern: Glob pattern for filtering
        recursive: Search recursively
        max_items: Maximum items to return
    
    Returns:
        Dict with items list and metadata
    """
    try:
        dir_path = Path(path).expanduser().resolve()
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {path}", "success": False}
        
        if not dir_path.is_dir():
            return {"error": f"Not a directory: {path}", "success": False}
        
        glob_method = dir_path.rglob if recursive else dir_path.glob
        items: list[dict[str, Any]] = []
        
        for item in glob_method(pattern):
            if len(items) >= max_items:
                break
            
            try:
                stats = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item.relative_to(dir_path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stats.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                })
            except Exception:
                continue
        
        return {
            "success": True,
            "path": str(dir_path),
            "items": items,
            "total": len(items),
            "truncated": len(items) >= max_items,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# CODE ANALYSIS
# ============================================================================

def analyze_python_file(path: str) -> Dict[str, Any]:
    """
    Analyze a Python file for structure and metrics.
    
    Args:
        path: Python file path
    
    Returns:
        Dict with classes, functions, imports, and metrics
    """
    try:
        content = Path(path).expanduser().read_text()
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    n.name for n in node.body 
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "bases": [ast.unparse(b) for b in node.bases],
                })
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.col_offset == 0:  # Top-level function
                    args = [a.arg for a in node.args.args]
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": args,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        lines = content.split("\n")
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith("#"))
        
        return {
            "success": True,
            "path": path,
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "metrics": {
                "total_lines": len(lines),
                "code_lines": code_lines,
                "class_count": len(classes),
                "function_count": len(functions),
                "import_count": len(imports),
            }
        }
    except Exception as e:
        return {"error": str(e), "success": False}


def search_codebase(
    pattern: str,
    path: str = ".",
    file_types: List[str] | None = None,
    case_sensitive: bool = False,
    max_results: int = 100,
) -> Dict[str, Any]:
    """
    Search for patterns in code files.
    
    Args:
        pattern: Search pattern (regex supported)
        path: Directory to search
        file_types: File extensions to include (e.g., [".py", ".js"])
        case_sensitive: Case sensitive search
        max_results: Maximum results to return
    
    Returns:
        Dict with matches and statistics
    """
    try:
        base_path = Path(path).expanduser().resolve()
        file_types = file_types or [".py", ".js", ".ts", ".md", ".json"]
        
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        
        matches = []
        files_searched = 0
        
        for filepath in base_path.rglob("*"):
            if not filepath.is_file():
                continue
            
            if not any(filepath.suffix == ext for ext in file_types):
                continue
            
            # Skip common non-code directories
            if any(p in filepath.parts for p in [".git", "node_modules", "__pycache__", ".venv"]):
                continue
            
            files_searched += 1
            
            try:
                content = filepath.read_text(errors="ignore")
                for i, line in enumerate(content.split("\n"), 1):
                    if regex.search(line):
                        matches.append({
                            "file": str(filepath.relative_to(base_path)),
                            "line": i,
                            "content": line.strip()[:200],
                        })
                        
                        if len(matches) >= max_results:
                            break
            except Exception:
                continue
            
            if len(matches) >= max_results:
                break
        
        return {
            "success": True,
            "pattern": pattern,
            "matches": matches,
            "total_matches": len(matches),
            "files_searched": files_searched,
            "truncated": len(matches) >= max_results,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# GIT OPERATIONS
# ============================================================================

def git_status(path: str = ".") -> Dict[str, Any]:
    """
    Get git repository status.
    
    Args:
        path: Repository path
    
    Returns:
        Dict with branch, changes, and status
    """
    try:
        cwd = Path(path).expanduser().resolve()
        
        # Get current branch
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True
        ).stdout.strip()
        
        # Get status
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd, capture_output=True, text=True
        ).stdout.strip()
        
        changes = []
        for line in status.split("\n"):
            if line:
                status_code = line[:2]
                file_path = line[3:]
                changes.append({
                    "status": status_code.strip(),
                    "file": file_path,
                })
        
        # Get recent commits
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=cwd, capture_output=True, text=True
        ).stdout.strip()
        
        commits = []
        for line in log.split("\n"):
            if line:
                parts = line.split(" ", 1)
                commits.append({
                    "hash": parts[0],
                    "message": parts[1] if len(parts) > 1 else "",
                })
        
        return {
            "success": True,
            "branch": branch,
            "changes": changes,
            "changed_files": len(changes),
            "recent_commits": commits,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


def git_diff(path: str = ".", staged: bool = False) -> Dict[str, Any]:
    """
    Get git diff for changes.
    
    Args:
        path: Repository path
        staged: Show staged changes only
    
    Returns:
        Dict with diff content
    """
    try:
        cwd = Path(path).expanduser().resolve()
        
        args = ["git", "diff"]
        if staged:
            args.append("--staged")
        
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True
        )
        
        return {
            "success": True,
            "diff": result.stdout,
            "lines": result.stdout.count("\n"),
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# SHELL COMMANDS
# ============================================================================

def run_shell_command(
    command: str,
    cwd: str = ".",
    timeout: int = 30,
    env: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    """
    Execute a shell command safely.
    
    Args:
        command: Command to execute
        cwd: Working directory
        timeout: Timeout in seconds
        env: Additional environment variables
    
    Returns:
        Dict with stdout, stderr, and exit code
    """
    try:
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        
        result = subprocess.run(
            command,
            shell=True,  # SECURITY: Intentional — this MCP tool's purpose is shell execution
            cwd=Path(cwd).expanduser().resolve(),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=cmd_env,
        )
        
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# DATA UTILITIES
# ============================================================================

def json_query(path: str, query: str | None = None) -> Dict[str, Any]:
    """
    Read and optionally query a JSON file.
    
    Args:
        path: JSON file path
        query: Optional dot-notation path (e.g., "data.items[0].name")
    
    Returns:
        Dict with data or queried value
    """
    try:
        content = Path(path).expanduser().read_text()
        data = json.loads(content)
        
        if query:
            # Simple dot-notation query
            parts = query.replace("[", ".").replace("]", "").split(".")
            result = data
            for part in parts:
                if part.isdigit():
                    result = result[int(part)]
                else:
                    result = result[part]
            return {"success": True, "result": result, "query": query}
        
        return {"success": True, "data": data}
    except Exception as e:
        return {"error": str(e), "success": False}


def checksum_file(path: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """
    Calculate file checksum.
    
    Args:
        path: File path
        algorithm: Hash algorithm (md5, sha1, sha256)
    
    Returns:
        Dict with checksum and metadata
    """
    try:
        file_path = Path(path).expanduser().resolve()
        content = file_path.read_bytes()
        
        if algorithm == "md5":
            hash_val = hashlib.md5(content).hexdigest()
        elif algorithm == "sha1":
            hash_val = hashlib.sha1(content).hexdigest()
        else:
            hash_val = hashlib.sha256(content).hexdigest()
        
        return {
            "success": True,
            "path": str(file_path),
            "algorithm": algorithm,
            "checksum": hash_val,
            "size": len(content),
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "read_file",
    "write_file",
    "list_directory",
    "analyze_python_file",
    "search_codebase",
    "git_status",
    "git_diff",
    "run_shell_command",
    "json_query",
    "checksum_file",
]
