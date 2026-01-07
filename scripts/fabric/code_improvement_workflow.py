#!/usr/bin/env python3
"""
Code Improvement Workflow using Fabric + Codomyrmex

Demonstrates analyzing code and getting improvement suggestions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

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
'''
    
    print("🔧 Code Improvement Workflow Starting...")
    
    # Step 1: Analyze code quality
    print("\n🔍 Analyzing code quality...")
    analysis_result = orchestrator.run_fabric_pattern("analyze_code", sample_code)
    
    # Step 2: Find code smells
    print("\n👃 Finding code smells...")
    smells_result = orchestrator.run_fabric_pattern("find_code_smells", sample_code)
    
    # Results summary
    results = {
        "analysis": analysis_result,
        "code_smells": smells_result
    }
    
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 Workflow Results: {successful}/{len(results)} patterns successful")
    
    return results

if __name__ == "__main__":
    code_improvement_workflow()
