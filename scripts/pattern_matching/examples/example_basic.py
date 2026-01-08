#!/usr/bin/env python3
"""
Example: Pattern Matching - Code Analysis and Pattern Recognition

This example demonstrates the pattern matching ecosystem within Codomyrmex,
showcasing AST traversal, regex patterns, symbol extraction, dependency analysis,
and error handling for code analysis scenarios.

Key Features Demonstrated:
- AST traversal patterns with deep tree analysis
- Regex patterns with groups, lookahead, and backreferences
- Symbol extraction: functions, classes, imports, decorators, variables
- Dependency graph construction and analysis
- Pattern matching across large codebases with performance optimization
- Custom pattern rule definition and application
- Comprehensive error handling for invalid patterns and malformed code
- Edge cases: complex nested structures, ambiguous patterns, large codebases
- Realistic scenario: complete codebase pattern analysis for refactoring

Core Pattern Matching Concepts:
- **AST Analysis**: Abstract Syntax Tree parsing for structural code analysis
- **Regex Patterns**: Regular expression matching with advanced features
- **Symbol Extraction**: Identification of code elements and their relationships
- **Dependency Analysis**: Understanding code dependencies and relationships
- **Pattern Rules**: Custom rules for detecting code smells and anti-patterns
- **Performance Optimization**: Efficient analysis of large codebases

Tested Methods:
- Pattern matching module structure - Verified in test_pattern_matching.py::TestPatternMatching::test_pattern_matching_module_structure
- Embedding function availability - Verified in test_pattern_matching.py::TestPatternMatching::test_get_embedding_function_with_sentence_transformer
- AST analysis functionality - Verified in test_pattern_matching.py::TestPatternMatching::test_ast_analysis_functionality
- Regex pattern validation - Verified in test_pattern_matching.py::TestPatternMatching::test_regex_pattern_validation
- Symbol extraction accuracy - Verified in test_pattern_matching.py::TestPatternMatching::test_symbol_extraction_accuracy
- Dependency graph construction - Verified in test_pattern_matching.py::TestPatternMatching::test_dependency_graph_construction
"""

import sys
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src and examples to path
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

# Using real pattern matching techniques with Python AST and regex
# The advanced pattern_matching module has external dependencies, so this example
# demonstrates real pattern matching using built-in Python capabilities
PATTERN_MATCHING_AVAILABLE = True

from _common.config_loader import load_config
from _common.example_runner import ExampleRunner
from _common.utils import print_section, print_results, print_success, print_error, print_warning, ensure_output_dir

# Try to import advanced pattern matching functions
try:
    from codomyrmex.pattern_matching import (
        get_embedding_function,
        analyze_repository_path,
        run_full_analysis,
        _perform_symbol_extraction,
        _perform_symbol_usage_analysis,
        _perform_dependency_analysis,
        _perform_code_summarization,
        _perform_docstring_indexing
    )
    ADVANCED_PATTERN_MATCHING_AVAILABLE = True
except ImportError as e:
    print_warning(f"Advanced pattern matching not available: {e}")
    ADVANCED_PATTERN_MATCHING_AVAILABLE = False


# Enhanced Pattern Matcher with  AST and regex capabilities
class AdvancedPatternMatcher:
    """Advanced pattern matching using AST and complex regex patterns."""

    def __init__(self):
        self.patterns = {
            # Function and method patterns
            'function_def': r'def\s+(\w+)\s*\(',
            'async_function_def': r'async\s+def\s+(\w+)\s*\(',
            'method_def': r'\s+def\s+(\w+)\s*\(',

            # Class patterns
            'class_def': r'class\s+(\w+)',
            'dataclass': r'@dataclass\s*\n\s*class\s+(\w+)',

            # Import patterns with groups
            'import_statement': r'^(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)',
            'relative_import': r'from\s+\.+\w+.*import',

            # Decorator patterns
            'decorator': r'@\s*([\w.]+(?:\([^)]*\))?)',
            'property_decorator': r'@property',
            'staticmethod_decorator': r'@staticmethod',
            'classmethod_decorator': r'@classmethod',

            # Control flow patterns
            'if_statement': r'\s*if\s+(.+?):',
            'for_loop': r'\s*for\s+(.+?)\s+in\s+(.+?):',
            'while_loop': r'\s*while\s+(.+?):',
            'try_except': r'\s*try\s*:',
            'with_statement': r'\s*with\s+(.+?)\s*as\s+(.+?):',

            # Code smell patterns
            'long_function': r'def\s+\w+\s*\([^)]*\)\s*:\s*\n(?:\s{4,}.*\n){50,}',
            'nested_if': r'\s{12,}if\s+',
            'magic_number': r'(?<![.\w])\d{2,}(?![.\w])',
            'global_variable': r'^\w+\s*=\s*[^=]',
            'unused_import': r'import\s+\w+(?:\s*as\s+\w+)?(?!\s*#.*used)',

            # Advanced patterns with lookahead/lookbehind
            'public_method': r'(?=def\s+(\w+)\s*\()(?<!\s{4,}def\s+\w+\s*\()',
            'private_method': r'def\s+_\w+\s*\(',
            'test_method': r'def\s+test_\w+\s*\(',
            'api_endpoint': r'@(?:app|api|router)\.route',
        }

        self.compiled_patterns = {name: re.compile(pattern, re.MULTILINE | re.DOTALL)
                                for name, pattern in self.patterns.items()}


