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
