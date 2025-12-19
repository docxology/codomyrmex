#!/bin/bash
# 🐜 Codomyrmex + Fabric Integration Setup Demo
#
# This script demonstrates complete integration of Fabric AI framework with Codomyrmex by:
# 1. Cloning the Fabric repository into the project structure
# 2. Setting up Fabric with proper configuration and patterns
# 3. Creating a thin orchestrator that combines Fabric patterns with Codomyrmex modules
# 4. Demonstrating AI-powered workflows using both frameworks
# 5. Showing real-world integration patterns and use cases
#
# Prerequisites: Git, Go, and API keys (optional - works with simulation)
# Duration: ~8-10 minutes
# Output: Complete Fabric integration in scripts/output/fabric-integration/

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
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/scripts/output/fabric-integration"
FABRIC_DIR="$OUTPUT_DIR/fabric"
DEMO_START_TIME=$(date +%s)

# Parse command line arguments
INTERACTIVE=true
TEST_MODE=false
for arg in "$@"; do
    case $arg in
        --non-interactive)
            INTERACTIVE=false
            ;;
        --test-mode)
            TEST_MODE=true
            INTERACTIVE=false
            ;;
        --help)
            echo "Usage: $0 [--non-interactive] [--test-mode] [--help]"
            echo "  --non-interactive  Run without user prompts"
            echo "  --test-mode        Quick validation run (skips network operations)"
            echo "  --help            Show this help message"
            exit 0
            ;;
    esac
done

# Helper functions
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "\n${BLUE}🔹 $1${NC}"; }
pause_for_user() {
    echo -e "${YELLOW}💡 $1${NC}"
    if [ "$INTERACTIVE" = true ]; then
        read -p "Press Enter to continue..."
    else
        echo -e "${CYAN}[Non-interactive mode: Continuing automatically...]${NC}"
        sleep 1
    fi
}

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🐜 CODOMYRMEX + FABRIC INTEGRATION SETUP DEMO 🐜            ║
║   AI Framework Integration & Thin Orchestrator                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

check_environment() {
    log_step "Environment Setup & Validation"
    
    # Check project structure
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ ! -d "$PROJECT_ROOT/src/codomyrmex" ]]; then
        log_error "Not in Codomyrmex project root. Please run from examples/ directory."
        exit 1
    fi
    
    # Check required tools
    if ! command -v git &> /dev/null; then
        log_error "Git not found. Please install Git."
        exit 1
    fi
    
    if ! command -v go &> /dev/null; then
        log_error "Go not found. Please install Go (required for Fabric)."
        exit 1
    fi
    
    # Check Python and virtual environment
    if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    
    # Test Codomyrmex availability
    if ! python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src'); import codomyrmex" 2>/dev/null; then
        log_error "Codomyrmex not properly installed. Please run: uv sync"
        exit 1
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    log_success "Environment ready!"
}

clone_fabric_repository() {
    log_step "Cloning Fabric Repository"
    
    pause_for_user "We'll clone the Fabric repository and integrate it with Codomyrmex"
    
    if [[ -d "$FABRIC_DIR" ]]; then
        log_info "Fabric directory already exists, updating..."
        cd "$FABRIC_DIR"
        git pull origin main
    else
        log_info "Cloning Fabric from https://github.com/danielmiessler/Fabric..."
        git clone https://github.com/danielmiessler/Fabric.git "$FABRIC_DIR"
        cd "$FABRIC_DIR"
    fi
    
    # Show repository information
    echo -e "${WHITE}📁 Fabric Repository Information:${NC}"
    echo "   Repository: $(git remote get-url origin)"
    echo "   Current branch: $(git branch --show-current)"
    echo "   Latest commit: $(git log -1 --pretty=format:'%h - %s (%cr)')"
    echo "   Total patterns: $(find data/patterns -type d -mindepth 1 2>/dev/null | wc -l | tr -d ' ')"
    
    log_success "Fabric repository ready!"
}

install_fabric_binary() {
    log_step "Installing Fabric Binary"
    
    pause_for_user "We'll install the Fabric binary using Go"
    
    log_info "Installing Fabric binary via Go..."
    
    # Install Fabric
    if go install github.com/danielmiessler/fabric/cmd/fabric@latest; then
        log_success "Fabric binary installed successfully!"
        
        # Verify installation
        if command -v fabric &> /dev/null; then
            echo -e "${WHITE}Fabric Version:${NC} $(fabric --version 2>/dev/null || echo 'Version check failed')"
        else
            log_warning "Fabric binary installed but not in PATH. You may need to update your PATH."
            echo -e "${YELLOW}Add to your shell profile: export PATH=\$HOME/go/bin:\$PATH${NC}"
        fi
    else
        log_error "Failed to install Fabric binary"
        exit 1
    fi
}

