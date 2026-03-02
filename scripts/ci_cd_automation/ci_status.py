#!/usr/bin/env python3
"""
CI/CD pipeline status and management utilities.

Usage:
    python ci_status.py [--provider PROVIDER] [--repo REPO]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os
import subprocess


def find_ci_configs() -> list:
    """Find CI/CD configuration files."""
    patterns = [
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        ".gitlab-ci.yml",
        "Jenkinsfile",
        ".circleci/config.yml",
        "azure-pipelines.yml",
        ".travis.yml",
        "bitbucket-pipelines.yml",
    ]
    found = []
    for pattern in patterns:
        found.extend(Path(".").glob(pattern))
    return found


def parse_github_workflow(path: Path) -> dict:
    """Parse GitHub Actions workflow."""
    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return {
            "name": data.get("name", path.name),
            "triggers": list(data.get("on", {}).keys()) if isinstance(data.get("on"), dict) else [str(data.get("on", ""))],
            "jobs": list(data.get("jobs", {}).keys()),
        }
    except ImportError:
        return {"name": path.name, "error": "PyYAML not installed"}
    except Exception as e:
        return {"name": path.name, "error": str(e)}


def get_git_info() -> dict:
    """Get current git info for CI context."""
    info = {}
    try:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                              capture_output=True, text=True)
        info["branch"] = result.stdout.strip()
        
        result = subprocess.run(["git", "rev-parse", "HEAD"], 
                              capture_output=True, text=True)
        info["commit"] = result.stdout.strip()[:8]
        
        result = subprocess.run(["git", "log", "-1", "--format=%s"], 
                              capture_output=True, text=True)
        info["message"] = result.stdout.strip()[:50]
    except:
        pass
    return info


def main():
    parser = argparse.ArgumentParser(description="CI/CD status and utilities")
    parser.add_argument("--provider", "-p", choices=["github", "gitlab", "all"], default="all")
    parser.add_argument("--list-workflows", "-l", action="store_true", help="List workflows")
    parser.add_argument("--context", "-c", action="store_true", help="Show CI context")
    args = parser.parse_args()
    
    print("🔄 CI/CD Status\n")
    
    # Git context
    git_info = get_git_info()
    if git_info:
        print(f"📌 Current context:")
        print(f"   Branch: {git_info.get('branch', 'unknown')}")
        print(f"   Commit: {git_info.get('commit', 'unknown')}")
        print(f"   Message: {git_info.get('message', '')}")
        print()
    
    # Find CI configs
    configs = find_ci_configs()
    
    if not configs:
        print("📋 No CI/CD configurations found")
        print("   Looking for: .github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc.")
        return 0
    
    print(f"📋 CI/CD Configurations ({len(configs)}):\n")
    
    for config in configs:
        if ".github/workflows" in str(config):
            info = parse_github_workflow(config)
            print(f"   🐙 GitHub: {info['name']}")
            if "error" not in info:
                print(f"      Triggers: {', '.join(info['triggers'])}")
                print(f"      Jobs: {', '.join(info['jobs'][:5])}")
            else:
                print(f"      {info['error']}")
        elif config.name == ".gitlab-ci.yml":
            print(f"   🦊 GitLab CI: {config}")
        elif config.name == "Jenkinsfile":
            print(f"   🔧 Jenkins: {config}")
        else:
            print(f"   📄 {config}")
        print()
    
    # CI environment variables
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "CIRCLECI"]
    detected = [v for v in ci_vars if os.environ.get(v)]
    if detected:
        print(f"🏃 Running in CI: {', '.join(detected)}")
    else:
        print("💻 Running locally (not in CI environment)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
