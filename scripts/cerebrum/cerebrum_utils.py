#!/usr/bin/env python3
"""
Cerebrum (brain/reasoning) utilities.

Usage:
    python cerebrum_utils.py <command> [options]
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


def analyze_reasoning_chain(steps: list) -> dict:
    """Analyze a reasoning chain."""
    analysis = {
        "total_steps": len(steps),
        "has_conclusion": False,
        "confidence_scores": [],
        "missing_evidence": []
    }
    
    for step in steps:
        if isinstance(step, dict):
            if step.get("type") == "conclusion":
                analysis["has_conclusion"] = True
            if "confidence" in step:
                analysis["confidence_scores"].append(step["confidence"])
            if step.get("evidence") is None:
                analysis["missing_evidence"].append(step.get("claim", "unnamed"))
    
    if analysis["confidence_scores"]:
        analysis["avg_confidence"] = sum(analysis["confidence_scores"]) / len(analysis["confidence_scores"])
    
    return analysis


def create_reasoning_template() -> dict:
    """Create a reasoning chain template."""
    return {
        "problem": "Define the problem here",
        "context": "Relevant context and constraints",
        "chain": [
            {"step": 1, "type": "observation", "claim": "What we observe", "evidence": None},
            {"step": 2, "type": "hypothesis", "claim": "What we hypothesize", "confidence": 0.7},
            {"step": 3, "type": "test", "claim": "How to test", "result": None},
            {"step": 4, "type": "conclusion", "claim": "What we conclude", "confidence": 0.0}
        ],
        "meta": {
            "created": None,
            "author": None,
            "version": "1.0"
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Cerebrum utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze reasoning chain")
    analyze.add_argument("file", help="Reasoning chain file (JSON)")
    
    # Create command
    create = subparsers.add_parser("create", help="Create reasoning template")
    create.add_argument("--output", "-o", default="reasoning.json")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🧠 Cerebrum Utilities\n")
        print("Brain/reasoning chain tools.\n")
        print("Commands:")
        print("  analyze - Analyze reasoning chain")
        print("  create  - Create reasoning template")
        return 0
    
    if args.command == "analyze":
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}")
            return 1
        
        data = json.loads(path.read_text())
        chain = data.get("chain", data.get("steps", []))
        analysis = analyze_reasoning_chain(chain)
        
        print(f"🧠 Reasoning Analysis: {path.name}\n")
        print(f"   Steps: {analysis['total_steps']}")
        print(f"   Has conclusion: {'Yes' if analysis['has_conclusion'] else 'No'}")
        if "avg_confidence" in analysis:
            print(f"   Avg confidence: {analysis['avg_confidence']:.1%}")
        if analysis["missing_evidence"]:
            print(f"   Missing evidence: {len(analysis['missing_evidence'])} claims")
    
    elif args.command == "create":
        template = create_reasoning_template()
        Path(args.output).write_text(json.dumps(template, indent=2))
        print(f"✅ Created: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
