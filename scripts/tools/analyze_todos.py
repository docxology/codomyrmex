#!/usr/bin/env python3
"""
TODO/FIXME Discovery and Categorization Script

This script scans the entire codebase for TODO/FIXME/XXX/HACK/NOTE/BUG comments,
extracts them with context, and categorizes them by priority.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, asdict
import json
import sys


@dataclass
class TodoItem:
    """Represents a TODO/FIXME comment."""
    file_path: str
    line_number: int
    comment_type: str  # TODO, FIXME, XXX, HACK, NOTE, BUG
    content: str
    context_before: str
    context_after: str
    priority: str = "unknown"  # critical, high, medium, low
    category: str = "unknown"  # security, functionality, performance, documentation, etc.


# Keywords that indicate priority
CRITICAL_KEYWORDS = [
    'security', 'vulnerability', 'exploit', 'injection', 'xss', 'csrf', 'sql',
    'broken', 'crash', 'exception', 'error', 'fail', 'bug', 'fix', 'critical',
    'missing implementation', 'not implemented', 'placeholder'
]

HIGH_KEYWORDS = [
    'important', 'performance', 'slow', 'optimize', 'memory leak', 'race condition',
    'deadlock', 'architecture', 'design', 'refactor', 'technical debt'
]

MEDIUM_KEYWORDS = [
    'improve', 'enhance', 'better', 'cleanup', 'style', 'format', 'documentation',
    'test', 'coverage'
]

LOW_KEYWORDS = [
    'future', 'maybe', 'consider', 'optional', 'nice to have', 'wishlist'
]


def categorize_todo(content: str, comment_type: str) -> Tuple[str, str]:
    """
    Categorize a TODO by priority and category.

    Returns: (priority, category)
    """
    content_lower = content.lower()

    # Determine priority
    if any(keyword in content_lower for keyword in CRITICAL_KEYWORDS):
        priority = "critical"
    elif any(keyword in content_lower for keyword in HIGH_KEYWORDS):
        priority = "high"
    elif any(keyword in content_lower for keyword in MEDIUM_KEYWORDS):
        priority = "medium"
    elif any(keyword in content_lower for keyword in LOW_KEYWORDS):
        priority = "low"
    else:
        priority = "medium"  # Default

    # Determine category
    if any(kw in content_lower for kw in ['security', 'vulnerability', 'exploit', 'injection']):
        category = "security"
    elif any(kw in content_lower for kw in ['performance', 'slow', 'optimize', 'memory']):
        category = "performance"
    elif any(kw in content_lower for kw in ['test', 'coverage', 'testing']):
        category = "testing"
    elif any(kw in content_lower for kw in ['documentation', 'doc', 'comment']):
        category = "documentation"
    elif any(kw in content_lower for kw in ['implementation', 'implement', 'missing', 'placeholder']):
        category = "implementation"
    elif any(kw in content_lower for kw in ['bug', 'error', 'fix', 'broken']):
        category = "bug_fix"
    elif any(kw in content_lower for kw in ['refactor', 'cleanup', 'style']):
        category = "refactoring"
    else:
        category = "general"

    # Override priority for certain comment types
    if comment_type in ['BUG', 'FIXME']:
        if priority == "unknown" or priority == "low":
            priority = "high"
    elif comment_type == 'HACK':
        priority = "high"
    elif comment_type == 'XXX':
        priority = "critical"

    return priority, category


def extract_todos_from_file(file_path: Path) -> List[TodoItem]:
    """Extract all TODO/FIXME comments from a file."""
    todos = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Pattern to match TODO/FIXME/XXX/HACK/NOTE/BUG comments
        # Matches: TODO: description, FIXME description, # TODO, etc.
        pattern = re.compile(
            r'#?\s*(TODO|FIXME|XXX|HACK|NOTE|BUG)'
            r'(?::\s*|\s+)(.*?)(?:\n|$)',
            re.IGNORECASE
        )

        for line_num, line in enumerate(lines, start=1):
            # Check for inline comments
            match = pattern.search(line)
            if match:
                comment_type = match.group(1).upper()
                content = match.group(2).strip()

                # Get context (2 lines before and after)
                context_before = ""
                context_after = ""

                if line_num > 1:
                    context_before = lines[line_num - 2].strip() if line_num > 2 else ""
                if line_num < len(lines):
                    context_after = lines[line_num].strip() if line_num < len(lines) else ""

                priority, category = categorize_todo(content, comment_type)

                todo = TodoItem(
                    file_path=str(file_path.relative_to(Path.cwd())),
                    line_number=line_num,
                    comment_type=comment_type,
                    content=content,
                    context_before=context_before,
                    context_after=context_after,
                    priority=priority,
                    category=category
                )
                todos.append(todo)

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)

    return todos


def find_all_todos(project_root: Path) -> List[TodoItem]:
    """Find all TODO/FIXME comments in the project."""
    all_todos = []

    # File extensions to search
    extensions = {'.py', '.md', '.sh', '.yaml', '.yml', '.json', '.txt', '.js', '.ts'}

    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv',
        'htmlcov', '.mypy_cache', '.ruff_cache', 'build', 'dist', '.eggs'
    }

    for root, dirs, files in os.walk(project_root):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions or file_path.name in ['Makefile', 'Dockerfile']:
                todos = extract_todos_from_file(file_path)
                all_todos.extend(todos)

    return all_todos


def generate_report(todos: List[TodoItem], output_dir: Path) -> Dict[str, Any]:
    """Generate a comprehensive report of all TODOs."""
    # Group by priority
    by_priority = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': [],
        'unknown': []
    }

    # Group by category
    by_category = {}

    # Group by file
    by_file = {}

    for todo in todos:
        by_priority[todo.priority].append(todo)

        if todo.category not in by_category:
            by_category[todo.category] = []
        by_category[todo.category].append(todo)

        if todo.file_path not in by_file:
            by_file[todo.file_path] = []
        by_file[todo.file_path].append(todo)

    # Summary statistics
    summary = {
        'total_todos': len(todos),
        'by_priority': {k: len(v) for k, v in by_priority.items()},
        'by_category': {k: len(v) for k, v in by_category.items()},
        'by_type': {},
        'files_with_todos': len(by_file)
    }

    # Count by comment type
    for todo in todos:
        comment_type = todo.comment_type
        summary['by_type'][comment_type] = summary['by_type'].get(comment_type, 0) + 1

    report = {
        'summary': summary,
        'todos': [asdict(todo) for todo in todos],
        'by_priority': {k: [asdict(t) for t in v] for k, v in by_priority.items()},
        'by_category': {k: [asdict(t) for t in v] for k, v in by_category.items()},
        'by_file': {k: [asdict(t) for t in v] for k, v in by_file.items()}
    }

    return report


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    output_dir = project_root / "@output"
    output_dir.mkdir(exist_ok=True)

    print("Scanning codebase for TODO/FIXME comments...")
    print("=" * 80)

    todos = find_all_todos(project_root)

    print(f"\nFound {len(todos)} TODO/FIXME comments")

    # Generate report
    report = generate_report(todos, output_dir)

    # Save JSON report
    json_path = output_dir / "todo_analysis_report.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nDetailed JSON report saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total TODOs: {report['summary']['total_todos']}")
    print(f"Files with TODOs: {report['summary']['files_with_todos']}")
    print("\nBy Priority:")
    for priority, count in sorted(report['summary']['by_priority'].items()):
        if count > 0:
            print(f"  {priority:10}: {count:4}")

    print("\nBy Category:")
    for category, count in sorted(report['summary']['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {category:15}: {count:4}")

    print("\nBy Type:")
    for todo_type, count in sorted(report['summary']['by_type'].items()):
        print(f"  {todo_type:10}: {count:4}")

    # Print critical items
    if report['by_priority']['critical']:
        print("\n" + "=" * 80)
        print("CRITICAL PRIORITY TODOs:")
        print("=" * 80)
        for todo in report['by_priority']['critical'][:20]:  # Show first 20
            print(f"\n{todo['file_path']}:{todo['line_number']}")
            print(f"  Type: {todo['comment_type']}")
            print(f"  Content: {todo['content']}")
            print(f"  Category: {todo['category']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())

