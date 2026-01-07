#!/bin/bash
# 🐜 Codomyrmex AI Development Assistant
# 
# This thin orchestrator demonstrates an AI-enhanced development workflow:
# 1. Interactive AI code generation with multiple LLM providers
# 2. Secure code execution and validation in sandbox environment
# 3. Iterative refinement based on execution results
# 4. Comprehensive logging and result tracking
#
# Prerequisites: API keys for OpenAI/Anthropic (in .env file)  
# Duration: ~6 minutes
# Modules: ai_code_editing + code + logging_monitoring + environment_setup

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
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/ai-development-assistant"
DEMO_START_TIME=$(date +%s)

# Banner
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    🤖 Codomyrmex AI Development Assistant 🤖           ║${NC}"
echo -e "${CYAN}║    AI Code Generation + Execution + Validation          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Helper functions
show_progress() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Phase 1: Environment Setup and API Key Validation
show_progress "Phase 1: Environment Setup and API Key Validation"
echo -e "${WHITE}Validating AI development environment...${NC}"

cd "$PROJECT_ROOT"

# Test module imports and API key availability
python3 -c "
import sys
import os
sys.path.insert(0, 'src')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print('✅ Environment variables loaded')
except ImportError:
    print('⚠️  python-dotenv not found, using system environment')

# Test core module imports
try:
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed
    from codomyrmex.agents.ai_code_editing.ai_code_helpers import generate_code_snippet, refactor_code_snippet
    from codomyrmex.coding.execution.executor import execute_code
    print('✅ All required modules imported successfully')
except ImportError as e:
    print(f'❌ Module import failed: {e}')
    exit(1)

# Check API keys
api_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
available_providers = []

for key in api_keys:
    if os.getenv(key):
        provider = key.replace('_API_KEY', '').lower()
        available_providers.append(provider)
        print(f'✅ {provider.title()} API key available')
    else:
        provider = key.replace('_API_KEY', '').lower()  
        print(f'⚠️  {provider.title()} API key not set')

if not available_providers:
    print('❌ No API keys found! Please set at least one:')
    print('   OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY')
    print('   Add them to .env file in project root')
    exit(1)

print(f'🎯 Available AI providers: {\", \".join([p.title() for p in available_providers])}')
"

if [ $? -ne 0 ]; then
    show_error "Environment validation failed."
    echo ""
    echo "To fix this:"
    echo "1. Ensure Codomyrmex is installed: pip install -e ."
    echo "2. Create .env file with API keys:"
    echo "   OPENAI_API_KEY=\"sk-...\""
    echo "   ANTHROPIC_API_KEY=\"sk-ant-...\""
    echo "   GOOGLE_API_KEY=\"AIzaSy...\""
    exit 1
fi

show_success "Environment validation completed"

# Phase 2: Interactive Development Task Selection
show_progress "Phase 2: Interactive Development Task Selection"
echo -e "${WHITE}Choose your AI development task:${NC}"
echo ""
echo "Available development scenarios:"
echo "  1. 🧮 Create a calculator with error handling"
echo "  2. 📊 Generate data processing functions" 
echo "  3. 🌐 Build a simple web scraper"
echo "  4. 🔍 Create file search utilities"
echo "  5. 🎲 Random number generation with statistics"
echo "  6. ✏️  Custom task (enter your own description)"
echo ""

read -p "Choose option (1-6): " task_choice

case $task_choice in
    1) 
        TASK_DESCRIPTION="Create a Python calculator class with methods for basic operations (add, subtract, multiply, divide) that includes proper error handling for division by zero and invalid inputs. Include a main function that demonstrates usage."
        TASK_NAME="calculator"
        ;;
    2)
        TASK_DESCRIPTION="Create Python functions to process a list of dictionaries representing sales data. Include functions to calculate total sales, average sale amount, find top performers, and generate a summary report. Include sample data and demonstration."
        TASK_NAME="data_processor"
        ;;
    3)
        TASK_DESCRIPTION="Create a simple Python web scraper using requests and BeautifulSoup to extract article titles and URLs from a news website. Include error handling for network issues and rate limiting. Provide a demonstration function."
        TASK_NAME="web_scraper"
        ;;
    4)
        TASK_DESCRIPTION="Create Python utilities to search for files in a directory tree by name, extension, size, or modification date. Include recursive search, pattern matching, and result formatting. Demonstrate with sample usage."
        TASK_NAME="file_search"
        ;;
    5)
        TASK_DESCRIPTION="Create a Python module for generating random numbers with statistical analysis. Include functions for generating random integers, floats, selecting from lists, and calculating mean, median, mode of generated sequences. Include visualization of distributions."
        TASK_NAME="random_stats"
        ;;
    6)
        read -p "Enter your custom task description: " custom_task
        if [ -z "$custom_task" ]; then
            show_error "Task description cannot be empty"
            exit 1
        fi
        TASK_DESCRIPTION="$custom_task"
        TASK_NAME="custom_task"
        ;;
    *)
        show_error "Invalid choice"
        exit 1
        ;;
