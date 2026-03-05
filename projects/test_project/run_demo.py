#!/usr/bin/env python3
"""Run test_project demonstration.

This script demonstrates the full capabilities of test_project,
showcasing integration with codomyrmex modules.

Usage:
    python run_demo.py [target_path]

Examples:
    python run_demo.py           # Analyze src/ directory
    python run_demo.py .         # Analyze current directory
    python run_demo.py ../..     # Analyze parent directories
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from src.agent_brain import AgentBrain
from src.git_workflow import GitWorkflow
from src.knowledge_search import KnowledgeSearch
from src.llm_inference import LLMInference
from src.main import run_analysis
from src.mcp_explorer import MCPExplorer
from src.pipeline import AnalysisPipeline
from src.reporter import ReportConfig, ReportGenerator
from src.security_audit import SecurityAudit
from src.visualizer import DataVisualizer


def print_header(text: str) -> None:
    """Print formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str) -> None:
    """Print section header."""
    print()
    print(f"▸ {text}")
    print("-" * 40)


def demo_analysis(target: Path) -> dict:
    """Demonstrate the analysis functionality."""
    print_section("Running Analysis")

    results = run_analysis(target)

    summary = results.get("summary", {})
    print(f"  Files analyzed:    {summary.get('total_files', 0)}")
    print(f"  Total lines:       {summary.get('total_lines', 0):,}")
    print(f"  Non-empty lines:   {summary.get('total_non_empty_lines', 0):,}")
    print(f"  Functions:         {summary.get('total_functions', 0)}")
    print(f"  Classes:           {summary.get('total_classes', 0)}")
    print(f"  Issues found:      {summary.get('total_issues', 0)}")

    # Show patterns
    patterns = summary.get("patterns_found", {})
    if patterns:
        print()
        print("  Patterns detected:")
        for pattern, count in sorted(
            patterns.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            print(f"    • {pattern.replace('_', ' ').title()}: {count}")

    return results


def demo_visualization(results: dict) -> Path:
    """Demonstrate the visualization functionality."""
    print_section("Generating Visualization")

    output_dir = Path(__file__).parent / "reports" / "visualizations"
    visualizer = DataVisualizer(output_dir=output_dir)

    dashboard_path = visualizer.create_dashboard(results)
    print(f"  Dashboard: {dashboard_path.relative_to(Path(__file__).parent)}")

    return dashboard_path


def demo_reporting(results: dict) -> dict:
    """Demonstrate the reporting functionality."""
    print_section("Generating Reports")

    output_dir = Path(__file__).parent / "reports" / "output"
    generator = ReportGenerator(output_dir=output_dir)

    # Generate all formats
    paths = {}
    for fmt in ["html", "json", "markdown"]:
        config = ReportConfig(
            title="Test Project Analysis Report", format=fmt, author="Codomyrmex Demo"
        )
        path = generator.generate(results, config)
        paths[fmt] = path
        rel_path = path.relative_to(Path(__file__).parent)
        print(f"  {fmt.upper():10} {rel_path}")

    return paths


def demo_pipeline(target: Path) -> None:
    """Demonstrate the pipeline functionality."""
    print_section("Running Full Pipeline")

    config_path = Path(__file__).parent / "config" / "workflows.yaml"
    pipeline = AnalysisPipeline(config_path if config_path.exists() else None)

    print(f"  Steps: {len(pipeline.steps)}")
    for name, step in pipeline.steps.items():
        deps = f" (after: {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"    {name}{deps}")

    print()
    print("  Executing...")
    result = pipeline.execute(target)

    print()
    status_emoji = "✅" if result.is_success else "❌"
    print(f"  Status: {status_emoji} {result.status.value}")
    print(f"  Duration: {result.duration_seconds:.2f} seconds")
    print(f"  Steps completed: {result.steps_completed}/{result.total_steps}")

    if result.step_durations:
        print()
        print("  Step timings:")
        for step, duration in result.step_durations.items():
            print(f"    • {step}: {duration:.2f}s")

    if result.errors:
        print()
        print("  Errors:")
        for error in result.errors:
            print(f"    ⚠ {error}")


def demo_agent_brain() -> None:
    """Demonstrate agents + agentic memory integration."""
    print_section("Agent Brain (agents + agentic_memory)")

    try:
        brain = AgentBrain()
        providers = brain.list_available_agents()
        print(f"  Available agent providers: {providers}")

        brain.remember("Python uses GIL for thread safety", "knowledge", "high")
        brain.remember(
            "codomyrmex has 121 auto-discovered modules", "knowledge", "normal"
        )
        results = brain.recall("Python", k=3)
        print(f"  Memory store: {len(results)} recall result(s) for 'Python'")

        summary = brain.agent_config_summary()
        print(f"  AgentInterface: {summary['agent_interface']}")
        print(f"  Capabilities: {len(summary['capabilities'])} values")
    except Exception as e:
        print(f"  [warning] Agent Brain demo failed: {e}")


def demo_git_workflow() -> None:
    """Demonstrate git_operations + git_analysis integration."""
    print_section("Git Workflow (git_operations + git_analysis)")

    try:
        repo_root = Path(__file__).parent.parent.parent
        wf = GitWorkflow()

        info = wf.inspect_repo(repo_root)
        print(f"  Is git repo: {info['is_git_repo']}")
        print(f"  Current branch: {info.get('current_branch', 'n/a')}")
        branch_count = len(info.get("branches", []))
        print(f"  Branches found: {branch_count}")

        history = wf.analyze_history(repo_root, max_commits=10)
        print(f"  Commits analyzed: {history['commit_count']}")
        print(f"  Contributors: {len(history['contributors'])}")
    except Exception as e:
        print(f"  [warning] Git Workflow demo failed: {e}")


def demo_knowledge_search() -> None:
    """Demonstrate search + scrape + formal_verification integration."""
    print_section("Knowledge Search (search + scrape + formal_verification)")

    try:
        ks = KnowledgeSearch()

        docs = [
            {"id": "1", "content": "Python is great for data science and ML"},
            {"id": "2", "content": "JavaScript and TypeScript run in the browser"},
            {
                "id": "3",
                "content": "Rust provides memory safety without garbage collection",
            },
            {"id": "4", "content": "codomyrmex integrates 121 modules via MCP tools"},
        ]
        results = ks.full_text_search("Python data", docs)
        print(f"  Full-text search 'Python data': {len(results)} result(s)")

        matches = ks.fuzzy_match("pythn", ["python", "kotlin", "java", "ruby"])
        print(f"  Fuzzy match 'pythn': {matches}")

        info = ks.scraper_info()
        print(f"  Scrape formats: {info['available_formats']}")

        constraints = ks.verify_constraints([], timeout_ms=500)
        print(
            f"  Constraint solver: {constraints['status']} (z3 available: {constraints['solver_available']})"
        )
    except Exception as e:
        print(f"  [warning] Knowledge Search demo failed: {e}")


def demo_security_audit() -> None:
    """Demonstrate security + crypto + maintenance + system_discovery."""
    print_section("Security Audit (security + crypto + system_discovery)")

    try:
        auditor = SecurityAudit()

        hashed = auditor.hash_and_verify(b"codomyrmex demo data")
        print(f"  SHA-256 digest: {hashed['hex_digest'][:16]}...")
        print(f"  Hash verified: {hashed['verified']}")

        health = auditor.system_health()
        print(f"  Modules discovered: {health['modules_found']}")
        print(f"  SystemDiscovery: {health['discovery_type']}")
    except Exception as e:
        print(f"  [warning] Security Audit demo failed: {e}")


def demo_mcp_explorer() -> None:
    """Demonstrate model_context_protocol + skills + plugin_system."""
    print_section("MCP Explorer (model_context_protocol + skills + plugin_system)")

    try:
        explorer = MCPExplorer()

        tools = explorer.list_tools()
        print(f"  MCP tool categories: {len(tools['categories'])}")
        print(f"  Discovery available: {tools['discovery_available']}")

        skills = explorer.discover_skills()
        print(f"  Skill registry: {skills['registry_type']}")
        print(f"  Skills found: {skills['skill_count']}")

        plugins = explorer.scan_plugins()
        print(f"  Plugin types: {plugins['plugin_types']}")
        print(f"  Plugins installed: {plugins['plugin_count']}")
    except Exception as e:
        print(f"  [warning] MCP Explorer demo failed: {e}")


def demo_llm_inference() -> None:
    """Demonstrate llm + collaboration integration."""
    print_section("LLM Inference (llm + collaboration)")

    try:
        inference = LLMInference()

        summary = inference.config_summary()
        print(f"  LLM config: {summary['config_class']}")
        print(f"  Ollama manager: {summary['ollama_manager']}")

        pool = inference.agent_pool_status()
        print(f"  Swarm: {pool['swarm_class']}")
        print(f"  Agent pool: {pool['pool_class']}")
        print(f"  Task priorities: {pool['task_priority_values']}")

        models = inference.list_models()
        if models["ollama_available"]:
            print(f"  Ollama models: {models['model_count']}")
        else:
            print("  Ollama: not running (expected in CI)")

        task = inference.swarm_task("Analyze Python codebase for improvements")
        print(f"  Swarm task submitted: {task['task_submitted']}")
    except Exception as e:
        print(f"  [warning] LLM Inference demo failed: {e}")


def main() -> int:
    """Run the demonstration."""
    print_header("Test Project - Codomyrmex Reference Implementation")

    # Determine target path
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "src"

    print(f"\nTarget: {target.absolute()}")

    try:
        # 1. Run analysis
        results = demo_analysis(target)

        # 2. Generate visualizations
        dashboard_path = demo_visualization(results)

        # 3. Generate reports
        report_paths = demo_reporting(results)

        # 4. Run full pipeline
        demo_pipeline(target)

        # 5. Agent brain
        demo_agent_brain()

        # 6. Git workflow
        demo_git_workflow()

        # 7. Knowledge search
        demo_knowledge_search()

        # 8. Security audit
        demo_security_audit()

        # 9. MCP explorer
        demo_mcp_explorer()

        # 10. LLM inference
        demo_llm_inference()

        # Summary
        print_header("Generated Outputs")
        print()
        print("  Visualizations:")
        print(f"    • {dashboard_path.relative_to(Path(__file__).parent)}")
        print()
        print("  Reports:")
        for path in report_paths.values():
            print(f"    • {path.relative_to(Path(__file__).parent)}")
        print()
        print("  Open the HTML files in your browser to view!")
        print()

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
