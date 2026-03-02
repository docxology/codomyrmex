#!/usr/bin/env python3
"""
Environment setup utilities.

Usage:
    python env_setup.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse


def check_requirements(req_file: Path) -> dict:
    """Check if requirements are installed."""
    if not req_file.exists():
        return {"error": f"File not found: {req_file}"}
    
    requirements = []
    with open(req_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Parse package name
                name = line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0]
                requirements.append(name)
    
    # Check each package
    installed = []
    missing = []
    
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
            installed.append(req)
        except ImportError:
            missing.append(req)
    
    return {"installed": installed, "missing": missing}


def create_env_file(env_vars: dict, output: Path) -> None:
    """Create .env file."""
    lines = ["# Environment configuration", ""]
    for key, value in env_vars.items():
        lines.append(f"{key}={value}")
    output.write_text("\n".join(lines))


def check_env_template() -> dict:
    """Check .env vs .env.example."""
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    result = {"env_exists": env_file.exists(), "example_exists": example_file.exists()}
    
    if example_file.exists():
        with open(example_file) as f:
            example_vars = set()
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    example_vars.add(line.split("=")[0].strip())
        
        if env_file.exists():
            with open(env_file) as f:
                env_vars = set()
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        env_vars.add(line.split("=")[0].strip())
            
            result["missing_in_env"] = list(example_vars - env_vars)
            result["extra_in_env"] = list(env_vars - example_vars)
        else:
            result["missing_in_env"] = list(example_vars)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Environment setup")
    subparsers = parser.add_subparsers(dest="command")
    
    # Check command
    check = subparsers.add_parser("check", help="Check requirements")
    check.add_argument("--file", "-f", default="requirements.txt")
    
    # Env command
    subparsers.add_parser("env", help="Check .env file")
    
    # Create command
    create = subparsers.add_parser("create", help="Create .env from template")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔧 Environment Setup\n")
        print("Commands:")
        print("  check  - Check if requirements are installed")
        print("  env    - Check .env file status")
        print("  create - Create .env from .env.example")
        return 0
    
    if args.command == "check":
        result = check_requirements(Path(args.file))
        
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
        
        print(f"📦 Requirements Check ({args.file}):\n")
        print(f"   ✅ Installed: {len(result['installed'])}")
        if result["missing"]:
            print(f"   ❌ Missing: {len(result['missing'])}")
            for m in result["missing"][:10]:
                print(f"      - {m}")
        else:
            print("   ✅ All requirements satisfied")
    
    elif args.command == "env":
        result = check_env_template()
        
        print("📋 Environment File Check:\n")
        print(f"   .env exists: {'✅' if result['env_exists'] else '❌'}")
        print(f"   .env.example exists: {'✅' if result['example_exists'] else '⚪'}")
        
        if result.get("missing_in_env"):
            print(f"\n   ⚠️  Missing in .env:")
            for v in result["missing_in_env"][:10]:
                print(f"      - {v}")
    
    elif args.command == "create":
        example = Path(".env.example")
        env = Path(".env")
        
        if not example.exists():
            print("❌ .env.example not found")
            return 1
        
        if env.exists():
            print("⚠️  .env already exists")
            return 0
        
        import shutil
        shutil.copy(example, env)
        print(f"✅ Created .env from .env.example")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