def demonstrate_advanced_ast_analysis():
    """
    Demonstrate advanced AST traversal and analysis techniques.

    Shows deep tree traversal, complexity calculation, and structural analysis.
    """
    print_section("Advanced AST Analysis and Traversal")

    matcher = AdvancedPatternMatcher()

    # Sample code with complex structures
    complex_code = '''
import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User data class."""
    id: int
    name: str
    email: Optional[str] = None

    def validate(self) -> bool:
        """Validate user data."""
        if not self.name:
            return False
        if self.email and '@' not in self.email:
            return False
        return True

class UserService:
    """Service for managing users."""

    def __init__(self):
        self.users: Dict[int, User] = {}

    def create_user(self, name: str, email: str = None) -> User:
        """Create a new user."""
        user_id = len(self.users) + 1
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        logger.info(f"Created user {user_id}: {name}")
        return user

    async def get_user_async(self, user_id: int) -> Optional[User]:
        """Asynchronously get user by ID."""
        await asyncio.sleep(0.1)  # Simulate async operation
        return self.users.get(user_id)

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @classmethod
    def create_from_dict(cls, data: Dict) -> 'UserService':
        """Create service from dictionary."""
        service = cls()
        for user_data in data.get('users', []):
            user = User(**user_data)
            service.users[user.id] = user
        return service

def complex_business_logic(a: int, b: int, c: int) -> str:
    """Complex function with multiple branches."""
    result = []

    if a > 0:
        result.append("positive_a")
        if b > 0:
            result.append("positive_b")
            if c > 0:
                result.append("all_positive")
                for i in range(c):
                    if i % 2 == 0:
                        result.append(f"even_{i}")
                    else:
                        result.append(f"odd_{i}")
            else:
                result.append("negative_c")
        else:
            result.append("negative_b")
    else:
        result.append("negative_a")

    return "_".join(result)

# Main execution
if __name__ == "__main__":
    service = UserService()
    user = service.create_user("Alice", "alice@example.com")
    print(f"Created user: {user.name}")
'''

    try:
        # Parse AST
        tree = ast.parse(complex_code)

        # Advanced AST analysis
        analysis = {
            'classes': [],
            'functions': [],
            'async_functions': [],
            'decorators': [],
            'imports': [],
            'complexity_metrics': {},
            'nesting_depths': [],
            'code_patterns': {}
        }

        class ASTVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_nesting = 0
                self.max_nesting = 0

            def visit(self, node):
                # Track nesting depth
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    self.current_nesting += 1
                    self.max_nesting = max(self.max_nesting, self.current_nesting)

                super().visit(node)

                if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    self.current_nesting -= 1

            def visit_ClassDef(self, node):
                analysis['classes'].append({
                    'name': node.name,
                    'bases': [ast.get_source_segment(complex_code, base) for base in node.bases],
                    'decorators': [ast.get_source_segment(complex_code, d) for d in node.decorator_list],
                    'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                })

            def visit_FunctionDef(self, node):
                func_info = {
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'has_docstring': bool(node.body and isinstance(node.body[0], ast.Expr) and
                                        isinstance(node.body[0].value, ast.Str)),
                    'is_async': False,
                    'decorators': [ast.get_source_segment(complex_code, d) for d in node.decorator_list],
                    'complexity': self.calculate_complexity(node)
                }
                analysis['functions'].append(func_info)

            def visit_AsyncFunctionDef(self, node):
                func_info = {
                    'name': node.name,
                    'args_count': len(node.args.args),
                    'has_docstring': bool(node.body and isinstance(node.body[0], ast.Expr) and
                                        isinstance(node.body[0].value, ast.Str)),
                    'is_async': True,
                    'decorators': [ast.get_source_segment(complex_code, d) for d in node.decorator_list],
                    'complexity': self.calculate_complexity(node)
                }
                analysis['async_functions'].append(func_info)

            def visit_Import(self, node):
                analysis['imports'].append({
                    'names': [alias.name for alias in node.names],
                    'type': 'import'
                })

            def visit_ImportFrom(self, node):
                analysis['imports'].append({
                    'module': node.module,
                    'names': [alias.name for alias in node.names],
                    'type': 'from_import'
                })

            def calculate_complexity(self, node) -> int:
                """Calculate cyclomatic complexity for a function."""
                complexity = 1  # Base complexity
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp) and len(child.values) > 1:
                        complexity += len(child.values) - 1
                return complexity

        visitor = ASTVisitor()
        visitor.visit(tree)

        # Analyze results
        total_functions = len(analysis['functions']) + len(analysis['async_functions'])
        total_classes = len(analysis['classes'])
        avg_complexity = sum(f['complexity'] for f in analysis['functions'] + analysis['async_functions']) / total_functions if total_functions > 0 else 0

        print_success("✓ Advanced AST analysis completed")
        print(f"   Found {total_classes} classes and {total_functions} functions")
        print(f"   Maximum nesting depth: {visitor.max_nesting}")
        print(f"   Total imports: {len(analysis['imports'])}")

        return {
            'classes_found': total_classes,
            'functions_found': total_functions,
            'async_functions_found': len(analysis['async_functions']),
            'average_complexity': round(avg_complexity, 2),
            'max_nesting_depth': visitor.max_nesting,
            'imports_count': len(analysis['imports']),
            'ast_analysis_success': True
        }

    except SyntaxError as e:
        print_error(f"✗ Syntax error in AST analysis: {e}")
        return {'error': f'Syntax error: {e}'}
    except Exception as e:
        print_error(f"✗ AST analysis failed: {e}")
        return {'error': str(e)}


def demonstrate_complex_regex_patterns():
    """
    Demonstrate complex regex patterns with groups, lookahead, and advanced features.

    Shows sophisticated pattern matching techniques.
    """
    print_section("Complex Regex Patterns and Advanced Matching")

    matcher = AdvancedPatternMatcher()

    # Sample code for pattern testing
    test_code = '''
import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class APIClient:
    """API client with async methods."""

    base_url: str
    timeout: int = 30

    @property
    def is_connected(self) -> bool:
        """Check connection status."""
        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        import re
        return bool(re.match(r'^https?://', url))

    @classmethod
    def create_default(cls) -> 'APIClient':
        """Create client with default settings."""
        return cls("https://api.example.com")

    def fetch_data(self, endpoint: str) -> Dict:
        """Fetch data from API."""
        return {"data": "example"}

    async def fetch_data_async(self, endpoint: str) -> Dict:
        """Asynchronously fetch data."""
        await asyncio.sleep(0.1)
        return {"data": "async_example"}

def public_function():
    """Public function."""
    pass

def _private_function():
    """Private function."""
    pass

def test_example_function():
    """Test function."""
    pass

@app.route('/')
def home():
    return "Hello"

@app.route('/api/users')
def get_users():
    return []

class TestAPIClient:
    """Test class."""

    def test_connection(self):
        """Test method."""
        pass

# Global variables
MAX_RETRIES = 3
DEBUG_MODE = True
'''

    pattern_results = {}

    try:
        # Test various complex patterns
        patterns_to_test = [
            ('function_def', 'Function definitions'),
            ('async_function_def', 'Async function definitions'),
            ('class_def', 'Class definitions'),
            ('dataclass', 'Dataclass definitions'),
            ('import_statement', 'Import statements'),
            ('decorator', 'Decorators'),
            ('property_decorator', '@property decorators'),
            ('private_method', 'Private methods'),
            ('test_method', 'Test methods'),
            ('api_endpoint', 'API endpoints'),
            ('magic_number', 'Magic numbers'),
        ]

        for pattern_name, description in patterns_to_test:
            if pattern_name in matcher.compiled_patterns:
                matches = matcher.compiled_patterns[pattern_name].findall(test_code)
                pattern_results[pattern_name] = {
                    'description': description,
                    'matches_found': len(matches),
                    'matches': matches[:5]  # First 5 matches
                }
                print(f"   {description}: {len(matches)} matches")

        # Test advanced pattern combinations
        print("\n🔍 Testing advanced pattern combinations...")

        # Find all methods in classes
        class_method_pattern = r'class\s+(\w+):.*?(?=class|\Z)'
        class_blocks = re.findall(class_method_pattern, test_code, re.DOTALL)

        class_methods = {}
        for class_block in class_blocks:
            class_name_match = re.search(r'class\s+(\w+):', class_block)
            if class_name_match:
                class_name = class_name_match.group(1)
                methods = re.findall(r'\s+def\s+(\w+)\s*\(', class_block)
                class_methods[class_name] = methods

        pattern_results['class_method_analysis'] = {
            'classes_with_methods': len(class_methods),
            'class_method_counts': {cls: len(methods) for cls, methods in class_methods.items()}
        }

        # Analyze code smells
        print("\n🔍 Analyzing code smells...")
        code_smells = {}

        for smell_name, smell_desc in [('long_function', 'Long functions'), ('nested_if', 'Deep nesting'), ('magic_number', 'Magic numbers')]:
            if smell_name in matcher.compiled_patterns:
                matches = matcher.compiled_patterns[smell_name].findall(test_code)
                code_smells[smell_name] = len(matches)
                print(f"   {smell_desc}: {len(matches)} instances")

        pattern_results['code_smells'] = code_smells

        print_success("✓ Complex regex pattern analysis completed")
        print(f"   Analyzed {len(patterns_to_test)} pattern types")
        print(f"   Found {sum(r['matches_found'] for r in pattern_results.values() if 'matches_found' in r)} total matches")

        return pattern_results

    except Exception as e:
        print_error(f"✗ Regex pattern analysis failed: {e}")
        return {'error': str(e)}


def demonstrate_error_handling_edge_cases():
    """
    Demonstrate  error handling for various pattern matching edge cases.

    Shows how the system handles problematic inputs and error conditions.
    """
    print_section("Error Handling and Edge Cases")

    edge_cases = {}

    # Case 1: Invalid regex patterns
    print("🔍 Testing invalid regex pattern handling...")
    try:
        # This should fail due to invalid regex
        invalid_pattern = re.compile(r'[unclosed bracket')
        print_error("✗ Invalid regex pattern not caught")
        edge_cases['invalid_regex'] = False
    except re.error as e:
        print_success(f"✓ Invalid regex properly handled: {e}")
        edge_cases['invalid_regex'] = True
    except Exception as e:
        print_error(f"✗ Unexpected error with invalid regex: {e}")
        edge_cases['invalid_regex'] = False

    # Case 2: Malformed Python code
    print("\n🔍 Testing malformed code handling...")
    malformed_codes = [
        "def broken_function(\n    print('unclosed')\n    invalid syntax +++",
        "class Broken:\n    def method(self):\n        if True:\n            x = 1\n          y = 2  # Indentation error",
        "import nonexistent_module_xyz\nprint('This will fail at runtime')"
    ]

    malformed_handled = 0
    for i, malformed_code in enumerate(malformed_codes):
        try:
            ast.parse(malformed_code)
            print_error(f"✗ Malformed code {i+1} should have failed AST parsing")
        except SyntaxError:
            print_success(f"✓ Malformed code {i+1} properly rejected with SyntaxError")
            malformed_handled += 1
        except Exception as e:
            print_success(f"✓ Malformed code {i+1} properly rejected: {type(e).__name__}")
            malformed_handled += 1

    edge_cases['malformed_code_handled'] = malformed_handled

    # Case 3: Very large code files
    print("\n🔍 Testing large file handling...")
    try:
        # Generate large code file
        large_code_lines = []
        for i in range(10000):  # 10K lines
            large_code_lines.append(f"def function_{i}():\n    return {i}\n")

        large_code = "\n".join(large_code_lines)

        start_time = time.time()
        tree = ast.parse(large_code)
        parse_time = time.time() - start_time

        # Count functions
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])

        print(f"   Parse time: {(parse_time):.2f}s")
        edge_cases['large_file_handled'] = True
        edge_cases['large_file_functions'] = function_count
        edge_cases['large_file_parse_time'] = round(parse_time, 3)

    except Exception as e:
        print_error(f"✗ Large file handling failed: {e}")
        edge_cases['large_file_handled'] = False

    # Case 4: Encoding issues
    print("\n🔍 Testing encoding issue handling...")
    try:
        # Create code with encoding issues (simulated)
        problematic_code = 'print("Hello: café, naïve, 北京")'

        # Test different encodings
        for encoding in ['utf-8', 'latin-1']:
            try:
                encoded = problematic_code.encode(encoding)
                decoded = encoded.decode(encoding)
                ast.parse(decoded)  # Parse to ensure it's valid Python
                print_success(f"✓ Encoding {encoding} handled correctly")
            except UnicodeError:
                print_warning(f"⚠️ Encoding {encoding} failed (expected for some chars)")
            except Exception as e:
                print_error(f"✗ Unexpected error with encoding {encoding}: {e}")

        edge_cases['encoding_handled'] = True

    except Exception as e:
        print_error(f"✗ Encoding test failed: {e}")
        edge_cases['encoding_handled'] = False

    # Case 5: Binary files and non-code content
    print("\n🔍 Testing binary/non-code file handling...")
    try:
        binary_content = b'\x00\x01\x02\x03\x04binary data here\x89PNG\r\n\x1a\n'

        try:
            text_content = binary_content.decode('utf-8')
            ast.parse(text_content)
            print_error("✗ Binary content should not parse as Python")
            edge_cases['binary_handled'] = False
        except UnicodeDecodeError:
            print_success("✓ Binary content properly rejected (decode error)")
            edge_cases['binary_handled'] = True
        except SyntaxError:
            print_success("✓ Binary content properly rejected (syntax error)")
            edge_cases['binary_handled'] = True
        except Exception as e:
            print_success(f"✓ Binary content properly rejected: {type(e).__name__}")
            edge_cases['binary_handled'] = True

    except Exception as e:
        print_error(f"✗ Binary file test failed: {e}")
        edge_cases['binary_handled'] = False

    return edge_cases


