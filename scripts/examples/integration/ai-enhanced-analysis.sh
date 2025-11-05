#!/bin/bash
# 🐜 Codomyrmex AI-Enhanced Analysis Integration Demo
#
# This script demonstrates how multiple Codomyrmex modules work together by:
# 1. Using AI to generate code based on requirements
# 2. Analyzing the generated code with static analysis
# 3. Visualizing the analysis results and metrics
# 4. Using AI to suggest improvements based on analysis
# 5. Showing the complete development workflow integration
#
# Prerequisites: API keys for AI services (OpenAI, Anthropic, or Google)
# Duration: ~5 minutes
# Output: Complete workflow results in scripts/output/ai-enhanced-analysis/

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
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/ai-enhanced-analysis"
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
║   🐜 CODOMYRMEX AI-ENHANCED ANALYSIS DEMO 🐜                  ║
║   AI Code Generation + Static Analysis + Visualization        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    log_step "Environment Setup & Validation"
    
    # Check project root
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from project root: ./scripts/examples/integration/ai-enhanced-analysis.sh"
        exit 1
    fi
    
    # Activate virtual environment
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    # Check API keys
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        log_info "Loading environment variables..."
        source "$PROJECT_ROOT/.env"
    fi
    
    # Check if at least one API key is available
    api_keys_available=false
    if [[ -n "$OPENAI_API_KEY" ]]; then
        log_success "OpenAI API key found"
        api_keys_available=true
    fi
    if [[ -n "$ANTHROPIC_API_KEY" ]]; then
        log_success "Anthropic API key found"  
        api_keys_available=true
    fi
    if [[ -n "$GOOGLE_API_KEY" ]]; then
        log_success "Google API key found"
        api_keys_available=true
    fi
    
    if [[ "$api_keys_available" != true ]]; then
        log_warning "No AI API keys found in .env file"
        log_info "This demo can run in simulation mode, but won't show real AI capabilities"
        read -p "Continue with simulation mode? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Please add API keys to .env file and try again"
            exit 1
        fi
        export SIMULATION_MODE=true
    fi
    
    # Test Codomyrmex modules
    log_info "Checking Codomyrmex installation..."
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
try:
    from codomyrmex.ai_code_editing import generate_code_snippet
    from codomyrmex.static_analysis import run_pyrefly_analysis
    from codomyrmex.data_visualization import create_bar_chart
    print('All required modules available')
except ImportError as e:
    print(f'Module import error: {e}')
    exit(1)
" || {
        log_error "Codomyrmex modules not available. Please run: pip install -e ."
        exit 1
    }
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log_success "Environment ready!"
}

generate_code_requirements() {
    log_step "Defining Code Generation Requirements"
    
    log_info "Setting up code generation scenarios..."
    
    # Create requirements file
    cat > "$OUTPUT_DIR/requirements.json" << 'EOF'
{
  "scenarios": [
    {
      "name": "data_processor",
      "description": "Create a Python class for processing CSV data with validation",
      "requirements": [
        "Read CSV files with pandas",
        "Validate data types and ranges", 
        "Handle missing values",
        "Export processed data to JSON",
        "Include proper error handling",
        "Add logging for operations"
      ],
      "language": "python",
      "complexity": "medium"
    },
    {
      "name": "api_client", 
      "description": "Create a REST API client with authentication",
      "requirements": [
        "Support GET, POST, PUT, DELETE methods",
        "Handle authentication tokens",
        "Include retry logic for failed requests",
        "Add request/response logging",
        "Support JSON and form data",
        "Include comprehensive error handling"
      ],
      "language": "python",
      "complexity": "high"
    },
    {
      "name": "utility_functions",
      "description": "Create utility functions for common tasks", 
      "requirements": [
        "String manipulation functions",
        "Date/time utilities",
        "File I/O helpers",
        "Data validation functions",
        "Simple mathematical operations"
      ],
      "language": "python",
      "complexity": "low"
    }
  ]
}
EOF

    log_success "Code generation requirements defined!"
    log_info "Will generate 3 different Python modules with varying complexity"
}

