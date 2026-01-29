#!/usr/bin/env python3
"""
Workflow execution utilities.

Usage:
    python workflow_runner.py [workflow_file] [--dry-run]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import subprocess
import time


def load_workflow(path: Path) -> dict:
    """Load workflow definition."""
    if path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    elif path.suffix in [".yaml", ".yml"]:
        try:
            import yaml
            with open(path) as f:
                return yaml.safe_load(f)
        except ImportError:
            return {"error": "PyYAML not installed"}
    else:
        return {"error": f"Unsupported format: {path.suffix}"}


def execute_step(step: dict, dry_run: bool = False) -> dict:
    """Execute a workflow step."""
    result = {"name": step.get("name", "unnamed"), "status": "pending"}
    
    if "command" in step:
        cmd = step["command"]
        result["command"] = cmd
        
        if dry_run:
            result["status"] = "dry_run"
            return result
        
        try:
            start = time.time()
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=step.get("timeout", 60))
            result["status"] = "success" if proc.returncode == 0 else "failed"
            result["exit_code"] = proc.returncode
            result["duration"] = round(time.time() - start, 2)
            result["output"] = proc.stdout[:500] if proc.stdout else ""
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    
    elif "script" in step:
        result["status"] = "script_not_implemented"
    
    return result


def run_workflow(workflow: dict, dry_run: bool = False) -> list:
    """Execute a workflow."""
    results = []
    
    steps = workflow.get("steps", [])
    if not steps:
        return [{"error": "No steps defined"}]
    
    for step in steps:
        result = execute_step(step, dry_run)
        results.append(result)
        
        # Stop on failure unless continue_on_error
        if result["status"] == "failed" and not step.get("continue_on_error"):
            break
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Workflow runner")
    parser.add_argument("workflow", nargs="?", help="Workflow file (JSON/YAML)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would run")
    parser.add_argument("--demo", action="store_true", help="Run demo workflow")
    args = parser.parse_args()
    
    if args.demo:
        workflow = {
            "name": "Demo Workflow",
            "steps": [
                {"name": "Check Python", "command": "python --version"},
                {"name": "List files", "command": "ls -la | head -5"},
                {"name": "Show date", "command": "date"},
            ]
        }
    elif args.workflow:
        path = Path(args.workflow)
        if not path.exists():
            print(f"❌ File not found: {args.workflow}")
            return 1
        workflow = load_workflow(path)
        if "error" in workflow:
            print(f"❌ {workflow['error']}")
            return 1
    else:
        print("🔄 Workflow Runner\n")
        print("Usage:")
        print("  python workflow_runner.py workflow.json")
        print("  python workflow_runner.py workflow.yaml --dry-run")
        print("  python workflow_runner.py --demo")
        print("\nWorkflow format:")
        print('  {"name": "My Workflow", "steps": [{"name": "Step 1", "command": "echo hello"}]}')
        return 0
    
    name = workflow.get("name", "Unnamed Workflow")
    steps = workflow.get("steps", [])
    
    print(f"🔄 Running: {name}")
    print(f"   Steps: {len(steps)}")
    if args.dry_run:
        print("   Mode: DRY RUN")
    print()
    
    results = run_workflow(workflow, args.dry_run)
    
    for r in results:
        icon = {"success": "✅", "failed": "❌", "dry_run": "🔍", "timeout": "⏰"}.get(r["status"], "⚪")
        print(f"   {icon} {r['name']}: {r['status']}")
        if "duration" in r:
            print(f"      Duration: {r['duration']}s")
        if r.get("output"):
            print(f"      Output: {r['output'][:80]}...")
    
    successful = sum(1 for r in results if r["status"] in ["success", "dry_run"])
    print(f"\n📊 Results: {successful}/{len(results)} steps completed")
    
    return 0 if successful == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
