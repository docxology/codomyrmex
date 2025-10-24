#!/usr/bin/env python3
"""
Documentation enhancement and docstring generation.

This script enhances existing documentation by:
- Adding missing docstrings to functions and classes
- Improving existing docstrings
- Generating module-level documentation
- Ensuring consistent documentation style
"""

import argparse
import ast
import inspect
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any


class DocumentationEnhancer:
    """Enhanced documentation generation and improvement."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "docstrings_added": 0,
            "docstrings_improved": 0,
            "modules_documented": 0
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        return (file_path.suffix == ".py" and
                not file_path.name.startswith("test_") and
                "__pycache__" not in str(file_path))

    def extract_existing_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract existing docstring from an AST node."""
        if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Str)):
            return node.body[0].value.s

        return None

    def generate_function_docstring(self, func_node: ast.FunctionDef) -> str:
        """Generate a docstring for a function."""
        func_name = func_node.name

        # Extract parameters
        params = []
        for arg in func_node.args.args:
            param_name = arg.arg
            # Try to infer parameter types and descriptions
            params.append(f"    {param_name} : Description of {param_name}")

        # Check return type annotation
        returns = "    Returns: Description of return value"
        if func_node.returns:
            # Try to get type annotation info
            returns = f"    Returns: Description of return value (type: {self._get_type_name(func_node.returns)})"

        docstring = f'''"""Brief description of {func_name}.

Args:
{chr(10).join(params)}

{returns}
"""'''
        return docstring

    def generate_class_docstring(self, class_node: ast.ClassDef) -> str:
        """Generate a docstring for a class."""
        class_name = class_node.name

        docstring = f'''"""Brief description of {class_name}.

This class provides functionality for...

Attributes:
    # Add attribute descriptions here

Methods:
    # Method descriptions will be added automatically
"""'''
        return docstring

    def generate_module_docstring(self, module_path: Path, tree: ast.Module) -> str:
        """Generate a module-level docstring."""
        module_name = module_path.stem

        # Try to infer module purpose from content
        functions = [node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree)
                  if isinstance(node, ast.ClassDef)]

        purpose = self._infer_module_purpose(functions, classes)

        docstring = f'''"""{purpose}

This module provides {module_name} functionality including:
- {len(functions)} functions: {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''}
- {len(classes)} classes: {', '.join(classes[:3])}{'...' if len(classes) > 3 else ''}

Usage:
    from {module_name} import FunctionName, ClassName
    # Example usage here
"""'''
        return docstring

    def _get_type_name(self, type_node: ast.AST) -> str:
        """Get a readable type name from AST type node."""
        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Str):
            return "str"
        elif isinstance(type_node, ast.Num):
            return "int"
        elif isinstance(type_node, ast.List):
            return "list"
        elif isinstance(type_node, ast.Dict):
            return "dict"
        else:
            return "Any"

    def _infer_module_purpose(self, functions: List[str], classes: List[str]) -> str:
        """Infer the purpose of a module from its contents."""
        if functions and "main" in functions:
            return "Main entry point and utility functions"
        elif classes and any("Manager" in cls or "Handler" in cls for cls in classes):
            return "Core business logic and data management"
        elif any("test" in func.lower() for func in functions):
            return "Testing utilities and test helpers"
        elif any("util" in func.lower() for func in functions):
            return "Utility functions and helper methods"
        else:
            return "Core functionality module"

    def enhance_file(self, file_path: Path) -> bool:
        """Enhance documentation in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            # Check if module already has a docstring
            module_docstring = self.extract_existing_docstring(tree)
            needs_module_doc = module_docstring is None

            # Find functions and classes that need docstrings
            functions_needing_docs = []
            classes_needing_docs = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if self.extract_existing_docstring(node) is None:
                        functions_needing_docs.append(node)
                elif isinstance(node, ast.ClassDef):
                    if self.extract_existing_docstring(node) is None:
                        classes_needing_docs.append(node)

            if not (needs_module_doc or functions_needing_docs or classes_needing_docs):
                print(f"  ⏭️  {file_path.name} already has complete documentation")
                return False

            # Generate new content
            lines = content.split('\n')
            modified = False

            # Add module docstring if needed
            if needs_module_doc:
                module_doc = self.generate_module_docstring(file_path, tree)
                # Insert after imports but before first function/class
                insert_pos = 0
                for i, line in enumerate(lines):
                    if (line.strip() and
                        not line.strip().startswith(("import ", "from ", '"""', "'''", "#"))):
                        insert_pos = i
                        break

                lines.insert(insert_pos, module_doc)
                modified = True
                self.stats["modules_documented"] += 1

            # Add function docstrings
            for func_node in functions_needing_docs:
                func_doc = self.generate_function_docstring(func_node)
                # Insert docstring as first statement in function
                func_start_line = func_node.lineno - 1  # Convert to 0-based

                # Find the function definition line
                for i in range(func_start_line, len(lines)):
                    if lines[i].strip().startswith(f"def {func_node.name}"):
                        # Insert docstring after the function definition
                        insert_pos = i + 1
                        # Skip any existing blank lines or comments
                        while (insert_pos < len(lines) and
                               (not lines[insert_pos].strip() or
                                lines[insert_pos].strip().startswith("#"))):
                            insert_pos += 1

                        lines.insert(insert_pos, f'    {func_doc}')
                        modified = True
                        self.stats["docstrings_added"] += 1
                        break

            # Add class docstrings
            for class_node in classes_needing_docs:
                class_doc = self.generate_class_docstring(class_node)
                # Insert docstring as first statement in class
                class_start_line = class_node.lineno - 1  # Convert to 0-based

                # Find the class definition line
                for i in range(class_start_line, len(lines)):
                    if lines[i].strip().startswith(f"class {class_node.name}"):
                        # Insert docstring after the class definition
                        insert_pos = i + 1
                        # Skip any existing blank lines or comments
                        while (insert_pos < len(lines) and
                               (not lines[insert_pos].strip() or
                                lines[insert_pos].strip().startswith("#"))):
                            insert_pos += 1

                        lines.insert(insert_pos, f'    {class_doc}')
                        modified = True
                        self.stats["docstrings_added"] += 1
                        break

            if modified and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

            self.stats["files_processed"] += 1
            if modified:
                status = " (dry run)" if self.dry_run else ""
                print(f"  ✅ Enhanced documentation in {file_path.name}{status}")

            return modified

        except Exception as e:
            print(f"  ❌ Error enhancing {file_path}: {e}")
            return False

    def process_directory(self, directory: Path, recursive: bool = True):
        """Process all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if self.should_process_file(file_path):
                self.enhance_file(file_path)

    def print_summary(self):
        """Print processing summary."""
        print("\n📊 Documentation Enhancement Summary:")
        print(f"  Files processed: {self.stats['files_processed']}")
        print(f"  Docstrings added: {self.stats['docstrings_added']}")
        print(f"  Modules documented: {self.stats['modules_documented']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Enhance Python documentation with docstrings")
    parser.add_argument("--path", default="src/codomyrmex", help="Path to process")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", help="Process a single file")

    args = parser.parse_args()

    print("📚 Codomyrmex Documentation Enhancer")
    print("=" * 45)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    enhancer = DocumentationEnhancer(dry_run=args.dry_run)
    target_path = Path(args.path)

    if args.file:
        file_path = Path(args.file)
        if enhancer.should_process_file(file_path):
            enhancer.enhance_file(file_path)
    elif target_path.is_file():
        if enhancer.should_process_file(target_path):
            enhancer.enhance_file(target_path)
    elif target_path.is_dir():
        enhancer.process_directory(target_path, args.recursive)
    else:
        print(f"❌ Path not found: {args.path}")
        return 1

    enhancer.print_summary()

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply enhancements")
    return 0


if __name__ == "__main__":
    exit(main())
