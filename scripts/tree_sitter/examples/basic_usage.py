#!/usr/bin/env python3
"""Tree-Sitter Module - Comprehensive Usage Script.

Demonstrates code parsing with tree-sitter for syntax analysis,
with full configurability, unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --language python        # Specific language
    python basic_usage.py --verbose                # Verbose output
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class TreeSitterScript(ScriptBase):
    """Comprehensive tree-sitter module demonstration."""

    def __init__(self):
        super().__init__(
            name="tree_sitter_usage",
            description="Demonstrate and test tree-sitter code parsing",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add tree-sitter-specific arguments."""
        group = parser.add_argument_group("Tree-Sitter Options")
        group.add_argument(
            "--language", default="python",
            choices=["python", "javascript", "typescript", "go", "rust", "java", "c", "cpp"],
            help="Target language for parsing (default: python)"
        )
        group.add_argument(
            "--source-file", type=Path,
            help="Source file to parse (uses built-in samples if not provided)"
        )
        group.add_argument(
            "--query", type=str,
            help="Tree-sitter query pattern to execute"
        )
        group.add_argument(
            "--benchmark-iterations", type=int, default=100,
            help="Number of iterations for parsing benchmark (default: 100)"
        )
        group.add_argument(
            "--show-ast", action="store_true",
            help="Display full AST structure"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute tree-sitter demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "language": args.language,
            "parser_tests": {},
            "query_tests": {},
        }

        if config.dry_run:
            self.log_info(f"Would parse code in language: {args.language}")
            self.log_info(f"Would run {args.benchmark_iterations} benchmark iterations")
            results["dry_run"] = True
            return results

        # Import tree_sitter module (after dry_run check)
        from codomyrmex.tree_sitter import TreeSitterParser, LanguageManager

        # Sample code for different languages
        sample_code = self._get_sample_code(args.language)

        # Test 1: LanguageManager initialization
        self.log_info(f"\n1. Testing LanguageManager for '{args.language}'")
        try:
            lang_manager = LanguageManager()
            available_languages = lang_manager.list_available()

            results["language_manager"] = {
                "available_languages": available_languages,
                "target_language": args.language,
                "initialized": True,
            }
            results["tests_passed"] += 1
            self.log_success(f"LanguageManager initialized, {len(available_languages)} languages available")
        except Exception as e:
            self.log_error(f"LanguageManager initialization failed: {e}")
            results["language_manager"] = {"error": str(e)}
        results["tests_run"] += 1

        # Test 2: Parser creation
        self.log_info("\n2. Testing TreeSitterParser creation")
        try:
            parser = TreeSitterParser(language=args.language)
            results["parser_tests"]["creation"] = {
                "language": args.language,
                "success": True,
            }
            results["tests_passed"] += 1
            self.log_success(f"TreeSitterParser created for {args.language}")
        except Exception as e:
            self.log_error(f"Parser creation failed: {e}")
            results["parser_tests"]["creation"] = {"error": str(e)}
            # Cannot continue without parser
            results["tests_run"] += 1
            return results
        results["tests_run"] += 1

        # Test 3: Source code parsing
        self.log_info("\n3. Testing source code parsing")
        try:
            # Use provided file or sample code
            if args.source_file and args.source_file.exists():
                source = args.source_file.read_text()
                source_type = "file"
            else:
                source = sample_code
                source_type = "sample"

            start_time = time.perf_counter()
            tree = parser.parse(source)
            parse_time = (time.perf_counter() - start_time) * 1000

            root_node = tree.root_node
            node_count = self._count_nodes(root_node)

            results["parser_tests"]["parsing"] = {
                "source_type": source_type,
                "source_length": len(source),
                "parse_time_ms": parse_time,
                "root_type": root_node.type,
                "node_count": node_count,
                "has_errors": root_node.has_error,
            }
            results["tests_passed"] += 1
            self.log_success(f"Parsed {len(source)} chars in {parse_time:.2f}ms, {node_count} nodes")

            # Show AST if requested
            if args.show_ast:
                self.log_info("\n   AST Structure:")
                self._print_ast(root_node, indent=3)

        except Exception as e:
            self.log_error(f"Parsing failed: {e}")
            results["parser_tests"]["parsing"] = {"error": str(e)}
        results["tests_run"] += 1

        # Test 4: Query execution
        self.log_info("\n4. Testing tree-sitter queries")
        try:
            # Use provided query or default queries based on language
            queries = self._get_default_queries(args.language, args.query)
            query_results = []

            for query_name, query_pattern in queries.items():
                try:
                    matches = parser.query(tree, query_pattern)
                    query_results.append({
                        "name": query_name,
                        "pattern": query_pattern,
                        "match_count": len(matches),
                        "success": True,
                    })
                    self.log_info(f"   Query '{query_name}': {len(matches)} matches")
                except Exception as e:
                    query_results.append({
                        "name": query_name,
                        "pattern": query_pattern,
                        "error": str(e),
                        "success": False,
                    })

            results["query_tests"] = {
                "queries_run": len(queries),
                "results": query_results,
            }
            results["tests_passed"] += 1
            self.log_success(f"Executed {len(queries)} queries")
        except Exception as e:
            self.log_error(f"Query execution failed: {e}")
            results["query_tests"] = {"error": str(e)}
        results["tests_run"] += 1

        # Test 5: Incremental parsing
        self.log_info("\n5. Testing incremental parsing")
        try:
            # Modify source and re-parse
            modified_source = source + "\n# Added comment"

            start_time = time.perf_counter()
            modified_tree = parser.parse(modified_source, old_tree=tree)
            incremental_time = (time.perf_counter() - start_time) * 1000

            results["parser_tests"]["incremental"] = {
                "original_length": len(source),
                "modified_length": len(modified_source),
                "incremental_time_ms": incremental_time,
                "speedup_vs_full": parse_time / incremental_time if incremental_time > 0 else float('inf'),
            }
            results["tests_passed"] += 1
            self.log_success(f"Incremental parse in {incremental_time:.2f}ms")
        except Exception as e:
            self.log_error(f"Incremental parsing failed: {e}")
            results["parser_tests"]["incremental"] = {"error": str(e)}
        results["tests_run"] += 1

        # Test 6: Parsing performance benchmark
        self.log_info(f"\n6. Performance benchmark ({args.benchmark_iterations} iterations)")
        try:
            parse_times = []
            for _ in range(args.benchmark_iterations):
                start_time = time.perf_counter()
                parser.parse(sample_code)
                parse_times.append((time.perf_counter() - start_time) * 1000)

            avg_time = sum(parse_times) / len(parse_times)
            min_time = min(parse_times)
            max_time = max(parse_times)

            results["benchmark"] = {
                "iterations": args.benchmark_iterations,
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "throughput_ops_per_sec": 1000 / avg_time if avg_time > 0 else float('inf'),
            }
            results["tests_passed"] += 1
            self.log_success(f"Benchmark: avg={avg_time:.3f}ms, min={min_time:.3f}ms, max={max_time:.3f}ms")
        except Exception as e:
            self.log_error(f"Benchmark failed: {e}")
            results["benchmark"] = {"error": str(e)}
        results["tests_run"] += 1

        # Test 7: Node traversal
        self.log_info("\n7. Testing AST node traversal")
        try:
            node_types = {}
            self._collect_node_types(root_node, node_types)

            results["traversal"] = {
                "unique_node_types": len(node_types),
                "node_type_counts": node_types,
                "most_common": max(node_types.items(), key=lambda x: x[1]) if node_types else None,
            }
            results["tests_passed"] += 1
            self.log_success(f"Found {len(node_types)} unique node types")
        except Exception as e:
            self.log_error(f"Traversal failed: {e}")
            results["traversal"] = {"error": str(e)}
        results["tests_run"] += 1

        # Summary
        results["summary"] = {
            "tests_passed": results["tests_passed"],
            "tests_run": results["tests_run"],
            "language": args.language,
        }

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        if "benchmark" in results and "throughput_ops_per_sec" in results["benchmark"]:
            self.add_metric("parsing_throughput", results["benchmark"]["throughput_ops_per_sec"])

        return results

    def _get_sample_code(self, language: str) -> str:
        """Get sample code for the specified language."""
        samples = {
            "python": '''
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """Simple calculator class."""

    def __init__(self, initial: float = 0):
        self.value = initial

    def add(self, x: float) -> float:
        self.value += x
        return self.value

if __name__ == "__main__":
    print(fibonacci(10))
''',
            "javascript": '''
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

class Calculator {
    constructor(initial = 0) {
        this.value = initial;
    }

    add(x) {
        this.value += x;
        return this.value;
    }
}

console.log(fibonacci(10));
''',
            "typescript": '''
function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

class Calculator {
    private value: number;

    constructor(initial: number = 0) {
        this.value = initial;
    }

    add(x: number): number {
        this.value += x;
        return this.value;
    }
}

console.log(fibonacci(10));
''',
            "go": '''
package main

import "fmt"

func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

type Calculator struct {
    value float64
}

func (c *Calculator) Add(x float64) float64 {
    c.value += x
    return c.value
}

func main() {
    fmt.Println(fibonacci(10))
}
''',
            "rust": '''
fn fibonacci(n: u32) -> u32 {
    if n <= 1 {
        return n;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

struct Calculator {
    value: f64,
}

impl Calculator {
    fn new(initial: f64) -> Self {
        Calculator { value: initial }
    }

    fn add(&mut self, x: f64) -> f64 {
        self.value += x;
        self.value
    }
}

fn main() {
    println!("{}", fibonacci(10));
}
''',
            "java": '''
public class Main {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    public static void main(String[] args) {
        System.out.println(fibonacci(10));
    }
}

class Calculator {
    private double value;

    public Calculator(double initial) {
        this.value = initial;
    }

    public double add(double x) {
        this.value += x;
        return this.value;
    }
}
''',
            "c": '''
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

typedef struct {
    double value;
} Calculator;

void calculator_init(Calculator *c, double initial) {
    c->value = initial;
}

double calculator_add(Calculator *c, double x) {
    c->value += x;
    return c->value;
}

int main() {
    printf("%d\\n", fibonacci(10));
    return 0;
}
''',
            "cpp": '''
#include <iostream>

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

class Calculator {
private:
    double value;

public:
    Calculator(double initial = 0) : value(initial) {}

    double add(double x) {
        value += x;
        return value;
    }
};

int main() {
    std::cout << fibonacci(10) << std::endl;
    return 0;
}
''',
        }
        return samples.get(language, samples["python"])

    def _get_default_queries(self, language: str, custom_query: Optional[str] = None) -> Dict[str, str]:
        """Get default queries for the language."""
        queries = {}

        if custom_query:
            queries["custom"] = custom_query

        # Language-specific queries
        if language == "python":
            queries.update({
                "functions": "(function_definition name: (identifier) @name)",
                "classes": "(class_definition name: (identifier) @name)",
                "imports": "(import_statement) @import",
            })
        elif language in ["javascript", "typescript"]:
            queries.update({
                "functions": "(function_declaration name: (identifier) @name)",
                "classes": "(class_declaration name: (identifier) @name)",
                "arrow_functions": "(arrow_function) @arrow",
            })
        elif language == "go":
            queries.update({
                "functions": "(function_declaration name: (identifier) @name)",
                "structs": "(type_declaration (type_spec name: (type_identifier) @name))",
            })
        elif language == "rust":
            queries.update({
                "functions": "(function_item name: (identifier) @name)",
                "structs": "(struct_item name: (type_identifier) @name)",
            })
        elif language == "java":
            queries.update({
                "methods": "(method_declaration name: (identifier) @name)",
                "classes": "(class_declaration name: (identifier) @name)",
            })
        elif language in ["c", "cpp"]:
            queries.update({
                "functions": "(function_definition declarator: (function_declarator declarator: (identifier) @name))",
                "structs": "(struct_specifier name: (type_identifier) @name)",
            })

        return queries

    def _count_nodes(self, node) -> int:
        """Count total nodes in the tree."""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def _collect_node_types(self, node, types: Dict[str, int]):
        """Collect node type counts."""
        types[node.type] = types.get(node.type, 0) + 1
        for child in node.children:
            self._collect_node_types(child, types)

    def _print_ast(self, node, indent: int = 0):
        """Print AST structure."""
        prefix = " " * indent
        text = node.text[:50].decode('utf-8') if node.text else ""
        text = text.replace('\n', '\\n')
        self.log_info(f"{prefix}{node.type}: {text}")
        for child in node.children[:5]:  # Limit children to avoid too much output
            self._print_ast(child, indent + 2)
        if len(node.children) > 5:
            self.log_info(f"{prefix}  ... ({len(node.children) - 5} more children)")


if __name__ == "__main__":
    script = TreeSitterScript()
    sys.exit(script.execute())
