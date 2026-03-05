#!/usr/bin/env python3
"""Thin orchestrator script for docs_gen.

Demonstrates the improved capabilities of the docs_gen module:
- Comprehensive API extraction
- Search indexing with CamelCase/snake_case support
- Static site configuration generation
"""

from codomyrmex.docs_gen import SiteGenerator

# Example source code with various features
SAMPLE_SOURCE = '''
"""Example Module.

This module demonstrates advanced API documentation extraction.
"""

from typing import Any, Optional

__all__ = ["ExampleClient", "process_data"]

class ExampleClient:
    """A client for demonstrating class documentation.
    
    Inherits from nothing in particular.
    """
    
    def __init__(self, endpoint: str, timeout: float = 30.0) -> None:
        """Initialize the client."""
        self.endpoint = endpoint
        self.timeout = timeout

    async def send_request(self, payload: dict[str, Any], retry: bool = True) -> Optional[dict]:
        """Send an async request to the endpoint."""
        return {"status": "ok"}

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return True

def process_data(data: list[int], *, factor: int = 1, verbose: bool = False) -> list[int]:
    """Process a list of integers using keyword-only arguments."""
    return [d * factor for d in data]
'''

def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "docs_gen" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    print("--- Starting Docs Generation Orchestrator ---")

    # 1. Initialize SiteGenerator
    gen = SiteGenerator(title="Codomyrmex Improved Docs")

    # 2. Add module source
    print("Extracting documentation from example source...")
    gen.add_module_source(SAMPLE_SOURCE, "example_mod")

    # 3. Add a custom page
    print("Adding custom introduction page...")
    intro_content = """# Introduction
    
Welcome to the improved documentation system.
This site was generated using the `docs_gen` orchestrator.
"""
    gen.add_page("index.md", intro_content, title="Welcome")

    # 4. Search demonstration
    print("\n--- Search Index Demonstration ---")
    idx = gen.search_index

    queries = ["ExampleClient", "process_data", "request", "connected"]
    for query in queries:
        results = idx.search(query, limit=3)
        print(f"Search for '{query}': found {len(results)} matches")
        for res in results:
            print(f"  - {res.title} (Score: {res.score}): {res.snippet}")

    # 5. Generate configuration and pages
    print("\n--- Generating Site Configuration ---")
    mkdocs_yaml = gen.to_mkdocs_yaml()
    print("Generated mkdocs.yml snippet (first 20 lines):")
    print("\n".join(mkdocs_yaml.splitlines()[:20]))

    pages = gen.generate_pages()
    print(f"\nTotal pages generated: {len(pages)}")
    for path in pages:
        print(f"  - {path} ({len(pages[path])} chars)")

    print("\n--- Orchestration Complete ---")

if __name__ == "__main__":
    main()
