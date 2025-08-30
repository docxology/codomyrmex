#!/bin/bash
# 🐜 Codomyrmex Static Analysis Demo
#
# This script demonstrates Codomyrmex's static analysis capabilities by:
# 1. Analyzing Python code for quality issues
# 2. Running security scans and complexity analysis
# 3. Generating comprehensive reports
# 4. Showing integration with data visualization for metrics
#
# Prerequisites: Sample Python code (generated automatically)
# Duration: ~2 minutes
# Output: Analysis reports in examples/output/static-analysis/

set -e  # Exit on any error

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/examples/output/static-analysis"
DEMO_START_TIME=$(date +%s)

# Helper functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "\n${BLUE}🔹 $1${NC}"; }
pause_for_user() { echo -e "${YELLOW}💡 $1${NC}"; read -p "Press Enter to continue..."; }

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐜 CODOMYRMEX STATIC ANALYSIS DEMO 🐜                       ║
║   Code Quality, Security, and Complexity Analysis             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    log_step "Environment Setup & Validation"
    
    # Check project root
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from examples/basic/"
        exit 1
    fi
    
    # Activate virtual environment
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    # Test Codomyrmex import
    log_info "Checking Codomyrmex installation..."
    if ! python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src'); from codomyrmex.static_analysis import run_pyrefly_analysis" 2>/dev/null; then
        log_error "Codomyrmex static analysis module not available. Please run: pip install -e ."
        exit 1
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log_success "Environment ready!"
}

