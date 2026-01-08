from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import ast
import logging
import re
import sys

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging














#!/usr/bin/env python3
"""
API Specification Verification Tool.

This script verifies that API_SPECIFICATION.md files match actual code signatures.
"""


try:

    setup_logging()
    logger = get_logger(__name__)
except ImportError:

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class APIVerifier:
    """Verifies API specifications against actual code."""

    def __init__(self, repo_root: Path):
        """Initialize verifier."""
        self.repo_root = repo_root.resolve()
        self.src_path = self.repo_root / "src" / "codomyrmex"
        self.mismatches: List[Dict[str, str]] = []
        self.missing_in_code: List[str] = []
        self.missing_in_docs: List[str] = []

    def extract_function_signature_from_docs(self, api_spec_path: Path) -> Dict[str, str]:
        """Extract function signatures from API_SPECIFICATION.md."""
        signatures = {}

        if not api_spec_path.exists():
            return signatures

        try:
            content = api_spec_path.read_text(encoding="utf-8")

            # Pattern to match function signatures like:
            # `generate_code_snippet(prompt: str, language: str, ...) -> dict`
            pattern = r"`([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*(?:->\s*([^`]+))?`"

            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                params = match.group(2)
                return_type = match.group(3) if match.group(3) else "None"

                # Normalize signature
                normalized = self.normalize_signature(func_name, params, return_type)
                signatures[func_name] = normalized

        except Exception as e:
            logger.error(f"Error parsing API spec {api_spec_path}: {e}")

        return signatures

    def normalize_signature(self, func_name: str, params: str, return_type: str) -> str:
        """Normalize function signature for comparison."""
        # Remove extra whitespace
        params = re.sub(r"\s+", " ", params.strip())
        return_type = return_type.strip() if return_type else "None"

        # Sort parameters (optional: can be disabled for order-sensitive comparison)
        # For now, keep order as is

        return f"{func_name}({params}) -> {return_type}"

    def extract_function_signature_from_code(
        self, module_path: Path, func_name: str
    ) -> Optional[str]:
        """Extract actual function signature from Python code."""
        signatures = []

        # Search all Python files in the module
        for py_file in module_path.rglob("*.py"):
            if py_file.name.startswith("test_"):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == func_name:
                        # Extract signature
                        sig = self.ast_to_signature(node)
                        signatures.append(sig)

            except SyntaxError:
                continue
            except Exception as e:
                logger.warning(f"Error parsing {py_file}: {e}")

        if len(signatures) == 1:
            return signatures[0]
        elif len(signatures) > 1:
            logger.warning(f"Multiple definitions of {func_name} found")
            return signatures[0]  # Return first match
        else:
            return None

    def ast_to_signature(self, node: ast.FunctionDef) -> str:
        """Convert AST function node to signature string."""
        params = []

        # Handle args
        for arg in node.args.args:
            param_name = arg.arg
            if arg.annotation:
                param_type = ast.unparse(arg.annotation) if hasattr(ast, "unparse") else self.annotation_to_string(arg.annotation)
            else:
                param_type = "Any"

            # Check for default value
            default_idx = len(node.args.args) - len(node.args.defaults) + node.args.args.index(arg)
            if default_idx < len(node.args.defaults):
                default = node.args.defaults[default_idx]
                default_str = ast.unparse(default) if hasattr(ast, "unparse") else "?"
                params.append(f"{param_name}: {param_type} = {default_str}")
            else:
                params.append(f"{param_name}: {param_type}")

        # Handle return type
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, "unparse") else self.annotation_to_string(node.returns)
        else:
            return_type = "None"

        params_str = ", ".join(params)
        return f"{node.name}({params_str}) -> {return_type}"

    def annotation_to_string(self, node: ast.expr) -> str:
        """Convert annotation node to string (fallback for Python < 3.9)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Str):  # Python < 3.8
            return node.s
        else:
            return "Any"

    def get_all_public_functions(self, module_path: Path) -> Set[str]:
        """Get all public functions from a module."""
        functions = set()

        for py_file in module_path.rglob("*.py"):
            if py_file.name.startswith("test_") or py_file.name.startswith("_"):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("_"):  # Public functions only
                            functions.add(node.name)

            except SyntaxError:
                continue
            except Exception as e:
                logger.warning(f"Error parsing {py_file}: {e}")

        return functions

    def compare_signatures(self, doc_sig: str, code_sig: str) -> bool:
        """Compare two function signatures (simplified comparison)."""
        # Extract function name and parameters
        doc_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)\s*->\s*(.+)", doc_sig)
        code_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)\s*->\s*(.+)", code_sig)

        if not doc_match or not code_match:
            return False

        doc_name, doc_params, doc_return = doc_match.groups()
        code_name, code_params, code_return = code_match.groups()

        if doc_name != code_name:
            return False

        # Compare parameters (simplified - just check count and names)
        doc_param_names = [p.split(":")[0].strip() for p in doc_params.split(",") if p.strip()]
        code_param_names = [p.split(":")[0].strip() for p in code_params.split(",") if p.strip()]

        if len(doc_param_names) != len(code_param_names):
            return False

        # Check if parameter names match (order matters)
        for doc_param, code_param in zip(doc_param_names, code_param_names):
            if doc_param != code_param:
                return False

        return True

    def verify_module(self, module_name: str) -> Dict[str, any]:
        """Verify API spec for a single module."""
        module_path = self.src_path / module_name
        api_spec_path = module_path / "API_SPECIFICATION.md"

        if not api_spec_path.exists():
            logger.warning(f"No API_SPECIFICATION.md found for {module_name}")
            return {
                "module": module_name,
                "status": "missing_spec",
                "mismatches": [],
                "missing_in_code": [],
                "missing_in_docs": [],
            }

        # Extract signatures from docs
        doc_signatures = self.extract_function_signature_from_docs(api_spec_path)

        # Extract signatures from code
        mismatches = []
        missing_in_code = []

        for func_name, doc_sig in doc_signatures.items():
            code_sig = self.extract_function_signature_from_code(module_path, func_name)

            if not code_sig:
                missing_in_code.append(func_name)
            elif not self.compare_signatures(doc_sig, code_sig):
                mismatches.append(
                    {
                        "function": func_name,
                        "documented": doc_sig,
                        "actual": code_sig,
                    }
                )

        # Find functions in code but not in docs
        all_functions = self.get_all_public_functions(module_path)
        missing_in_docs = [f for f in all_functions if f not in doc_signatures]

        return {
            "module": module_name,
            "status": "ok" if not mismatches and not missing_in_code else "mismatch",
            "mismatches": mismatches,
            "missing_in_code": missing_in_code,
            "missing_in_docs": missing_in_docs,
        }

    def verify_all_modules(self) -> Dict[str, any]:
        """Verify all modules with API specifications."""
        results = {}
        total_mismatches = 0
        total_missing_in_code = 0
        total_missing_in_docs = 0

        # Find all modules
        if not self.src_path.exists():
            logger.error(f"Source path not found: {self.src_path}")
            return results

        for item in self.src_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name != "output":
                module_result = self.verify_module(item.name)
                results[item.name] = module_result

                total_mismatches += len(module_result["mismatches"])
                total_missing_in_code += len(module_result["missing_in_code"])
                total_missing_in_docs += len(module_result["missing_in_docs"])

        return {
            "results": results,
            "summary": {
                "total_modules": len(results),
                "total_mismatches": total_mismatches,
                "total_missing_in_code": total_missing_in_code,
                "total_missing_in_docs": total_missing_in_docs,
            },
        }


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    verifier = APIVerifier(repo_root)

    logger.info("Verifying API specifications...")
    results = verifier.verify_all_modules()

    # Print summary
    print("\n" + "=" * 60)
    print("API Specification Verification Results")
    print("=" * 60)
    print(f"\nModules checked: {results['summary']['total_modules']}")
    print(f"Signature mismatches: {results['summary']['total_mismatches']}")
    print(f"Functions documented but not in code: {results['summary']['total_missing_in_code']}")
    print(f"Functions in code but not documented: {results['summary']['total_missing_in_docs']}")

    # Show details for modules with issues
    has_issues = False
    for module_name, result in results["results"].items():
        if result["status"] != "ok":
            has_issues = True
            print(f"\n❌ {module_name}:")
            if result["mismatches"]:
                print("  Signature mismatches:")
                for mismatch in result["mismatches"][:5]:  # Show first 5
                    print(f"    - {mismatch['function']}")
                    print(f"      Documented: {mismatch['documented']}")
                    print(f"      Actual: {mismatch['actual']}")
            if result["missing_in_code"]:
                print(f"  Missing in code: {', '.join(result['missing_in_code'][:5])}")
            if result["missing_in_docs"]:
                print(f"  Missing in docs: {', '.join(result['missing_in_docs'][:5])}")

    if not has_issues:
        print("\n✅ All API specifications match code!")

    return 1 if has_issues else 0


if __name__ == "__main__":
    sys.exit(main())

