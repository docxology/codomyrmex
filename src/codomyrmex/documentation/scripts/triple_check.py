#!/usr/bin/env python3
"""Comprehensive triple-check of all SPEC, AGENTS, and README files."""

import os
import re
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# Placeholder patterns (using raw strings for proper regex escaping)
PLACEHOLDER_PATTERNS = [
    (r'\[Architecture description[^\]]*\]', 'Architecture description placeholder'),
    (r'\[Functional requirements[^\]]*\]', 'Functional requirements placeholder'),
    (r'\[Testing, documentation[^\]]*\]', 'Requirements placeholder'),
    (r'\[APIs, data structures[^\]]*\]', 'Interface placeholder'),
    (r'\[How to implement[^\]]*\]', 'Implementation placeholder'),
    (r'\[Brief description[^\]]*\]', 'Brief description placeholder'),
    (r'\[Module Name\]', 'Module name placeholder'),
    (r'\[MainClass\]', 'Main class placeholder'),
    (r'\[module_name\]', 'Module name variable placeholder'),
    (r'\bTODO\b', 'TODO marker'),
    (r'\bFIXME\b', 'FIXME marker'),
    (r'\bTBD\b', 'TBD marker'),
    (r'\bPLACEHOLDER\b', 'PLACEHOLDER marker'),
    (r'to be completed', 'To be completed'),
    (r'coming soon', 'Coming soon'),
    (r'needs filling', 'Needs filling'),
    (r'needs specific content', 'Needs specific content'),
    (r'Contains components for the src system', 'Generic placeholder'),
    (r'Documentation files and guides\.$', 'Generic docs placeholder'),
    (r'Test files and validation suites\.$', 'Generic test placeholder'),
]


def find_placeholders(content: str, file_path: Path) -> list[dict]:
    """Find placeholder content in file."""
    issues = []
    for pattern, description in PLACEHOLDER_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Get context
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].replace('\n', ' ')

            issues.append({
                'pattern': pattern,
                'description': description,
                'match': match.group(0),
                'position': match.start(),
                'line': content[:match.start()].count('\n') + 1,
                'context': context
            })
    return issues


def verify_relative_path(link_url: str, from_file: Path, base_path: Path) -> tuple[bool, str, Path]:
    """Verify if a relative path is correct."""
    if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
        return (True, "", None)  # External links and anchors are OK

    # Remove anchor
    clean_url = link_url.split('#')[0]
    if not clean_url:
        return (True, "", None)

    # Resolve path
    if clean_url.startswith('./'):
        clean_url = clean_url[2:]

    if clean_url.startswith('../'):
        levels_up = clean_url.count('../')
        base_dir = from_file.parent
        for _ in range(levels_up):
            if base_dir == base_dir.parent:  # Reached root
                return (False, "Too many ../ levels", None)
            base_dir = base_dir.parent
        resolved = base_dir / clean_url.lstrip('../')
    elif clean_url.startswith('/'):
        resolved = base_path / clean_url.lstrip('/')
    else:
        resolved = from_file.parent / clean_url

    # Normalize path
    try:
        resolved = resolved.resolve()
        exists = resolved.exists()
        if not exists:
            return (False, f"Path does not exist: {resolved}", resolved)
        return (True, "", resolved)
    except Exception as e:
        return (False, f"Error resolving path: {e}", None)


def check_file_completeness(content: str, file_path: Path) -> list[str]:
    """Check if file has required sections."""
    issues = []
    file_name = file_path.name

    # Check for version/status
    if "**Version**" not in content and "Version" not in content:
        issues.append("Missing version information")

    if "**Status**" not in content and "Status" not in content:
        issues.append("Missing status information")

    # Check for navigation
    if "## Navigation" not in content and "## Navigation Links" not in content:
        issues.append("Missing Navigation section")

    # Check for cross-references
    if file_name == "README.md":
        if "AGENTS.md" not in content and "AGENTS" not in content:
            issues.append("Missing reference to AGENTS.md")
        if "SPEC.md" not in content and "SPEC" not in content:
            issues.append("Missing reference to SPEC.md")
    elif file_name == "AGENTS.md":
        if "README.md" not in content and "README" not in content:
            issues.append("Missing reference to README.md")
        if "SPEC.md" not in content and "SPEC" not in content:
            issues.append("Missing reference to SPEC.md")
    elif file_name == "SPEC.md":
        if "README.md" not in content and "README" not in content:
            issues.append("Missing reference to README.md")
        if "AGENTS.md" not in content and "AGENTS" not in content:
            issues.append("Missing reference to AGENTS.md")

    # Check for empty or minimal content
    non_empty_lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
    if len(non_empty_lines) < 10:
        issues.append("File appears to have minimal content")

    return issues


