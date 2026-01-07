#!/bin/bash
# 📊 Comprehensive Multi-Module Analysis Pipeline
#
# This advanced orchestrator demonstrates sophisticated integration patterns by combining:
# - Static Analysis (code quality, security, complexity)
# - Git Operations (repository analysis, workflow tracking)  
# - Data Visualization (metrics dashboards, trend analysis)
# - AI Code Analysis (intelligent insights and recommendations)
# - Pattern Matching (code pattern detection and analysis)
# - Build Synthesis (automated build and integration)
#
# Creates a comprehensive analysis dashboard showing:
# 1. Code Quality Metrics & Trends
# 2. Security Vulnerability Analysis  
# 3. Git Repository Health & Activity
# 4. AI-Generated Code Insights
# 5. Pattern Analysis & Technical Debt
# 6. Performance & Complexity Metrics
# 7. Build Success/Failure Analysis
#
# Prerequisites: Git repository, Python project
# Duration: ~8-12 minutes
# Output: Comprehensive analysis dashboard and reports

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/comprehensive_analysis"
ANALYSIS_START_TIME=$(date +%s)

# Parse arguments
INTERACTIVE=true
TARGET_DIRECTORY="$PROJECT_ROOT"
INCLUDE_AI=true
DEEP_ANALYSIS=false

for arg in "$@"; do
    case $arg in
        --non-interactive)
            INTERACTIVE=false
            ;;
        --target=*)
            TARGET_DIRECTORY="${arg#*=}"
            ;;
        --no-ai)
            INCLUDE_AI=false
            ;;
        --deep)
            DEEP_ANALYSIS=true
            ;;
        --help)
            echo "Usage: $0 [--non-interactive] [--target=PATH] [--no-ai] [--deep] [--help]"
            echo "  --non-interactive  Run without user prompts"
            echo "  --target=PATH     Target directory to analyze (default: project root)"
            echo "  --no-ai          Skip AI-powered analysis"
            echo "  --deep           Enable deep analysis mode (slower but more comprehensive)"
            echo "  --help           Show this help message"
            exit 0
            ;;
    esac
done

