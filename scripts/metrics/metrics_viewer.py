#!/usr/bin/env python3
"""
Metrics collection and display utilities.

Usage:
    python metrics_viewer.py [--source SOURCE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
from datetime import datetime


def collect_system_metrics() -> dict:
    """Collect basic system metrics."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version.split()[0],
    }
    
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        metrics["memory_mb"] = usage.ru_maxrss / 1024 / 1024
        metrics["user_time"] = usage.ru_utime
        metrics["system_time"] = usage.ru_stime
    except:
        pass
    
    return metrics


def collect_code_metrics(path: str) -> dict:
    """Collect code metrics for a directory."""
    metrics = {
        "files": 0,
        "lines": 0,
        "blank_lines": 0,
        "comment_lines": 0,
        "by_language": {}
    }
    
    extensions = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".go": "Go", ".rs": "Rust"}
    
    for f in Path(path).rglob("*"):
        if f.is_file() and f.suffix in extensions:
            lang = extensions[f.suffix]
            if lang not in metrics["by_language"]:
                metrics["by_language"][lang] = {"files": 0, "lines": 0}
            
            try:
                with open(f) as file:
                    lines = file.readlines()
                    metrics["files"] += 1
                    metrics["lines"] += len(lines)
                    metrics["by_language"][lang]["files"] += 1
                    metrics["by_language"][lang]["lines"] += len(lines)
                    
                    for line in lines:
                        stripped = line.strip()
                        if not stripped:
                            metrics["blank_lines"] += 1
                        elif stripped.startswith("#") or stripped.startswith("//"):
                            metrics["comment_lines"] += 1
            except:
                pass
    
    return metrics


def format_metric(name: str, value, unit: str = "") -> str:
    if isinstance(value, float):
        return f"{name}: {value:.2f} {unit}".strip()
    return f"{name}: {value} {unit}".strip()


def main():
    parser = argparse.ArgumentParser(description="Metrics viewer")
    parser.add_argument("--source", "-s", choices=["system", "code", "all"], default="all")
    parser.add_argument("--path", "-p", default=".", help="Path for code metrics")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    all_metrics = {}
    
    if args.source in ["system", "all"]:
        system = collect_system_metrics()
        all_metrics["system"] = system
        
        if not args.json:
            print("📊 System Metrics:\n")
            print(f"   Timestamp: {system['timestamp']}")
            print(f"   Python: {system['python_version']}")
            if "memory_mb" in system:
                print(f"   Memory: {system['memory_mb']:.1f} MB")
            print()
    
    if args.source in ["code", "all"]:
        code = collect_code_metrics(args.path)
        all_metrics["code"] = code
        
        if not args.json:
            print(f"📈 Code Metrics ({args.path}):\n")
            print(f"   Files: {code['files']}")
            print(f"   Lines: {code['lines']:,}")
            print(f"   Blank: {code['blank_lines']:,}")
            print(f"   Comments: {code['comment_lines']:,}")
            if code["by_language"]:
                print("\n   By language:")
                for lang, stats in code["by_language"].items():
                    print(f"      {lang}: {stats['files']} files, {stats['lines']:,} lines")
    
    if args.json:
        print(json.dumps(all_metrics, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
