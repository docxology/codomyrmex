#!/usr/bin/env python3
"""
Advanced import management and dependency resolution.

This script performs comprehensive import analysis including:
- Detecting unused imports
- Finding missing imports
- Circular import detection
- Import optimization suggestions
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import argparse
import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


class AdvancedImportAnalyzer:
    """Advanced import analysis and optimization."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "files_analyzed": 0,
            "unused_imports_found": 0,
            "missing_imports_found": 0,
            "circular_imports_found": 0,
            "optimizations_suggested": 0
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        return (file_path.suffix == ".py" and
                not file_path.name.startswith("test_") and
                "__pycache__" not in str(file_path))

    def analyze_imports(self, file_path: Path) -> Dict[str, any]:
        """Comprehensive import analysis for a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            # Extract all import statements
            imports = self._extract_imports_from_ast(tree)

            # Find all names used in the code
            used_names = self._find_used_names(tree)

            # Analyze imports vs usage
            unused_imports = self._find_unused_imports(imports, used_names)

            # Check for missing imports (names used but not imported)
            missing_imports = self._find_missing_imports(used_names, imports, file_path)

            # Check for potential circular imports
            circular_imports = self._check_circular_imports(file_path, imports)

            return {
                "imports": imports,
                "used_names": used_names,
                "unused_imports": unused_imports,
                "missing_imports": missing_imports,
                "circular_imports": circular_imports,
                "suggestions": self._generate_suggestions(unused_imports, missing_imports, circular_imports)
            }

        except SyntaxError as e:
            return {"error": f"Syntax error: {e}"}
        except Exception as e:
            return {"error": f"Analysis error: {e}"}

    def _extract_imports_from_ast(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Extract import information from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "name": alias.asname or alias.name,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from",
                        "module": node.module or "",
                        "name": alias.name,
                        "asname": alias.asname,
                        "line": node.lineno
                    })

        return imports

    def _find_used_names(self, tree: ast.AST) -> Set[str]:
        """Find all names used in the code."""
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For attributes like module.function, add the module name
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        return used_names

    def _find_unused_imports(self, imports: List[Dict], used_names: Set[str]) -> List[Dict]:
        """Find imports that are not used."""
        unused = []

        for imp in imports:
            # Check if the imported name is used
            if imp["type"] == "import":
                if imp["name"] not in used_names:
                    unused.append(imp)
            elif imp["type"] == "from":
                if imp["asname"]:
                    if imp["asname"] not in used_names:
                        unused.append(imp)
                else:
                    if imp["name"] not in used_names:
                        unused.append(imp)

        return unused

    def _find_missing_imports(self, used_names: Set[str], imports: List[Dict], file_path: Path) -> List[str]:
        """Find names that are used but not imported."""
        imported_names = set()

        for imp in imports:
            if imp["type"] == "import":
                imported_names.add(imp["name"])
            elif imp["type"] == "from":
                if imp["asname"]:
                    imported_names.add(imp["asname"])
            else:
                    imported_names.add(imp["name"])

        # Common built-in names that don't need imports
        builtins = {
            'print', 'len', 'range', 'enumerate', 'zip', 'list', 'dict', 'str',
            'int', 'float', 'bool', 'set', 'tuple', 'type', 'isinstance',
            'hasattr', 'getattr', 'setattr', 'delattr', 'open', 'file',
            'input', 'raw_input', 'Exception', 'BaseException', 'KeyboardInterrupt',
            'SystemExit', 'GeneratorExit', 'StopIteration', 'ArithmeticError',
            'AssertionError', 'AttributeError', 'BufferError', 'EOFError',
            'ImportError', 'LookupError', 'MemoryError', 'NameError', 'OSError',
            'ReferenceError', 'RuntimeError', 'SyntaxError', 'SystemError',
            'TypeError', 'ValueError', 'Warning', 'UserWarning', 'DeprecationWarning',
            'PendingDeprecationWarning', 'SyntaxWarning', 'RuntimeWarning',
            'FutureWarning', 'ImportWarning', 'UnicodeWarning', 'BytesWarning'
        }

        missing = []
        for name in used_names:
            if (name not in imported_names and
                name not in builtins and
                not name.startswith('_')):
                missing.append(name)

        return list(set(missing))  # Remove duplicates

    def _check_circular_imports(self, file_path: Path, imports: List[Dict]) -> List[str]:
        """Check for potential circular imports."""
        circular = []

        # Get the module name from file path
        module_name = self._get_module_name(file_path)

        for imp in imports:
            if imp["type"] == "from" and imp["module"]:
                # Check if importing from a related module that might import back
                imported_module = imp["module"]
                if (imported_module.startswith(module_name.split('.')[0]) or
                    module_name.startswith(imported_module.split('.')[0])):
                    circular.append(imported_module)

        return list(set(circular))

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        # This is a simplified version - in practice you'd need more sophisticated logic
        rel_path = file_path.relative_to(Path("src"))
        module_parts = rel_path.with_suffix("").parts
        return ".".join(module_parts)

    def _generate_suggestions(self, unused: List[Dict], missing: List[str], circular: List[str]) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []

        if unused:
            suggestions.append(f"Remove {len(unused)} unused imports")
            self.stats["unused_imports_found"] += len(unused)

        if missing:
            suggestions.append(f"Add imports for {len(missing)} missing names: {', '.join(missing[:5])}")
            if len(missing) > 5:
                suggestions[-1] += f" and {len(missing) - 5} more"
            self.stats["missing_imports_found"] += len(missing)

        if circular:
            suggestions.append(f"Review {len(circular)} potential circular imports: {', '.join(circular)}")
            self.stats["circular_imports_found"] += len(circular)

        if suggestions:
            self.stats["optimizations_suggested"] += len(suggestions)

        return suggestions

    def analyze_file(self, file_path: Path) -> bool:
        """Analyze a single file and report findings."""
        analysis = self.analyze_imports(file_path)

        if "error" in analysis:
            print(f"  ❌ Error analyzing {file_path.name}: {analysis['error']}")
            return False

        print(f"\n📄 {file_path.name}")
        print(f"  Imports: {len(analysis['imports'])}")
        print(f"  Used names: {len(analysis['used_names'])}")

        if analysis['unused_imports']:
            print(f"  ❌ Unused imports: {len(analysis['unused_imports'])}")
            for imp in analysis['unused_imports'][:3]:  # Show first 3
                print(f"    Line {imp['line']}: {imp['module'] or imp['name']}")

        if analysis['missing_imports']:
            print(f"  ⚠️  Missing imports: {len(analysis['missing_imports'])}")
            for name in analysis['missing_imports'][:3]:  # Show first 3
                print(f"    {name}")

        if analysis['circular_imports']:
            print(f"  ⚠️  Potential circular imports: {len(analysis['circular_imports'])}")
            for module in analysis['circular_imports'][:3]:  # Show first 3
                print(f"    {module}")

        if analysis['suggestions']:
            print(f"  💡 Suggestions: {len(analysis['suggestions'])}")
            for suggestion in analysis['suggestions']:
                print(f"    • {suggestion}")

        self.stats["files_analyzed"] += 1
        return True

    def process_directory(self, directory: Path, recursive: bool = True):
        """Process all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if self.should_process_file(file_path):
                self.analyze_file(file_path)

    def print_summary(self):
        """Print analysis summary."""
        print("-" * 50)
        print("📊 Advanced Import Analysis Summary:")
        print(f"  Unused imports found: {self.stats['unused_imports_found']}")
        print(f"  Missing imports found: {self.stats['missing_imports_found']}")
        print(f"  Potential circular imports: {self.stats['circular_imports_found']}")
        print(f"  Optimizations suggested: {self.stats['optimizations_suggested']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Advanced import analysis and optimization")
    parser.add_argument("--path", default="src/codomyrmex", help="Path to analyze")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process subdirectories")
    parser.add_argument("--file", help="Analyze a single file")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")

    args = parser.parse_args()

    print("🔍 Codomyrmex Advanced Import Analyzer")
    print("=" * 50)

    analyzer = AdvancedImportAnalyzer()
    target_path = Path(args.path)

    if args.file:
        file_path = Path(args.file)
        if analyzer.should_process_file(file_path):
            analyzer.analyze_file(file_path)
    elif target_path.is_file():
        if analyzer.should_process_file(target_path):
            analyzer.analyze_file(target_path)
    elif target_path.is_dir():
        analyzer.process_directory(target_path, args.recursive)
    else:
        print(f"❌ Path not found: {args.path}")
        return 1

    analyzer.print_summary()
    return 0


if __name__ == "__main__":
    exit(main())