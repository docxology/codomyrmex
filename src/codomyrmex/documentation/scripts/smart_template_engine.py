from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import argparse
import ast
import inspect
import json
import logging
import sys

from dataclasses import dataclass, asdict
import importlib

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging








































"""
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class APIFunction:
    """



    #!/usr/bin/env python3
    """

Smart Template Engine for Codomyrmex Documentation.

Analyzes Python modules to extract API information, generate code examples,
infer relationships, and populate documentation templates with real content.
"""


try:
    setup_logging()


logger = get_logger(__name__)

Represents an API function."""
    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, str]]
    returns: str
    example: str
    line_number: int


@dataclass
class ModuleAnalysis:
    """Analysis results for a module."""
    module_path: str
    module_name: str
    docstring: str
    public_functions: List[APIFunction]
    public_classes: List[str]
    imports: List[str]
    relationships: List[Dict[str, str]]
    architecture_diagram: str


class SmartTemplateEngine:
    """Intelligent documentation template engine."""
    
    def __init__(self, repo_root: Path):
        """Initialize template engine."""
        self.repo_root = repo_root.resolve()
        self.src_path = repo_root / 'src'
        
        # Add src to Python path
        if str(self.src_path) not in sys.path:
            sys.path.insert(0, str(self.src_path))
    
    def analyze_module(self, module_path: Path) -> ModuleAnalysis:
        """Analyze a Python module."""
        logger.info(f"Analyzing module: {module_path}")
        
        try:
            # Read module content
            content = module_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract module docstring
            module_docstring = ast.get_docstring(tree) or ""
            
            # Extract public functions
            public_functions = self.extract_api_functions(tree, content, module_path)
            
            # Extract public classes
            public_classes = self.extract_public_classes(tree)
            
            # Extract imports
            imports = self.extract_imports(tree)
            
            # Infer relationships
            relationships = self.infer_relationships(imports, module_path)
            
            # Generate architecture diagram
            architecture_diagram = self.create_architecture_diagram(
                module_path, public_functions, public_classes
            )
            
            module_name = module_path.stem
            
            return ModuleAnalysis(
                module_path=str(module_path.relative_to(self.repo_root)),
                module_name=module_name,
                docstring=module_docstring,
                public_functions=public_functions,
                public_classes=public_classes,
                imports=imports,
                relationships=relationships,
                architecture_diagram=architecture_diagram
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {module_path}: {e}")
            return ModuleAnalysis(
                module_path=str(module_path.relative_to(self.repo_root)),
                module_name=module_path.stem,
                docstring="",
                public_functions=[],
                public_classes=[],
                imports=[],
                relationships=[],
                architecture_diagram=""
            )
    
    def extract_api_functions(self, tree: ast.AST, content: str, module_path: Path) -> List[APIFunction]:
        """Extract public API functions from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
                # Extract function information
                func_name = node.name
                docstring = ast.get_docstring(node) or ""
                
                # Extract signature
                args = []
                for arg in node.args.args:
                    arg_name = arg.arg
                    # Try to get type annotation
                    arg_type = ""
                    if arg.annotation:
                        try:
                            arg_type = ast.unparse(arg.annotation)
                        except (AttributeError, ValueError) as e:
                            arg_type = "Any"
                    args.append(f"{arg_name}: {arg_type}" if arg_type else arg_name)
                
                signature = f"{func_name}({', '.join(args)})"
                
                # Extract parameters from docstring
                parameters = self.parse_docstring_params(docstring)
                
                # Extract return type
                returns = "None"
                if node.returns:
                    try:
                        returns = ast.unparse(node.returns)
                    except (AttributeError, ValueError) as e:
                        returns = "Any"
                
                # Generate example
                example = self.generate_code_example(func_name, args, docstring)
                
                functions.append(APIFunction(
                    name=func_name,
                    signature=signature,
                    docstring=docstring,
                    parameters=parameters,
                    returns=returns,
                    example=example,
                    line_number=node.lineno
                ))
        
        return functions
    
    def extract_public_classes(self, tree: ast.AST) -> List[str]:
        """Extract public class names."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    classes.append(node.name)
        
        return classes
    
    def extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def parse_docstring_params(self, docstring: str) -> List[Dict[str, str]]:
        """Parse parameters from docstring."""
        parameters = []
        
        # Look for Google-style docstring parameters
        lines = docstring.split('\n')
        in_args = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.lower().startswith('args:') or stripped.lower().startswith('parameters:'):
                in_args = True
                continue
            
            if in_args:
                if stripped.startswith('Returns:') or stripped.startswith('Raises:'):
                    break
                
                # Parse parameter line: "param_name (type): description"
                if ':' in stripped:
                    parts = stripped.split(':', 1)
                    param_part = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Extract name and type
                    param_name = param_part
                    param_type = "Any"
                    
                    if '(' in param_part and ')' in param_part:
                        param_name = param_part[:param_part.index('(')].strip()
                        param_type = param_part[param_part.index('(')+1:param_part.index(')')].strip()
                    
                    if param_name:
                        parameters.append({
                            'name': param_name,
                            'type': param_type,
                            'description': description
                        })
        
        return parameters
    
    def generate_code_example(self, func_name: str, args: List[str], docstring: str) -> str:
        """Generate a code example for a function."""
        # Extract actual argument names (without types)
        arg_names = []
        for arg in args:
            if ':' in arg:
                arg_names.append(arg.split(':')[0].strip())
            else:
                arg_names.append(arg)
        
        # Filter out 'self' and 'cls'
        arg_names = [a for a in arg_names if a not in ['self', 'cls']]
        
        # Generate example call
        if arg_names:
            # Generate placeholder values based on arg names
            example_args = []
            for arg in arg_names:
                if 'path' in arg.lower() or 'file' in arg.lower():
                    example_args.append(f'"{arg}_value"')
                elif 'count' in arg.lower() or 'number' in arg.lower() or 'size' in arg.lower():
                    example_args.append('10')
                elif 'flag' in arg.lower() or 'enable' in arg.lower() or 'is_' in arg.lower():
                    example_args.append('True')
                else:
                    example_args.append(f'"{arg}_value"')
            
            example = f"{func_name}({', '.join(example_args)})"
        else:
            example = f"{func_name}()"
        
        return example
    
    def infer_relationships(self, imports: List[str], module_path: Path) -> List[Dict[str, str]]:
        """Infer module relationships from imports."""
        relationships = []
        
        for imp in imports:
            # Check if it's a codomyrmex module
            if 'codomyrmex' in imp:
                module_name = imp.split('.')[-1]
                relationship = {
                    'name': module_name.replace('_', ' ').title(),
                    'path': imp.replace('.', '/'),
                    'relationship': 'imports from'
                }
                relationships.append(relationship)
        
        return relationships
    
    def create_architecture_diagram(self, module_path: Path, 
                                   functions: List[APIFunction],
                                   classes: List[str]) -> str:
        """Create a mermaid architecture diagram."""
        module_name = module_path.stem
        
        diagram = f"""graph TB
    Module["{module_name}"]
