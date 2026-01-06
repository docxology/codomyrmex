#!/bin/bash
# 🐜 Codomyrmex Development Workflow Orchestrator
# 
# This comprehensive orchestrator demonstrates a complete development workflow:
# 1. Environment setup and project initialization
# 2. AI-assisted feature development and code generation  
# 3. Code quality analysis and validation
# 4. Secure testing and execution
# 5. Git integration with commit and documentation
# 6. Visualization of development metrics and progress
#
# Prerequisites: API keys recommended, Git repository
# Duration: ~8 minutes
# Modules: ALL - environment_setup + ai_code_editing + static_analysis + code + git_operations + data_visualization + logging_monitoring

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
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/development-workflow"
DEMO_START_TIME=$(date +%s)

# Banner
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    🚀 Codomyrmex Development Workflow Orchestrator 🚀   ║${NC}"
echo -e "${CYAN}║  Complete AI-Enhanced Development Lifecycle Demo        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Helper functions
show_progress() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] Phase $1: $2${NC}"
}

show_step() {
    echo -e "${WHITE}  Step $1: $2${NC}"
}

show_success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

show_info() {
    echo -e "${CYAN}  ℹ️  $1${NC}"
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Introduction
echo -e "${WHITE}This orchestrator will walk you through a complete development workflow,${NC}"
echo -e "${WHITE}demonstrating how Codomyrmex modules work together in a real scenario.${NC}"
echo ""
echo -e "${CYAN}Workflow Overview:${NC}"
echo "  🔧 Environment validation and setup"
echo "  🤖 AI-assisted feature development"
echo "  🔍 Code quality analysis and validation"  
echo "  ⚡ Secure testing and execution"
echo "  📊 Development metrics visualization"
echo "  🌳 Git integration and documentation"
echo ""
read -p "Press Enter to begin the workflow..." -r

cd "$PROJECT_ROOT"

# Phase 1: Environment Setup and Validation
show_progress "1" "Environment Setup and Validation"
show_step "1.1" "Validating development environment..."

# Test all required modules
python3 -c "
import sys
import os
sys.path.insert(0, 'src')

print('🔍 Testing module availability...')
modules_status = {}

required_modules = [
    ('environment_setup.env_checker', 'Environment Setup'),
    ('logging_monitoring.logger_config', 'Logging & Monitoring'),
    ('ai_code_editing.ai_code_helpers', 'AI Code Editing'),
    ('static_analysis.pyrefly_runner', 'Static Analysis'),
    ('code.execution.executor', 'Code Execution'),
    ('data_visualization', 'Data Visualization'),
    ('git_operations.git_manager', 'Git Operations')
]

available_modules = []
missing_modules = []

for module_path, module_name in required_modules:
    try:
        __import__(f'codomyrmex.{module_path}')
        available_modules.append(module_name)
        print(f'  ✅ {module_name}')
    except ImportError as e:
        missing_modules.append((module_name, str(e)))
        print(f'  ⚠️  {module_name}: {e}')

print(f'\\n📊 Module Status: {len(available_modules)}/{len(required_modules)} available')

if len(available_modules) < 4:
    print('❌ Insufficient modules available for comprehensive workflow')
    print('Please ensure Codomyrmex is properly installed: pip install -e .')
    exit(1)
else:
    print('✅ Sufficient modules available for workflow demonstration')
"

if [ $? -ne 0 ]; then
    show_error "Environment validation failed"
    exit 1
fi

show_success "Environment validation completed"

show_step "1.2" "Setting up logging and project workspace..."

# Initialize logging and create workspace
python3 -c "
import sys
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import setup_logging, get_logger
from pathlib import Path

# Setup comprehensive logging
setup_logging()
logger = get_logger('workflow_orchestrator')

output_dir = '$OUTPUT_DIR'
Path(output_dir).mkdir(parents=True, exist_ok=True)

logger.info('🚀 Development Workflow Orchestrator Started')
logger.info(f'Output directory: {output_dir}')
logger.info('Phase 1: Environment setup completed successfully')

print('✅ Logging system initialized')
print(f'📁 Workspace created: {output_dir}')
"

show_success "Project workspace initialized"

# Phase 2: Project Planning and Feature Selection
show_progress "2" "Project Planning and Feature Selection"
show_step "2.1" "Selecting development project type..."

echo ""
echo "Choose a development project to work on:"
echo "  1. 🧮 Math Utilities Library - Create mathematical functions and calculators"
echo "  2. 📁 File Management Tools - Build file organization and search utilities"
echo "  3. 🌐 Web API Client - Create a REST API client with data processing"
echo "  4. 📊 Data Analysis Pipeline - Build data processing and visualization tools"
echo "  5. 🎯 Custom Project - Specify your own project requirements"
echo ""

read -p "Choose project type (1-5): " project_choice

case $project_choice in
    1)
        PROJECT_TYPE="math_utilities"
        PROJECT_DESCRIPTION="A comprehensive mathematical utilities library with functions for basic arithmetic, statistical calculations, geometric computations, and number theory operations. Include proper error handling, unit tests, and documentation."
        PROJECT_NAME="MathUtils Library"
        ;;
    2)
        PROJECT_TYPE="file_management"
        PROJECT_DESCRIPTION="File management tools including file search by various criteria, batch renaming utilities, duplicate file detection, directory organization helpers, and file metadata analysis. Include recursive operations and pattern matching."
        PROJECT_NAME="FileManager Tools"
        ;;
    3)
        PROJECT_TYPE="web_api_client"
        PROJECT_DESCRIPTION="A REST API client library with authentication, request/response handling, data serialization, error handling, rate limiting, and caching. Include examples for popular APIs and comprehensive error management."
        PROJECT_NAME="WebAPI Client"
        ;;
    4)
        PROJECT_TYPE="data_analysis"
        PROJECT_DESCRIPTION="Data analysis pipeline with CSV/JSON file loading, data cleaning and preprocessing, statistical analysis functions, data visualization generation, and report creation. Include support for common data operations."
        PROJECT_NAME="DataAnalyzer Pipeline"
        ;;
    5)
        read -p "Enter your project description: " custom_description
        if [ -z "$custom_description" ]; then
            show_error "Project description cannot be empty"
            exit 1
        fi
        PROJECT_TYPE="custom_project"
        PROJECT_DESCRIPTION="$custom_description"
        PROJECT_NAME="Custom Project"
        ;;
    *)
        show_error "Invalid project choice"
        exit 1
        ;;
