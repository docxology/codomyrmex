"""
Shared utility functions for examples.

Provides common helpers for path resolution, data formatting,
and validation.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def setup_example_paths() -> Dict[str, Path]:
    """
    Setup and return common paths for examples.
    
    Returns:
        Dictionary with 'src', 'examples', 'output', 'logs' paths
    """
    # Determine repo root (3 levels up from _common/)
    repo_root = Path(__file__).parent.parent.parent
    
    paths = {
        'repo_root': repo_root,
        'src': repo_root / 'src',
        'examples': repo_root / 'examples',
        'output': repo_root / 'examples' / 'output',
        'logs': repo_root / 'examples' / 'logs',
        'testing': repo_root / 'testing',
    }
    
    # Add src to Python path if not already there
    src_str = str(paths['src'])
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    
    return paths


def ensure_output_dir(output_path: Path) -> Path:
    """
    Ensure output directory exists.
    
    Args:
        output_path: Path to output file or directory
        
    Returns:
        The output path
    """
    if output_path.suffix:
        # It's a file, create parent directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # It's a directory
        output_path.mkdir(parents=True, exist_ok=True)
    
    return output_path


def format_output(data: Any, format: str = 'json', indent: int = 2) -> str:
    """
    Format data for output.
    
    Args:
        data: Data to format
        format: Output format ('json', 'text', 'pretty')
        indent: Indentation level for JSON
        
    Returns:
        Formatted string
    """
    if format == 'json':
        return json.dumps(data, indent=indent, default=str)
    elif format == 'pretty':
        import pprint
        return pprint.pformat(data, indent=indent)
    else:
        return str(data)


def print_section(title: str, width: int = 80):
    """
    Print a section header.

    Args:
        title: Section title
        width: Total width of the header
    """
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width + "\n")


def print_success(message: str):
    """
    Print a success message with green color.

    Args:
        message: Success message
    """
    try:
        # Try to use color if available
        print(f"\033[92m✓ {message}\033[0m")
    except:
        print(f"✓ {message}")


def print_error(message: str):
    """
    Print an error message with red color.

    Args:
        message: Error message
    """
    try:
        # Try to use color if available
        print(f"\033[91m✗ {message}\033[0m")
    except:
        print(f"✗ {message}")


def print_results(results: Dict[str, Any], title: str = "Results"):
    """
    Print results in a formatted way.
    
    Args:
        results: Results dictionary
        title: Title for the results section
    """
    print_section(title)
    
    if isinstance(results, dict):
        for key, value in results.items():
            if isinstance(value, (dict, list)):
                print(f"{key}:")
                print(f"  {format_output(value, format='json')}")
            else:
                print(f"{key}: {value}")
    else:
        print(format_output(results, format='pretty'))
    
    print()


def safe_import(module_path: str, fallback_message: Optional[str] = None) -> Optional[Any]:
    """
    Safely import a module with fallback.
    
    Args:
        module_path: Module import path (e.g., 'codomyrmex.logging_monitoring')
        fallback_message: Optional message to print if import fails
        
    Returns:
        Imported module or None if import fails
    """
    try:
        parts = module_path.split('.')
        module = __import__(module_path)
        for part in parts[1:]:
            module = getattr(module, part)
        return module
    except ImportError as e:
        if fallback_message:
            print(f"Warning: {fallback_message}")
            print(f"  Import error: {e}")
        return None


def load_test_data(test_file: str = "sample_data.json") -> Dict[str, Any]:
    """
    Load sample test data for examples.
    
    Args:
        test_file: Name of test data file
        
    Returns:
        Test data dictionary
    """
    paths = setup_example_paths()
    test_data_path = paths['examples'] / '_common' / 'test_data' / test_file
    
    if test_data_path.exists():
        with open(test_data_path, 'r') as f:
            return json.load(f)
    else:
        # Return minimal default data
        return {
            "sample": "data",
            "for": "testing"
        }


def get_module_info(module_name: str) -> Dict[str, Any]:
    """
    Get information about a Codomyrmex module.
    
    Args:
        module_name: Name of the module (e.g., 'logging_monitoring')
        
    Returns:
        Dictionary with module information
    """
    paths = setup_example_paths()
    module_path = paths['src'] / 'codomyrmex' / module_name
    
    info = {
        'name': module_name,
        'path': str(module_path),
        'exists': module_path.exists(),
        'has_tests': (paths['testing'] / 'unit' / f'test_{module_name}.py').exists(),
    }
    
    # Try to get module docstring
    if info['exists']:
        init_file = module_path / '__init__.py'
        if init_file.exists():
            try:
                with open(init_file, 'r') as f:
                    content = f.read()
                    # Extract docstring (simplified)
                    if '"""' in content:
                        start = content.find('"""') + 3
                        end = content.find('"""', start)
                        info['description'] = content[start:end].strip()
            except:
                pass
    
    return info