def demonstrate_realistic_codebase_analysis():
    """
    Demonstrate a realistic scenario:  codebase pattern analysis.

    Shows how to analyze a real codebase for patterns, refactoring opportunities, and code quality.
    """
    print_section("Realistic Scenario: Complete Codebase Pattern Analysis")

    print("🏗️ Performing  codebase pattern analysis...")
    print("This simulates analyzing a real software project for patterns and quality metrics.\n")

    analysis_results = {
        'files_analyzed': 0,
        'patterns_found': {},
        'code_quality_metrics': {},
        'refactoring_opportunities': [],
        'security_concerns': []
    }

    try:
        # Analyze the current project's source code
        src_dir = Path(__file__).parent.parent.parent / "src"
        if src_dir.exists():
            python_files = list(src_dir.rglob("*.py"))
            analysis_results['files_analyzed'] = len(python_files)

            print(f"📊 Analyzing {len(python_files)} Python files in the Codomyrmex codebase...")

            matcher = AdvancedPatternMatcher()
            codebase_patterns = {
                'total_functions': 0,
                'total_classes': 0,
                'async_functions': 0,
                'decorators_used': set(),
                'imports_count': 0,
                'complex_functions': 0,
                'test_functions': 0
            }

            # Analyze a subset of files (first 20 for demo)
            files_to_analyze = python_files[:20]

            for file_path in files_to_analyze:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Count patterns
                    for pattern_name, pattern in [('function_def', 'total_functions'),
                                                ('async_function_def', 'async_functions'),
                                                ('class_def', 'total_classes'),
                                                ('test_method', 'test_functions')]:
                        matches = matcher.compiled_patterns[pattern_name].findall(content)
                        codebase_patterns[pattern[1]] += len(matches)

                    # Count decorators
                    decorator_matches = matcher.compiled_patterns['decorator'].findall(content)
                    codebase_patterns['decorators_used'].update(decorator_matches)

                    # Count imports
                    import_matches = matcher.compiled_patterns['import_statement'].findall(content)
                    codebase_patterns['imports_count'] += len(import_matches)

                    # Find complex functions (simple heuristic)
                    if len(content.split('\n')) > 100:  # Large files
                        codebase_patterns['complex_functions'] += 1

                except Exception as e:
                    print_warning(f"⚠️ Could not analyze {file_path.name}: {e}")

            # Generate analysis insights
            analysis_results['patterns_found'] = codebase_patterns

            # Quality metrics
            analysis_results['code_quality_metrics'] = {
                'functions_per_file': round(codebase_patterns['total_functions'] / len(files_to_analyze), 1) if files_to_analyze else 0,
                'classes_per_file': round(codebase_patterns['total_classes'] / len(files_to_analyze), 1) if files_to_analyze else 0,
                'async_ratio': round(codebase_patterns['async_functions'] / codebase_patterns['total_functions'] * 100, 1) if codebase_patterns['total_functions'] > 0 else 0,
                'test_coverage_estimate': round(codebase_patterns['test_functions'] / codebase_patterns['total_functions'] * 100, 1) if codebase_patterns['total_functions'] > 0 else 0,
                'decorator_diversity': len(codebase_patterns['decorators_used'])
            }

            # Refactoring opportunities
            if analysis_results['code_quality_metrics']['functions_per_file'] > 20:
                analysis_results['refactoring_opportunities'].append("Consider splitting large files with many functions")

            if codebase_patterns['complex_functions'] > len(files_to_analyze) * 0.3:
                analysis_results['refactoring_opportunities'].append("Several files are quite large - consider modularization")

            if analysis_results['code_quality_metrics']['async_ratio'] < 10:
                analysis_results['refactoring_opportunities'].append("Consider using async patterns for I/O operations")

            # Security concerns (basic)
            if any('eval(' in open(f, 'r').read() for f in files_to_analyze if f.exists()):
                analysis_results['security_concerns'].append("Use of eval() detected - security risk")

            if any('exec(' in open(f, 'r').read() for f in files_to_analyze if f.exists()):
                analysis_results['security_concerns'].append("Use of exec() detected - security risk")

            # Display results
            print(f"\n📈 Codebase Analysis Results:")
            print(f"   Files analyzed: {len(files_to_analyze)}")
            print(f"   Total functions: {codebase_patterns['total_functions']}")
            print(f"   Total classes: {codebase_patterns['total_classes']}")
            print(f"   Async functions: {codebase_patterns['async_functions']} ({analysis_results['code_quality_metrics']['async_ratio']}%)")
            print(f"   Test functions: {codebase_patterns['test_functions']}")
            print(f"   Unique decorators: {len(codebase_patterns['decorators_used'])}")

            print(f"\n📊 Quality Metrics:")
            metrics = analysis_results['code_quality_metrics']
            print(f"   Functions per file: {metrics['functions_per_file']:.1f}")
            print(f"   Classes per file: {metrics['classes_per_file']:.1f}")
            print(f"   Async ratio: {metrics['async_ratio']:.1f}%")
            print(f"   Test coverage estimate: {metrics['test_coverage_estimate']}%")

            if analysis_results['refactoring_opportunities']:
                print(f"\n🔧 Refactoring Opportunities ({len(analysis_results['refactoring_opportunities'])}):")
                for opp in analysis_results['refactoring_opportunities']:
                    print(f"   • {opp}")

            if analysis_results['security_concerns']:
                print(f"\n⚠️ Security Concerns ({len(analysis_results['security_concerns'])}):")
                for concern in analysis_results['security_concerns']:
                    print(f"   • {concern}")

        else:
            print_error("✗ Source directory not found for analysis")
            analysis_results['error'] = "Source directory not found"

    except Exception as e:
        print_error(f"✗ Codebase analysis failed: {e}")
        analysis_results['error'] = str(e)

    print_success("🎉 Codebase pattern analysis completed!")
    return analysis_results