def analyze_file(file_path: Path, base_path: Path) -> dict:
    """Comprehensively analyze a documentation file."""
    if not file_path.exists():
        return {'path': str(file_path.relative_to(base_path)), 'error': 'File does not exist'}

    try:
        content = file_path.read_text(encoding='utf-8')
        rel_path = str(file_path.relative_to(base_path))

        result = {
            'path': rel_path,
            'placeholders': find_placeholders(content, file_path),
            'broken_links': [],
            'completeness_issues': check_file_completeness(content, file_path),
            'total_issues': 0
        }

        # Check all links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, content)

        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip template placeholders in code blocks
            if '[' in link_text and ']' in link_text and link_text.startswith('['):
                # Check if it's in a code block
                start_pos = match.start()
                # Look backwards for code block markers
                before = content[max(0, start_pos-100):start_pos]
                if '```' in before:
                    # Count code block markers
                    code_blocks = before.count('```')
                    if code_blocks % 2 == 1:  # Inside code block
                        continue

            is_valid, error, resolved = verify_relative_path(link_url, file_path, base_path)
            if not is_valid:
                result['broken_links'].append({
                    'text': link_text,
                    'url': link_url,
                    'error': error,
                    'line': content[:match.start()].count('\n') + 1
                })

        result['total_issues'] = (
            len(result['placeholders']) +
            len(result['broken_links']) +
            len(result['completeness_issues'])
        )

        return result if result['total_issues'] > 0 else None

    except Exception as e:
        return {
            'path': str(file_path.relative_to(base_path)),
            'error': str(e)
        }


def main():
    """Run comprehensive triple-check."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")

    doc_files = []
    for root, dirs, _files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]

        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists():
                doc_files.append(file_path)

    print(f"Triple-checking {len(doc_files)} documentation files...\n")

    results = []
    for file_path in doc_files:
        result = analyze_file(file_path, base_path)
        if result:
            results.append(result)

    # Categorize issues
    files_with_placeholders = [r for r in results if r.get('placeholders')]
    files_with_broken_links = [r for r in results if r.get('broken_links')]
    files_with_completeness = [r for r in results if r.get('completeness_issues')]

    total_placeholders = sum(len(r.get('placeholders', [])) for r in results)
    total_broken_links = sum(len(r.get('broken_links', [])) for r in results)
    total_completeness = sum(len(r.get('completeness_issues', [])) for r in results)

    print("\n=== TRIPLE-CHECK SUMMARY ===")
    print(f"Total files checked: {len(doc_files)}")
    print(f"Files with issues: {len(results)}")
    print(f"Total placeholders: {total_placeholders}")
    print(f"Total broken links: {total_broken_links}")
    print(f"Total completeness issues: {total_completeness}")

    # Show top issues
    if files_with_placeholders:
        print(f"\n=== FILES WITH PLACEHOLDERS ({len(files_with_placeholders)}) ===")
        for result in sorted(files_with_placeholders, key=lambda x: len(x.get('placeholders', [])), reverse=True)[:10]:
            print(f"\n{result['path']}: {len(result['placeholders'])} placeholder(s)")
            for placeholder in result['placeholders'][:3]:
                print(f"  Line {placeholder['line']}: {placeholder['description']} - {placeholder['match'][:50]}")

    if files_with_broken_links:
        print(f"\n=== FILES WITH BROKEN LINKS ({len(files_with_broken_links)}) ===")
        for result in sorted(files_with_broken_links, key=lambda x: len(x.get('broken_links', [])), reverse=True)[:10]:
            print(f"\n{result['path']}: {len(result['broken_links'])} broken link(s)")
            for link in result['broken_links'][:3]:
                print(f"  Line {link['line']}: [{link['text']}]({link['url']}) - {link['error']}")

    if files_with_completeness:
        print(f"\n=== FILES WITH COMPLETENESS ISSUES ({len(files_with_completeness)}) ===")
        for result in sorted(files_with_completeness, key=lambda x: len(x.get('completeness_issues', [])), reverse=True)[:10]:
            print(f"\n{result['path']}:")
            for issue in result['completeness_issues']:
                print(f"  - {issue}")

    # Generate detailed report
    report_path = base_path / "output" / "triple_check_report.md"
    report_path.parent.mkdir(exist_ok=True)

    report = ["# Documentation Triple-Check Report\n\n"]
    report.append(f"**Generated**: {Path(__file__).stat().st_mtime}\n\n")
    report.append("## Summary\n\n")
    report.append(f"- **Total Files Checked**: {len(doc_files)}\n")
    report.append(f"- **Files with Issues**: {len(results)}\n")
    report.append(f"- **Total Placeholders**: {total_placeholders}\n")
    report.append(f"- **Total Broken Links**: {total_broken_links}\n")
    report.append(f"- **Total Completeness Issues**: {total_completeness}\n\n")

    if files_with_placeholders:
        report.append("## Placeholders\n\n")
        for result in sorted(files_with_placeholders, key=lambda x: len(x.get('placeholders', [])), reverse=True):
            report.append(f"### {result['path']}\n\n")
            for placeholder in result['placeholders']:
                report.append(f"- **Line {placeholder['line']}**: {placeholder['description']}\n")
                report.append(f"  - Match: `{placeholder['match']}`\n")
                report.append(f"  - Context: `{placeholder['context'][:100]}...`\n\n")

    if files_with_broken_links:
        report.append("## Broken Links\n\n")
        for result in sorted(files_with_broken_links, key=lambda x: len(x.get('broken_links', [])), reverse=True):
            report.append(f"### {result['path']}\n\n")
            for link in result['broken_links']:
                report.append(f"- **Line {link['line']}**: `[{link['text']}]({link['url']})`\n")
                report.append(f"  - Error: {link['error']}\n\n")

    if files_with_completeness:
        report.append("## Completeness Issues\n\n")
        for result in sorted(files_with_completeness, key=lambda x: len(x.get('completeness_issues', [])), reverse=True):
            report.append(f"### {result['path']}\n\n")
            for issue in result['completeness_issues']:
                report.append(f"- {issue}\n")
            report.append("\n")

    report_path.write_text(''.join(report), encoding='utf-8')
    print(f"\nDetailed report: {report_path}")


if __name__ == "__main__":
    main()
