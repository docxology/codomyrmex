#!/usr/bin/env python3
"""
Content Analysis Workflow using Fabric + Codomyrmex

Demonstrates analyzing content using Fabric patterns and visualizing results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

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
    """
    
    print("📄 Content Analysis Workflow Starting...")
    
    # Step 1: Extract key insights
    print("\n🔍 Extracting key insights...")
    insights_result = orchestrator.run_fabric_pattern("extract_wisdom", sample_content)
    
    # Step 2: Summarize content  
    print("\n📋 Creating summary...")
    summary_result = orchestrator.run_fabric_pattern("summarize", sample_content)
    
    # Results summary
    results = {
        "insights": insights_result,
        "summary": summary_result
    }
    
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 Workflow Results: {successful}/{len(results)} patterns successful")
    
    return results

if __name__ == "__main__":
    analyze_content_workflow()