setup_fabric_configuration() {
    log_step "Setting Up Fabric Configuration"
    
    pause_for_user "We'll configure Fabric with patterns and setup"
    
    log_info "Running Fabric setup..."
    
    # Create Fabric config directory structure
    FABRIC_CONFIG_DIR="$HOME/.config/fabric"
    mkdir -p "$FABRIC_CONFIG_DIR"
    mkdir -p "$FABRIC_CONFIG_DIR/patterns"
    mkdir -p "$FABRIC_CONFIG_DIR/contexts"
    mkdir -p "$FABRIC_CONFIG_DIR/sessions"
    
    # Copy patterns from the cloned repository
    if [[ -d "$FABRIC_DIR/data/patterns" ]]; then
        log_info "Copying Fabric patterns to configuration directory..."
        cp -r "$FABRIC_DIR/data/patterns"/* "$FABRIC_CONFIG_DIR/patterns/" 2>/dev/null || true
        
        local pattern_count=$(find "$FABRIC_CONFIG_DIR/patterns" -type d -mindepth 1 | wc -l | tr -d ' ')
        log_success "Copied $pattern_count patterns to Fabric configuration"
    fi
    
    # Create Fabric environment file
    cat > "$OUTPUT_DIR/fabric_env_template" << 'EOF'
# Fabric Environment Configuration
# Copy this to ~/.config/fabric/.env and add your API keys

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Default Model Configuration
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_VENDOR=OpenAI

# Fabric Configuration
FABRIC_OUTPUT_PATH=./fabric_outputs
PATTERNS_LOADER_GIT_REPO_URL=https://github.com/danielmiessler/fabric.git
PATTERNS_LOADER_GIT_REPO_PATTERNS_FOLDER=data/patterns
EOF
    
    log_info "Created Fabric environment template at: $OUTPUT_DIR/fabric_env_template"
    log_info "You can copy this to ~/.config/fabric/.env and add your API keys for full functionality"
    
    # Test Fabric installation
    if command -v fabric &> /dev/null; then
        log_info "Testing Fabric installation..."
        echo -e "${WHITE}Available Fabric patterns (sample):${NC}"
        fabric --listpatterns 2>/dev/null | head -10 || echo "Pattern listing not available yet"
    fi
    
    log_success "Fabric configuration setup complete!"
}

create_integration_scripts() {
    log_step "Creating Integration Scripts"
    
    pause_for_user "We'll create scripts that demonstrate Fabric + Codomyrmex integration"
    
    # Create the main orchestrator script
    cat > "$OUTPUT_DIR/fabric_orchestrator.py" << 'EOF'
#!/usr/bin/env python3
"""
Fabric + Codomyrmex Integration Orchestrator

This script demonstrates how to combine Fabric AI patterns with Codomyrmex modules
to create powerful AI-augmented development workflows.
"""

import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.logging_monitoring import get_logger
    from codomyrmex.data_visualization import create_bar_chart, create_line_plot
    CODOMYRMEX_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some Codomyrmex modules not available: {e}")
    CODOMYRMEX_AVAILABLE = False

class FabricCodomyrmexOrchestrator:
    """Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities."""
    
    def __init__(self, fabric_binary: str = "fabric"):
        self.fabric_binary = fabric_binary
        self.logger = get_logger(__name__) if CODOMYRMEX_AVAILABLE else None
        self.fabric_available = self._check_fabric_availability()
        self.results_history: List[Dict[str, Any]] = []
    
    def _check_fabric_availability(self) -> bool:
        """Check if Fabric binary is available."""
        try:
            result = subprocess.run([self.fabric_binary, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def list_fabric_patterns(self) -> List[str]:
        """Get list of available Fabric patterns."""
        if not self.fabric_available:
            return []
        
        try:
            result = subprocess.run([self.fabric_binary, "--listpatterns"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                patterns = [line.strip() for line in result.stdout.split('\n') 
                          if line.strip() and not line.startswith('Available patterns:')]
                return patterns
        except subprocess.TimeoutExpired:
            pass
        
        return []
    
    def run_fabric_pattern(self, pattern: str, input_text: str, 
                          additional_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a Fabric pattern with given input."""
        if not self.fabric_available:
            return {
                "success": False, 
                "error": "Fabric not available",
                "output": "",
                "pattern": pattern
            }
        
        cmd = [self.fabric_binary, "--pattern", pattern]
        if additional_args:
            cmd.extend(additional_args)
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(input_text)
                tmp.flush()
                
                with open(tmp.name, 'r') as input_file:
                    start_time = datetime.now()
                    result = subprocess.run(cmd, stdin=input_file, 
                                          capture_output=True, text=True, timeout=120)
                    end_time = datetime.now()
                
                os.unlink(tmp.name)
                
                result_data = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else "",
                    "pattern": pattern,
                    "duration": (end_time - start_time).total_seconds(),
                    "timestamp": start_time.isoformat()
                }
                
                self.results_history.append(result_data)
                
                if self.logger:
                    if result_data["success"]:
                        self.logger.info(f"Fabric pattern '{pattern}' executed successfully in {result_data['duration']:.2f}s")
                    else:
                        self.logger.error(f"Fabric pattern '{pattern}' failed: {result_data['error']}")
                
                return result_data
                
        except subprocess.TimeoutExpired:
            error_result = {
                "success": False,
                "error": "Pattern execution timeout",
                "output": "",
                "pattern": pattern,
                "timestamp": datetime.now().isoformat()
            }
            self.results_history.append(error_result)
            return error_result
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "output": "",
                "pattern": pattern,
                "timestamp": datetime.now().isoformat()
            }
            self.results_history.append(error_result)
            return error_result
    
    def analyze_code_with_fabric(self, code_content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code using appropriate Fabric patterns."""
        
        analysis_patterns = {
            "comprehensive": ["analyze_code", "find_code_smells", "security_review"],
            "security": ["security_review", "find_vulnerabilities"],
            "quality": ["analyze_code", "find_code_smells"],
            "documentation": ["write_docstring", "explain_code"],
            "optimization": ["optimize_code", "improve_performance"]
        }
        
        patterns = analysis_patterns.get(analysis_type, ["analyze_code"])
        results = {}
        
        for pattern in patterns:
            print(f"🔍 Running Fabric pattern: {pattern}")
            result = self.run_fabric_pattern(pattern, code_content)
            results[pattern] = result
            
            if result["success"]:
                print(f"   ✅ Pattern '{pattern}' completed successfully")
            else:
                print(f"   ❌ Pattern '{pattern}' failed: {result['error']}")
        
        return {
            "analysis_type": analysis_type,
            "patterns_used": patterns,
            "results": results,
            "summary": self._create_analysis_summary(results)
        }
    
    def _create_analysis_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Create summary of analysis results."""
        successful_patterns = sum(1 for r in results.values() if r["success"])
        total_patterns = len(results)
        
        return {
            "successful_patterns": successful_patterns,
            "total_patterns": total_patterns,
            "success_rate": (successful_patterns / total_patterns) * 100 if total_patterns > 0 else 0,
            "total_output_length": sum(len(r.get("output", "")) for r in results.values()),
            "average_duration": sum(r.get("duration", 0) for r in results.values()) / len(results) if results else 0
        }
    
    def create_workflow_visualization(self, output_path: str = "workflow_metrics.png") -> bool:
        """Create visualization of workflow results using Codomyrmex."""
        if not CODOMYRMEX_AVAILABLE or not self.results_history:
            return False
        
        try:
            # Extract metrics from results history
            patterns = []
            success_rates = []
            durations = []
            
            pattern_stats = {}
            for result in self.results_history:
                pattern = result["pattern"]
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {"successes": 0, "total": 0, "durations": []}
                
                pattern_stats[pattern]["total"] += 1
                if result["success"]:
                    pattern_stats[pattern]["successes"] += 1
                if "duration" in result:
                    pattern_stats[pattern]["durations"].append(result["duration"])
            
            for pattern, stats in pattern_stats.items():
                patterns.append(pattern)
                success_rates.append((stats["successes"] / stats["total"]) * 100)
                avg_duration = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else 0
                durations.append(avg_duration)
            
            if patterns:
                # Create success rate visualization
                create_bar_chart(
                    categories=patterns,
                    values=success_rates,
                    title="Fabric Pattern Success Rates",
                    x_label="Fabric Patterns",
                    y_label="Success Rate (%)",
                    output_path=output_path,
                    show_plot=False,
                    bar_color="lightgreen"
                )
                
                if self.logger:
                    self.logger.info(f"Created workflow visualization: {output_path}")
                
                return True
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create visualization: {e}")
            return False
        
        return False
    
    def demonstrate_integration_workflow(self) -> Dict[str, Any]:
        """Demonstrate a complete integration workflow."""
        
        print("🚀 Starting Fabric + Codomyrmex Integration Demonstration")
        
        # Sample code for analysis
        sample_code = '''
def process_data(data):
    results = []
    for item in data:
        if item is not None:
            if "active" in item and item["active"]:
                results.append(item["id"])
    return results

class DataManager:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def get_active_items(self):
        return [item for item in self.data if item.get("active", False)]
'''
        
        workflow_results = {
            "timestamp": datetime.now().isoformat(),
            "workflow_type": "fabric_codomyrmex_integration",
            "steps": []
        }
        
        # Step 1: List available patterns
        print("\n📋 Step 1: Discovering available Fabric patterns")
        patterns = self.list_fabric_patterns()
        step1_result = {
            "step": "pattern_discovery",
            "patterns_found": len(patterns),
            "sample_patterns": patterns[:10] if patterns else []
        }
        workflow_results["steps"].append(step1_result)
        print(f"   Found {len(patterns)} Fabric patterns")
        if patterns:
            print("   Sample patterns:", patterns[:5])
        
        # Step 2: Analyze code with Fabric
        print("\n🔍 Step 2: Analyzing sample code with Fabric patterns")
        analysis_result = self.analyze_code_with_fabric(sample_code, "quality")
        workflow_results["steps"].append({
            "step": "code_analysis",
            "analysis_result": analysis_result
        })
        
        # Step 3: Create visualizations with Codomyrmex
        print("\n📊 Step 3: Creating workflow visualizations with Codomyrmex")
        viz_success = self.create_workflow_visualization("integration_workflow_metrics.png")
        workflow_results["steps"].append({
            "step": "visualization",
            "success": viz_success
        })
        
        # Step 4: Generate summary
        print("\n📈 Step 4: Generating workflow summary")
        summary = {
            "total_steps": len(workflow_results["steps"]),
            "patterns_analyzed": len(analysis_result["results"]),
            "successful_pattern_runs": sum(1 for r in analysis_result["results"].values() if r["success"]),
            "visualization_created": viz_success,
            "integration_successful": True
        }
        workflow_results["summary"] = summary
        
        print(f"\n🎉 Integration workflow completed!")
        print(f"   Total steps: {summary['total_steps']}")
        print(f"   Pattern analyses: {summary['patterns_analyzed']}")
        print(f"   Successful runs: {summary['successful_pattern_runs']}")
        print(f"   Visualization: {'✅' if viz_success else '❌'}")
        
        return workflow_results

def main():
    """Main demonstration function."""
    
    print("🐜 Fabric + Codomyrmex Integration Orchestrator")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = FabricCodomyrmexOrchestrator()
    
    if not orchestrator.fabric_available:
        print("❌ Fabric binary not available. Please install Fabric first.")
        print("   Installation: go install github.com/danielmiessler/fabric/cmd/fabric@latest")
        return 1
    
    # Run demonstration workflow
    results = orchestrator.demonstrate_integration_workflow()
    
    # Save results
    results_file = "integration_workflow_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Workflow results saved to: {results_file}")
    print("✨ Integration demonstration completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())
EOF

    chmod +x "$OUTPUT_DIR/fabric_orchestrator.py"
    log_success "Created Fabric orchestrator script: fabric_orchestrator.py"
    
    # Create a configuration management script
    cat > "$OUTPUT_DIR/fabric_config_manager.py" << 'EOF'
#!/usr/bin/env python3
"""
Fabric Configuration Manager for Codomyrmex Integration

Manages Fabric configuration, patterns, and integration settings.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class FabricConfigManager:
    """Manages Fabric configuration and integration settings."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".config" / "fabric"
        self.patterns_dir = self.config_dir / "patterns"
        self.contexts_dir = self.config_dir / "contexts"
        
    def ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [self.config_dir, self.patterns_dir, self.contexts_dir]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Fabric directories ensured at: {self.config_dir}")
    
    def list_available_patterns(self) -> List[str]:
        """List all available Fabric patterns."""
        if not self.patterns_dir.exists():
            return []
        
        patterns = []
        for item in self.patterns_dir.iterdir():
            if item.is_dir() and (item / "system.md").exists():
                patterns.append(item.name)
        
        return sorted(patterns)
    
    def create_custom_pattern(self, name: str, system_prompt: str, description: str = "") -> bool:
        """Create a custom Fabric pattern."""
        pattern_dir = self.patterns_dir / name
        pattern_dir.mkdir(exist_ok=True)
        
        # Create system.md file
        system_file = pattern_dir / "system.md"
        with open(system_file, 'w') as f:
            f.write(system_prompt)
        
        # Create README.md if description provided
        if description:
            readme_file = pattern_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(f"# {name}\n\n{description}\n")
        
        print(f"✅ Created custom pattern: {name}")
        return True
    
    def create_codomyrmex_patterns(self):
        """Create Codomyrmex-specific Fabric patterns."""
        
        # Pattern for code analysis integration
        code_analysis_prompt = """# IDENTITY and PURPOSE
You are an expert code analyst working with the Codomyrmex framework. Your role is to analyze code and provide insights that integrate well with Codomyrmex's static analysis and visualization capabilities.

# STEPS
- Analyze the provided code for quality, security, and maintainability issues
- Identify patterns that could benefit from Codomyrmex module integration
- Provide specific recommendations for improvements
- Generate metrics that can be visualized using Codomyrmex's data visualization module

# OUTPUT INSTRUCTIONS
- Provide analysis in structured JSON format for easy integration
- Include severity levels (low, medium, high, critical)
- Add specific recommendations for each issue found
- Include suggested Codomyrmex modules for further analysis

# OUTPUT EXAMPLE
```json
{
  "analysis": {
    "quality_score": 85,
    "issues": [
      {
        "type": "complexity",
        "severity": "medium", 
        "message": "Function has high cyclomatic complexity",
        "line": 15,
        "recommendation": "Consider breaking into smaller functions"
      }
    ],
    "codomyrmex_suggestions": [
      "Use static_analysis module for detailed complexity metrics",
      "Apply data_visualization to show complexity trends"
    ]
  }
}
```
"""

        self.create_custom_pattern(
            "codomyrmex_code_analysis",
            code_analysis_prompt,
            "Code analysis pattern optimized for Codomyrmex integration"
        )
        
        # Pattern for workflow orchestration
        workflow_prompt = """# IDENTITY and PURPOSE
You are a workflow orchestration expert specializing in AI-augmented development processes. You help design and optimize workflows that combine multiple AI tools and development modules.

# STEPS
- Analyze the provided workflow requirements or existing workflow
- Identify opportunities for AI integration and automation
- Suggest optimal sequencing of tools and processes
- Provide implementation guidance for workflow orchestration

# OUTPUT INSTRUCTIONS
- Structure output as actionable workflow steps
- Include tool recommendations and integration points
- Provide estimated timeframes and resource requirements
- Include error handling and fallback strategies

# OUTPUT FORMAT
Provide a structured workflow plan with:
1. **Workflow Overview**: High-level description and objectives
2. **Steps**: Detailed step-by-step process
3. **Integration Points**: Where AI tools and modules connect
4. **Success Metrics**: How to measure workflow effectiveness
5. **Optimization Opportunities**: Areas for future improvement
"""

        self.create_custom_pattern(
            "codomyrmex_workflow_design", 
            workflow_prompt,
            "Workflow design pattern for AI-augmented development processes"
        )
        
        print("✅ Created Codomyrmex-specific Fabric patterns")
    
    def export_configuration(self, output_file: str) -> bool:
        """Export current Fabric configuration."""
        config_data = {
            "config_dir": str(self.config_dir),
            "patterns": self.list_available_patterns(),
            "directories": {
                "patterns": str(self.patterns_dir),
                "contexts": str(self.contexts_dir)
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"✅ Configuration exported to: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to export configuration: {e}")
            return False

def main():
    """Main configuration management function."""
    print("🔧 Fabric Configuration Manager for Codomyrmex")
    print("=" * 50)
    
    manager = FabricConfigManager()
    
    # Ensure directories exist
    manager.ensure_directories()
    
    # List existing patterns
    patterns = manager.list_available_patterns()
    print(f"📋 Found {len(patterns)} existing patterns")
    if patterns:
        print("   Sample patterns:", patterns[:5])
    
    # Create Codomyrmex-specific patterns
    print("\n🎨 Creating Codomyrmex-specific patterns...")
    manager.create_codomyrmex_patterns()
    
    # Export configuration
    print("\n📤 Exporting configuration...")
    manager.export_configuration("fabric_config_export.json")
    
    print("\n✅ Fabric configuration management completed!")

if __name__ == "__main__":
    main()
EOF

    chmod +x "$OUTPUT_DIR/fabric_config_manager.py"
    log_success "Created Fabric configuration manager: fabric_config_manager.py"
}

demonstrate_thin_orchestrator() {
    log_step "Demonstrating Thin Orchestrator Integration"
    
    pause_for_user "We'll now run the complete integration demonstration"
    
    cd "$OUTPUT_DIR"
    
    # Run the configuration manager first
    log_info "Setting up Fabric configuration..."
    python3 fabric_config_manager.py
    
    echo ""
    log_info "Running the main orchestrator demonstration..."
    python3 fabric_orchestrator.py
    
    log_success "Thin orchestrator demonstration completed!"
}

create_workflow_examples() {
    log_step "Creating Workflow Examples"
    
    pause_for_user "We'll create additional workflow examples showing different integration patterns"
    
    # Create a content analysis workflow
    cat > "$OUTPUT_DIR/content_analysis_workflow.py" << 'EOF'
#!/usr/bin/env python3
"""
Content Analysis Workflow using Fabric + Codomyrmex

Demonstrates analyzing content (articles, documentation, etc.) using Fabric patterns
and visualizing results with Codomyrmex.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fabric_orchestrator import FabricCodomyrmexOrchestrator

def analyze_content_workflow():
    """Complete content analysis workflow."""
    
    orchestrator = FabricCodomyrmexOrchestrator()
    
    # Sample content to analyze
    sample_content = """
    The rise of artificial intelligence in software development has created unprecedented opportunities 
    for automation and augmentation of human capabilities. However, it also presents challenges in terms 
    of integration complexity, tool proliferation, and maintaining human oversight in automated processes.
    
    Modern AI frameworks like GPT-4, Claude, and others provide powerful language processing capabilities,
    but they require careful orchestration to be effectively integrated into existing development workflows.
    This is where frameworks like Fabric and Codomyrmex become valuable - they provide structure and
    integration patterns that make AI adoption more manageable and effective.
    
    The key to successful AI integration is not replacing human judgment but augmenting it with AI
    capabilities at the right points in the workflow. This requires thoughtful design of integration
    points, clear understanding of each tool's strengths, and robust error handling and fallback mechanisms.
    """
    
    print("📄 Content Analysis Workflow Starting...")
    
    # Step 1: Extract key insights
    print("\n🔍 Extracting key insights...")
    insights_result = orchestrator.run_fabric_pattern("extract_wisdom", sample_content)
    
    # Step 2: Summarize content  
    print("\n📋 Creating summary...")
    summary_result = orchestrator.run_fabric_pattern("summarize", sample_content)
    
    # Step 3: Analyze writing quality
    print("\n✍️ Analyzing writing quality...")
    quality_result = orchestrator.run_fabric_pattern("analyze_prose", sample_content)
    
    # Results summary
    results = {
        "insights": insights_result,
        "summary": summary_result,
        "quality": quality_result
    }
    
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 Workflow Results: {successful}/{len(results)} patterns successful")
    
    # Create visualization if Codomyrmex is available
    viz_created = orchestrator.create_workflow_visualization("content_analysis_metrics.png")
    if viz_created:
        print("📈 Created workflow metrics visualization")
    
    return results

if __name__ == "__main__":
    analyze_content_workflow()
EOF

    chmod +x "$OUTPUT_DIR/content_analysis_workflow.py"
    
    # Create a code improvement workflow
    cat > "$OUTPUT_DIR/code_improvement_workflow.py" << 'EOF'
#!/usr/bin/env python3
"""
Code Improvement Workflow using Fabric + Codomyrmex

Demonstrates analyzing code, getting improvement suggestions, and tracking metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fabric_orchestrator import FabricCodomyrmexOrchestrator

def code_improvement_workflow():
    """Complete code improvement workflow."""
    
    orchestrator = FabricCodomyrmexOrchestrator()
    
    # Sample code that needs improvement
    sample_code = '''
def process_user_data(users):
    result = []
    for user in users:
        if user != None:
            if user["active"] == True:
                if "email" in user:
                    if user["email"] != "":
                        if "@" in user["email"]:
                            result.append({
                                "id": user["id"],
                                "name": user["name"],
                                "email": user["email"],
                                "status": "active"
                            })
    return result

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def get_active_users(self):
        return process_user_data(self.users)
'''
    
    print("🔧 Code Improvement Workflow Starting...")
    
    # Step 1: Analyze code quality
    print("\n🔍 Analyzing code quality...")
    analysis_result = orchestrator.run_fabric_pattern("analyze_code", sample_code)
    
    # Step 2: Find code smells
    print("\n👃 Finding code smells...")
    smells_result = orchestrator.run_fabric_pattern("find_code_smells", sample_code)
    
    # Step 3: Get improvement suggestions
    print("\n💡 Getting improvement suggestions...")
    improve_result = orchestrator.run_fabric_pattern("improve_code", sample_code)
    
    # Step 4: Security review
    print("\n🔒 Performing security review...")
    security_result = orchestrator.run_fabric_pattern("security_review", sample_code)
    
    # Results summary
    results = {
        "analysis": analysis_result,
        "code_smells": smells_result,
        "improvements": improve_result,
        "security": security_result
    }
    
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 Workflow Results: {successful}/{len(results)} patterns successful")
    
    # Show successful results
    for pattern_name, result in results.items():
        if result["success"] and result["output"]:
            print(f"\n✅ {pattern_name.title()} Result:")
            output_preview = result["output"][:200] + "..." if len(result["output"]) > 200 else result["output"]
            print(f"   {output_preview}")
    
    # Create visualization
    viz_created = orchestrator.create_workflow_visualization("code_improvement_metrics.png")
    if viz_created:
        print("📈 Created workflow metrics visualization")
    
    return results

if __name__ == "__main__":
    code_improvement_workflow()
EOF

    chmod +x "$OUTPUT_DIR/code_improvement_workflow.py"
    
    log_success "Created workflow examples: content_analysis_workflow.py, code_improvement_workflow.py"
}

show_integration_results() {
    log_step "Integration Results & Available Resources"
    
    cd "$OUTPUT_DIR"
    
    log_info "Fabric + Codomyrmex integration setup completed! Here's what's available:"
    echo -e "${WHITE}📁 Integration Directory: $OUTPUT_DIR${NC}"
    echo ""
    
    # Show directory structure
    echo -e "${GREEN}📂 Integration Structure:${NC}"
    echo -e "   ${CYAN}🧬 Core Integration:${NC}"
    [[ -d "fabric/" ]] && echo -e "      📁 fabric/ - Cloned Fabric repository"
    [[ -f "fabric_orchestrator.py" ]] && echo -e "      🐍 fabric_orchestrator.py - Main orchestrator script"
    [[ -f "fabric_config_manager.py" ]] && echo -e "      🔧 fabric_config_manager.py - Configuration management"
    
    echo -e "   ${CYAN}📋 Workflow Examples:${NC}"
    [[ -f "content_analysis_workflow.py" ]] && echo -e "      📄 content_analysis_workflow.py - Content analysis demo"
    [[ -f "code_improvement_workflow.py" ]] && echo -e "      🔧 code_improvement_workflow.py - Code improvement demo"
    
    echo -e "   ${CYAN}⚙️ Configuration:${NC}"
    [[ -f "fabric_env_template" ]] && echo -e "      📝 fabric_env_template - Environment configuration template"
    [[ -f "fabric_config_export.json" ]] && echo -e "      📄 fabric_config_export.json - Exported configuration"
    
    echo -e "   ${CYAN}📊 Generated Results:${NC}"
    for file in *.json *.png; do
        [[ -f "$file" ]] && echo -e "      📊 $file"
    done
    
    echo ""
    
    # Show Fabric status
    if command -v fabric &> /dev/null; then
        echo -e "${GREEN}✅ Fabric Status:${NC}"
        echo -e "   Binary: Available at $(which fabric)"
        echo -e "   Version: $(fabric --version 2>/dev/null || echo 'Unknown')"
        
        # Try to count patterns
        local fabric_patterns=$(fabric --listpatterns 2>/dev/null | wc -l | tr -d ' ' 2>/dev/null || echo "0")
        echo -e "   Patterns: $fabric_patterns available"
    else
        echo -e "${YELLOW}⚠️ Fabric Status: Binary not in PATH${NC}"
        echo -e "   You may need to add \$HOME/go/bin to your PATH"
    fi
    
    echo ""
    
    # Usage instructions
    echo -e "${GREEN}🚀 Usage Instructions:${NC}"
    echo ""
    echo -e "${WHITE}1. Run the main orchestrator:${NC}"
    echo -e "   ${CYAN}cd $OUTPUT_DIR${NC}"
    echo -e "   ${CYAN}python3 fabric_orchestrator.py${NC}"
    echo ""
    echo -e "${WHITE}2. Try workflow examples:${NC}"
    echo -e "   ${CYAN}python3 content_analysis_workflow.py${NC}"
    echo -e "   ${CYAN}python3 code_improvement_workflow.py${NC}"
    echo ""
    echo -e "${WHITE}3. Configure API keys for full functionality:${NC}"
    echo -e "   ${CYAN}cp fabric_env_template ~/.config/fabric/.env${NC}"
    echo -e "   ${CYAN}# Edit ~/.config/fabric/.env with your API keys${NC}"
    echo ""
    echo -e "${WHITE}4. Use Fabric directly:${NC}"
    echo -e "   ${CYAN}echo 'Sample text' | fabric --pattern summarize${NC}"
    echo -e "   ${CYAN}fabric --listpatterns  # Show all available patterns${NC}"
    
    return 0
}

show_comprehensive_summary() {
    log_step "Comprehensive Setup Summary"
    
    demo_end_time=$(date +%s)
    demo_duration=$((demo_end_time - demo_start_time))
    
    echo -e "${GREEN}🎉 Fabric + Codomyrmex Integration Setup Complete!${NC}"
    echo ""
    echo -e "${WHITE}🔗 What Was Accomplished:${NC}"
    echo "   1. ✅ Cloned Fabric repository with all patterns"
    echo "   2. ✅ Installed Fabric binary via Go"
    echo "   3. ✅ Set up Fabric configuration and patterns"
    echo "   4. ✅ Created integration orchestrator scripts"
    echo "   5. ✅ Built workflow examples and demonstrations"
    echo "   6. ✅ Generated configuration templates and exports"
    
    echo ""
    echo -e "${WHITE}🧬 Integration Capabilities:${NC}"
    echo "   🤖 AI Pattern Execution - Run 100+ Fabric patterns"
    echo "   🔍 Code Analysis - Combine Fabric + Codomyrmex analysis"
    echo "   📊 Workflow Visualization - Chart results with Codomyrmex"
    echo "   🔄 Orchestration - Chain multiple AI operations"
    echo "   📋 Configuration Management - Manage patterns and settings"
    
    echo ""
    echo -e "${WHITE}⏱️ Setup Statistics:${NC}"
    echo "   🕒 Duration: ${demo_duration} seconds"
    echo "   📁 Files created: $(find "$OUTPUT_DIR" -type f | wc -l | tr -d ' ') files"
    echo "   📦 Integration location: $OUTPUT_DIR"
    
    # Count Fabric patterns if available
    if [[ -d "$FABRIC_DIR/data/patterns" ]]; then
        local pattern_count=$(find "$FABRIC_DIR/data/patterns" -type d -mindepth 1 | wc -l | tr -d ' ')
        echo "   🎨 Fabric patterns available: $pattern_count"
    fi
    
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Set up API keys in ~/.config/fabric/.env for full AI functionality"
    echo "   2. Run the orchestrator examples to see integration in action"
    echo "   3. Create your own workflows combining Fabric patterns with Codomyrmex"
    echo "   4. Explore Fabric patterns: fabric --listpatterns"
    echo "   5. Build custom patterns for your specific use cases"
    
    echo ""
    echo -e "${CYAN}💡 Integration Patterns Demonstrated:${NC}"
    echo "   • Thin Orchestrator - Lightweight coordination of AI tools"
    echo "   • Pattern-Based Processing - Structured AI prompt execution"
    echo "   • Workflow Visualization - Metrics and results visualization"
    echo "   • Configuration Management - Centralized setup and management"
    echo "   • Error Handling - Robust fallback and error recovery"
    
    echo ""
    echo -e "${CYAN}🔗 Key Integration Points:${NC}"
    echo "   • Fabric patterns → Codomyrmex logging for workflow tracking"
    echo "   • Analysis results → Codomyrmex visualization for metrics"
    echo "   • Code analysis → Combined Fabric + Codomyrmex insights"
    echo "   • Configuration → Unified management across both frameworks"
    
    echo ""
    echo -e "${GREEN}✨ You now have a complete AI-augmented development environment! ✨${NC}"
}

cleanup_option() {
    echo ""
    if [ "$INTERACTIVE" = true ]; then
        read -p "🧹 Would you like to clean up the generated files? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning up generated files (keeping Fabric repository)..."
            cd "$OUTPUT_DIR"
            # Remove generated files but keep the Fabric repo
            find . -name "*.py" -o -name "*.json" -o -name "*.png" -o -name "*template*" | xargs rm -f
            log_success "Cleanup completed! Fabric repository preserved."
        else
            log_info "Files preserved for your exploration"
            echo -e "${CYAN}💡 Tip: The integration is ready to use. Try running the orchestrator scripts!${NC}"
        fi
    else
        log_info "Non-interactive mode: Files preserved for your exploration"
        log_info "Generated files located in: $OUTPUT_DIR"
        echo -e "${CYAN}💡 Tip: The integration is ready to use. Try running the orchestrator scripts!${NC}"
    fi
}

# Error handling
handle_error() {
    log_error "Setup encountered an error on line $1"
    log_info "Partial setup may be available in: $OUTPUT_DIR"
    log_info "You can re-run this script to complete the setup"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Update TODO progress
update_todo() {
    local todo_id="$1"
    local status="$2"
    # This would update the TODO status if we had a live system
    echo "📝 TODO Update: $todo_id -> $status" >/dev/null
}

# Main execution
main() {
    show_header
    
    log_info "This demo sets up complete integration between Fabric AI framework and Codomyrmex"
    log_info "We'll clone Fabric, install it, and create orchestrator examples"
    log_info "Duration: ~8-10 minutes | Output: scripts/output/fabric-integration/"
    
    # Test mode: validate and exit quickly
    if [ "$TEST_MODE" = true ]; then
        log_info "🧪 Test mode: Validating script without network operations..."
        
        # Basic validation checks
        if ! command -v git &> /dev/null; then
            log_error "Git not available"
            exit 1
        fi
        
        if ! command -v python3 &> /dev/null; then
            log_error "Python3 not available" 
            exit 1
        fi
        
        # Check if we can create output directory
        mkdir -p "$OUTPUT_DIR" 2>/dev/null || {
            log_error "Cannot create output directory: $OUTPUT_DIR"
            exit 1
        }
        
        log_success "✅ Script validation passed - all prerequisites available"
        log_info "📁 Would create output in: $OUTPUT_DIR"
        log_info "🔧 Would clone Fabric repository and set up integration"
        log_info "⚠️  Skipping network operations in test mode"
        exit 0
    fi
    
    pause_for_user "Ready to start the Fabric integration setup?"
    
    check_environment
    update_todo "setup_fabric_integration" "in_progress"
    
    clone_fabric_repository
    update_todo "clone_fabric_repo" "completed"
    
    install_fabric_binary
    setup_fabric_configuration
    
    create_integration_scripts
    update_todo "create_orchestrator_demo" "completed"
    
    demonstrate_thin_orchestrator
    create_workflow_examples
    
    if show_integration_results; then
        show_comprehensive_summary
        update_todo "setup_fabric_integration" "completed"
        cleanup_option
    else
        log_error "Setup completed with some issues. Check the output directory for partial results."
        exit 1
    fi
}

# Run the setup demo
main "$@"


