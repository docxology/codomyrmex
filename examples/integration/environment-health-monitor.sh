#!/bin/bash
# 🐜 Codomyrmex Environment Health Monitor
# 
# This thin orchestrator provides comprehensive environment health monitoring:
# 1. Development environment validation and dependency checking
# 2. Git repository health assessment and metadata analysis
# 3. System resource monitoring and performance metrics
# 4. Comprehensive health reporting with recommendations
#
# Prerequisites: None (self-contained health check)
# Duration: ~3 minutes  
# Modules: environment_setup + git_operations + logging_monitoring + system_discovery

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
OUTPUT_DIR="$PROJECT_ROOT/examples/output/environment-health-monitor"
DEMO_START_TIME=$(date +%s)

# Banner
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      🏥 Codomyrmex Environment Health Monitor 🏥       ║${NC}"
echo -e "${CYAN}║   Environment + Git + System + Performance Monitoring   ║${NC}"
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

show_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Phase 1: System Information Gathering
show_progress "Phase 1: System Information Gathering"
echo -e "${WHITE}Collecting system and environment information...${NC}"

cd "$PROJECT_ROOT"

# Gather system information
SYSTEM_INFO=$(uname -a)
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Python not found")
NODE_VERSION=$(node --version 2>/dev/null || echo "Node.js not found")
GIT_VERSION=$(git --version 2>/dev/null || echo "Git not found") 
SHELL_INFO="$SHELL"
USER_INFO="$(whoami)@$(hostname)"

echo -e "${CYAN}System Information:${NC}"
echo "  🖥️  System: $SYSTEM_INFO"
echo "  👤 User: $USER_INFO"
echo "  🐍 Python: $PYTHON_VERSION"
echo "  📦 Node.js: $NODE_VERSION"
echo "  🌳 Git: $GIT_VERSION"
echo "  🐚 Shell: $SHELL_INFO"

show_success "System information collected"

# Phase 2: Environment Health Assessment
show_progress "Phase 2: Environment Health Assessment"
echo -e "${WHITE}Running comprehensive environment validation...${NC}"

# Run the environment health monitor
python3 -c "
import sys
import os
import json
import time
import subprocess
from pathlib import Path
import platform
sys.path.insert(0, 'src')

try:
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed, is_uv_available, is_uv_environment
    setup_logging_available = True
except ImportError as e:
    print(f'⚠️  Codomyrmex modules not fully available: {e}')
    print('Using basic Python logging as fallback')
    setup_logging_available = False
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

if setup_logging_available:
    setup_logging()
    logger = get_logger(__name__)

logger.info('🏥 Starting Environment Health Monitor')

output_dir = '$OUTPUT_DIR'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Health assessment results
health_results = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'system_info': {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor() or 'Unknown'
    },
    'environment_health': {},
    'git_health': {},
    'dependency_health': {},
    'performance_metrics': {},
    'recommendations': [],
    'overall_score': 0,
    'status': 'unknown'
}

logger.info('Starting comprehensive health assessment')