create_sample_code() {
    log_step "Creating Sample Code for Analysis"
    
    log_info "Generating sample Python files with various quality issues..."
    
    # Create a good quality file
    cat > "$OUTPUT_DIR/good_code.py" << 'EOF'
"""
High-quality Python module demonstrating best practices.

This module shows well-structured, documented, and maintainable code
that follows Python conventions and best practices.
"""

import typing
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class User:
    """Represents a user with validation and clean structure."""
    
    name: str
    email: str
    age: int
    is_active: bool = True
    
    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Name cannot be empty")
        
        if "@" not in self.email or "." not in self.email:
            raise ValueError("Invalid email format")
        
        if self.age < 0 or self.age > 120:
            raise ValueError("Age must be between 0 and 120")
    
    def get_display_name(self) -> str:
        """Return formatted display name for UI purposes."""
        return f"{self.name} ({self.email})"
    
    def is_adult(self) -> bool:
        """Check if user is an adult (18 or older)."""
        return self.age >= 18


class UserManager:
    """Manages user operations with proper error handling and validation."""
    
    def __init__(self) -> None:
        """Initialize user manager with empty user list."""
        self._users: List[User] = []
    
    def add_user(self, user: User) -> bool:
        """
        Add a user to the system.
        
        Args:
            user: User object to add
            
        Returns:
            bool: True if user was added successfully
            
        Raises:
            ValueError: If user already exists or is invalid
        """
        if not isinstance(user, User):
            raise ValueError("Expected User object")
        
        # Check for duplicate emails
        if self.get_user_by_email(user.email) is not None:
            raise ValueError(f"User with email {user.email} already exists")
        
        self._users.append(user)
        return True
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        if not email or not isinstance(email, str):
            return None
        
        email = email.lower().strip()
        for user in self._users:
            if user.email.lower() == email:
                return user
        return None
    
    def get_active_users(self) -> List[User]:
        """Return list of all active users."""
        return [user for user in self._users if user.is_active]
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Calculate user statistics.
        
        Returns:
            Dict containing various user statistics
        """
        total_users = len(self._users)
        active_users = len(self.get_active_users())
        adult_users = len([u for u in self._users if u.is_adult()])
        
        if total_users == 0:
            average_age = 0.0
        else:
            average_age = sum(u.age for u in self._users) / total_users
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'adult_users': adult_users,
            'average_age': round(average_age, 2),
            'activity_rate': round((active_users / total_users) * 100, 2) if total_users > 0 else 0
        }


def create_sample_users() -> List[User]:
    """Create sample users for testing purposes."""
    users = [
        User("Alice Johnson", "alice@example.com", 28),
        User("Bob Smith", "bob@example.com", 34),
        User("Charlie Brown", "charlie@example.com", 16),
    ]
    return users


if __name__ == "__main__":
    # Demonstration of usage
    manager = UserManager()
    users = create_sample_users()
    
    for user in users:
        try:
            manager.add_user(user)
            print(f"Added user: {user.get_display_name()}")
        except ValueError as e:
            print(f"Error adding user: {e}")
    
    stats = manager.get_user_statistics()
    print(f"User statistics: {stats}")
EOF

    # Create a file with various quality issues
    cat > "$OUTPUT_DIR/problematic_code.py" << 'EOF'
# Poor quality Python code with multiple issues

import os,sys,json
import requests
import time

# Global variables (not recommended)
USERS = []
api_key = "sk-1234567890abcdef"  # Hardcoded secret (security issue)
DEBUG = True

def addUser(name,email,age):  # Poor naming convention
    global USERS
    # No input validation
    u = {"name":name,"email":email,"age":age}  # Poor formatting
    USERS.append(u)
    return True

def getUser(email):
    for u in USERS:
        if u["email"]==email:
            return u
    return None

# Overly complex function
def processData(data):
    result = []
    for item in data:
        if item is not None:
            if "type" in item:
                if item["type"] == "user":
                    if "active" in item:
                        if item["active"] == True:
                            if "name" in item and "email" in item:
                                if len(item["name"]) > 0 and "@" in item["email"]:
                                    processed = {
                                        "id": item.get("id", 0),
                                        "name": item["name"].strip().title(),
                                        "email": item["email"].lower(),
                                        "status": "active",
                                        "processed_at": time.time()
                                    }
                                    result.append(processed)
    return result

class userManager:  # Should be UserManager
    def __init__(self):
        pass
    
    def saveUsers(self,filename):  # No error handling
        f = open(filename, "w")
        json.dump(USERS, f)
        f.close()
    
    def loadUsers(self,filename):
        f = open(filename, "r")
        data = f.read()
        f.close()
        USERS = json.loads(data)  # This won't work (global scope issue)
    
    # Unused method
    def deleteUser(self, email):
        pass
    
    # Method with security issue
    def fetchUserData(self, user_id):
        url = f"https://api.example.com/users/{user_id}?key={api_key}"  # Exposed API key
        response = requests.get(url)
        return response.json()

# Unreachable code
if False:
    print("This will never execute")

# Long line that exceeds PEP 8 recommendations
def very_long_function_name_that_does_something_complex(parameter_one, parameter_two, parameter_three, parameter_four, parameter_five):
    return parameter_one + parameter_two + parameter_three + parameter_four + parameter_five

# SQL injection vulnerability (simulated)
def getUserByQuery(query):
    sql = f"SELECT * FROM users WHERE {query}"  # Dangerous string formatting
    # Simulated database execution
    print(f"Executing: {sql}")

# No main guard
print("This code runs when imported!")
EOF

    # Create a medium complexity file
    cat > "$OUTPUT_DIR/medium_complexity.py" << 'EOF'
"""
Medium complexity Python code with some issues but reasonable structure.
"""

import json
import os
from typing import List, Dict, Union


class DataProcessor:
    """Data processor with some complexity issues."""
    
    def __init__(self, config_file: str = None):
        self.config = {}
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, filename: str):
        """Load configuration from file."""
        try:
            with open(filename, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Config file {filename} not found")  # Should use logging
            self.config = {}
        except json.JSONDecodeError:
            print("Invalid JSON in config file")  # Should use logging
            self.config = {}
    
    def process_items(self, items: List[Dict]) -> List[Dict]:
        """Process a list of items with various transformations."""
        results = []
        
        for item in items:
            # Nested conditions (complexity issue)
            if 'type' in item:
                if item['type'] == 'user':
                    if 'status' in item:
                        if item['status'] == 'active':
                            processed_item = self._process_user(item)
                            if processed_item:
                                results.append(processed_item)
                        elif item['status'] == 'inactive':
                            # Different processing for inactive users
                            processed_item = self._process_inactive_user(item)
                            if processed_item:
                                results.append(processed_item)
                elif item['type'] == 'admin':
                    processed_item = self._process_admin(item)
                    if processed_item:
                        results.append(processed_item)
            else:
                # Handle items without type
                if 'name' in item:
                    processed_item = self._process_generic(item)
                    if processed_item:
                        results.append(processed_item)
        
        return results
    
    def _process_user(self, user: Dict) -> Dict:
        """Process regular user."""
        return {
            'id': user.get('id'),
            'name': user.get('name', '').strip().title(),
            'email': user.get('email', '').lower(),
            'type': 'processed_user'
        }
    
    def _process_inactive_user(self, user: Dict) -> Dict:
        """Process inactive user."""
        processed = self._process_user(user)
        processed['status'] = 'inactive'
        return processed
    
    def _process_admin(self, admin: Dict) -> Dict:
        """Process admin user."""
        return {
            'id': admin.get('id'),
            'name': admin.get('name', '').strip().title(),
            'email': admin.get('email', '').lower(),
            'type': 'admin',
            'permissions': admin.get('permissions', [])
        }
    
    def _process_generic(self, item: Dict) -> Dict:
        """Process generic item."""
        return {
            'name': item.get('name', 'Unknown'),
            'type': 'generic'
        }
    
    def validate_email(self, email: str) -> bool:
        """Simple email validation."""
        # Simplified validation (could be more robust)
        return '@' in email and '.' in email and len(email) > 5
    
    def export_results(self, results: List[Dict], filename: str) -> bool:
        """Export results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            return True
        except Exception as e:  # Too broad exception handling
            print(f"Error exporting results: {e}")
            return False


def main():
    """Main function demonstrating processor usage."""
    processor = DataProcessor()
    
    sample_data = [
        {'id': 1, 'type': 'user', 'status': 'active', 'name': 'john doe', 'email': 'JOHN@EXAMPLE.COM'},
        {'id': 2, 'type': 'user', 'status': 'inactive', 'name': 'jane smith', 'email': 'jane@example.com'},
        {'id': 3, 'type': 'admin', 'name': 'admin user', 'email': 'admin@example.com', 'permissions': ['read', 'write']},
        {'name': 'unknown item'}
    ]
    
    results = processor.process_items(sample_data)
    
    if processor.export_results(results, 'processed_data.json'):
        print(f"Processed {len(results)} items successfully")
    else:
        print("Failed to export results")


if __name__ == "__main__":
    main()
EOF

    log_success "Sample code files created!"
    log_info "Created: good_code.py (high quality), problematic_code.py (many issues), medium_complexity.py (moderate issues)"
}