"""
        
        # Add functions
        for i, func in enumerate(functions[:5]):  # Limit to 5 for readability
            func_node = f"    Func{i}[{func.name}]"
            diagram += func_node + "\n"
            diagram += f"    Module --> Func{i}\n"
        
        # Add classes
        for i, cls in enumerate(classes[:5]):
            cls_node = f"    Class{i}[{cls}]"
            diagram += cls_node + "\n"
            diagram += f"    Module --> Class{i}\n"
        
        return diagram
    
    def populate_template(self, template: str, data: Dict[str, Any]) -> str:
        """Populate a template with data using simple variable substitution."""
        result = template
        
        # Simple {{variable}} substitution
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in result:
                # Handle different value types
                if isinstance(value, (list, dict)):
                    value_str = json.dumps(value, indent=2)
                else:
                    value_str = str(value)
                result = result.replace(placeholder, value_str)
        
        return result
    
    def generate_readme_content(self, analysis: ModuleAnalysis) -> Dict[str, Any]:
        """Generate README content from module analysis."""
        content = {
            'project_name': analysis.module_name.replace('_', ' ').title(),
            'module_name': analysis.module_name,
            'description': analysis.docstring.split('\n')[0] if analysis.docstring else f"The {analysis.module_name} module",
            'version': '0.1.0',
            'status': 'Active',
            'language': 'python'
        }
        
        # Add API functions
        if analysis.public_functions:
            func_docs = []
            for func in analysis.public_functions:
                func_doc = {
                    'name': func.name,
                    'signature': func.signature,
                    'description': func.docstring.split('\n')[0] if func.docstring else f"Execute {func.name} operation",
                    'parameters': func.parameters,
                    'returns': func.returns,
                    'example': f"result = {func.example}"
                }
                func_docs.append(func_doc)
            content['api_functions'] = func_docs
        
        # Add quick start example
        if analysis.public_functions:
            first_func = analysis.public_functions[0]
            content['quick_start_example'] = f"""from codomyrmex.{analysis.module_name} import {first_func.name}

