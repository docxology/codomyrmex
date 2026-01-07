#!/usr/bin/env python3
"""
Example: FPF - First Principles Framework

Demonstrates:
- FPF specification fetching from GitHub
- FPF specification parsing
- Pattern searching and retrieval
- Context building for prompt engineering

Tested Methods:
- FPFClient.fetch_and_load() - Verified in test_fpf.py::TestFPFClient::test_fetch_and_load
- FPFClient.load_from_file() - Verified in test_fpf.py::TestFPFClient::test_load_from_file
- FPFClient.search() - Verified in test_fpf.py::TestFPFClient::test_search
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for importing Codomyrmex modules
# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).resolve().parent
# Setup paths: scripts/fpf/examples -> scripts/fpf -> scripts -> root
# So root is 3 levels up from current_dir
root_dir = current_dir.parent.parent.parent

sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))
# Add common tools to path
sys.path.insert(0, str(root_dir / "scripts/tools/_common"))

# Import common utilities
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.fpf import FPFClient

def main():
    """Run the FPF example."""
    print_section("FPF Module Example")
    print("Demonstrating First Principles Framework functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize FPF client
        client = FPFClient()
        print_success("✓ FPF client initialized")

        # Check if we should fetch from GitHub or use local file
        fpf_config = config.get("fpf", {})
        use_local = fpf_config.get("use_local_file", False)
        local_file_path = fpf_config.get("local_file_path")

        if use_local and local_file_path:
            # Load from local file
            try:
                spec = client.load_from_file(local_file_path)
                print_success(f"✓ FPF specification loaded from {local_file_path}")
            except Exception as e:
                print_error(f"Failed to load from local file: {e}")
                print("Attempting to fetch from GitHub instead...")
                spec = client.fetch_and_load(
                    repo=fpf_config.get("repo", "ailev/FPF"),
                    branch=fpf_config.get("branch", "main")
                )
                print_success("✓ FPF specification fetched from GitHub")
        else:
            # Fetch from GitHub
            try:
                spec = client.fetch_and_load(
                    repo=fpf_config.get("repo", "ailev/FPF"),
                    branch=fpf_config.get("branch", "main")
                )
                print_success("✓ FPF specification fetched from GitHub")
            except Exception as e:
                print_error(f"Failed to fetch from GitHub: {e}")
                print("Note: Network access may be required for fetching from GitHub")
                # Create a mock result for demonstration
                operations_summary = {
                    "client_initialized": True,
                    "fetch_attempted": True,
                    "fetch_successful": False,
                    "error": str(e)
                }
                print_results(operations_summary, "Operations Summary")
                runner.validate_results(operations_summary)
                runner.save_results(operations_summary)
                runner.complete()
                print("\n⚠️ FPF example completed with limitations (network access required)")
                return

        # Get pattern count
        pattern_count = len(spec.patterns) if spec and spec.patterns else 0
        print_success(f"✓ Loaded {pattern_count} patterns")

        # Search for patterns (example search)
        search_query = fpf_config.get("search_query", "pattern")
        try:
            search_results = client.search(search_query, filters=None)
            print_success(f"✓ Found {len(search_results)} patterns matching '{search_query}'")
        except Exception as e:
            print_error(f"Search failed: {e}")
            search_results = []

        # Get a specific pattern if available
        pattern_id = fpf_config.get("pattern_id")
        pattern_retrieved = False
        if pattern_id and spec:
            try:
                pattern = client.get_pattern(pattern_id)
                print_success(f"✓ Retrieved pattern {pattern_id}: {pattern.title if hasattr(pattern, 'title') else 'N/A'}")
                pattern_retrieved = True
            except Exception as e:
                print_error(f"Failed to retrieve pattern {pattern_id}: {e}")

        # Build context (if spec is available)
        context_built = False
        if spec:
            try:
                context = client.build_context()
                context_length = len(context) if context else 0
                print_success(f"✓ Built context string ({context_length} characters)")
                context_built = True
            except Exception as e:
                print_error(f"Context building failed: {e}")

        operations_summary = {
            "client_initialized": True,
            "specification_loaded": spec is not None,
            "pattern_count": pattern_count,
            "search_performed": len(search_results) > 0,
            "search_results_count": len(search_results),
            "pattern_retrieved": pattern_retrieved,
            "context_built": context_built
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ FPF example completed successfully!")
    except Exception as e:
        runner.error("FPF example failed", e)
        print_error(f"FPF example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