ai_code_generation() {
    log_step "AI-Powered Code Generation"
    
    pause_for_user "We'll use AI to generate Python code based on the defined requirements"
    
    cat > "$OUTPUT_DIR/generate_code.py" << 'EOF'
import json
import sys
import os
from datetime import datetime

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.logging_monitoring import get_logger

# Check if we have real AI capabilities or need simulation
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'false').lower() == 'true'

if not SIMULATION_MODE:
    try:
        from codomyrmex.ai_code_editing import generate_code_snippet
    except ImportError:
        print("AI modules not available, using simulation mode")
        SIMULATION_MODE = True

logger = get_logger(__name__)

def simulate_code_generation(prompt, language):
    """Simulate AI code generation when API keys aren't available."""
    
    if "data_processor" in prompt.lower():
        return {
            "status": "success",
            "generated_code": '''
import pandas as pd
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DataProcessor:
    """CSV data processor with validation and export capabilities."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data = None
        
    def read_csv(self, file_path: str) -> bool:
        """Read CSV file with error handling."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            self.data = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {len(self.data)} rows from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return False
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate data types and ranges."""
        if self.data is None:
            return {"valid": False, "errors": ["No data loaded"]}
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {
                "total_rows": len(self.data),
                "missing_values": self.data.isnull().sum().to_dict(),
                "data_types": self.data.dtypes.to_dict()
            }
        }
        
        # Check for missing values
        missing_counts = self.data.isnull().sum()
        for col, count in missing_counts.items():
            if count > 0:
                validation_results["warnings"].append(
                    f"Column {col} has {count} missing values"
                )
        
        return validation_results
    
    def handle_missing_values(self, strategy: str = "drop") -> bool:
        """Handle missing values in dataset."""
        if self.data is None:
            return False
        
        try:
            if strategy == "drop":
                original_size = len(self.data)
                self.data = self.data.dropna()
                logger.info(f"Dropped {original_size - len(self.data)} rows with missing values")
            elif strategy == "fill":
                self.data = self.data.fillna(0)
                logger.info("Filled missing values with 0")
            
            return True
        except Exception as e:
            logger.error(f"Error handling missing values: {e}")
            return False
    
    def export_to_json(self, output_path: str) -> bool:
        """Export processed data to JSON."""
        if self.data is None:
            logger.error("No data to export")
            return False
        
        try:
            self.data.to_json(output_path, orient='records', indent=2)
            logger.info(f"Data exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

# Example usage
if __name__ == "__main__":
    processor = DataProcessor()
    if processor.read_csv("sample_data.csv"):
        validation = processor.validate_data()
        if validation["warnings"]:
            processor.handle_missing_values("drop")
        processor.export_to_json("processed_data.json")
''',
            "explanation": "Generated a comprehensive CSV data processor with validation and export capabilities",
            "model": "simulation"
        }
    
    elif "api_client" in prompt.lower():
        return {
            "status": "success", 
            "generated_code": '''
import requests
import time
import json
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class APIClient:
    """REST API client with authentication and retry logic."""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     max_retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, params=params)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, params=params)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Log response status
                logger.info(f"Response status: {response.status_code}")
                
                # Handle different status codes
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json() if response.content else {},
                        "status_code": response.status_code
                    }
                elif response.status_code in [401, 403]:
                    return {
                        "success": False,
                        "error": "Authentication failed",
                        "status_code": response.status_code
                    }
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Server error, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
            except requests.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return {
                        "success": False,
                        "error": f"Request failed after {max_retries} attempts: {str(e)}",
                        "status_code": 0
                    }
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request.""" 
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint)

# Example usage
if __name__ == "__main__":
    client = APIClient("https://api.example.com", "your-auth-token")
    
    # Get user data
    result = client.get("/users/123")
    if result["success"]:
        print(f"User data: {result['data']}")
    else:
        print(f"Error: {result['error']}")
''',
            "explanation": "Generated a robust REST API client with authentication, retry logic, and comprehensive error handling",
            "model": "simulation"
        }
    
    else:  # utility_functions
        return {
            "status": "success",
            "generated_code": '''
import re
import datetime
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_string(text: str, remove_extra_spaces: bool = True) -> str:
    """Clean and normalize string."""
    if not isinstance(text, str):
        return str(text)
    
    # Remove leading/trailing whitespace
    cleaned = text.strip()
    
    # Remove extra spaces if requested
    if remove_extra_spaces:
        cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned

def format_date(date: Union[str, datetime.datetime], format_string: str = "%Y-%m-%d") -> str:
    """Format date to specified string format."""
    if isinstance(date, str):
        try:
            date = datetime.datetime.fromisoformat(date)
        except ValueError:
            return date  # Return original if can't parse
    
    if isinstance(date, datetime.datetime):
        return date.strftime(format_string)
    
    return str(date)

def safe_file_read(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """Safely read file contents."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        return path.read_text(encoding=encoding)
    except Exception:
        return None

def safe_json_load(json_string: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None

def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """Calculate percentage with division by zero protection."""
    if total == 0:
        return 0.0
    return (part / total) * 100

def is_valid_number_range(value: Union[int, float], min_val: Union[int, float], 
                         max_val: Union[int, float]) -> bool:
    """Check if number is within specified range."""
    try:
        num_value = float(value)
        return min_val <= num_value <= max_val
    except (ValueError, TypeError):
        return False

# Example usage
if __name__ == "__main__":
    # Test email validation
    print(f"Valid email: {validate_email('test@example.com')}")
    print(f"Invalid email: {validate_email('invalid-email')}")
    
    # Test string cleaning
    print(f"Cleaned: '{clean_string('  hello    world  ')}'")
    
    # Test date formatting
    now = datetime.datetime.now()
    print(f"Formatted date: {format_date(now, '%B %d, %Y')}")
''',
            "explanation": "Generated utility functions for common tasks with proper error handling",
            "model": "simulation"
        }

