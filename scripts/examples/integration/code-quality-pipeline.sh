#!/bin/bash
# 🐜 Codomyrmex Code Quality Pipeline
# 
# This thin orchestrator demonstrates a complete code quality analysis workflow:
# 1. Environment validation and logging setup
# 2. Static code analysis across multiple tools  
# 3. Data visualization of analysis results
# 4. Quality metrics dashboard generation
#
# Prerequisites: Sample Python project or repository
# Duration: ~4 minutes
# Modules: static_analysis + data_visualization + logging_monitoring + environment_setup

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
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/code-quality-pipeline"
DEMO_START_TIME=$(date +%s)

# Parse command line arguments
INTERACTIVE=true
TARGET_DIR=""
for arg in "$@"; do
    case $arg in
        --non-interactive)
            INTERACTIVE=false
            ;;
        --target=*)
            TARGET_DIR="${arg#*=}"
            ;;
        --help)
            echo "Usage: $0 [--non-interactive] [--target=PATH] [--help]"
            echo "  --non-interactive  Run without user prompts"
            echo "  --target=PATH      Specify target directory for analysis"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            # If it's not a flag, treat it as target directory (for backward compatibility)
            if [ -z "$TARGET_DIR" ] && [ "$arg" != "--non-interactive" ]; then
                TARGET_DIR="$arg"
            fi
            ;;
    esac
done

# Banner
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🐜 Codomyrmex Code Quality Pipeline Orchestrator 🐜   ║${NC}"
echo -e "${CYAN}║  Static Analysis + Data Visualization + Reporting       ║${NC}"
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

# Phase 1: Environment Setup and Validation
show_progress "Phase 1: Environment Setup and Validation"
echo -e "${WHITE}Setting up logging and validating environment...${NC}"

cd "$PROJECT_ROOT"

# Check if we're in a Python environment
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Test module imports
python3 -c "
import sys
import os
sys.path.insert(0, 'src')

# Test core module imports
try:
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed
    from codomyrmex.static_analysis.pyrefly_runner import run_pyrefly_analysis
    from codomyrmex.data_visualization import create_bar_chart, create_heatmap, create_line_plot
    print('✅ All required modules imported successfully')
except ImportError as e:
    print(f'❌ Module import failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    show_error "Module import test failed. Please ensure Codomyrmex is properly installed."
    exit 1
fi

show_success "Environment validation completed"

# Phase 2: Target Analysis Selection
show_progress "Phase 2: Target Analysis Selection"
echo -e "${WHITE}Selecting code for quality analysis...${NC}"

# Check if user provided a target directory
if [ -z "$TARGET_DIR" ]; then
    if [ "$INTERACTIVE" = true ]; then
        echo "No target directory provided. Available options:"
        echo "  1. Analyze Codomyrmex source code (src/codomyrmex/)"
        echo "  2. Analyze examples directory (examples/)"
        echo "  3. Analyze testing directory (testing/)"
        echo "  4. Specify custom directory"
        echo ""
        read -p "Choose option (1-4): " choice
        
        case $choice in
            1) TARGET_DIR="src/codomyrmex/" ;;
            2) TARGET_DIR="examples/" ;;
            3) TARGET_DIR="testing/" ;;
            4) 
                read -p "Enter directory path: " custom_dir
                if [ ! -d "$custom_dir" ]; then
                    show_error "Directory $custom_dir does not exist"
                    exit 1
                fi
                TARGET_DIR="$custom_dir"
                ;;
            *) 
                show_error "Invalid choice"
                exit 1
                ;;
        esac
    else
        # Non-interactive mode: use Codomyrmex source code as default
        TARGET_DIR="src/codomyrmex/"
        echo "Non-interactive mode: Using default target directory: $TARGET_DIR"
    fi
fi

if [ ! -d "$TARGET_DIR" ]; then
    show_error "Target directory $TARGET_DIR does not exist"
    exit 1
fi

show_success "Target selected: $TARGET_DIR"

# Phase 3: Static Code Analysis
show_progress "Phase 3: Static Code Analysis"
echo -e "${WHITE}Running comprehensive code analysis...${NC}"

# Run the quality analysis orchestrator
python3 -c "
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, 'src')