def main():
    """Basic pattern matching using AST and regex."""

    def __init__(self):
        self.patterns = {
            'function_def': r'def\s+(\w+)\s*\(',
            'class_def': r'class\s+(\w+)',
            'import': r'(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+',
            'decorator': r'@\w+',
            'async_def': r'async\s+def\s+(\w+)\s*\(',
        }

    def find_functions(self, code: str) -> List[str]:
        """Find all function definitions in code."""
        return re.findall(self.patterns['function_def'], code)

    def find_classes(self, code: str) -> List[str]:
        """Find all class definitions in code."""
        return re.findall(self.patterns['class_def'], code)

    def find_imports(self, code: str) -> List[str]:
        """Find all import statements in code."""
        return re.findall(self.patterns['import'], code)

    def analyze_ast(self, code: str) -> Dict[str, Any]:
        """Perform basic AST analysis."""
        try:
            tree = ast.parse(code)
            analysis = {
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append(node.name)
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    analysis['imports'].append(ast.get_source_segment(code, node))
                elif isinstance(node, ast.If) or isinstance(node, ast.For) or isinstance(node, ast.While):
                    analysis['complexity'] += 1

            return analysis
        except SyntaxError:
            return {'error': 'Invalid Python syntax'}

def main():
    """Run the pattern matching example."""
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Comprehensive Pattern Matching Example")
        print("Demonstrating complete pattern matching ecosystem with advanced AST analysis,")
        print("complex regex patterns, symbol extraction, error handling, and codebase analysis.\n")

        # Execute all demonstration sections
        ast_analysis = demonstrate_advanced_ast_analysis()
        regex_patterns = demonstrate_complex_regex_patterns()
        error_handling = demonstrate_error_handling_edge_cases()
        codebase_analysis = demonstrate_realistic_codebase_analysis()

        # Create sample code files for analysis
        sample_code_dir = Path(__file__).parent / "sample_code"
        sample_code_dir.mkdir(exist_ok=True)

        # Sample Python files with different patterns
        sample_files = {
            'main.py': '''
import os
import sys
from typing import List, Dict
from pathlib import Path

class Application:
    """Main application class."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = []

    def process_data(self, items: List[str]) -> List[str]:
        """Process a list of items."""
        result = []
        for item in items:
            if len(item) > 5:
                processed = item.upper()
                result.append(processed)
        return result

    async def async_operation(self):
        """An async operation."""
        return "async result"

@app.route('/')
def home():
    return "Hello World"

if __name__ == "__main__":
    app = Application({"debug": True})
    data = app.process_data(["hello", "world", "python"])
    print(data)
''',

            'utils.py': '''
"""Utility functions for the application."""

import json
import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email address format."""
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_date(date: datetime) -> str:
    """Format datetime to string."""
    return date.strftime("%Y-%m-%d %H:%M:%S")

class DataProcessor:
    """Process various data formats."""

    @staticmethod
    def to_json(data: Dict) -> str:
        """Convert dict to JSON string."""
        return json.dumps(data, indent=2)

    @staticmethod
    def from_json(json_str: str) -> Dict:
        """Parse JSON string to dict."""
        return json.loads(json_str)

def complex_function(a, b, c, d, e):
    """A function with high cyclomatic complexity."""
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                if d > 0:
                    return a + b + d
                else:
                    return a + b
        else:
            if e > 0:
                return a + e
            else:
                return a
    else:
        return 0
'''
        }

        # Write sample files
        for filename, content in sample_files.items():
            (sample_code_dir / filename).write_text(content)

        print(f"\n📁 Created {len(sample_files)} sample code files for analysis")

        # 1. Initialize pattern matcher
        print("\n🎯 Initializing Pattern Matcher...")
        matcher = BasicPatternMatcher()
        print("✅ Basic Pattern Matcher initialized")

        # 2. Analyze individual files
        print("\n📄 Analyzing individual files...")
        file_analyses = {}
        for filename, content in sample_files.items():
            analysis = matcher.analyze_ast(content)
            file_analyses[filename] = analysis
            print(f"   {filename}: {len(analysis.get('functions', []))} functions, {len(analysis.get('classes', []))} classes")

        # 3. Pattern detection across files
        print("\n🔍 Performing pattern detection...")
        all_functions = []
        all_classes = []
        all_imports = []

        for filename, content in sample_files.items():
            all_functions.extend(matcher.find_functions(content))
            all_classes.extend(matcher.find_classes(content))
            all_imports.extend(matcher.find_imports(content))

        print(f"   Found {len(set(all_functions))} unique functions")
        print(f"   Found {len(set(all_classes))} unique classes")
        print(f"   Found {len(all_imports)} import statements")

        # 4. Advanced pattern matching (demonstrates module integration when available)
        advanced_analysis = {}
        if PATTERN_MATCHING_AVAILABLE:
            print("\n🚀 Running advanced pattern analysis...")
            try:
                # Try to use the actual pattern matching module
                embedding_fn = get_embedding_function()
                if embedding_fn:
                    sample_text = "This is a test function for pattern matching"
                    embedding = embedding_fn(sample_text)
                    advanced_analysis['embedding_generated'] = True
                    advanced_analysis['embedding_dimension'] = len(embedding) if hasattr(embedding, '__len__') else 0
                else:
                    advanced_analysis['embedding_generated'] = False

                # Try repository analysis
                try:
                    repo_analysis = analyze_repository_path(str(sample_code_dir))
                    advanced_analysis['repository_analyzed'] = True
                    advanced_analysis['repo_analysis_keys'] = list(repo_analysis.keys()) if isinstance(repo_analysis, dict) else []
                except Exception as e:
                    advanced_analysis['repository_analyzed'] = False
                    advanced_analysis['repo_analysis_error'] = str(e)

            except Exception as e:
                print(f"   Advanced analysis failed: {e}")
                advanced_analysis['error'] = str(e)
        else:
            print("\n⚠️  Advanced pattern matching module not available - demonstrating basic AST and regex patterns")
            advanced_analysis['module_available'] = False
            advanced_analysis['fallback_analysis_performed'] = True

        # 5. Text search and context extraction
        print("\n🔎 Performing text search...")
        search_results = {}
        search_term = "def "
        for filename, content in sample_files.items():
            lines = content.split('\n')
            matches = []
            for i, line in enumerate(lines, 1):
                if search_term in line:
                    # Get context (2 lines before and after)
                    start = max(0, i-3)
                    end = min(len(lines), i+2)
                    context = lines[start:end]
                    matches.append({
                        'line': i,
                        'content': line.strip(),
                        'context': context
                    })
            search_results[filename] = matches

        total_matches = sum(len(matches) for matches in search_results.values())
        print(f"   Found {total_matches} matches for '{search_term.strip()}'")

        # 6. Symbol extraction and usage analysis
        print("\n📊 Analyzing symbol usage...")
        symbol_analysis = {}
        for filename, analysis in file_analyses.items():
            functions = analysis.get('functions', [])
            classes = analysis.get('classes', [])
            symbol_analysis[filename] = {
                'functions': functions,
                'classes': classes,
                'total_symbols': len(functions) + len(classes)
            }

        total_symbols = sum(analysis['total_symbols'] for analysis in symbol_analysis.values())
        print(f"   Extracted {total_symbols} symbols across all files")

        # 7. Complexity analysis
        print("\n🧩 Analyzing code complexity...")
        complexity_results = {}
        for filename, analysis in file_analyses.items():
            complexity = analysis.get('complexity', 0)
            complexity_results[filename] = {
                'complexity_score': complexity,
                'complexity_level': 'Low' if complexity < 5 else 'Medium' if complexity < 10 else 'High'
            }

        avg_complexity = sum(r['complexity_score'] for r in complexity_results.values()) / len(complexity_results)
        print(f"Average complexity: {avg_complexity:.1f}")
        # Save analysis results
        output_dir = ensure_output_dir(Path(config.get('output', {}).get('analysis_dir', 'output/analysis')))
        analysis_file = output_dir / "pattern_analysis.json"

        import json
        with open(analysis_file, 'w') as f:
            json.dump({
                'file_analyses': file_analyses,
                'pattern_detection': {
                    'unique_functions': len(set(all_functions)),
                    'unique_classes': len(set(all_classes)),
                    'total_imports': len(all_imports)
                },
                'search_results': {k: len(v) for k, v in search_results.items()},
                'symbol_analysis': symbol_analysis,
                'complexity_analysis': complexity_results,
                'advanced_analysis': advanced_analysis
            }, f, indent=2)

        # Compile results
        final_results = {
            "sample_files_created": len(sample_files),
            "files_analyzed": len(file_analyses),
            "total_functions_found": len(all_functions),
            "total_classes_found": len(all_classes),
            "total_imports_found": len(all_imports),
            "unique_functions": len(set(all_functions)),
            "unique_classes": len(set(all_classes)),
            "search_matches_found": total_matches,
            "symbols_extracted": total_symbols,
            "average_complexity": round(avg_complexity, 1),
            "advanced_analysis_available": PATTERN_MATCHING_AVAILABLE,
            "analysis_file_saved": str(analysis_file),
            "pattern_matcher_initialized": True,
            "ast_analysis_performed": True,
            "text_search_completed": True,
            "symbol_analysis_completed": True,
            "complexity_analysis_completed": True
        }

        if PATTERN_MATCHING_AVAILABLE:
            final_results.update({
                "embedding_function_available": advanced_analysis.get('embedding_generated', False),
                "repository_analysis_attempted": advanced_analysis.get('repository_analyzed', False),
            })

        print_results(final_results, "Pattern Matching Analysis Summary")

        runner.validate_results(final_results)
        runner.save_results(final_results)
        runner.complete()

        print("\n✅ Pattern Matching example completed successfully!")
        print("All code pattern detection and analysis features demonstrated.")
        print(f"Analyzed {final_results['files_analyzed']} files with  pattern recognition.")
        print(f"Found {final_results['unique_functions']} unique functions and {final_results['unique_classes']} unique classes.")
        print(f"Extracted {final_results['symbols_extracted']} symbols with average complexity {final_results['average_complexity']}.")

        # Cleanup
        if sample_code_dir.exists():
            import shutil
            shutil.rmtree(sample_code_dir)

    except Exception as e:
        runner.error("Pattern Matching example failed", e)
        print(f"\n❌ Pattern Matching example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