esac

show_success "Selected task: $TASK_NAME"
echo -e "${CYAN}Task: $TASK_DESCRIPTION${NC}"
echo ""

# Phase 3: AI-Powered Code Generation
show_progress "Phase 3: AI-Powered Code Generation"
echo -e "${WHITE}Generating code with AI assistance...${NC}"

# Run the AI development assistant orchestrator
python3 -c "
import sys
import os
import json
import time
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.agents.ai_code_editing.ai_code_helpers import generate_code_snippet, refactor_code_snippet  
from codomyrmex.coding_execution_sandbox.code_executor import execute_code

# Setup logging
setup_logging()
logger = get_logger(__name__)

logger.info('🤖 Starting AI Development Assistant')

task_description = '''$TASK_DESCRIPTION'''
task_name = '$TASK_NAME'
output_dir = '$OUTPUT_DIR'

logger.info(f'Task: {task_name}')
logger.info(f'Description: {task_description[:100]}...')

# Ensure output directory exists
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Development session results
session_results = {
    'task_name': task_name,
    'task_description': task_description,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'iterations': [],
    'final_code': '',
    'execution_results': [],
    'success': False
}

try:
    # Phase 1: Initial Code Generation
    logger.info('🎯 Generating initial code with AI...')
    print('\\n🤖 Generating initial code solution...')
    
    generation_result = generate_code_snippet(
        prompt=task_description,
        language='python',
        llm_provider='openai'  # Will fall back to available provider
    )
    
    if generation_result['status'] != 'success':
        logger.error(f'Code generation failed: {generation_result.get(\"error\", \"Unknown error\")}')
        print(f'❌ Code generation failed: {generation_result.get(\"error\", \"Unknown error\")}')
        exit(1)
    
    generated_code = generation_result['generated_code']
    iteration_1 = {
        'iteration': 1,
        'action': 'initial_generation',
        'prompt': task_description,
        'code': generated_code,
        'timestamp': time.strftime('%H:%M:%S')
    }
    session_results['iterations'].append(iteration_1)
    
    print('✅ Initial code generated successfully')
    logger.info(f'Generated code length: {len(generated_code)} characters')
    
    # Save initial code
    with open(f'{output_dir}/{task_name}_v1.py', 'w') as f:
        f.write(generated_code)
    
    # Phase 2: Code Execution and Validation
    logger.info('⚡ Testing generated code in sandbox...')
    print('\\n⚡ Testing code in secure sandbox environment...')
    
    execution_result = execute_code(
        language='python',
        code=generated_code,
        timeout=30
    )
    
    session_results['execution_results'].append({
        'iteration': 1,
        'result': execution_result
    })
    
    print(f'📊 Execution completed with exit code: {execution_result.get(\"exit_code\", \"unknown\")}')
    
    if execution_result.get('exit_code') == 0:
        print('✅ Code executed successfully!')
        logger.info('Code execution successful')
        
        # Show output
        if execution_result.get('stdout'):
            print('\\n📋 Program output:')
            print('─' * 40)
            print(execution_result['stdout'])
            print('─' * 40)
        
        session_results['success'] = True
        session_results['final_code'] = generated_code
        
    else:
        print('❌ Code execution failed')
        logger.warning('Initial code execution failed, attempting refinement...')
        
        # Show error details
        if execution_result.get('stderr'):
            print('\\n🔍 Error details:')
            print('─' * 40)  
            print(execution_result['stderr'])
            print('─' * 40)
        
        # Phase 3: AI-Powered Refinement
        print('\\n🔧 Refining code based on execution results...')
        
        error_context = f\"\"\"
        The code failed with:
        Exit code: {execution_result.get('exit_code', 'unknown')}
        Error: {execution_result.get('stderr', 'No error details')}
        
        Please fix the issues and ensure the code runs correctly.
        \"\"\"
        
        refinement_result = refactor_code_snippet(
            code_snippet=generated_code,
            refactoring_instruction=error_context,
            language='python',
            llm_provider='openai'
        )
        
        if refinement_result['status'] == 'success':
            refined_code = refinement_result['refactored_code']
            
            iteration_2 = {
                'iteration': 2,
                'action': 'refinement',
                'prompt': error_context,
                'code': refined_code,
                'timestamp': time.strftime('%H:%M:%S')
            }
            session_results['iterations'].append(iteration_2)
            
            # Save refined code
            with open(f'{output_dir}/{task_name}_v2.py', 'w') as f:
                f.write(refined_code)
            
            # Test refined code
            print('⚡ Testing refined code...')
            refined_execution = execute_code(
                language='python',
                code=refined_code,
                timeout=30
            )
            
            session_results['execution_results'].append({
                'iteration': 2,
                'result': refined_execution
            })
            
            if refined_execution.get('exit_code') == 0:
                print('✅ Refined code executed successfully!')
                session_results['success'] = True
                session_results['final_code'] = refined_code
                
                if refined_execution.get('stdout'):
                    print('\\n📋 Program output:')
                    print('─' * 40)
                    print(refined_execution['stdout'])
                    print('─' * 40)
            else:
                print('❌ Refined code still has issues')
                if refined_execution.get('stderr'):
                    print(f'Error: {refined_execution[\"stderr\"]}')
        else:
            print('❌ Code refinement failed')
            logger.error(f'Refinement failed: {refinement_result.get(\"error\", \"Unknown error\")}')
    
    # Save final results
    with open(f'{output_dir}/session_results.json', 'w') as f:
        json.dump(session_results, f, indent=2)
    
    # Generate development report
    with open(f'{output_dir}/development_report.md', 'w') as f:
        f.write(f'# AI Development Session Report\\n\\n')
        f.write(f'**Task**: {task_name}\\n')
        f.write(f'**Generated**: {session_results[\"timestamp\"]}\\n')
        f.write(f'**Success**: {\"✅ Yes\" if session_results[\"success\"] else \"❌ No\"}\\n\\n')
        
        f.write('## Task Description\\n\\n')
        f.write(f'{task_description}\\n\\n')
        
        f.write('## Development Process\\n\\n')
        for i, iteration in enumerate(session_results['iterations']):
            f.write(f'### Iteration {iteration[\"iteration\"]} - {iteration[\"action\"].title()}\\n')
            f.write(f'**Time**: {iteration[\"timestamp\"]}\\n\\n')
            
            exec_result = session_results['execution_results'][i]['result']
            f.write(f'**Execution Result**: ')
            if exec_result.get('exit_code') == 0:
                f.write('✅ Success\\n')
            else:
                f.write(f'❌ Failed (exit code: {exec_result.get(\"exit_code\")})\\n')
            
            if exec_result.get('stderr'):
                f.write(f'**Error**: {exec_result[\"stderr\"]}\\n')
            f.write('\\n')
        
        f.write('## Generated Files\\n\\n')
        for iteration in session_results['iterations']:
            f.write(f'- `{task_name}_v{iteration[\"iteration\"]}.py` - {iteration[\"action\"]} code\\n')
        f.write('- `session_results.json` - Complete session data\\n')
        f.write('- `development_report.md` - This report\\n')
    
    logger.info('📄 Generated development report')
    logger.info('🎉 AI Development Assistant completed successfully!')
    
    # Final summary
    print('\\n' + '='*60)
    print('🎉 AI DEVELOPMENT ASSISTANT COMPLETE')
    print('='*60)
    print(f'📁 Session results saved to: {output_dir}')
    print(f'🤖 Iterations completed: {len(session_results[\"iterations\"])}')
    print(f'⚡ Executions performed: {len(session_results[\"execution_results\"])}')
    print(f'🎯 Final status: {\"✅ Success\" if session_results[\"success\"] else \"❌ Needs work\"}')
    print('')
    
    if session_results['success']:
        print('🏆 Generated working code solution!')
        print(f'📝 Final code saved as: {task_name}_v{len(session_results[\"iterations\"])}.py')
    else:
        print('🔧 Code needs further refinement')
        print('💡 Review the error details and try manual fixes')
    