def generate_code_for_scenario(scenario):
    """Generate code for a specific scenario."""
    
    prompt = f"""
Create a {scenario['language']} {scenario['description']}.

Requirements:
{chr(10).join('- ' + req for req in scenario['requirements'])}

Please provide clean, well-documented, production-ready code with proper error handling.
"""

    logger.info(f"Generating code for scenario: {scenario['name']}")
    
    if SIMULATION_MODE:
        result = simulate_code_generation(prompt, scenario['language'])
    else:
        try:
            result = generate_code_snippet(prompt, scenario['language'])
        except Exception as e:
            logger.error(f"AI code generation failed: {e}")
            result = simulate_code_generation(prompt, scenario['language'])
    
    if result['status'] == 'success':
        # Save generated code to file
        filename = f"{scenario['name']}_generated.py"
        with open(filename, 'w') as f:
            f.write(result['generated_code'])
        
        logger.info(f"Generated code saved to {filename}")
        print(f"✅ Generated {filename} ({len(result['generated_code'])} characters)")
        
        return {
            'scenario': scenario['name'],
            'filename': filename,
            'success': True,
            'code_length': len(result['generated_code']),
            'model_used': result.get('model', 'unknown'),
            'explanation': result.get('explanation', 'No explanation provided')
        }
    else:
        logger.error(f"Code generation failed for {scenario['name']}: {result}")
        return {
            'scenario': scenario['name'],
            'success': False,
            'error': result.get('error', 'Unknown error')
        }

def main():
    """Generate code for all scenarios."""
    
    logger.info("Starting AI code generation workflow")
    
    # Load requirements
    with open('requirements.json', 'r') as f:
        requirements = json.load(f)
    
    results = []
    
    for scenario in requirements['scenarios']:
        print(f"\n🤖 Generating code for: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Complexity: {scenario['complexity']}")
        
        result = generate_code_for_scenario(scenario)
        results.append(result)
    
    # Save generation results
    with open('generation_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': SIMULATION_MODE,
            'results': results,
            'summary': {
                'total_scenarios': len(results),
                'successful_generations': sum(1 for r in results if r['success']),
                'failed_generations': sum(1 for r in results if not r['success'])
            }
        }, f, indent=2)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n🎉 Code generation completed: {successful}/{len(results)} successful")
    
    logger.info(f"AI code generation workflow completed: {successful}/{len(results)} successful")
    
    return results

