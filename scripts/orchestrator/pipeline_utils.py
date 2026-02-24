#!/usr/bin/env python3
"""
Orchestrator utilities for pipeline management.

Usage:
    python pipeline_utils.py <command> [options]
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
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_pipeline(path: Path) -> dict:
    """Load pipeline definition."""
    if path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    return {"error": f"Unsupported format: {path.suffix}"}


def execute_step(step: dict, context: dict = None) -> dict:
    """Execute a pipeline step."""
    result = {"name": step.get("name", "unnamed"), "status": "pending"}
    
    start = time.time()
    
    if "script" in step:
        result["type"] = "script"
        result["status"] = "would_execute"
    elif "command" in step:
        result["type"] = "command"
        result["status"] = "would_execute"
    elif "parallel" in step:
        result["type"] = "parallel"
        result["status"] = "would_execute"
    else:
        result["status"] = "unknown_step_type"
    
    result["duration"] = round(time.time() - start, 3)
    return result


def validate_pipeline(pipeline: dict) -> list:
    """Validate pipeline structure."""
    errors = []
    
    if "name" not in pipeline:
        errors.append("Missing 'name' field")
    
    if "steps" not in pipeline:
        errors.append("Missing 'steps' field")
    elif not isinstance(pipeline["steps"], list):
        errors.append("'steps' must be a list")
    else:
        for i, step in enumerate(pipeline["steps"]):
            if "name" not in step:
                errors.append(f"Step {i} missing 'name'")
            if not any(k in step for k in ["script", "command", "parallel"]):
                errors.append(f"Step {i} missing action (script/command/parallel)")
    
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Validate command
    validate = subparsers.add_parser("validate", help="Validate pipeline")
    validate.add_argument("file", help="Pipeline file")
    
    # Run command
    run = subparsers.add_parser("run", help="Run pipeline")
    run.add_argument("file", help="Pipeline file")
    run.add_argument("--dry-run", "-n", action="store_true")
    
    # List command
    list_cmd = subparsers.add_parser("list", help="List pipeline steps")
    list_cmd.add_argument("file", help="Pipeline file")
    
    # Create command
    create = subparsers.add_parser("create", help="Create pipeline template")
    create.add_argument("name", help="Pipeline name")
    create.add_argument("--output", "-o", default="pipeline.json")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔄 Pipeline Utilities\n")
        print("Commands:")
        print("  validate - Validate pipeline definition")
        print("  run      - Run pipeline")
        print("  list     - List pipeline steps")
        print("  create   - Create pipeline template")
        return 0
    
    if args.command == "validate":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        pipeline = load_pipeline(path)
        errors = validate_pipeline(pipeline)
        
        if errors:
            print(f"❌ Validation failed:\n")
            for e in errors:
                print(f"   - {e}")
            return 1
        else:
            print(f"✅ Pipeline valid: {pipeline.get('name', path.name)}")
            print(f"   Steps: {len(pipeline.get('steps', []))}")
    
    elif args.command == "run":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        pipeline = load_pipeline(path)
        print(f"🔄 Pipeline: {pipeline.get('name', path.name)}")
        if args.dry_run:
            print("   Mode: DRY RUN\n")
        
        for step in pipeline.get("steps", []):
            result = execute_step(step)
            print(f"   {'✅' if result['status'] != 'error' else '❌'} {result['name']}: {result['status']}")
    
    elif args.command == "list":
        path = Path(args.file)
        pipeline = load_pipeline(path)
        
        print(f"📋 Pipeline: {pipeline.get('name', path.name)}\n")
        for i, step in enumerate(pipeline.get("steps", []), 1):
            print(f"   {i}. {step.get('name', 'unnamed')}")
    
    elif args.command == "create":
        template = {
            "name": args.name,
            "version": "1.0",
            "steps": [
                {"name": "build", "command": "echo 'Building...'"},
                {"name": "test", "command": "echo 'Testing...'"},
                {"name": "deploy", "command": "echo 'Deploying...'"}
            ]
        }
        
        Path(args.output).write_text(json.dumps(template, indent=2))
        print(f"✅ Created: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