except Exception as e:
    logger.error(f'Development session failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ Session failed: {e}')
    exit(1)
"

# Phase 4: Results Summary and Next Steps
DEMO_END_TIME=$(date +%s)
DEMO_DURATION=$((DEMO_END_TIME - DEMO_START_TIME))

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           🎉 SESSION COMPLETE 🎉             ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🤖 Development session completed in ${DEMO_DURATION} seconds${NC}"
echo -e "${GREEN}📁 All results available at: $OUTPUT_DIR${NC}"
echo ""
echo -e "${WHITE}Generated outputs:${NC}"
echo "  • development_report.md - Session summary and process documentation"
echo "  • session_results.json - Complete session data and metadata"
echo "  • ${TASK_NAME}_v1.py - Initial AI-generated code"
echo "  • ${TASK_NAME}_v2.py - Refined code (if refinement occurred)"
echo ""
echo -e "${YELLOW}💡 This orchestrator demonstrated:${NC}"
echo "  ✅ AI code generation (ai_code_editing module)"
echo "  ✅ Secure code execution (code module)" 
echo "  ✅ Iterative refinement based on execution feedback"
echo "  ✅ Comprehensive logging and session tracking"
echo ""
echo -e "${BLUE}🔗 Next steps:${NC}"
echo "  📖 Review development_report.md for detailed process analysis"
echo "  🧪 Run the generated code files independently to verify functionality"
echo "  🔄 Use the session results to improve future development tasks"
echo ""
echo -e "${BLUE}📂 View results: open $OUTPUT_DIR${NC}"