# Example usage
{first_func.example}
"""
        
        # Add architecture diagram
        content['architecture_diagram'] = analysis.architecture_diagram
        
        return content
    
    def generate_agents_content(self, module_path: Path, analysis: ModuleAnalysis) -> Dict[str, Any]:
        """Generate AGENTS.md content from module analysis."""
        relative_path = module_path.parent.relative_to(self.repo_root)
        
        content = {
            'relative_path': str(relative_path).replace('\\', '/'),
            'purpose_description': analysis.docstring.split('\n\n')[0] if analysis.docstring else f"Coordination and orchestration for the {analysis.module_name} module",
            'components': []
        }
        
        # Add functions as components
        for func in analysis.public_functions[:5]:  # Limit to top 5
            content['components'].append({
                'name': func.name,
                'description': func.docstring.split('\n')[0] if func.docstring else f"Provides {func.name} functionality"
            })
        
        # Add classes as components
        for cls in analysis.public_classes[:5]:
            content['components'].append({
                'name': cls,
                'description': f"Core {cls} implementation"
            })
        
        # Add related modules
        content['related_modules'] = analysis.relationships
        
        # Add navigation links
        content['nav_links'] = [
            {
                'icon': '📚',
                'label': 'Module README',
                'title': 'Module Documentation',
                'path': 'README.md',
                'description': 'Complete module documentation'
            },
            {
                'icon': '🏠',
                'label': 'Project Root',
                'title': 'Main Project',
                'path': '../../README.md',
                'description': 'Main project README'
            }
        ]
        
        return content
    
    def export_analysis(self, analysis: ModuleAnalysis, output_path: Path) -> Path:
        """Export module analysis to JSON."""
        output_file = output_path / f"{analysis.module_name}_analysis.json"
        
        # Convert to dict
        analysis_dict = asdict(analysis)
        
        # Write JSON
        output_file.write_text(json.dumps(analysis_dict, indent=2))
        
        logger.info(f"Analysis exported to {output_file}")
        return output_file


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Smart documentation template engine")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--module', type=Path, required=True,
                       help='Module file to analyze')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for analysis')
    parser.add_argument('--export-json', action='store_true',
                       help='Export analysis as JSON')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Analyze module
    engine = SmartTemplateEngine(args.repo_root)
    analysis = engine.analyze_module(args.module)
    
    # Print summary
    print("\n" + "="*80)
    print("MODULE ANALYSIS")
    print("="*80)
    print(f"Module: {analysis.module_name}")
    print(f"Path: {analysis.module_path}")
    print(f"Public functions: {len(analysis.public_functions)}")
    print(f"Public classes: {len(analysis.public_classes)}")
    print(f"Imports: {len(analysis.imports)}")
    print(f"Relationships: {len(analysis.relationships)}")
    
    if analysis.public_functions:
        print("\nPublic Functions:")
        for func in analysis.public_functions:
            print(f"  - {func.name}: {func.signature}")
    
    if args.export_json:
        output_file = engine.export_analysis(analysis, args.output)
        print(f"\n✅ Analysis exported to: {output_file}")
    
    print("="*80)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