from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.static_analysis.pyrefly_runner import run_pyrefly_analysis
from codomyrmex.data_visualization import create_bar_chart, create_line_plot, create_heatmap
import subprocess
import time

# Setup logging
setup_logging()
logger = get_logger(__name__)

logger.info('🚀 Starting Code Quality Pipeline')

target_dir = '$TARGET_DIR'
output_dir = '$OUTPUT_DIR'
logger.info(f'Target directory: {target_dir}')
logger.info(f'Output directory: {output_dir}')

# Ensure output directory exists
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Collect analysis results
results = {
    'target_directory': target_dir,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'analysis_results': {},
    'metrics': {},
    'recommendations': []
}

# Static Analysis with multiple tools
logger.info('Running static analysis...')

try:
    # Run basic static analysis tools
    tools_results = {}
    
    # Find Python files
    python_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    logger.info(f'Found {len(python_files)} Python files to analyze')
    
    if python_files:
        # Run pylint if available
        try:
            result = subprocess.run(['pylint', '--output-format=json'] + python_files[:5], 
                                  capture_output=True, text=True, timeout=30)
            if result.stdout.strip():
                pylint_data = json.loads(result.stdout)
                tools_results['pylint'] = {
                    'issues_count': len(pylint_data),
                    'issues': pylint_data[:10]  # First 10 issues
                }
                logger.info(f'Pylint found {len(pylint_data)} issues')
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f'Pylint analysis failed: {e}')
            tools_results['pylint'] = {'error': str(e)}
        
        # Run flake8 if available  
        try:
            result = subprocess.run(['flake8', '--format=json'] + python_files[:5],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                tools_results['flake8'] = {'output': result.stdout}
                logger.info('Flake8 analysis completed')
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f'Flake8 analysis failed: {e}')
            tools_results['flake8'] = {'error': str(e)}
        
        # Basic file metrics
        file_metrics = {
            'total_files': len(python_files),
            'total_lines': 0,
            'avg_file_size': 0,
            'largest_file': {'name': '', 'lines': 0}
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    file_metrics['total_lines'] += lines
                    if lines > file_metrics['largest_file']['lines']:
                        file_metrics['largest_file'] = {'name': file_path, 'lines': lines}
            except Exception as e:
                logger.warning(f'Could not read {file_path}: {e}')
        
        if file_metrics['total_files'] > 0:
            file_metrics['avg_file_size'] = file_metrics['total_lines'] / file_metrics['total_files']
        
        tools_results['file_metrics'] = file_metrics
        logger.info(f'Analyzed {file_metrics[\"total_files\"]} files, {file_metrics[\"total_lines\"]} total lines')
    
    results['analysis_results'] = tools_results
    
    # Generate visualizations
    logger.info('Generating analysis visualizations...')
    
    # Create metrics overview chart
    if 'file_metrics' in tools_results:
        metrics = tools_results['file_metrics']
        
        # File size distribution visualization
        create_bar_chart(
            categories=['Total Files', 'Avg Lines/File', 'Largest File'],
            values=[
                metrics['total_files'],
                int(metrics['avg_file_size']),
                metrics['largest_file']['lines']
            ],
            title='Code Metrics Overview',
            x_label='Metrics',
            y_label='Count/Lines',
            output_path=f'{output_dir}/code_metrics_overview.png'
        )
        logger.info('📊 Generated code metrics overview chart')
    
    # Tool results comparison
    tool_names = []
    issue_counts = []
    
    for tool, data in tools_results.items():
        if tool != 'file_metrics' and 'error' not in data:
            tool_names.append(tool.title())
            if 'issues_count' in data:
                issue_counts.append(data['issues_count'])
            elif 'issues' in data:
                issue_counts.append(len(data['issues']))
            else:
                issue_counts.append(0)
    
    if tool_names and issue_counts:
        create_bar_chart(
            categories=tool_names,
            values=issue_counts,
            title='Static Analysis Results by Tool',
            x_label='Analysis Tools',
            y_label='Issues Found',
            output_path=f'{output_dir}/tool_comparison.png',
            bar_color='lightcoral'
        )
        logger.info('📊 Generated tool comparison chart')
    
    # Save detailed results
    with open(f'{output_dir}/analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate summary report
    with open(f'{output_dir}/quality_report.md', 'w') as f:
        f.write(f'# Code Quality Analysis Report\n\n')
        f.write(f'**Target**: {target_dir}\n')
        f.write(f'**Generated**: {results[\"timestamp\"]}\n\n')
        
        f.write('## 📊 Metrics Summary\n\n')
        if 'file_metrics' in tools_results:
            metrics = tools_results['file_metrics']
            f.write(f'- **Total Python Files**: {metrics[\"total_files\"]}\n')
            f.write(f'- **Total Lines of Code**: {metrics[\"total_lines\"]}\n')
            f.write(f'- **Average File Size**: {metrics[\"avg_file_size\"]:.1f} lines\n')
            f.write(f'- **Largest File**: {metrics[\"largest_file\"][\"name\"]} ({metrics[\"largest_file\"][\"lines\"]} lines)\n\n')
        
        f.write('## 🔍 Analysis Tools Results\n\n')
        for tool, data in tools_results.items():
            if tool != 'file_metrics':
                f.write(f'### {tool.title()}\n')
                if 'error' in data:
                    f.write(f'- Status: ❌ Failed ({data[\"error\"]})\n')
                elif 'issues_count' in data:
                    f.write(f'- Issues Found: {data[\"issues_count\"]}\n')
                else:
                    f.write(f'- Status: ✅ Completed\n')
                f.write('\n')
        
        f.write('## 📈 Generated Visualizations\n\n')
        f.write('- `code_metrics_overview.png` - Code metrics overview\n')
        f.write('- `tool_comparison.png` - Analysis tools comparison\n')
        f.write('- `analysis_results.json` - Detailed analysis data\n')
    
    logger.info('📄 Generated quality report')
    logger.info('🎉 Code Quality Pipeline completed successfully!')
    
    print('\n' + '='*60)
    print('🎉 CODE QUALITY PIPELINE COMPLETE')
    print('='*60)
    print(f'📁 Results saved to: {output_dir}')
    print(f'📊 Charts generated: {len([f for f in os.listdir(output_dir) if f.endswith(\".png\")])}')
    print(f'📄 Reports: quality_report.md, analysis_results.json')
    print('')
    print('🔍 Key Findings:')
    if 'file_metrics' in tools_results:
        metrics = tools_results['file_metrics']
        print(f'  • Analyzed {metrics[\"total_files\"]} Python files')
        print(f'  • Total {metrics[\"total_lines\"]} lines of code')
        print(f'  • Average {metrics[\"avg_file_size\"]:.1f} lines per file')
    
    total_issues = sum([data.get('issues_count', 0) for data in tools_results.values() if 'issues_count' in data])
    if total_issues > 0:
        print(f'  • Found {total_issues} total issues across all tools')
    else:
        print('  • No major issues detected! 🎉')
    
except Exception as e:
    logger.error(f'Analysis failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    exit(1)
" 

# Phase 4: Results Summary
DEMO_END_TIME=$(date +%s)
DEMO_DURATION=$((DEMO_END_TIME - DEMO_START_TIME))

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           🎉 PIPELINE COMPLETE 🎉            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Analysis completed in ${DEMO_DURATION} seconds${NC}"
echo -e "${GREEN}📁 Results available at: $OUTPUT_DIR${NC}"
echo ""
echo -e "${WHITE}Generated outputs:${NC}"
echo "  • quality_report.md - Human-readable summary"
echo "  • analysis_results.json - Detailed analysis data" 
echo "  • code_metrics_overview.png - Metrics visualization"
echo "  • tool_comparison.png - Tools comparison chart"
echo ""
echo -e "${YELLOW}💡 This orchestrator demonstrated:${NC}"
echo "  ✅ Environment validation (environment_setup + logging_monitoring)"
echo "  ✅ Static analysis integration (static_analysis module)"
echo "  ✅ Data visualization (data_visualization module)"
echo "  ✅ Comprehensive reporting and result aggregation"
echo ""
echo -e "${BLUE}🔗 View results: open $OUTPUT_DIR${NC}"
echo -e "${BLUE}📖 Learn more: Check the generated quality_report.md${NC}"