run_static_analysis() {
    log_step "Running Static Analysis"
    
    pause_for_user "We'll now analyze the sample code using Codomyrmex static analysis tools"
    
    cat > "$OUTPUT_DIR/run_analysis.py" << 'EOF'
import sys
import os
import json
from pathlib import Path

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.static_analysis import run_pyrefly_analysis
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def analyze_code_files():
    """Analyze sample code files and generate reports."""
    
    current_dir = Path(__file__).parent
    
    # Files to analyze
    files_to_analyze = [
        str(current_dir / "good_code.py"),
        str(current_dir / "problematic_code.py"), 
        str(current_dir / "medium_complexity.py")
    ]
    
    print("🔍 Running static analysis on sample code files...")
    
    results = {}
    
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            print(f"\n📋 Analyzing {filename}...")
            
            try:
                # Run analysis on individual file
                analysis_result = run_pyrefly_analysis([file_path], str(current_dir))
                
                results[filename] = {
                    'file_path': file_path,
                    'analysis': analysis_result,
                    'status': 'completed'
                }
                
                # Print summary
                issue_count = analysis_result.get('issue_count', 0)
                if issue_count == 0:
                    print(f"   ✅ No issues found in {filename}")
                else:
                    print(f"   ⚠️  Found {issue_count} issues in {filename}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {filename}: {e}")
                results[filename] = {
                    'file_path': file_path,
                    'error': str(e),
                    'status': 'error'
                }
        else:
            print(f"   ❌ File not found: {file_path}")
    
    # Save detailed results
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Static analysis completed!")
    print("📄 Detailed results saved to: analysis_results.json")
    
    return results

def generate_summary_report(results):
    """Generate a human-readable summary report."""
    
    print("\n📊 STATIC ANALYSIS SUMMARY REPORT")
    print("=" * 50)
    
    total_files = len(results)
    files_with_issues = 0
    total_issues = 0
    
    for filename, result in results.items():
        if result['status'] == 'completed':
            issue_count = result['analysis'].get('issue_count', 0)
            total_issues += issue_count
            if issue_count > 0:
                files_with_issues += 1
            
            print(f"\n📁 {filename}:")
            print(f"   Issues: {issue_count}")
            
            # Show sample issues if any
            issues = result['analysis'].get('issues', [])
            if issues and len(issues) > 0:
                print("   Sample issues:")
                for issue in issues[:3]:  # Show first 3 issues
                    severity = issue.get('severity', 'unknown')
                    message = issue.get('message', 'No message')
                    line = issue.get('line', 'unknown')
                    print(f"     • Line {line}: {message} ({severity})")
                
                if len(issues) > 3:
                    print(f"     ... and {len(issues) - 3} more issues")
        else:
            print(f"\n📁 {filename}: ❌ {result.get('error', 'Analysis failed')}")
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Total files analyzed: {total_files}")
    print(f"   Files with issues: {files_with_issues}")
    print(f"   Total issues found: {total_issues}")
    
    if total_files > 0:
        avg_issues = total_issues / total_files
        print(f"   Average issues per file: {avg_issues:.1f}")
    
    # Generate recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if total_issues == 0:
        print("   🎉 Excellent! No issues found. Keep up the good work!")
    elif total_issues < 5:
        print("   ✅ Good code quality. Address the few issues found.")
    elif total_issues < 20:
        print("   ⚠️  Moderate issues found. Consider refactoring problematic areas.")
    else:
        print("   🚨 Many issues found. Prioritize code quality improvements.")
    
    return {
        'total_files': total_files,
        'files_with_issues': files_with_issues,
        'total_issues': total_issues
    }

if __name__ == "__main__":
    results = analyze_code_files()
    summary = generate_summary_report(results)
    
    logger.info(f"Static analysis completed: {summary['total_issues']} issues in {summary['total_files']} files")
EOF

    cd "$OUTPUT_DIR"
    python3 run_analysis.py
    
    log_success "Static analysis completed!"
}

