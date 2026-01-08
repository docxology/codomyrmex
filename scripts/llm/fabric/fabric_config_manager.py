#!/usr/bin/env python3
"""
Fabric Configuration Manager for Codomyrmex Integration

Manages Fabric configuration, patterns, and integration settings.
This script provides CLI access to the core FabricConfigManager.
"""

import os
import sys
from pathlib import Path

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

try:
    from codomyrmex.llm.fabric import FabricConfigManager as CoreFabricConfigManager
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("Warning: Core Fabric module not available, using fallback implementation")

if not CORE_AVAILABLE:
    # Fallback implementation
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
    import argparse
    parser = argparse.ArgumentParser(description="Fabric Configuration Manager")
    parser.add_argument("--check", action="store_true", help="Run in check mode (verify imports and basic setup)")
    args = parser.parse_args()

    print("🔧 Fabric Configuration Manager for Codomyrmex")
    print("=" * 50)
    
    if CORE_AVAILABLE:
        manager = CoreFabricConfigManager()
    else:
        manager = FabricConfigManager()
        
    if args.check:
        print("✅ Check mode: Manager initialized successfully")
        return

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