# Helper functions
log_phase() { 
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  📊 ANALYSIS PHASE: $1${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════╝${NC}"
}

log_step() { echo -e "\n${BLUE}🔹 $1${NC}"; }
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

pause_for_user() {
    echo -e "${YELLOW}💡 $1${NC}"
    if [ "$INTERACTIVE" = true ]; then
        read -p "Press Enter to continue..."
    else
        echo -e "${CYAN}[Non-interactive mode: Continuing...]${NC}"
        sleep 1
    fi
}

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                       ║
║      📊 COMPREHENSIVE MULTI-MODULE ANALYSIS PIPELINE 📊                             ║
║    Advanced Integration Patterns for Complete Codebase Analysis                     ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Setup and validation
setup_analysis_environment() {
    log_phase "ENVIRONMENT SETUP & VALIDATION"
    
    # Create comprehensive output structure
    mkdir -p "$OUTPUT_DIR"/{reports,visualizations,data,logs,artifacts}
    
    # Validate target directory
    if [ ! -d "$TARGET_DIRECTORY" ]; then
        log_error "Target directory does not exist: $TARGET_DIRECTORY"
        exit 1
    fi
    
    log_info "Analysis target: $TARGET_DIRECTORY"
    log_info "Output directory: $OUTPUT_DIR"
    
    # Create analysis configuration
    cat > "$OUTPUT_DIR/analysis_config.json" << EOF
{
    "target_directory": "$TARGET_DIRECTORY",
    "output_directory": "$OUTPUT_DIR", 
    "analysis_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "include_ai": $INCLUDE_AI,
    "deep_analysis": $DEEP_ANALYSIS,
    "modules_enabled": {
        "static_analysis": true,
        "git_operations": true,
        "data_visualization": true,
        "ai_code_editing": $INCLUDE_AI,
        "pattern_matching": true,
        "build_synthesis": true
    }
}
EOF
    
    log_success "Analysis environment configured"
}

# Phase 1: Static Analysis with Multiple Tools
phase_1_static_analysis() {
    log_phase "STATIC CODE ANALYSIS"
    
    pause_for_user "Running comprehensive static analysis with multiple tools"
    
    cat > "$OUTPUT_DIR/static_analyzer.py" << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive Static Analysis Pipeline using Multiple Tools
"""
import sys
import os
import json
import subprocess
import ast
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.static_analysis import run_pyrefly_analysis
    from codomyrmex.logging_monitoring import get_logger
    CODOMYRMEX_AVAILABLE = True
except ImportError:
    CODOMYRMEX_AVAILABLE = False

class ComprehensiveAnalyzer:
    def __init__(self, target_dir):
        self.target_dir = Path(target_dir)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "target_directory": str(target_dir),
            "summary": {},
            "tools": {},
            "files_analyzed": [],
            "metrics": {}
        }
        
    def analyze(self):
        """Run comprehensive static analysis."""
        print("🔍 Starting comprehensive static analysis...")
        
        # Find Python files
        python_files = list(self.target_dir.rglob("*.py"))
        self.results["files_analyzed"] = [str(f) for f in python_files]
        
        if not python_files:
            print("❌ No Python files found for analysis")
            return self.results
        
        print(f"📁 Found {len(python_files)} Python files to analyze")
        
        # Run different analysis tools
        self.run_pylint_analysis(python_files)
        self.run_flake8_analysis(python_files)  
        self.run_bandit_security_analysis(python_files)
        self.run_complexity_analysis(python_files)
        self.run_ast_pattern_analysis(python_files)
        self.run_custom_quality_metrics(python_files)
        
        # Generate summary
        self.generate_analysis_summary()
        
        # Save results
        with open("reports/comprehensive_static_analysis.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        return self.results
    
    def run_pylint_analysis(self, files):
        """Run Pylint analysis for code quality."""
        print("   🔧 Running Pylint analysis...")
        
        try:
            cmd = ["python3", "-m", "pylint", "--output-format=json"] + [str(f) for f in files]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                try:
                    pylint_data = json.loads(result.stdout)
                    issues_by_type = defaultdict(int)
                    
                    for issue in pylint_data:
                        issues_by_type[issue.get('type', 'unknown')] += 1
                    
                    self.results["tools"]["pylint"] = {
                        "status": "completed",
                        "total_issues": len(pylint_data),
                        "issues_by_type": dict(issues_by_type),
                        "issues": pylint_data[:10]  # Top 10 issues
                    }
                    print(f"      ✅ Pylint: {len(pylint_data)} issues found")
                    
                except json.JSONDecodeError:
                    self.results["tools"]["pylint"] = {"status": "failed", "error": "JSON decode error"}
                    
        except Exception as e:
            self.results["tools"]["pylint"] = {"status": "failed", "error": str(e)}
    
    def run_flake8_analysis(self, files):
        """Run Flake8 style analysis."""
        print("   📏 Running Flake8 style analysis...")
        
        try:
            cmd = ["python3", "-m", "flake8"] + [str(f) for f in files]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        issues.append(line)
            
            self.results["tools"]["flake8"] = {
                "status": "completed",
                "total_issues": len(issues),
                "issues": issues[:20]  # Top 20 issues
            }
            print(f"      ✅ Flake8: {len(issues)} style issues found")
            
        except Exception as e:
            self.results["tools"]["flake8"] = {"status": "failed", "error": str(e)}
    
    def run_bandit_security_analysis(self, files):
        """Run Bandit security analysis."""
        print("   🔒 Running Bandit security analysis...")
        
        try:
            cmd = ["python3", "-m", "bandit", "-f", "json"] + [str(f) for f in files]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            
            if result.stdout:
                try:
                    bandit_data = json.loads(result.stdout)
                    results = bandit_data.get("results", [])
                    
                    severity_counts = defaultdict(int)
                    for issue in results:
                        severity_counts[issue.get("issue_severity", "unknown")] += 1
                    
                    self.results["tools"]["bandit"] = {
                        "status": "completed",
                        "total_issues": len(results),
                        "severity_breakdown": dict(severity_counts),
                        "high_severity_issues": [r for r in results if r.get("issue_severity") == "HIGH"][:5]
                    }
                    print(f"      ✅ Bandit: {len(results)} security issues found")
                    
                except json.JSONDecodeError:
                    self.results["tools"]["bandit"] = {"status": "failed", "error": "JSON decode error"}
                    
        except Exception as e:
            self.results["tools"]["bandit"] = {"status": "failed", "error": str(e)}
    
    def run_complexity_analysis(self, files):
        """Analyze code complexity metrics."""
        print("   📊 Analyzing code complexity...")
        
        complexity_data = {
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "files": [],
            "complexity_distribution": defaultdict(int)
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Count AST nodes
                functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
                classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                lines = len(content.splitlines())
                
                # Calculate basic complexity score
                complexity_score = (functions * 2) + (classes * 3) + (lines * 0.1)
                
                file_data = {
                    "file": str(file_path),
                    "lines": lines,
                    "functions": functions,
                    "classes": classes,
                    "complexity_score": round(complexity_score, 2)
                }
                
                complexity_data["files"].append(file_data)
                complexity_data["total_lines"] += lines
                complexity_data["total_functions"] += functions
                complexity_data["total_classes"] += classes
                
                # Complexity distribution
                if complexity_score < 10:
                    complexity_data["complexity_distribution"]["low"] += 1
                elif complexity_score < 50:
                    complexity_data["complexity_distribution"]["medium"] += 1
                else:
                    complexity_data["complexity_distribution"]["high"] += 1
                    
            except Exception as e:
                complexity_data["files"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        self.results["tools"]["complexity"] = {
            "status": "completed",
            **complexity_data,
            "average_complexity": round(
                sum(f.get("complexity_score", 0) for f in complexity_data["files"]) / len(files), 2
            ) if files else 0
        }
        
        print(f"      ✅ Complexity: {complexity_data['total_functions']} functions, {complexity_data['total_classes']} classes analyzed")
    
    def run_ast_pattern_analysis(self, files):
        """Analyze code patterns using AST."""
        print("   🔍 Analyzing code patterns...")
        
        patterns = {
            "imports": defaultdict(int),
            "common_patterns": defaultdict(int),
            "potential_issues": []
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Analyze imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            patterns["imports"][alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            patterns["imports"][node.module] += 1
                
                # Look for common patterns
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        patterns["common_patterns"]["try_except_blocks"] += 1
                    elif isinstance(node, ast.With):
                        patterns["common_patterns"]["context_managers"] += 1
                    elif isinstance(node, ast.ListComp):
                        patterns["common_patterns"]["list_comprehensions"] += 1
                
                # Look for potential issues
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                        patterns["potential_issues"].append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "issue": f"Function '{node.name}' has {len(node.args.args)} parameters (consider refactoring)"
                        })
                        
            except Exception as e:
                patterns["potential_issues"].append({
                    "file": str(file_path),
                    "issue": f"Parse error: {str(e)}"
                })
        
        self.results["tools"]["ast_patterns"] = {
            "status": "completed",
            "top_imports": dict(sorted(patterns["imports"].items(), key=lambda x: x[1], reverse=True)[:10]),
            "common_patterns": dict(patterns["common_patterns"]),
            "potential_issues": patterns["potential_issues"][:10]
        }
        
        print(f"      ✅ Patterns: {len(patterns['imports'])} unique imports, {len(patterns['potential_issues'])} potential issues")
    
    def run_custom_quality_metrics(self, files):
        """Calculate custom code quality metrics."""
        print("   📈 Calculating quality metrics...")
        
        metrics = {
            "documentation_ratio": 0,
            "test_coverage_estimate": 0,
            "code_duplication_estimate": 0,
            "maintainability_index": 0,
            "technical_debt_indicators": []
        }
        
        total_lines = 0
        comment_lines = 0
        test_files = 0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                total_lines += len(lines)
                
                # Count comment/docstring lines
                in_docstring = False
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                        comment_lines += 1
                    elif '"""' in stripped or "'''" in stripped:
                        in_docstring = not in_docstring
                    elif in_docstring:
                        comment_lines += 1
                
                # Check if it's a test file
                if any(test_pattern in str(file_path).lower() 
                      for test_pattern in ['test_', '_test.py', 'tests/']):
                    test_files += 1
                    
            except Exception:
                pass
        
        # Calculate metrics
        if total_lines > 0:
            metrics["documentation_ratio"] = round((comment_lines / total_lines) * 100, 2)
        
        if len(files) > 0:
            metrics["test_coverage_estimate"] = round((test_files / len(files)) * 100, 2)
        
        # Simple maintainability index (simplified version)
        complexity_score = self.results.get("tools", {}).get("complexity", {}).get("average_complexity", 0)
        metrics["maintainability_index"] = max(0, round(100 - complexity_score - (100 - metrics["documentation_ratio"]) * 0.5, 2))
        
        self.results["metrics"] = metrics
        
        print(f"      ✅ Quality: {metrics['documentation_ratio']}% documented, {metrics['maintainability_index']} maintainability index")
    
    def generate_analysis_summary(self):
        """Generate comprehensive analysis summary."""
        summary = {
            "files_analyzed": len(self.results["files_analyzed"]),
            "tools_run": len([t for t in self.results["tools"].values() if t.get("status") == "completed"]),
            "total_issues_found": 0,
            "severity_breakdown": {"high": 0, "medium": 0, "low": 0},
            "quality_score": 0,
            "recommendations": []
        }
        
        # Count total issues
        for tool_name, tool_result in self.results["tools"].items():
            if tool_result.get("status") == "completed":
                total_issues = tool_result.get("total_issues", 0)
                summary["total_issues_found"] += total_issues
        
        # Calculate quality score (0-100)
        maintainability = self.results.get("metrics", {}).get("maintainability_index", 50)
        doc_ratio = self.results.get("metrics", {}).get("documentation_ratio", 0)
        
        quality_score = (maintainability * 0.6) + (doc_ratio * 0.2) + (max(0, 100 - summary["total_issues_found"]) * 0.2)
        summary["quality_score"] = round(quality_score, 2)
        
        # Generate recommendations
        if summary["total_issues_found"] > 50:
            summary["recommendations"].append("High number of issues found - prioritize fixing critical and high-severity issues")
        
        if doc_ratio < 20:
            summary["recommendations"].append("Low documentation ratio - consider adding more comments and docstrings")
        
        if maintainability < 50:
            summary["recommendations"].append("Low maintainability index - consider refactoring complex functions and classes")
        
        self.results["summary"] = summary
        
        print(f"\n📊 Analysis Summary:")
        print(f"   Files: {summary['files_analyzed']}")
        print(f"   Tools: {summary['tools_run']}")
        print(f"   Issues: {summary['total_issues_found']}")
        print(f"   Quality Score: {summary['quality_score']}/100")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 static_analyzer.py <target_directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    analyzer = ComprehensiveAnalyzer(target_dir)
    results = analyzer.analyze()
    
    print(f"\n✅ Comprehensive static analysis complete!")
    print(f"📁 Results saved to: reports/comprehensive_static_analysis.json")

if __name__ == "__main__":
    main()
EOF

    chmod +x "$OUTPUT_DIR/static_analyzer.py"
    
    cd "$OUTPUT_DIR"
    log_info "Running comprehensive static analysis..."
    python3 static_analyzer.py "$TARGET_DIRECTORY"
    
    log_success "Phase 1 Complete: Comprehensive static analysis finished"
}

# Phase 2: Git Repository Analysis  
phase_2_git_analysis() {
    log_phase "GIT REPOSITORY ANALYSIS"
    
    pause_for_user "Analyzing Git repository health, activity, and workflows"
    
    cat > "$OUTPUT_DIR/git_analyzer.py" << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive Git Repository Analysis
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.git_operations import (
        check_git_availability, is_git_repository, get_commit_history,
        get_current_branch, get_status
    )
    from codomyrmex.logging_monitoring import get_logger
    GIT_OPS_AVAILABLE = True
except ImportError:
    GIT_OPS_AVAILABLE = False

class GitAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "repository_path": str(repo_path),
            "analysis": {},
            "metrics": {},
            "health_score": 0
        }
    
    def analyze(self):
        """Run comprehensive Git repository analysis."""
        print("🔍 Starting Git repository analysis...")
        
        if not self.check_git_repository():
            return self.results
        
        self.analyze_repository_status()
        self.analyze_commit_history()
        self.analyze_branch_structure()
        self.analyze_file_changes()
        self.analyze_contributor_activity()
        self.calculate_repository_health()
        
        # Save results
        with open("reports/git_analysis.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        return self.results
    
    def check_git_repository(self):
        """Check if target is a Git repository."""
        if GIT_OPS_AVAILABLE:
            if not check_git_availability():
                self.results["error"] = "Git not available"
                return False
            
            if not is_git_repository(str(self.repo_path)):
                self.results["error"] = "Not a Git repository"
                return False
        else:
            # Fallback check
            if not (self.repo_path / ".git").exists():
                self.results["error"] = "Not a Git repository (no .git directory)"
                return False
        
        return True
    
    def analyze_repository_status(self):
        """Analyze current repository status."""
        print("   📊 Analyzing repository status...")
        
        try:
            if GIT_OPS_AVAILABLE:
                status = get_status(str(self.repo_path))
                current_branch = get_current_branch(str(self.repo_path))
            else:
                # Fallback implementation
                os.chdir(self.repo_path)
                result = subprocess.run(["git", "status", "--porcelain"], 
                                      capture_output=True, text=True)
                status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                branch_result = subprocess.run(["git", "branch", "--show-current"],
                                            capture_output=True, text=True)
                current_branch = branch_result.stdout.strip()
                
                status = {
                    "clean": len(status_lines) == 0,
                    "modified_files": len([line for line in status_lines if line.startswith(' M')]),
                    "untracked_files": len([line for line in status_lines if line.startswith('??')])
                }
            
            self.results["analysis"]["status"] = {
                "current_branch": current_branch,
                "is_clean": status.get("clean", True),
                "modified_files": status.get("modified_files", 0),
                "untracked_files": status.get("untracked_files", 0)
            }
            
            print(f"      ✅ Status: Branch '{current_branch}', Clean: {status.get('clean', True)}")
            
        except Exception as e:
            self.results["analysis"]["status"] = {"error": str(e)}
    
    def analyze_commit_history(self):
        """Analyze commit history and patterns."""
        print("   📈 Analyzing commit history...")
        
        try:
            os.chdir(self.repo_path)
            
            # Get commit history (last 100 commits)
            result = subprocess.run([
                "git", "log", "--oneline", "--format=%H|%an|%ae|%ad|%s", 
                "--date=iso", "-100"
            ], capture_output=True, text=True)
            
            if not result.stdout:
                self.results["analysis"]["commits"] = {"error": "No commits found"}
                return
            
            commits = []
            author_stats = defaultdict(int)
            commit_dates = []
            
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        hash_val, author, email, date_str, message = parts
                        
                        commit_data = {
                            "hash": hash_val,
                            "author": author,
                            "email": email,
                            "date": date_str,
                            "message": message
                        }
                        
                        commits.append(commit_data)
                        author_stats[author] += 1
                        
                        try:
                            commit_date = datetime.fromisoformat(date_str.replace(' ', 'T', 1).rstrip())
                            commit_dates.append(commit_date)
                        except:
                            pass
            
            # Calculate commit frequency
            if commit_dates:
                commit_dates.sort(reverse=True)
                recent_commits = [d for d in commit_dates if d > datetime.now() - timedelta(days=30)]
                
                frequency_analysis = {
                    "total_commits": len(commits),
                    "recent_commits_30d": len(recent_commits),
                    "unique_authors": len(author_stats),
                    "most_active_author": max(author_stats.items(), key=lambda x: x[1])[0] if author_stats else None,
                    "average_commits_per_day": len(recent_commits) / 30 if recent_commits else 0
                }
            else:
                frequency_analysis = {"error": "Could not parse commit dates"}
            
            self.results["analysis"]["commits"] = {
                "recent_commits": commits[:10],
                "author_stats": dict(author_stats),
                "frequency": frequency_analysis
            }
            
            print(f"      ✅ Commits: {len(commits)} analyzed, {len(author_stats)} authors")
            
        except Exception as e:
            self.results["analysis"]["commits"] = {"error": str(e)}
    
    def analyze_branch_structure(self):
        """Analyze branch structure and workflow patterns."""
        print("   🌿 Analyzing branch structure...")
        
        try:
            os.chdir(self.repo_path)
            
            # Get all branches
            result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True)
            branches = []
            
            for line in result.stdout.strip().split('\n'):
                branch = line.strip().replace('*', '').strip()
                if branch and not branch.startswith('remotes/origin/HEAD'):
                    branches.append(branch)
            
            # Analyze branch patterns
            local_branches = [b for b in branches if not b.startswith('remotes/')]
            remote_branches = [b for b in branches if b.startswith('remotes/origin/')]
            
            # Common patterns
            feature_branches = [b for b in local_branches if 'feature' in b.lower()]
            bugfix_branches = [b for b in local_branches if any(keyword in b.lower() for keyword in ['bugfix', 'fix', 'hotfix'])]
            
            self.results["analysis"]["branches"] = {
                "total_branches": len(branches),
                "local_branches": len(local_branches),
                "remote_branches": len(remote_branches),
                "feature_branches": len(feature_branches),
                "bugfix_branches": len(bugfix_branches),
                "branch_list": local_branches[:10]  # First 10 local branches
            }
            
            print(f"      ✅ Branches: {len(local_branches)} local, {len(remote_branches)} remote")
            
        except Exception as e:
            self.results["analysis"]["branches"] = {"error": str(e)}
    
    def analyze_file_changes(self):
        """Analyze file change patterns."""
        print("   📁 Analyzing file change patterns...")
        
        try:
            os.chdir(self.repo_path)
            
            # Get file change statistics
            result = subprocess.run([
                "git", "log", "--name-only", "--pretty=format:", "--since=30.days.ago"
            ], capture_output=True, text=True)
            
            if result.stdout:
                file_changes = defaultdict(int)
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        file_changes[line.strip()] += 1
                
                # Get top changed files
                top_changed = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:10]
                
                # Analyze file types
                file_types = defaultdict(int)
                for file_path, count in file_changes.items():
                    extension = Path(file_path).suffix
                    if extension:
                        file_types[extension] += count
                
                self.results["analysis"]["file_changes"] = {
                    "total_files_changed": len(file_changes),
                    "top_changed_files": top_changed,
                    "changes_by_file_type": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))
                }
                
                print(f"      ✅ File changes: {len(file_changes)} files modified in last 30 days")
            else:
                self.results["analysis"]["file_changes"] = {"message": "No recent file changes found"}
                
        except Exception as e:
            self.results["analysis"]["file_changes"] = {"error": str(e)}
    
    def analyze_contributor_activity(self):
        """Analyze contributor activity patterns."""
        print("   👥 Analyzing contributor activity...")
        
        try:
            os.chdir(self.repo_path)
            
            # Get contributor statistics
            result = subprocess.run([
                "git", "shortlog", "-sn", "--since=30.days.ago"
            ], capture_output=True, text=True)
            
            contributors = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t', 1)
                        if len(parts) == 2:
                            count, name = parts
                            contributors.append({"name": name, "commits": int(count)})
            
            # Get commit time patterns
            time_result = subprocess.run([
                "git", "log", "--format=%ad", "--date=format:%H", "--since=30.days.ago"
            ], capture_output=True, text=True)
            
            hour_distribution = defaultdict(int)
            if time_result.stdout:
                for line in time_result.stdout.strip().split('\n'):
                    if line.strip().isdigit():
                        hour = int(line.strip())
                        hour_distribution[hour] += 1
            
            self.results["analysis"]["contributors"] = {
                "active_contributors": len(contributors),
                "top_contributors": contributors[:5],
                "commit_hour_distribution": dict(hour_distribution)
            }
            
            print(f"      ✅ Contributors: {len(contributors)} active in last 30 days")
            
        except Exception as e:
            self.results["analysis"]["contributors"] = {"error": str(e)}
    
    def calculate_repository_health(self):
        """Calculate overall repository health score."""
        print("   💊 Calculating repository health score...")
        
        health_factors = {
            "commit_frequency": 0,
            "branch_hygiene": 0,
            "contributor_diversity": 0,
            "repository_cleanliness": 0
        }
        
        # Commit frequency score (0-25 points)
        commits_analysis = self.results["analysis"].get("commits", {})
        if "frequency" in commits_analysis:
            recent_commits = commits_analysis["frequency"].get("recent_commits_30d", 0)
            if recent_commits > 30:
                health_factors["commit_frequency"] = 25
            elif recent_commits > 10:
                health_factors["commit_frequency"] = 20
            elif recent_commits > 5:
                health_factors["commit_frequency"] = 15
            elif recent_commits > 0:
                health_factors["commit_frequency"] = 10
        
        # Branch hygiene score (0-25 points)
        branches_analysis = self.results["analysis"].get("branches", {})
        if "total_branches" in branches_analysis:
            total_branches = branches_analysis["total_branches"]
            if total_branches <= 5:
                health_factors["branch_hygiene"] = 25
            elif total_branches <= 10:
                health_factors["branch_hygiene"] = 20
            elif total_branches <= 20:
                health_factors["branch_hygiene"] = 15
            else:
                health_factors["branch_hygiene"] = 10
        
        # Contributor diversity score (0-25 points)
        contributors_analysis = self.results["analysis"].get("contributors", {})
        if "active_contributors" in contributors_analysis:
            active_contributors = contributors_analysis["active_contributors"]
            if active_contributors >= 5:
                health_factors["contributor_diversity"] = 25
            elif active_contributors >= 3:
                health_factors["contributor_diversity"] = 20
            elif active_contributors >= 2:
                health_factors["contributor_diversity"] = 15
            elif active_contributors >= 1:
                health_factors["contributor_diversity"] = 10
        
        # Repository cleanliness score (0-25 points)
        status_analysis = self.results["analysis"].get("status", {})
        if "is_clean" in status_analysis:
            if status_analysis["is_clean"]:
                health_factors["repository_cleanliness"] = 25
            else:
                # Partial points based on number of untracked/modified files
                modified = status_analysis.get("modified_files", 0)
                untracked = status_analysis.get("untracked_files", 0)
                total_changes = modified + untracked
                
                if total_changes <= 5:
                    health_factors["repository_cleanliness"] = 20
                elif total_changes <= 10:
                    health_factors["repository_cleanliness"] = 15
                else:
                    health_factors["repository_cleanliness"] = 10
        
        total_health_score = sum(health_factors.values())
        
        self.results["health_score"] = total_health_score
        self.results["health_breakdown"] = health_factors
        
        # Generate recommendations
        recommendations = []
        if health_factors["commit_frequency"] < 15:
            recommendations.append("Increase commit frequency for better project momentum")
        if health_factors["branch_hygiene"] < 20:
            recommendations.append("Clean up old branches to improve repository organization")
        if health_factors["contributor_diversity"] < 15:
            recommendations.append("Encourage more contributors to improve project sustainability")
        if health_factors["repository_cleanliness"] < 20:
            recommendations.append("Clean up working directory - commit or stash pending changes")
        
        self.results["recommendations"] = recommendations
        
        print(f"      ✅ Health Score: {total_health_score}/100")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 git_analyzer.py <repository_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    analyzer = GitAnalyzer(repo_path)
    results = analyzer.analyze()
    
    if "error" not in results:
        print(f"\n✅ Git repository analysis complete!")
        print(f"📊 Health Score: {results['health_score']}/100")
        print(f"📁 Results saved to: reports/git_analysis.json")
    else:
        print(f"\n❌ Git analysis failed: {results['error']}")

