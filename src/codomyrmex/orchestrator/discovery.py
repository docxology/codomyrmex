"""
Script Discovery

Handles finding scripts to run based on criteria.
"""

from pathlib import Path
from typing import List, Optional

# Constants
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "venv", 
    ".venv", 
    "node_modules",
    "build",
    "dist",
    "egg-info",
    "output",
    "_templates",
    "module_template",
    "examples",
    "tests",
    ".cursor",
    ".DS_Store"
}

SKIP_PATTERNS = {
    "__init__.py",
    "conftest.py",
    "_orchestrator_utils.py",
    "run_all_scripts.py"
}

def discover_scripts(
    scripts_dir: Path,
    subdirs: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    max_depth: int = 2,
) -> List[Path]:
    """
    Discover all Python scripts in the scripts directory.
    
    Args:
        scripts_dir: Base scripts directory
        subdirs: Optional list of subdirectory names to filter
        pattern: Optional glob pattern to filter script names
        max_depth: Maximum directory depth to search
        
    Returns:
        List of script paths
    """
    scripts = []
    
    # Get subdirectories to search
    if subdirs:
        search_dirs = [scripts_dir / subdir for subdir in subdirs if (scripts_dir / subdir).is_dir()]
    else:
        search_dirs = [d for d in scripts_dir.iterdir() if d.is_dir() and d.name not in SKIP_DIRS]
    
    for subdir in search_dirs:
        if subdir.name in SKIP_DIRS:
            continue
            
        # Find Python files
        for py_file in subdir.rglob("*.py"):
            # Check depth
            try:
                relative = py_file.relative_to(scripts_dir)
            except ValueError:
                # Should not happen if py_file is in subdir which is in scripts_dir
                continue
                
            if len(relative.parts) > max_depth + 1:  # +1 for the file itself
                continue
                
            # Skip patterns
            if py_file.name in SKIP_PATTERNS:
                continue
                
            # Check if parent directory should be skipped
            if any(part in SKIP_DIRS for part in relative.parts[:-1]):
                continue
                
            # Apply pattern filter if specified
            if pattern and pattern not in py_file.name:
                continue
                
            scripts.append(py_file)
    
    return sorted(scripts)
