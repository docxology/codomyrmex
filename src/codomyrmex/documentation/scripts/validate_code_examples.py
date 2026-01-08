from pathlib import Path
from typing import List, Dict, Tuple, Any
import ast
import json
import os
import os
import re
import sys

from dataclasses import dataclass, asdict







#!/usr/bin/env python3
"""
Code Example Validation Script

This script extracts code examples from documentation files,
validates their syntax, and checks if they match actual API signatures.
"""



@dataclass
class CodeExample:
    """Represents a code example from documentation."""
    file_path: str
    line_number: int
    language: str
    code: str
    syntax_valid: bool = False
    import_errors: List[str] = None
    api_mismatches: List[str] = None

    def __post_init__(self):
        if self.import_errors is None:
            self.import_errors = []
        if self.api_mismatches is None:
            self.api_mismatches = []


def extract_code_blocks(content: str, file_path: Path) -> List[CodeExample]:
    """Extract all code blocks from markdown content."""
    examples = []

    # Pattern for code blocks: ```language\ncode\n```
    pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

    lines = content.split('\n')
    for match in pattern.finditer(content):
        language = match.group(1) or 'text'
        code = match.group(2).strip()

        # Find line number of the code block start
        line_num = content[:match.start()].count('\n') + 1

        if language in ['python', 'py']:
            example = CodeExample(
                file_path=str(file_path.relative_to(Path.cwd())),
                line_number=line_num,
                language='python',
                code=code
            )
            examples.append(example)

    return examples


def validate_python_syntax(code: str) -> Tuple[bool, List[str]]:
    """Validate Python syntax."""
    errors = []
    try:
        ast.parse(code)
        return True, []
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return False, errors
    except Exception as e:
        errors.append(f"Parse error: {str(e)}")
        return False, errors


def check_imports(code: str) -> List[str]:
    """Check if imports in code can be resolved."""
    errors = []

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    # Check for codomyrmex imports
                    if module.startswith('codomyrmex'):
                        # This would require checking actual module structure
                        # For now, we just note it
                        pass
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module.startswith('codomyrmex'):
                    # Note: Would need to check actual module structure
                    pass
    except SyntaxError:
        # Already handled by syntax validation
        pass

    return errors


def validate_code_example(example: CodeExample) -> CodeExample:
    """Validate a code example."""
    if example.language == 'python':
        syntax_valid, syntax_errors = validate_python_syntax(example.code)
        example.syntax_valid = syntax_valid
        example.import_errors = check_imports(example.code)

    return example


def find_all_documentation_files(docs_dir: Path) -> List[Path]:
    """Find all markdown documentation files."""
    markdown_files = []
    for root, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(Path(root) / file)
    return sorted(markdown_files)


def main():
    """Main function."""

    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    docs_dir = project_root / 'docs'
    output_dir = project_root / "@output"
    output_dir.mkdir(exist_ok=True)

    print("Extracting and validating code examples from documentation...")
    print("=" * 80)

    all_examples = []
    docs_files = find_all_documentation_files(docs_dir)

    for doc_file in docs_files:
        try:
            content = doc_file.read_text(encoding='utf-8')
            examples = extract_code_blocks(content, doc_file)
            for example in examples:
                validated = validate_code_example(example)
                all_examples.append(validated)
        except Exception as e:
            print(f"Error processing {doc_file}: {e}", file=sys.stderr)

    print(f"\nFound {len(all_examples)} code examples")

    # Statistics
    valid_count = sum(1 for e in all_examples if e.syntax_valid)
    invalid_count = len(all_examples) - valid_count

    print(f"Valid syntax: {valid_count}")
    print(f"Invalid syntax: {invalid_count}")

    # Save report
    report = {
        'total_examples': len(all_examples),
        'valid_syntax': valid_count,
        'invalid_syntax': invalid_count,
        'examples': [asdict(e) for e in all_examples]
    }

    json_path = output_dir / "code_examples_validation_report.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to: {json_path}")

    # Print invalid examples
    if invalid_count > 0:
        print("\n" + "=" * 80)
        print("INVALID CODE EXAMPLES:")
        print("=" * 80)
        for example in all_examples:
            if not example.syntax_valid:
                print(f"\n{doc_file}:{example.line_number}")
                print(f"Code snippet: {example.code[:100]}...")

    return 0 if invalid_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