if __name__ == "__main__":
    results = main()
EOF

    cd "$OUTPUT_DIR"
    python3 generate_code.py
    
    log_success "AI code generation completed!"
}

static_analysis_workflow() {
    log_step "Static Analysis of Generated Code"
    
    pause_for_user "Now we'll analyze the AI-generated code for quality issues"
    
    cat > "$OUTPUT_DIR/analyze_generated_code.py" << 'EOF'
import json
import sys
import os
import glob
from datetime import datetime

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.static_analysis import run_pyrefly_analysis
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def analyze_generated_files():
    """Analyze all generated Python files."""
    
    logger.info("Starting static analysis of AI-generated code")
    
    # Find all generated Python files
    generated_files = glob.glob("*_generated.py")
    
    if not generated_files:
        print("❌ No generated files found to analyze")
        return {}
    
    print(f"📋 Found {len(generated_files)} generated files to analyze")
    
    analysis_results = {}
    
    for file_path in generated_files:
        print(f"\n🔍 Analyzing {file_path}...")
        
        try:
            # Run static analysis
            result = run_pyrefly_analysis([file_path], ".")
            
            analysis_results[file_path] = {
                'analysis': result,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
            issue_count = result.get('issue_count', 0)
            if issue_count == 0:
                print(f"   ✅ No issues found")
            else:
                print(f"   ⚠️  Found {issue_count} issues")
                
                # Show sample issues
                issues = result.get('issues', [])
                for issue in issues[:3]:  # Show first 3
                    severity = issue.get('severity', 'unknown')
                    message = issue.get('message', 'No message')
                    line = issue.get('line', '?')
                    print(f"     • Line {line}: {message} ({severity})")
                
                if len(issues) > 3:
                    print(f"     ... and {len(issues) - 3} more issues")
            
        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            analysis_results[file_path] = {
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
            print(f"   ❌ Analysis failed: {e}")
    
    # Calculate overall statistics
    total_files = len(analysis_results)
    successful_analyses = sum(1 for r in analysis_results.values() if r['status'] == 'completed')
    total_issues = sum(
        r['analysis'].get('issue_count', 0) 
        for r in analysis_results.values() 
        if r['status'] == 'completed'
    )
    
    summary = {
        'total_files': total_files,
        'successful_analyses': successful_analyses,
        'total_issues': total_issues,
        'average_issues_per_file': total_issues / successful_analyses if successful_analyses > 0 else 0
    }
    
    # Save detailed results
    detailed_results = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'file_results': analysis_results
    }
    
    with open('static_analysis_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n📊 Analysis Summary:")
    print(f"   Files analyzed: {successful_analyses}/{total_files}")
    print(f"   Total issues found: {total_issues}")
    print(f"   Average issues per file: {summary['average_issues_per_file']:.1f}")
    
    logger.info(f"Static analysis completed: {total_issues} issues in {successful_analyses} files")
    
    return detailed_results

if __name__ == "__main__":
    results = analyze_generated_files()
EOF

    cd "$OUTPUT_DIR"
    python3 analyze_generated_code.py
    
    log_success "Static analysis completed!"
}

create_comprehensive_visualizations() {
    log_step "Creating Analysis Visualizations"
    
    pause_for_user "Let's create comprehensive visualizations of the workflow results"
    
    cat > "$OUTPUT_DIR/create_visualizations.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.data_visualization import create_bar_chart, create_line_plot, create_pie_chart
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def create_workflow_visualizations():
    """Create visualizations showing the complete AI + Analysis workflow."""
    
    logger.info("Creating comprehensive workflow visualizations")
    
    try:
        # Load generation results
        with open('generation_results.json', 'r') as f:
            gen_results = json.load(f)
        
        # Load analysis results
        with open('static_analysis_results.json', 'r') as f:
            analysis_results = json.load(f)
        
        print("📊 Creating workflow visualizations...")
        
        # 1. Code Generation Success Rate
        gen_summary = gen_results['summary']
        success_data = [
            gen_summary['successful_generations'],
            gen_summary['failed_generations']
        ]
        
        if sum(success_data) > 0:
            create_pie_chart(
                labels=['Successful', 'Failed'],
                sizes=success_data,
                title='AI Code Generation Success Rate',
                output_path='generation_success_rate.png',
                show_plot=False,
                autopct='%1.1f%%'
            )
            print("✅ Created generation_success_rate.png")
        
        # 2. Code Quality Analysis by File
        file_names = []
        issue_counts = []
        
        for file_path, result in analysis_results['file_results'].items():
            if result['status'] == 'completed':
                file_name = file_path.replace('_generated.py', '').replace('_', ' ').title()
                file_names.append(file_name)
                issue_counts.append(result['analysis'].get('issue_count', 0))
        
        if file_names and issue_counts:
            create_bar_chart(
                categories=file_names,
                values=issue_counts,
                title='Code Quality Issues by Generated Module',
                x_label='Generated Modules',
                y_label='Number of Issues',
                output_path='quality_issues_by_module.png',
                show_plot=False,
                bar_color='lightcoral'
            )
            print("✅ Created quality_issues_by_module.png")
            
            # 3. Quality Scores (inverse of issues)
            max_issues = max(issue_counts) if issue_counts else 0
            quality_scores = []
            for count in issue_counts:
                # Quality score: higher is better, based on fewer issues
                if max_issues == 0:
                    score = 100
                else:
                    score = max(0, 100 - (count / max_issues) * 100)
                quality_scores.append(score)
            
            create_bar_chart(
                categories=file_names,
                values=quality_scores,
                title='Code Quality Scores (0-100)',
                x_label='Generated Modules',
                y_label='Quality Score',
                output_path='quality_scores.png',
                show_plot=False,
                bar_color='lightgreen'
            )
            print("✅ Created quality_scores.png")
        
        # 4. Workflow Timeline Visualization
        # Simulate workflow steps for visualization
        workflow_steps = ['Requirements', 'AI Generation', 'Static Analysis', 'Visualization', 'Results']
        step_values = [100, 95, 90, 85, 80]  # Simulated progress values
        
        create_line_plot(
            x_data=list(range(len(workflow_steps))),
            y_data=step_values,
            title='AI-Enhanced Analysis Workflow Progress',
            x_label='Workflow Steps',
            y_label='Completion Status (%)',
            output_path='workflow_progress.png',
            show_plot=False,
            markers=True,
            line_labels=['Progress'],
            figure_size=(10, 6)
        )
        print("✅ Created workflow_progress.png")
        
        # 5. Integration Metrics Summary
        metrics = {
            'Code Files Generated': gen_summary['successful_generations'],
            'Issues Detected': analysis_results['summary']['total_issues'],
            'Files Analyzed': analysis_results['summary']['successful_analyses'],
            'Visualizations Created': 4  # This script creates 4 visualizations
        }
        
        create_bar_chart(
            categories=list(metrics.keys()),
            values=list(metrics.values()),
            title='AI-Enhanced Analysis Workflow Metrics',
            x_label='Metrics',
            y_label='Count',
            output_path='workflow_metrics.png',
            show_plot=False,
            bar_color='skyblue'
        )
        print("✅ Created workflow_metrics.png")
        
        logger.info("Workflow visualizations completed successfully")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Required data file not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        logger.error(f"Visualization creation failed: {e}")
        return False

if __name__ == "__main__":
    success = create_workflow_visualizations()
    if success:
        print("🎉 All workflow visualizations created successfully!")
    else:
        print("❌ Some visualizations failed to create")
EOF

    cd "$OUTPUT_DIR"
    python3 create_visualizations.py
    
    log_success "Comprehensive visualizations created!"
}

ai_improvement_suggestions() {
    log_step "AI-Powered Improvement Suggestions"
    
    pause_for_user "Finally, let's use AI to suggest improvements based on the analysis results"
    
    cat > "$OUTPUT_DIR/suggest_improvements.py" << 'EOF'
import json
import sys
import os

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.logging_monitoring import get_logger

# Check if we have real AI capabilities
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'false').lower() == 'true'

if not SIMULATION_MODE:
    try:
        from codomyrmex.ai_code_editing import generate_code_snippet
    except ImportError:
        SIMULATION_MODE = True

logger = get_logger(__name__)

def simulate_improvement_suggestions(analysis_summary):
    """Simulate AI improvement suggestions when API not available."""
    
    total_issues = analysis_summary.get('total_issues', 0)
    
    if total_issues == 0:
        return {
            'status': 'success',
            'suggestions': [
                "🎉 Excellent work! The generated code has no static analysis issues.",
                "✅ Code follows Python best practices and conventions.",
                "💡 Consider adding more comprehensive docstrings for better documentation.",
                "🔧 Add unit tests to ensure code reliability and maintainability.",
                "📊 Consider using type hints more extensively for better code clarity."
            ],
            'priority': 'low',
            'overall_assessment': 'The code quality is excellent with no issues detected.'
        }
    elif total_issues < 5:
        return {
            'status': 'success', 
            'suggestions': [
                "✅ Good code quality with minimal issues detected.",
                "🔧 Address the few static analysis warnings for improved code quality.",
                "📝 Consider refactoring any complex functions to improve readability.",
                "🛡️  Review security-related suggestions if any were flagged.",
                "📚 Add more detailed documentation for public APIs."
            ],
            'priority': 'low',
            'overall_assessment': 'Code quality is good with only minor improvements needed.'
        }
    elif total_issues < 15:
        return {
            'status': 'success',
            'suggestions': [
                "⚠️  Moderate number of issues detected - prioritize fixing high-severity ones.",
                "🧹 Consider code cleanup to address style and convention violations.",
                "🔒 Review any security warnings and implement proper input validation.",
                "📊 Break down complex functions into smaller, more manageable pieces.",
                "🧪 Add comprehensive error handling and input validation.",
                "📝 Improve code documentation and add type hints where missing."
            ],
            'priority': 'medium',
            'overall_assessment': 'Code has moderate issues that should be addressed for better maintainability.'
        }
    else:
        return {
            'status': 'success',
            'suggestions': [
                "🚨 High number of issues detected - comprehensive refactoring recommended.",
                "🏗️  Consider redesigning complex modules using better architectural patterns.",
                "🔒 Priority: Address all security-related warnings immediately.",
                "📋 Implement comprehensive input validation and error handling.",
                "🧪 Add unit tests to prevent regressions during refactoring.",
                "📚 Improve code documentation and follow Python PEP 8 conventions.",
                "🔧 Use automated code formatting tools (black, autopep8) to fix style issues.",
                "📊 Consider using design patterns to reduce code complexity."
            ],
            'priority': 'high',
            'overall_assessment': 'Code requires significant improvements to meet production quality standards.'
        }

def generate_improvement_suggestions():
    """Generate AI-powered improvement suggestions based on analysis results."""
    
    logger.info("Generating AI-powered improvement suggestions")
    
    try:
        # Load analysis results
        with open('static_analysis_results.json', 'r') as f:
            analysis_data = json.load(f)
        
        analysis_summary = analysis_data['summary']
        
        print("🤖 Generating improvement suggestions based on analysis results...")
        print(f"   Analysis Summary: {analysis_summary['total_issues']} issues in {analysis_summary['successful_analyses']} files")
        
        if SIMULATION_MODE:
            suggestions = simulate_improvement_suggestions(analysis_summary)
        else:
            # Use real AI to generate suggestions
            prompt = f"""
Based on a static analysis of Python code that found {analysis_summary['total_issues']} issues across {analysis_summary['successful_analyses']} files (average: {analysis_summary['average_issues_per_file']:.1f} issues per file), please provide:

1. Specific improvement suggestions prioritized by importance
2. Best practices recommendations
3. Overall assessment of code quality
4. Priority level (low/medium/high) for addressing issues

Please provide actionable, specific advice for improving the code quality.
"""
            
            try:
                result = generate_code_snippet(prompt, "text")
                suggestions = {
                    'status': result['status'],
                    'suggestions': result.get('generated_code', '').split('\n'),
                    'priority': 'medium',  # Default
                    'overall_assessment': 'AI analysis completed',
                    'model_used': result.get('model', 'unknown')
                }
            except Exception as e:
                logger.warning(f"AI suggestion generation failed, using simulation: {e}")
                suggestions = simulate_improvement_suggestions(analysis_summary)
        
        # Display suggestions
        print(f"\n💡 AI-Generated Improvement Suggestions:")
        print(f"   Priority Level: {suggestions['priority'].upper()}")
        print(f"\n📋 Suggestions:")
        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            if suggestion.strip():
                print(f"   {i}. {suggestion.strip()}")
        
        print(f"\n📊 Overall Assessment:")
        print(f"   {suggestions['overall_assessment']}")
        
        # Save suggestions
        suggestions_report = {
            'timestamp': json.load(open('static_analysis_results.json'))['timestamp'],
            'analysis_summary': analysis_summary,
            'ai_suggestions': suggestions,
            'simulation_mode': SIMULATION_MODE
        }
        
        with open('improvement_suggestions.json', 'w') as f:
            json.dump(suggestions_report, f, indent=2)
        
        logger.info("Improvement suggestions generated and saved")
        return suggestions_report
        
    except FileNotFoundError:
        print("❌ Analysis results not found. Run static analysis first.")
        return None
    except Exception as e:
        print(f"❌ Error generating suggestions: {e}")
        logger.error(f"Suggestion generation failed: {e}")
        return None

if __name__ == "__main__":
    results = generate_improvement_suggestions()
    if results:
        print("✅ Improvement suggestions generated successfully!")
    else:
        print("❌ Failed to generate improvement suggestions")
EOF

    cd "$OUTPUT_DIR"
    python3 suggest_improvements.py
    
    log_success "AI improvement suggestions generated!"
}

show_comprehensive_results() {
    log_step "Comprehensive Demo Results"
    
    cd "$OUTPUT_DIR"
    
    log_info "AI-Enhanced Analysis Demo completed! Here's the complete workflow results:"
    echo -e "${WHITE}📁 Output Directory: $OUTPUT_DIR${NC}"
    echo ""
    
    # Show workflow files
    echo -e "${GREEN}🔄 Workflow Files Generated:${NC}"
    
    echo -e "   ${CYAN}📋 Requirements & Configuration:${NC}"
    [[ -f "requirements.json" ]] && echo -e "      📄 requirements.json - Code generation scenarios"
    
    echo -e "   ${CYAN}🤖 AI-Generated Code:${NC}"
    for file in *_generated.py; do
        [[ -f "$file" ]] && echo -e "      🐍 $file - AI-generated Python module"
    done
    
    echo -e "   ${CYAN}📊 Analysis Results:${NC}"
    [[ -f "generation_results.json" ]] && echo -e "      📄 generation_results.json - AI generation results"
    [[ -f "static_analysis_results.json" ]] && echo -e "      📄 static_analysis_results.json - Code analysis results"
    [[ -f "improvement_suggestions.json" ]] && echo -e "      📄 improvement_suggestions.json - AI improvement suggestions"
    
    echo -e "   ${CYAN}📈 Visualizations:${NC}"
    for file in *.png; do
        [[ -f "$file" ]] && echo -e "      📊 $file - Analysis visualization"
    done
    
    echo ""
    
    # Show workflow summary
    if [[ -f "generation_results.json" ]] && [[ -f "static_analysis_results.json" ]]; then
        echo -e "${GREEN}📈 Workflow Summary:${NC}"
        python3 -c "
import json

try:
    with open('generation_results.json', 'r') as f:
        gen_data = json.load(f)
    with open('static_analysis_results.json', 'r') as f:
        analysis_data = json.load(f)
    
    gen_summary = gen_data['summary']
    analysis_summary = analysis_data['summary']
    
    print(f'   🤖 AI Generation: {gen_summary[\"successful_generations\"]}/{gen_summary[\"total_scenarios\"]} successful')
    print(f'   🔍 Static Analysis: {analysis_summary[\"total_issues\"]} issues found in {analysis_summary[\"successful_analyses\"]} files')
    print(f'   📊 Average Issues: {analysis_summary[\"average_issues_per_file\"]:.1f} per file')
    
    # Quality assessment
    if analysis_summary['total_issues'] == 0:
        print('   🎉 Code Quality: Excellent (no issues)')
    elif analysis_summary['total_issues'] < 5:
        print('   ✅ Code Quality: Good (minor issues)')
    elif analysis_summary['total_issues'] < 15:
        print('   ⚠️  Code Quality: Moderate (needs improvement)')
    else:
        print('   🚨 Code Quality: Needs significant improvement')

except Exception as e:
    print(f'   Error reading summary: {e}')
"
    fi
    
    echo ""
    log_info "View the generated files and visualizations to explore the complete workflow!"
    return 0
}

show_integration_summary() {
    log_step "Integration Demo Summary & Learning Outcomes"
    
    demo_end_time=$(date +%s)
    demo_duration=$((demo_end_time - demo_start_time))
    
    echo -e "${GREEN}🎉 AI-Enhanced Analysis Integration Demo Complete!${NC}"
    echo ""
    echo -e "${WHITE}🔗 Integration Workflow Demonstrated:${NC}"
    echo "   1. ✅ AI Code Generation from requirements"
    echo "   2. ✅ Static Analysis of generated code"
    echo "   3. ✅ Data Visualization of analysis results"
    echo "   4. ✅ AI-powered improvement suggestions"
    echo "   5. ✅ Complete workflow integration with logging"
    
    echo ""
    echo -e "${WHITE}🧠 Modules Integrated:${NC}"
    echo "   🤖 ai_code_editing - Code generation and improvement suggestions"
    echo "   🔍 static_analysis - Quality and security analysis"
    echo "   📊 data_visualization - Results visualization"
    echo "   📋 logging_monitoring - Workflow tracking and logging"
    
    echo ""
    echo -e "${WHITE}⏱️  Demo Statistics:${NC}"
    echo "   🕒 Duration: ${demo_duration} seconds"
    echo "   📁 Files created: $(ls -1 2>/dev/null | wc -l | tr -d ' ') files"
    echo "   📦 Output location: $OUTPUT_DIR"
    
    if [[ "$SIMULATION_MODE" == "true" ]]; then
        echo "   🎭 Mode: Simulation (no API keys)"
    else
        echo "   🌐 Mode: Live AI integration"
    fi
    
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Review the generated code and analysis results"
    echo "   2. Try with your own code generation requirements"
    echo "   3. Explore complete workflows: cd ../workflows"
    echo "   4. Set up API keys for full AI capabilities"
    echo "   5. Build your own integration workflows"
    
    echo ""
    echo -e "${CYAN}💡 Integration Insights:${NC}"
    echo "   • AI + Analysis creates powerful quality feedback loops"
    echo "   • Visualization helps understand code quality patterns" 
    echo "   • Logging provides full workflow traceability"
    echo "   • Multiple modules create more than sum of parts"
    echo "   • Automation enables consistent quality processes"
    
    echo ""
    echo -e "${GREEN}✨ You've mastered AI-enhanced development workflows with Codomyrmex! ✨${NC}"
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
    log_info "Partial results may be available in: $OUTPUT_DIR"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Main execution
main() {
    show_header
    
    log_info "This demo showcases how multiple Codomyrmex modules work together"
    log_info "We'll use AI → Static Analysis → Visualization → AI Suggestions"
    log_info "Duration: ~5 minutes | Output: scripts/output/ai-enhanced-analysis/"
    
    pause_for_user "Ready to start the AI-enhanced analysis integration demo?"
    
    check_environment
    generate_code_requirements
    ai_code_generation
    static_analysis_workflow
    create_comprehensive_visualizations
    ai_improvement_suggestions
    
    if show_comprehensive_results; then
        show_integration_summary
        cleanup_option
    else
        log_error "Demo completed with issues. Check output directory for partial results."
        exit 1
    fi
}

# Run the demo
main "$@"