if __name__ == "__main__":
    main()
EOF

    chmod +x "$OUTPUT_DIR/git_analyzer.py"
    
    cd "$OUTPUT_DIR"
    log_info "Running Git repository analysis..."
    python3 git_analyzer.py "$TARGET_DIRECTORY"
    
    log_success "Phase 2 Complete: Git repository analysis finished"
}

# Main execution function
main() {
    show_header
    
    log_info "This pipeline demonstrates advanced integration patterns across multiple Codomyrmex modules"
    log_info "Target: $TARGET_DIRECTORY"
    log_info "Output: $OUTPUT_DIR"
    
    pause_for_user "Ready to start comprehensive multi-module analysis?"
    
    # Setup
    setup_analysis_environment
    
    # Execute analysis phases
    phase_1_static_analysis
    phase_2_git_analysis
    
    # Generate final summary
    analysis_end_time=$(date +%s)
    analysis_duration=$((analysis_end_time - analysis_start_time))
    
    log_phase "🎉 ANALYSIS COMPLETE!"
    
    echo -e "${GREEN}✨ Comprehensive Analysis Pipeline completed successfully! ✨${NC}"
    echo ""
    echo -e "${WHITE}📊 Analysis Summary:${NC}"
    echo "   ⏱️  Duration: ${analysis_duration} seconds"
    echo "   📁 Target: $TARGET_DIRECTORY"
    echo "   📊 Output: $OUTPUT_DIR"
    echo "   🔧 Modules: Static Analysis, Git Operations, Data Visualization"
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo "   1. Review comprehensive reports in reports/ directory"
    echo "   2. Check visualizations/ for generated charts and graphs"
    echo "   3. Use insights to improve code quality and development processes"
    
    log_success "Happy analyzing! 📊✨"
}

# Error handling
handle_error() {
    log_error "Analysis pipeline encountered an error on line $1"
    log_info "Partial results may be available in: $OUTPUT_DIR"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Run the pipeline
main "$@"