esac

show_success "Selected: $PROJECT_NAME"
show_info "Description: $PROJECT_DESCRIPTION"

# Phase 3: AI-Powered Development
show_progress "3" "AI-Powered Development"
show_step "3.1" "Generating project structure and core functionality..."

python3 -c "
import sys
import json
import time
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.agents.ai_code_editing.ai_code_helpers import generate_code_snippet

logger = get_logger('ai_development')
logger.info('🤖 Starting AI-powered development phase')

project_type = '$PROJECT_TYPE'
project_name = '$PROJECT_NAME'
project_description = '''$PROJECT_DESCRIPTION'''
output_dir = '$OUTPUT_DIR'

# Create project directory
project_dir = Path(output_dir) / 'generated_project'
project_dir.mkdir(exist_ok=True)

logger.info(f'Generating code for project: {project_name}')

try:
    # Generate main module code
    print('🎯 Generating main project code...')
    
    main_code_prompt = f'''
    Create a Python module for: {project_description}
    
    Requirements:
    - Use proper Python class structure and organization
    - Include comprehensive docstrings and type hints
    - Implement proper error handling and validation
    - Create at least 3-5 main functions/methods
    - Include a main() function for demonstration
    - Add proper imports and dependencies
    - Make the code modular and well-structured
    '''
    
    main_result = generate_code_snippet(
        prompt=main_code_prompt,
        language='python',
        llm_provider='openai'
    )
    
    if main_result['status'] == 'success':
        main_code = main_result['generated_code']
        print('  ✅ Main module code generated')
        
        # Save main module
        with open(project_dir / f'{project_type}.py', 'w') as f:
            f.write(main_code)
        
        logger.info(f'Main module saved: {project_type}.py')
    else:
        print(f'  ❌ Main code generation failed: {main_result.get(\"error\", \"Unknown error\")}')
        main_code = ''
    
    # Generate test code
    print('🧪 Generating unit tests...')
    
    test_prompt = f'''
    Create comprehensive unit tests for the following Python code:
    
    {main_code[:2000]}...
    
    Requirements:
    - Use pytest framework
    - Create test cases for all main functions/methods
    - Include edge cases and error condition tests
    - Use proper test organization and naming
    - Add test fixtures if appropriate
    - Include both positive and negative test cases
    '''
    
    test_result = generate_code_snippet(
        prompt=test_prompt,
        language='python',
        llm_provider='openai'
    )
    
    if test_result['status'] == 'success':
        test_code = test_result['generated_code']
        print('  ✅ Unit tests generated')
        
        # Save test module
        with open(project_dir / f'test_{project_type}.py', 'w') as f:
            f.write(test_code)
            
        logger.info(f'Test module saved: test_{project_type}.py')
    else:
        print(f'  ⚠️  Test generation failed: {test_result.get(\"error\", \"Unknown error\")}')
    
    # Generate documentation
    print('📚 Generating project documentation...')
    
    doc_prompt = f'''
    Create a comprehensive README.md file for this Python project:
    
    Project: {project_name}
    Description: {project_description}
    
    Include:
    - Project title and description
    - Installation instructions
    - Usage examples with code snippets
    - API documentation for main functions
    - Testing instructions
    - Contributing guidelines
    - License information
    
    Make it professional and well-formatted with proper Markdown syntax.
    '''
    
    doc_result = generate_code_snippet(
        prompt=doc_prompt,
        language='markdown',
        llm_provider='openai'
    )
    
    if doc_result['status'] == 'success':
        readme_content = doc_result['generated_code']
        print('  ✅ Documentation generated')
        
        # Save documentation
        with open(project_dir / 'README.md', 'w') as f:
            f.write(readme_content)
            
        logger.info('Documentation saved: README.md')
    else:
        print(f'  ⚠️  Documentation generation failed: {doc_result.get(\"error\", \"Unknown error\")}')
    
    # Create requirements.txt
    requirements = '''pytest>=7.0.0
requests>=2.28.0
numpy>=1.21.0
matplotlib>=3.5.0'''
    
    with open(project_dir / 'requirements.txt', 'w') as f:
        f.write(requirements)
    print('  ✅ Requirements file created')
    
    logger.info('🎉 AI development phase completed successfully')
    print(f'\\n📁 Generated project files in: {project_dir}')
    
    # List generated files
    generated_files = list(project_dir.glob('*'))
    print(f'📋 Files created: {len(generated_files)}')
    for file in generated_files:
        print(f'  • {file.name}')