create_analysis_visualization() {
    log_step "Creating Analysis Visualizations"
    
    pause_for_user "Let's create visualizations of the analysis results"
    
    cat > "$OUTPUT_DIR/visualize_results.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_bar_chart, create_pie_chart

print("📊 Creating visualizations of static analysis results...")

# Load analysis results
try:
    with open('analysis_results.json', 'r') as f:
        results = json.load(f)
    
    # Extract data for visualization
    filenames = []
    issue_counts = []
    
    for filename, result in results.items():
        if result['status'] == 'completed':
            filenames.append(filename.replace('.py', ''))
            issue_counts.append(result['analysis'].get('issue_count', 0))
    
    if filenames and issue_counts:
        # Create bar chart of issues by file
        create_bar_chart(
            categories=filenames,
            values=issue_counts,
            title="Code Issues by File",
            x_label="Python Files",
            y_label="Number of Issues",
            output_path="issues_by_file.png",
            show_plot=False,
            bar_color="lightcoral"
        )
        print("✅ Created issues_by_file.png")
        
        # Create pie chart for issue distribution
        if sum(issue_counts) > 0:
            create_pie_chart(
                labels=filenames,
                sizes=issue_counts,
                title="Distribution of Code Issues",
                output_path="issue_distribution.png",
                show_plot=False,
                autopct='%1.1f%%'
            )
            print("✅ Created issue_distribution.png")
        else:
            print("🎉 No issues found - no distribution chart needed!")
        
        # Create quality score visualization
        max_possible_score = 100
        quality_scores = []
        for count in issue_counts:
            # Simple quality score: start at 100, subtract points for issues
            score = max(0, max_possible_score - (count * 5))
            quality_scores.append(score)
        
        create_bar_chart(
            categories=filenames,
            values=quality_scores,
            title="Code Quality Scores (0-100)",
            x_label="Python Files", 
            y_label="Quality Score",
            output_path="quality_scores.png",
            show_plot=False,
            bar_color="lightgreen"
        )
        print("✅ Created quality_scores.png")
    else:
        print("❌ No analysis results found to visualize")

except FileNotFoundError:
    print("❌ Analysis results file not found. Run static analysis first.")
except Exception as e:
    print(f"❌ Error creating visualizations: {e}")

print("🎉 Analysis visualizations completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 visualize_results.py
    
    log_success "Analysis visualizations created!"
}

demo_integration_example() {
    log_step "Integration Example: Analysis + Logging + Visualization"
    
    pause_for_user "Let's see how static analysis integrates with other Codomyrmex modules"
    
    cat > "$OUTPUT_DIR/integration_demo.py" << 'EOF'
import json
import sys
import os
from datetime import datetime

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.static_analysis import run_pyrefly_analysis
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def comprehensive_analysis_workflow():
    """Demonstrate integration between static analysis, logging, and visualization."""
    
    logger.info("Starting comprehensive code analysis workflow")
    
    # Files to analyze
    code_files = [
        "good_code.py",
        "problematic_code.py", 
        "medium_complexity.py"
    ]
    
    analysis_timeline = []
    issue_counts = []
    
    for i, filename in enumerate(code_files):
        if os.path.exists(filename):
            logger.info(f"Analyzing file {i+1}/{len(code_files)}: {filename}")
            
            try:
                start_time = datetime.now()
                result = run_pyrefly_analysis([filename], ".")
                end_time = datetime.now()
                
                analysis_duration = (end_time - start_time).total_seconds()
                issue_count = result.get('issue_count', 0)
                
                analysis_timeline.append({
                    'file': filename,
                    'duration': analysis_duration,
                    'issues': issue_count,
                    'timestamp': start_time.isoformat()
                })
                
                issue_counts.append(issue_count)
                
                logger.info(f"Completed analysis of {filename}: {issue_count} issues in {analysis_duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to analyze {filename}: {e}")
                analysis_timeline.append({
                    'file': filename,
                    'duration': 0,
                    'issues': -1,  # Indicate error
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    # Create workflow visualization
    if len(issue_counts) > 0:
        create_line_plot(
            x_data=list(range(len(code_files))),
            y_data=issue_counts,
            title="Code Analysis Workflow: Issues Over Time",
            x_label="File Analysis Order",
            y_label="Issues Found",
            output_path="analysis_workflow.png",
            show_plot=False,
            markers=True
        )
        logger.info("Created workflow visualization: analysis_workflow.png")
    
    # Save comprehensive report
    workflow_report = {
        'analysis_date': datetime.now().isoformat(),
        'total_files_analyzed': len(code_files),
        'total_issues_found': sum(i for i in issue_counts if i >= 0),
        'analysis_timeline': analysis_timeline,
        'summary': {
            'files_with_issues': sum(1 for count in issue_counts if count > 0),
            'average_issues_per_file': sum(issue_counts) / len(issue_counts) if issue_counts else 0,
            'most_problematic_file': code_files[issue_counts.index(max(issue_counts))] if issue_counts else None
        }
    }
    
    with open('workflow_report.json', 'w') as f:
        json.dump(workflow_report, f, indent=2)
    
    logger.info("Comprehensive analysis workflow completed")
    logger.info(f"Generated workflow report: workflow_report.json")
    
    print("🔗 Integration Demo Results:")
    print(f"   📊 Analyzed {workflow_report['total_files_analyzed']} files")
    print(f"   ⚠️  Found {workflow_report['total_issues_found']} total issues")
    print(f"   📈 Created workflow visualization")
    print(f"   📄 Generated comprehensive report")
    
    return workflow_report

if __name__ == "__main__":
    report = comprehensive_analysis_workflow()
    print("✅ Integration demonstration completed!")
EOF

    cd "$OUTPUT_DIR"
    python3 integration_demo.py
    
    log_success "Integration example completed!"
    log_info "This shows how static analysis works with logging and visualization modules"
}

show_results() {
    log_step "Demo Results & Analysis"
    
    cd "$OUTPUT_DIR"
    
    log_info "Static analysis demo completed! Here's what was generated:"
    echo -e "${WHITE}📁 Output Directory: $OUTPUT_DIR${NC}"
    echo ""
    
    # Show generated files
    echo -e "${GREEN}📄 Generated Files:${NC}"
    for file in *.py; do
        [[ -f "$file" ]] && echo -e "   🐍 $file - Python analysis script"
    done
    
    for file in *.json; do 
        [[ -f "$file" ]] && echo -e "   📊 $file - Analysis results"
    done
    
    for file in *.png; do
        [[ -f "$file" ]] && echo -e "   📈 $file - Analysis visualization"
    done
    
    echo ""
    
    # Show analysis summary if available
    if [[ -f "analysis_results.json" ]]; then
        log_info "Analysis Summary:"
        python3 -c "
import json
with open('analysis_results.json', 'r') as f:
    results = json.load(f)
    
total_issues = 0
for filename, result in results.items():
    if result['status'] == 'completed':
        issues = result['analysis'].get('issue_count', 0)
        total_issues += issues
        status = '✅' if issues == 0 else f'⚠️  {issues} issues'
        print(f'   {filename}: {status}')

print(f'   Total issues found: {total_issues}')
"
    fi
    
    echo ""
    log_info "You can view the generated visualizations and detailed reports"
    return 0
}

show_summary() {
    log_step "Demo Summary & Learning Outcomes"
    
    demo_end_time=$(date +%s)
    demo_duration=$((demo_end_time - demo_start_time))
    
    echo -e "${GREEN}🎉 Static Analysis Demo Complete!${NC}"
    echo ""
    echo -e "${WHITE}🔍 What You've Learned:${NC}"
    echo "   ✅ How to analyze Python code for quality issues"
    echo "   ✅ Generate comprehensive analysis reports"
    echo "   ✅ Create visualizations of code metrics"
    echo "   ✅ Integrate analysis with logging and other modules"
    echo "   ✅ Understand different code quality levels"
    
    echo ""
    echo -e "${WHITE}📊 Demo Statistics:${NC}"
    echo "   🕒 Duration: ${demo_duration} seconds"
    echo "   📄 Files analyzed: 3 Python files"
    echo "   🎯 Modules used: static_analysis, data_visualization, logging_monitoring"
    echo "   📦 Output location: $OUTPUT_DIR"
    
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Review the analysis results and visualizations"
    echo "   2. Try analyzing your own Python code"
    echo "   3. Run integration examples: cd ../integration"
    echo "   4. Check documentation: docs/modules/static_analysis/"
    echo "   5. Explore code execution sandbox: ./code-execution-demo.sh"
    
    echo ""
    echo -e "${CYAN}💡 Pro Tips:${NC}"
    echo "   • Use static analysis in your CI/CD pipelines"
    echo "   • Combine with AI code editing for automated fixes"
    echo "   • Create custom quality metrics for your projects"
    echo "   • Integrate with build processes for quality gates"
}

cleanup_option() {
    echo ""
    read -p "🧹 Would you like to clean up the generated files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up generated files..."
        cd "$OUTPUT_DIR"
        rm -f *.py *.json *.png
        log_success "Cleanup completed!"
    else
        log_info "Files preserved for your exploration"
    fi
}

# Error handling
handle_error() {
    log_error "Demo encountered an error on line $1"
    log_info "Check the logs above for details"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Main execution
main() {
    show_header
    
    log_info "This demo showcases Codomyrmex's static analysis capabilities"
    log_info "We'll analyze Python code for quality, security, and complexity issues"
    log_info "Duration: ~2 minutes | Output: examples/output/static-analysis/"
    
    pause_for_user "Ready to start the static analysis demo?"
    
    check_environment
    create_sample_code
    run_static_analysis
    create_analysis_visualization
    demo_integration_example
    
    if show_results; then
        show_summary
        cleanup_option
    else
        log_error "Demo completed with issues. Check output directory for partial results."
        exit 1
    fi
}

# Run the demo
main "$@"