try:
    # Environment Health Assessment
    logger.info('📋 Assessing environment health...')
    print('\\n📋 Environment Health Assessment')
    print('─' * 40)
    
    env_health = {
        'python_available': False,
        'pip_available': False,
        'uv_available': False,
        'virtual_env': False,
        'git_available': False,
        'node_available': False,
        'codomyrmex_installed': False
    }
    
    # Python check
    try:
        import sys
        env_health['python_available'] = True
        python_version = sys.version_info
        if python_version >= (3, 9):
            print('✅ Python 3.9+ available')
        else:
            print(f'⚠️  Python {python_version.major}.{python_version.minor} (recommend 3.9+)')
            health_results['recommendations'].append('Upgrade to Python 3.9 or higher for better compatibility')
    except Exception as e:
        print(f'❌ Python check failed: {e}')
    
    # Package managers
    try:
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            env_health['pip_available'] = True
            print('✅ pip available')
    except Exception:
        print('❌ pip not available')
    
    if setup_logging_available:
        try:
            uv_available = is_uv_available()
            env_health['uv_available'] = uv_available
            if uv_available:
                print('✅ uv available (fast package manager)')
                uv_env = is_uv_environment()
                if uv_env:
                    print('✅ Running in uv-managed environment')
                else:
                    print('ℹ️  uv available but not in uv environment')
            else:
                print('⚠️  uv not available (consider installing for faster package management)')
                health_results['recommendations'].append('Install uv for faster package management: https://github.com/astral-sh/uv')
        except Exception as e:
            print(f'⚠️  uv check failed: {e}')
    
    # Virtual environment check
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        env_health['virtual_env'] = True
        print('✅ Running in virtual environment')
    else:
        print('⚠️  Not in virtual environment (recommended for development)')
        health_results['recommendations'].append('Use a virtual environment to isolate project dependencies')
    
    # Git availability
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            env_health['git_available'] = True
            print('✅ Git available')
    except Exception:
        print('❌ Git not available')
        health_results['recommendations'].append('Install Git for version control functionality')
    
    # Node.js check (for documentation)
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            env_health['node_available'] = True
            node_version = result.stdout.strip()
            print(f'✅ Node.js available ({node_version})')
    except Exception:
        print('⚠️  Node.js not available (needed for documentation generation)')
        health_results['recommendations'].append('Install Node.js 18+ for documentation website generation')
    
    # Codomyrmex installation check
    try:
        import codomyrmex
        env_health['codomyrmex_installed'] = True
        print('✅ Codomyrmex package installed')
    except ImportError:
        try:
            # Check if we can import individual modules from src
            sys.path.insert(0, 'src')
            from codomyrmex import logging_monitoring
            env_health['codomyrmex_installed'] = True
            print('✅ Codomyrmex modules available (development mode)')
        except ImportError:
            print('❌ Codomyrmex not properly installed')
            health_results['recommendations'].append('Install Codomyrmex: pip install -e . (from project root)')
    
    health_results['environment_health'] = env_health
    
    # Git Repository Health
    logger.info('🌳 Assessing Git repository health...')
    print('\\n🌳 Git Repository Health Assessment')
    print('─' * 40)
    
    git_health = {
        'is_git_repo': False,
        'has_remote': False,
        'clean_working_tree': False,
        'current_branch': 'unknown',
        'commit_count': 0,
        'uncommitted_changes': 0
    }
    
    if env_health['git_available']:
        try:
            # Check if in git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                git_health['is_git_repo'] = True
                print('✅ In Git repository')
                
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    git_health['current_branch'] = result.stdout.strip()
                    print(f'📍 Current branch: {git_health[\"current_branch\"]}')
                
                # Check for remote
                result = subprocess.run(['git', 'remote'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    git_health['has_remote'] = True
                    print('✅ Has remote repository')
                else:
                    print('⚠️  No remote repository configured')
                
                # Check working tree status
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    uncommitted = result.stdout.strip()
                    if not uncommitted:
                        git_health['clean_working_tree'] = True
                        print('✅ Clean working tree')
                    else:
                        git_health['uncommitted_changes'] = len(uncommitted.split('\\n'))
                        print(f'⚠️  {git_health[\"uncommitted_changes\"]} uncommitted changes')
                
                # Get commit count
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    git_health['commit_count'] = int(result.stdout.strip())
                    print(f'📊 Total commits: {git_health[\"commit_count\"]}')
                
            else:
                print('❌ Not in a Git repository')
                health_results['recommendations'].append('Initialize Git repository: git init')
        except Exception as e:
            print(f'❌ Git assessment failed: {e}')
    else:
        print('❌ Git not available for repository assessment')
    
    health_results['git_health'] = git_health
    
    # Dependency Health Check
    logger.info('📦 Checking dependency health...')
    print('\\n📦 Dependency Health Assessment')
    print('─' * 40)
    
    dependency_health = {
        'requirements_file_exists': False,
        'pyproject_toml_exists': False,
        'package_json_exists': False,
        'installed_packages': 0,
        'outdated_packages': []
    }
    
    # Check for dependency files
    files_to_check = ['requirements.txt', 'pyproject.toml', 'package.json', 'uv.lock']
    for filename in files_to_check:
        if os.path.exists(filename):
            dependency_health[f'{filename.replace(\".\", \"_\").replace(\"-\", \"_\")}_exists'] = True
            print(f'✅ {filename} found')
    
    # Count installed Python packages
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\\n')
            # Skip header lines
            package_lines = [line for line in lines if line and not line.startswith('---') and 'Package' not in line]
            dependency_health['installed_packages'] = len(package_lines)
            print(f'📦 Installed Python packages: {dependency_health[\"installed_packages\"]}')
    except Exception as e:
        print(f'⚠️  Could not count installed packages: {e}')
    
    health_results['dependency_health'] = dependency_health
    
    # Performance Metrics
    logger.info('⚡ Collecting performance metrics...')
    print('\\n⚡ Performance Metrics')
    print('─' * 40)
    
    performance = {
        'disk_usage': {},
        'memory_info': {},
        'python_startup_time': 0
    }
    
    # Disk usage of current directory
    try:
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk('.'):
            # Skip .git and other heavy directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            for file in files:
                try:
                    size = os.path.getsize(os.path.join(root, file))
                    total_size += size
                    file_count += 1
                except OSError:
                    pass  # Skip files we can't read
        
        performance['disk_usage'] = {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count
        }
        print(f'💾 Project size: {performance[\"disk_usage\"][\"total_size_mb\"]} MB ({file_count} files)')
    except Exception as e:
        print(f'⚠️  Could not calculate disk usage: {e}')
    
    # Python startup time
    start_time = time.time()
    try:
        result = subprocess.run([sys.executable, '-c', 'import sys; print(\"OK\")'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            startup_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            performance['python_startup_time'] = round(startup_time, 2)
            print(f'🚀 Python startup time: {performance[\"python_startup_time\"]} ms')
    except Exception as e:
        print(f'⚠️  Could not measure Python startup time: {e}')
    
    health_results['performance_metrics'] = performance
    
    # Calculate Overall Health Score
    logger.info('📊 Calculating overall health score...')
    score = 0
    max_score = 0
    
    # Environment score (40 points)
    env_points = 0
    if env_health['python_available']: env_points += 8
    if env_health['pip_available']: env_points += 5
    if env_health['uv_available']: env_points += 5
    if env_health['virtual_env']: env_points += 7
    if env_health['git_available']: env_points += 8
    if env_health['node_available']: env_points += 4
    if env_health['codomyrmex_installed']: env_points += 10
    score += env_points
    max_score += 40
    
    # Git score (30 points)
    git_points = 0
    if git_health['is_git_repo']: git_points += 10
    if git_health['has_remote']: git_points += 8
    if git_health['clean_working_tree']: git_points += 7
    if git_health['commit_count'] > 0: git_points += 5
    score += git_points
    max_score += 30
    
    # Dependency score (20 points)
    dep_points = 0
    if dependency_health.get('requirements_txt_exists') or dependency_health.get('pyproject_toml_exists'): dep_points += 10
    if dependency_health['installed_packages'] > 0: dep_points += 5
    if dependency_health.get('uv_lock_exists'): dep_points += 5
    score += dep_points
    max_score += 20
    
    # Performance score (10 points)
    perf_points = 0
    if performance.get('python_startup_time', 1000) < 500: perf_points += 5
    if performance.get('disk_usage', {}).get('total_size_mb', 1000) < 100: perf_points += 5
    score += perf_points
    max_score += 10
    
    health_percentage = round((score / max_score) * 100, 1)
    health_results['overall_score'] = health_percentage
    
    if health_percentage >= 85:
        health_results['status'] = 'excellent'
        status_emoji = '🟢'
        status_text = 'Excellent'
    elif health_percentage >= 70:
        health_results['status'] = 'good'
        status_emoji = '🟡'
        status_text = 'Good'
    elif health_percentage >= 50:
        health_results['status'] = 'fair'
        status_emoji = '🟠'
        status_text = 'Fair'
    else:
        health_results['status'] = 'poor'
        status_emoji = '🔴'
        status_text = 'Needs Attention'
    
    print('\\n' + '='*50)
    print(f'{status_emoji} OVERALL HEALTH SCORE: {health_percentage}% ({status_text})')
    print('='*50)
    
    # Save results
    with open(f'{output_dir}/health_report.json', 'w') as f:
        json.dump(health_results, f, indent=2)
    
    # Generate health report
    with open(f'{output_dir}/health_report.md', 'w') as f:
        f.write(f'# Environment Health Report\\n\\n')
        f.write(f'**Generated**: {health_results[\"timestamp\"]}\\n')
        f.write(f'**Overall Score**: {health_percentage}% ({status_text}) {status_emoji}\\n\\n')
        
        f.write('## System Information\\n\\n')
        sys_info = health_results['system_info']
        f.write(f'- **Platform**: {sys_info[\"platform\"]}\\n')
        f.write(f'- **Python**: {sys_info[\"python_version\"]}\\n')
        f.write(f'- **Architecture**: {sys_info[\"architecture\"]}\\n')
        f.write(f'- **Processor**: {sys_info[\"processor\"]}\\n\\n')
        
        f.write('## Environment Health\\n\\n')
        for check, status in env_health.items():
            emoji = '✅' if status else '❌'
            f.write(f'- {emoji} **{check.replace(\"_\", \" \").title()}**: {\"Yes\" if status else \"No\"}\\n')
        f.write('\\n')
        
        f.write('## Git Repository Health\\n\\n')
        for check, value in git_health.items():
            if isinstance(value, bool):
                emoji = '✅' if value else '❌'
                f.write(f'- {emoji} **{check.replace(\"_\", \" \").title()}**: {\"Yes\" if value else \"No\"}\\n')
            else:
                f.write(f'- **{check.replace(\"_\", \" \").title()}**: {value}\\n')
        f.write('\\n')
        
        f.write('## Performance Metrics\\n\\n')
        if 'disk_usage' in performance and performance['disk_usage']:
            f.write(f'- **Project Size**: {performance[\"disk_usage\"][\"total_size_mb\"]} MB\\n')
            f.write(f'- **File Count**: {performance[\"disk_usage\"][\"file_count\"]}\\n')
        if performance.get('python_startup_time'):
            f.write(f'- **Python Startup Time**: {performance[\"python_startup_time\"]} ms\\n')
        f.write('\\n')
        
        if health_results['recommendations']:
            f.write('## Recommendations\\n\\n')
            for i, rec in enumerate(health_results['recommendations'], 1):
                f.write(f'{i}. {rec}\\n')
            f.write('\\n')
        
        f.write('## Generated Files\\n\\n')
        f.write('- `health_report.json` - Complete health data\\n')
        f.write('- `health_report.md` - This human-readable report\\n')
    
    logger.info('📄 Generated comprehensive health report')
    logger.info('🎉 Environment Health Monitor completed successfully!')
    
    print(f'\\n📁 Health report saved to: {output_dir}')
    if health_results['recommendations']:
        print(f'\\n💡 {len(health_results[\"recommendations\"])} recommendations generated for improvement')
    
except Exception as e:
    logger.error(f'Health assessment failed: {e}')
    import traceback
    logger.error(traceback.format_exc())
    print(f'❌ Health assessment failed: {e}')
    exit(1)
"

# Phase 3: Results Summary and Recommendations
DEMO_END_TIME=$(date +%s)
DEMO_DURATION=$((DEMO_END_TIME - DEMO_START_TIME))

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🎉 HEALTH CHECK COMPLETE 🎉           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🏥 Health assessment completed in ${DEMO_DURATION} seconds${NC}"
echo -e "${GREEN}📁 Full report available at: $OUTPUT_DIR${NC}"
echo ""
echo -e "${WHITE}Generated outputs:${NC}"
echo "  • health_report.md - Human-readable health summary"
echo "  • health_report.json - Complete health assessment data"
echo ""
echo -e "${YELLOW}💡 This orchestrator demonstrated:${NC}"
echo "  ✅ Environment validation (environment_setup module)"
echo "  ✅ Git repository health assessment (git_operations integration)"
echo "  ✅ System performance monitoring and metrics collection"
echo "  ✅ Comprehensive health scoring and recommendations"
echo "  ✅ Structured logging and reporting (logging_monitoring module)"
echo ""
echo -e "${BLUE}🔗 Next steps:${NC}"
echo "  📖 Review health_report.md for detailed findings and recommendations"
echo "  🔧 Address any issues highlighted in the assessment"
echo "  📊 Use the health score to track improvements over time"
echo "  🔄 Run this monitor regularly to maintain optimal environment health"
echo ""
echo -e "${BLUE}📂 View results: open $OUTPUT_DIR${NC}"
echo -e "${BLUE}📋 Quick view: cat $OUTPUT_DIR/health_report.md${NC}"