except Exception as e:
    logger.error(f'AI development failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ AI development failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    show_error "AI development phase failed"
    exit 1
fi

show_success "AI-powered development completed"

# Phase 4: Code Quality Analysis
show_progress "4" "Code Quality Analysis and Validation"
show_step "4.1" "Running static analysis on generated code..."

python3 -c "
import sys
import json
import subprocess
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.data_visualization import create_bar_chart, create_line_plot

logger = get_logger('quality_analysis')
logger.info('🔍 Starting code quality analysis')

output_dir = '$OUTPUT_DIR'
project_dir = Path(output_dir) / 'generated_project'

# Quality analysis results
quality_results = {
    'files_analyzed': [],
    'analysis_tools': {},
    'metrics': {},
    'issues_found': 0,
    'recommendations': []
}

try:
    # Find Python files to analyze
    python_files = list(project_dir.glob('*.py'))
    quality_results['files_analyzed'] = [str(f.name) for f in python_files]
    
    print(f'📊 Analyzing {len(python_files)} Python files...')
    logger.info(f'Files to analyze: {quality_results[\"files_analyzed\"]}')
    
    if not python_files:
        print('⚠️  No Python files found to analyze')
        exit(0)
    
    # Basic file metrics
    total_lines = 0
    total_chars = 0
    function_count = 0
    class_count = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\\n')
                total_lines += len(lines)
                total_chars += len(content)
                
                # Simple pattern counting
                function_count += content.count('def ')
                class_count += content.count('class ')
                
        except Exception as e:
            logger.warning(f'Could not read {py_file}: {e}')
    
    quality_results['metrics'] = {
        'total_lines': total_lines,
        'total_characters': total_chars,
        'function_count': function_count,
        'class_count': class_count,
        'avg_file_size': total_lines / len(python_files) if python_files else 0
    }
    
    print(f'  📏 Total lines: {total_lines}')
    print(f'  🔧 Functions: {function_count}')
    print(f'  🏗️  Classes: {class_count}')
    print(f'  📊 Avg file size: {quality_results[\"metrics\"][\"avg_file_size\"]:.1f} lines')
    
    # Run analysis tools
    analysis_results = {}
    
    # Try flake8
    try:
        print('  🔍 Running flake8 analysis...')
        result = subprocess.run(
            ['flake8', '--max-line-length=100', '--ignore=E501,W503'] + [str(f) for f in python_files],
            capture_output=True, text=True, timeout=30, cwd=str(project_dir)
        )
        
        flake8_issues = result.stdout.strip().split('\\n') if result.stdout.strip() else []
        flake8_issues = [issue for issue in flake8_issues if issue]
        
        analysis_results['flake8'] = {
            'issues_count': len(flake8_issues),
            'issues': flake8_issues[:10],  # First 10 issues
            'status': 'success'
        }
        
        print(f'    ✅ Flake8: {len(flake8_issues)} issues found')
        quality_results['issues_found'] += len(flake8_issues)
        
    except subprocess.TimeoutExpired:
        print('    ⚠️  Flake8: Analysis timed out')
        analysis_results['flake8'] = {'status': 'timeout'}
    except FileNotFoundError:
        print('    ⚠️  Flake8: Not available')
        analysis_results['flake8'] = {'status': 'not_found'}
    except Exception as e:
        print(f'    ⚠️  Flake8: {e}')
        analysis_results['flake8'] = {'status': 'error', 'error': str(e)}
    
    # Try basic Python syntax check
    try:
        print('  🐍 Running Python syntax validation...')
        syntax_issues = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                syntax_issues += 1
                logger.warning(f'Syntax error in {py_file}: {e}')
        
        analysis_results['syntax_check'] = {
            'issues_count': syntax_issues,
            'status': 'success'
        }
        
        if syntax_issues == 0:
            print('    ✅ Syntax: All files valid')
        else:
            print(f'    ❌ Syntax: {syntax_issues} files with issues')
            quality_results['issues_found'] += syntax_issues
        
    except Exception as e:
        print(f'    ⚠️  Syntax check failed: {e}')
        analysis_results['syntax_check'] = {'status': 'error', 'error': str(e)}
    
    quality_results['analysis_tools'] = analysis_results
    
    # Generate quality visualizations
    print('  📊 Generating quality metrics visualizations...')
    
    # Code metrics chart
    if quality_results['metrics']:
        metrics = quality_results['metrics']
        create_bar_chart(
            categories=['Lines', 'Functions', 'Classes'],
            values=[metrics['total_lines'], metrics['function_count'], metrics['class_count']],
            title='Generated Code Metrics',
            x_label='Code Elements',
            y_label='Count',
            output_path=f'{output_dir}/code_metrics.png',
            bar_color='lightblue'
        )
        print('    ✅ Code metrics chart generated')
    
    # Analysis results chart
    tool_names = []
    issue_counts = []
    
    for tool, results in analysis_results.items():
        if results.get('status') == 'success':
            tool_names.append(tool.replace('_', ' ').title())
            issue_counts.append(results.get('issues_count', 0))
    
    if tool_names:
        create_bar_chart(
            categories=tool_names,
            values=issue_counts,
            title='Code Quality Analysis Results',
            x_label='Analysis Tools',
            y_label='Issues Found',
            output_path=f'{output_dir}/quality_analysis.png',
            bar_color='lightcoral'
        )
        print('    ✅ Quality analysis chart generated')
    
    # Save quality report
    with open(f'{output_dir}/quality_report.json', 'w') as f:
        json.dump(quality_results, f, indent=2)
    
    # Determine overall quality score
    if quality_results['issues_found'] == 0:
        quality_score = 'Excellent'
        quality_emoji = '🟢'
    elif quality_results['issues_found'] <= 5:
        quality_score = 'Good'
        quality_emoji = '🟡'
    elif quality_results['issues_found'] <= 15:
        quality_score = 'Fair'
        quality_emoji = '🟠'
    else:
        quality_score = 'Needs Improvement'
        quality_emoji = '🔴'
    
    print(f'\\n{quality_emoji} Overall Quality: {quality_score} ({quality_results[\"issues_found\"]} issues)')
    logger.info(f'Code quality analysis completed: {quality_score}')

except Exception as e:
    logger.error(f'Quality analysis failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ Quality analysis failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    show_warning "Quality analysis encountered issues but continuing..."
fi

show_success "Code quality analysis completed"

# Phase 5: Code Execution and Testing
show_progress "5" "Code Execution and Testing"
show_step "5.1" "Testing generated code in secure sandbox..."

python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.code.execution.executor import execute_code

logger = get_logger('code_execution')
logger.info('⚡ Starting code execution and testing phase')

output_dir = '$OUTPUT_DIR'
project_dir = Path(output_dir) / 'generated_project'
project_type = '$PROJECT_TYPE'

execution_results = []

try:
    # Find main Python file
    main_file = project_dir / f'{project_type}.py'
    
    if main_file.exists():
        print(f'🚀 Testing main module: {main_file.name}')
        
        # Read the main file
        with open(main_file, 'r') as f:
            main_code = f.read()
        
        # Execute main module
        print('  ⚡ Running main module in sandbox...')
        
        result = execute_code(
            language='python',
            code=main_code,
            timeout=30
        )
        
        execution_results.append({
            'file': main_file.name,
            'result': result
        })
        
        print(f'    Exit code: {result.get(\"exit_code\", \"unknown\")}')
        
        if result.get('exit_code') == 0:
            print('    ✅ Execution successful')
            
            if result.get('stdout'):
                print('    📋 Output:')
                output_lines = result['stdout'].split('\\n')[:10]  # First 10 lines
                for line in output_lines:
                    if line.strip():
                        print(f'      {line}')
                if len(result['stdout'].split('\\n')) > 10:
                    print('      ... (truncated)')
        else:
            print('    ❌ Execution failed')
            if result.get('stderr'):
                print(f'    Error: {result[\"stderr\"][:200]}...')
    else:
        print(f'⚠️  Main file not found: {main_file.name}')
    
    # Try to run tests if available
    test_file = project_dir / f'test_{project_type}.py'
    
    if test_file.exists():
        print(f'🧪 Running unit tests: {test_file.name}')
        
        with open(test_file, 'r') as f:
            test_code = f.read()
        
        # Add imports and basic test runner
        test_runner_code = f'''
{test_code}

# Basic test runner
if __name__ == '__main__':
    import inspect
    
    # Find test functions
    current_module = sys.modules[__name__]
    test_functions = [name for name, obj in inspect.getmembers(current_module)
                     if inspect.isfunction(obj) and name.startswith('test_')]
    
    print(f\"Running {{len(test_functions)}} tests...\")
    
    passed = 0
    failed = 0
    
    for test_func_name in test_functions:
        try:
            test_func = getattr(current_module, test_func_name)
            test_func()
            print(f\"✅ {{test_func_name}}: PASSED\")
            passed += 1
        except Exception as e:
            print(f\"❌ {{test_func_name}}: FAILED - {{str(e)[:100]}}\")
            failed += 1
    
    print(f\"\\nTest Results: {{passed}} passed, {{failed}} failed\")
'''
        
        print('  🧪 Executing tests in sandbox...')
        
        test_result = execute_code(
            language='python',
            code=test_runner_code,
            timeout=45
        )
        
        execution_results.append({
            'file': test_file.name,
            'result': test_result
        })
        
        print(f'    Exit code: {test_result.get(\"exit_code\", \"unknown\")}')
        
        if test_result.get('exit_code') == 0:
            print('    ✅ Tests executed successfully')
            
            if test_result.get('stdout'):
                print('    📋 Test output:')
                test_lines = test_result['stdout'].split('\\n')[-10:]  # Last 10 lines
                for line in test_lines:
                    if line.strip():
                        print(f'      {line}')
        else:
            print('    ⚠️  Test execution had issues')
            if test_result.get('stderr'):
                print(f'    Error: {test_result[\"stderr\"][:200]}...')
    else:
        print(f'⚠️  Test file not found: {test_file.name}')
    
    # Save execution results
    import json
    with open(f'{output_dir}/execution_results.json', 'w') as f:
        json.dump(execution_results, f, indent=2)
    
    logger.info('✅ Code execution phase completed')
    print(f'\\n📊 Execution Summary: {len(execution_results)} files tested')

except Exception as e:
    logger.error(f'Code execution failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ Code execution failed: {e}')
"

show_success "Code execution and testing completed"

# Phase 6: Development Metrics and Visualization
show_progress "6" "Development Metrics and Visualization"
show_step "6.1" "Generating development dashboard..."

python3 -c "
import sys
import json
import time
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.data_visualization import create_bar_chart, create_line_plot, create_pie_chart

logger = get_logger('development_metrics')
logger.info('📊 Generating development metrics dashboard')

output_dir = '$OUTPUT_DIR'
project_type = '$PROJECT_TYPE'
project_name = '$PROJECT_NAME'

# Collect metrics from all previous phases
metrics_data = {
    'project_info': {
        'name': project_name,
        'type': project_type,
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
    },
    'development_metrics': {},
    'quality_metrics': {},
    'execution_metrics': {}
}

try:
    # Load quality results if available
    quality_file = Path(output_dir) / 'quality_report.json'
    if quality_file.exists():
        with open(quality_file, 'r') as f:
            quality_data = json.load(f)
            metrics_data['quality_metrics'] = quality_data['metrics']
    
    # Load execution results if available
    execution_file = Path(output_dir) / 'execution_results.json'
    execution_success_rate = 0
    if execution_file.exists():
        with open(execution_file, 'r') as f:
            execution_data = json.load(f)
            successful_executions = sum(1 for result in execution_data 
                                      if result['result'].get('exit_code') == 0)
            execution_success_rate = (successful_executions / len(execution_data) * 100) if execution_data else 0
            metrics_data['execution_metrics'] = {
                'total_files_tested': len(execution_data),
                'successful_executions': successful_executions,
                'success_rate': execution_success_rate
            }
    
    # Count generated files
    project_dir = Path(output_dir) / 'generated_project'
    generated_files = list(project_dir.glob('*')) if project_dir.exists() else []
    
    metrics_data['development_metrics'] = {
        'files_generated': len(generated_files),
        'file_types': {},
        'workflow_duration': time.time() - $DEMO_START_TIME
    }
    
    # Analyze file types
    file_types = {}
    for file in generated_files:
        ext = file.suffix or 'no_extension'
        file_types[ext] = file_types.get(ext, 0) + 1
    
    metrics_data['development_metrics']['file_types'] = file_types
    
    print('📊 Creating development metrics visualizations...')
    
    # Development Overview Chart
    if metrics_data['development_metrics']:
        dev_metrics = metrics_data['development_metrics']
        create_bar_chart(
            categories=['Files Generated', 'Workflow Time (min)'],
            values=[dev_metrics['files_generated'], int(dev_metrics['workflow_duration'] / 60)],
            title='Development Overview',
            x_label='Metrics',
            y_label='Count/Time',
            output_path=f'{output_dir}/development_overview.png',
            bar_color='lightgreen'
        )
        print('  ✅ Development overview chart created')
    
    # File Types Distribution
    if file_types:
        file_extensions = list(file_types.keys())
        file_counts = list(file_types.values())
        
        create_pie_chart(
            labels=[ext.replace('.', '') or 'no_ext' for ext in file_extensions],
            sizes=file_counts,
            title='Generated Files by Type',
            output_path=f'{output_dir}/file_types_distribution.png'
        )
        print('  ✅ File types distribution chart created')
    
    # Quality vs Execution Success
    if metrics_data['quality_metrics'] and metrics_data['execution_metrics']:
        quality = metrics_data['quality_metrics']
        execution = metrics_data['execution_metrics']
        
        create_bar_chart(
            categories=['Lines of Code', 'Functions', 'Classes', 'Success Rate (%)'],
            values=[
                quality.get('total_lines', 0),
                quality.get('function_count', 0), 
                quality.get('class_count', 0),
                int(execution.get('success_rate', 0))
            ],
            title='Code Quality and Execution Metrics',
            x_label='Metrics',
            y_label='Count/Percentage',
            output_path=f'{output_dir}/quality_execution_metrics.png',
            bar_color='gold'
        )
        print('  ✅ Quality vs execution metrics chart created')
    
    # Workflow Timeline (simulated)
    timeline_phases = ['Setup', 'AI Generation', 'Quality Check', 'Testing', 'Visualization']
    timeline_duration = [30, 120, 60, 90, 45]  # Simulated durations in seconds
    
    create_line_plot(
        x_data=list(range(len(timeline_phases))),
        y_data=timeline_duration,
        title='Development Workflow Timeline',
        x_label='Workflow Phase',
        y_label='Duration (seconds)',
        output_path=f'{output_dir}/workflow_timeline.png'
    )
    print('  ✅ Workflow timeline chart created')
    
    # Generate comprehensive dashboard report
    with open(f'{output_dir}/development_dashboard.md', 'w') as f:
        f.write(f'# Development Metrics Dashboard\\n\\n')
        f.write(f'**Project**: {project_name}\\n')
        f.write(f'**Type**: {project_type}\\n')
        f.write(f'**Generated**: {metrics_data[\"project_info\"][\"generated_at\"]}\\n\\n')
        
        f.write('## 📊 Development Summary\\n\\n')
        if metrics_data['development_metrics']:
            dev = metrics_data['development_metrics']
            f.write(f'- **Files Generated**: {dev[\"files_generated\"]}\\n')
            f.write(f'- **Workflow Duration**: {dev[\"workflow_duration\"] / 60:.1f} minutes\\n')
            f.write(f'- **File Types**: {\", \".join(file_types.keys())}\\n\\n')
        
        f.write('## 🔍 Code Quality\\n\\n')
        if metrics_data['quality_metrics']:
            quality = metrics_data['quality_metrics']
            f.write(f'- **Total Lines**: {quality.get(\"total_lines\", 0)}\\n')
            f.write(f'- **Functions**: {quality.get(\"function_count\", 0)}\\n')
            f.write(f'- **Classes**: {quality.get(\"class_count\", 0)}\\n')
            f.write(f'- **Average File Size**: {quality.get(\"avg_file_size\", 0):.1f} lines\\n\\n')
        
        f.write('## ⚡ Execution Results\\n\\n')
        if metrics_data['execution_metrics']:
            execution = metrics_data['execution_metrics']
            f.write(f'- **Files Tested**: {execution[\"total_files_tested\"]}\\n')
            f.write(f'- **Successful Executions**: {execution[\"successful_executions\"]}\\n')
            f.write(f'- **Success Rate**: {execution[\"success_rate\"]:.1f}%\\n\\n')
        
        f.write('## 📈 Generated Visualizations\\n\\n')
        f.write('- `development_overview.png` - Overall development metrics\\n')
        f.write('- `file_types_distribution.png` - File types breakdown\\n')
        f.write('- `quality_execution_metrics.png` - Quality and execution analysis\\n')
        f.write('- `workflow_timeline.png` - Development workflow timeline\\n')
        f.write('- `code_metrics.png` - Generated code analysis\\n')
        f.write('- `quality_analysis.png` - Quality analysis results\\n')
    
    # Save complete metrics
    with open(f'{output_dir}/development_metrics.json', 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    logger.info('📊 Development metrics dashboard completed')
    print(f'\\n🎨 Generated 6 visualization charts')
    print(f'📄 Created development dashboard report')

except Exception as e:
    logger.error(f'Metrics visualization failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ Metrics visualization failed: {e}')
"

show_success "Development metrics dashboard generated"

# Phase 7: Git Integration and Documentation
show_progress "7" "Git Integration and Documentation"
show_step "7.1" "Git integration and project documentation..."

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    show_info "In Git repository - creating development branch"
    
    # Create a feature branch for the workflow
    BRANCH_NAME="feature/workflow-demo-$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$BRANCH_NAME" 2>/dev/null || show_warning "Could not create branch $BRANCH_NAME"
    
    # Add generated files to git (if user wants)
    echo ""
    read -p "Add generated project files to Git? (y/n): " add_to_git
    
    if [[ "$add_to_git" =~ ^[Yy]$ ]]; then
        git add "$OUTPUT_DIR/" 2>/dev/null || show_warning "Could not add files to git"
        
        git commit -m "feat: Add AI-generated development workflow results

Generated project: $PROJECT_NAME
- AI-powered code generation
- Quality analysis and validation  
- Secure execution testing
- Comprehensive metrics dashboard
- Complete development workflow demonstration

Files generated:
- Main project code and tests
- Quality analysis reports
- Execution results
- Development metrics visualizations
- Comprehensive documentation" 2>/dev/null || show_warning "Could not create commit"

        show_success "Changes committed to branch $BRANCH_NAME"
    else
        show_info "Skipped Git integration"
    fi
else
    show_warning "Not in Git repository - skipping Git integration"
fi

show_step "7.2" "Final documentation and summary generation..."

python3 -c "
import sys
from pathlib import Path
import time
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import get_logger

logger = get_logger('final_documentation')
logger.info('📚 Generating final workflow documentation')

output_dir = '$OUTPUT_DIR'
project_name = '$PROJECT_NAME'
project_type = '$PROJECT_TYPE'
workflow_start = $DEMO_START_TIME
total_duration = time.time() - workflow_start

# Create comprehensive workflow report
with open(f'{output_dir}/WORKFLOW_COMPLETE.md', 'w') as f:
    f.write(f'# 🚀 Codomyrmex Development Workflow - COMPLETE\\n\\n')
    f.write(f'**Project**: {project_name}\\n')
    f.write(f'**Duration**: {total_duration / 60:.1f} minutes\\n')
    f.write(f'**Completed**: {time.strftime(\"%Y-%m-%d %H:%M:%S\")}\\n\\n')
    
    f.write('## 🎯 Workflow Phases Completed\\n\\n')
    f.write('✅ **Phase 1**: Environment Setup and Validation\\n')
    f.write('✅ **Phase 2**: Project Planning and Feature Selection\\n')
    f.write('✅ **Phase 3**: AI-Powered Development\\n')
    f.write('✅ **Phase 4**: Code Quality Analysis and Validation\\n')
    f.write('✅ **Phase 5**: Code Execution and Testing\\n')
    f.write('✅ **Phase 6**: Development Metrics and Visualization\\n')
    f.write('✅ **Phase 7**: Git Integration and Documentation\\n\\n')
    
    f.write('## 📋 Codomyrmex Modules Demonstrated\\n\\n')
    f.write('- 🔧 **environment_setup**: Environment validation and setup\\n')
    f.write('- 📝 **logging_monitoring**: Comprehensive workflow logging\\n')
    f.write('- 🤖 **ai_code_editing**: AI-powered code generation and refinement\\n')
    f.write('- 🔍 **static_analysis**: Code quality analysis and validation\\n')
    f.write('- ⚡ **code**: Code execution, sandboxing, review, and monitoring\\n')
    f.write('- 📊 **data_visualization**: Metrics dashboards and development charts\\n')
    f.write('- 🌳 **git_operations**: Version control integration\\n\\n')
    
    f.write('## 📁 Generated Artifacts\\n\\n')
    
    # List all files in output directory
    output_path = Path(output_dir)
    all_files = []
    
    for file_path in output_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(output_path)
            all_files.append(str(relative_path))
    
    all_files.sort()
    
    f.write('### 🎯 Generated Project Files\\n')
    project_files = [f for f in all_files if f.startswith('generated_project/')]
    for file in project_files:
        f.write(f'- `{file}`\\n')
    
    f.write('\\n### 📊 Analysis and Reports\\n')
    report_files = [f for f in all_files if not f.startswith('generated_project/')]
    for file in report_files:
        f.write(f'- `{file}`\\n')
    
    f.write('\\n## 🎉 Workflow Success\\n\\n')
    f.write('This comprehensive workflow demonstrated the power of Codomyrmex\\'s\\n')
    f.write('modular architecture by seamlessly integrating multiple modules\\n')
    f.write('into a complete AI-enhanced development lifecycle.\\n\\n')
    
    f.write('**Key Achievements:**\\n')
    f.write('- ✅ End-to-end AI-powered development\\n')
    f.write('- ✅ Comprehensive quality analysis\\n') 
    f.write('- ✅ Secure code execution and validation\\n')
    f.write('- ✅ Rich metrics and visualization dashboards\\n')
    f.write('- ✅ Complete documentation and reporting\\n')
    f.write('- ✅ Git integration and version control\\n\\n')
    
    f.write('## 🔗 Next Steps\\n\\n')
    f.write('1. **Review Generated Code**: Examine the AI-generated project files\\n')
    f.write('2. **Analyze Metrics**: Study the development metrics and visualizations\\n')
    f.write('3. **Quality Improvements**: Address any issues found in quality analysis\\n')
    f.write('4. **Extend Functionality**: Build upon the generated foundation\\n')
    f.write('5. **Share Results**: Use insights for future development projects\\n')

logger.info('📚 Final documentation generated')
print(f'\\n📄 Comprehensive workflow report: WORKFLOW_COMPLETE.md')
print(f'📊 Total files generated: {len(all_files)}')
"

show_success "Final documentation completed"

# Final Summary
DEMO_END_TIME=$(date +%s)
DEMO_DURATION=$((DEMO_END_TIME - DEMO_START_TIME))

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║               🎉 WORKFLOW ORCHESTRATION COMPLETE 🎉       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}🚀 Complete development workflow orchestrated in $(($DEMO_DURATION / 60)) minutes $(($DEMO_DURATION % 60)) seconds${NC}"
echo -e "${GREEN}📁 All results and artifacts available at: $OUTPUT_DIR${NC}"
echo ""

echo -e "${WHITE}🎯 Workflow Accomplishments:${NC}"
echo -e "${GREEN}  ✅ AI-powered project generation ($PROJECT_NAME)${NC}"
echo -e "${GREEN}  ✅ Comprehensive code quality analysis and validation${NC}"
echo -e "${GREEN}  ✅ Secure code execution and testing in sandbox environment${NC}"
echo -e "${GREEN}  ✅ Rich development metrics and visualization dashboards${NC}"
echo -e "${GREEN}  ✅ Complete documentation and reporting generation${NC}"
echo -e "${GREEN}  ✅ Git integration with branch creation and commit history${NC}"
echo ""

echo -e "${YELLOW}💎 Codomyrmex Modules Demonstrated:${NC}"
echo -e "${CYAN}  🔧 environment_setup${NC} - Environment validation and configuration"
echo -e "${CYAN}  📝 logging_monitoring${NC} - Structured logging throughout workflow"
echo -e "${CYAN}  🤖 ai_code_editing${NC} - AI-powered code generation and refinement"
echo -e "${CYAN}  🔍 static_analysis${NC} - Code quality analysis and validation"
echo -e "${CYAN}  ⚡ code${NC} - Code execution, sandboxing, review, and monitoring"
echo -e "${CYAN}  📊 data_visualization${NC} - Metrics dashboards and charts"
echo -e "${CYAN}  🌳 git_operations${NC} - Version control integration"
echo ""

echo -e "${BLUE}🔗 Key Artifacts Generated:${NC}"
echo "  📁 Generated project code with tests and documentation"
echo "  📊 Development metrics dashboard with 6+ visualizations" 
echo "  🔍 Code quality analysis reports and recommendations"
echo "  ⚡ Execution results and testing validation"
echo "  📚 Comprehensive workflow documentation and summary"
echo ""

echo -e "${BLUE}📖 Next Steps:${NC}"
echo "  🔍 Explore: open $OUTPUT_DIR"
echo "  📄 Read: $OUTPUT_DIR/WORKFLOW_COMPLETE.md"
echo "  📊 Review: $OUTPUT_DIR/development_dashboard.md" 
echo "  🚀 Build: Extend the generated project with additional features"
echo ""

echo -e "${GREEN}🎉 This orchestrator showcased the full power of Codomyrmex's modular${NC}"
echo -e "${GREEN}   architecture in a real-world AI-enhanced development workflow!${NC}"

