#!/usr/bin/env python3
"""
Fabric + Codomyrmex Integration Orchestrator

This script demonstrates how to combine Fabric AI patterns with Codomyrmex modules
to create powerful AI-augmented development workflows.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add Codomyrmex to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.logging_monitoring import get_logger
    from codomyrmex.llm.fabric import FabricOrchestrator as CoreFabricOrchestrator
    CODOMYRMEX_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some Codomyrmex modules not available: {e}")
    CODOMYRMEX_AVAILABLE = False

class FabricCodomyrmexOrchestrator:
    """Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities."""
    
    def __init__(self, fabric_binary: str = "fabric"):
        if CODOMYRMEX_AVAILABLE:
            self.core_orchestrator = CoreFabricOrchestrator(fabric_binary)
            self.logger = get_logger(__name__)
        else:
            self.core_orchestrator = None
            self.logger = None
    
    def list_fabric_patterns(self) -> List[str]:
        """Get list of available Fabric patterns."""
        if self.core_orchestrator:
            return self.core_orchestrator.list_patterns()
        return []
    
    def run_fabric_pattern(self, pattern: str, input_text: str, 
                          additional_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a Fabric pattern with given input."""
        if self.core_orchestrator:
            return self.core_orchestrator.fabric_manager.run_pattern(pattern, input_text, additional_args)
        return {
            "success": False,
            "error": "Fabric not available",
            "output": "",
            "pattern": pattern
        }
    
    def analyze_code_with_fabric(self, code_content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code using appropriate Fabric patterns."""
        if self.core_orchestrator:
            return self.core_orchestrator.analyze_code(code_content, analysis_type)
        return {
            "analysis_type": analysis_type,
            "patterns_used": [],
            "results": {},
            "summary": {"successful_patterns": 0, "total_patterns": 0, "success_rate": 0}
        }
    
    def create_workflow_visualization(self, output_path: str = "workflow_metrics.png") -> bool:
        """Create visualization of workflow results using Codomyrmex."""
        if self.core_orchestrator:
            return self.core_orchestrator.create_workflow_visualization(output_path)
        return False
    
    @property
    def fabric_available(self) -> bool:
        """Check if Fabric is available."""
        if self.core_orchestrator:
            return self.core_orchestrator.is_available()
        return False
    
    @property
    def results_history(self) -> List[Dict[str, Any]]:
        """Get results history."""
        if self.core_orchestrator:
            return self.core_orchestrator.fabric_manager.get_results_history()
        return []
    
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
        print("   Then run: python3 setup_fabric_env.py for interactive API configuration")
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
