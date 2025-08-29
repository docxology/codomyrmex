#!/usr/bin/env python3
"""
Codomyrmex Orchestrator Demo Script

This script demonstrates the key features of the Codomyrmex orchestrator
system including system discovery, capability scanning, and interactive
exploration.
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def demo_header(title: str):
    """Print a demo section header."""
    print(f"\n{'='*70}")
    print(f"  🎬 DEMO: {title.upper()}")
    print(f"{'='*70}")


def demo_pause(message: str = "Press Enter to continue..."):
    """Pause for user interaction."""
    input(f"\n💡 {message}")


def demo_system_discovery():
    """Demonstrate system discovery capabilities."""
    demo_header("System Discovery")
    
    print("🔍 The Codomyrmex orchestrator can automatically discover all modules,")
    print("   functions, classes, and capabilities across the entire ecosystem!")
    
    demo_pause("Let's discover the ecosystem...")
    
    try:
        from codomyrmex.system_discovery import SystemDiscovery
        
        print("\n🚀 Initializing System Discovery...")
        discovery = SystemDiscovery()
        
        print("📡 Scanning all modules...")
        discovery._discover_modules()
        
        print(f"\n✅ Discovery Complete!")
        print(f"   📦 Found {len(discovery.modules)} modules")
        
        # Show summary
        importable = sum(1 for m in discovery.modules.values() if m.is_importable)
        tested = sum(1 for m in discovery.modules.values() if m.has_tests)
        documented = sum(1 for m in discovery.modules.values() if m.has_docs)
        total_caps = sum(len(m.capabilities) for m in discovery.modules.values())
        
        print(f"   ✅ {importable}/{len(discovery.modules)} modules are importable")
        print(f"   🧪 {tested}/{len(discovery.modules)} modules have tests")
        print(f"   📚 {documented}/{len(discovery.modules)} modules have documentation") 
        print(f"   🔧 {total_caps} total capabilities discovered")
        
        print(f"\n📋 Module Summary:")
        for name, info in list(discovery.modules.items())[:5]:  # Show first 5
            status = "✅" if info.is_importable else "❌"
            print(f"   {status} {name:<20} ({len(info.capabilities):2d} capabilities)")
        
        if len(discovery.modules) > 5:
            print(f"   ... and {len(discovery.modules) - 5} more modules!")
        
        return discovery
        
    except Exception as e:
        print(f"❌ Error in system discovery: {e}")
        return None


def demo_capability_analysis(discovery):
    """Demonstrate capability analysis."""
    demo_header("Capability Analysis")
    
    print("🔬 Let's analyze the discovered capabilities in detail...")
    
    if not discovery or not discovery.modules:
        print("❌ No discovery data available")
        return
    
    demo_pause("Analyzing capabilities...")
    
    # Find a module with interesting capabilities
    interesting_modules = [
        (name, info) for name, info in discovery.modules.items() 
        if len(info.capabilities) > 5
    ]
    
    if interesting_modules:
        module_name, module_info = interesting_modules[0]
        
        print(f"\n🔍 Deep dive into: {module_name}")
        print(f"📍 Location: {module_info.path}")
        print(f"📝 Description: {module_info.description[:100]}...")
        print(f"🔧 Capabilities: {len(module_info.capabilities)}")
        
        # Group capabilities by type
        by_type = {}
        for cap in module_info.capabilities:
            if cap.type not in by_type:
                by_type[cap.type] = []
            by_type[cap.type].append(cap)
        
        print(f"\n🛠️  Capability Breakdown:")
        for cap_type, caps in by_type.items():
            print(f"   📂 {cap_type.title()}s: {len(caps)}")
            
            # Show a few examples
            for cap in caps[:3]:
                print(f"      • {cap.name}")
                if cap.docstring and cap.docstring != "No docstring":
                    doc_preview = cap.docstring.split('\n')[0][:60]
                    print(f"        💬 {doc_preview}...")
            
            if len(caps) > 3:
                print(f"      ... and {len(caps) - 3} more")
    else:
        print("🤷 No modules with substantial capabilities found")


def demo_interactive_features():
    """Demonstrate interactive shell features."""
    demo_header("Interactive Shell Features")
    
    print("🎮 The Codomyrmex Interactive Shell provides an engaging way to")
    print("   explore the ecosystem like an epistemic forager in a vast nest!")
    
    demo_pause("Let's see the interactive features...")
    
    try:
        from codomyrmex.terminal_interface import InteractiveShell
        
        print("\n🐜 Interactive Shell Commands Available:")
        
        commands = [
            ("explore", "Overview of all modules in the nest"),
            ("explore <module>", "Deep dive into specific module"), 
            ("capabilities", "Show all discovered capabilities"),
            ("forage", "Random discovery of interesting capabilities"),
            ("forage <search>", "Search capabilities by name"),
            ("demo", "Run live demonstrations"),
            ("status", "System health check"),
            ("dive <module>", "Detailed capability inspection"),
            ("export", "Generate inventory report"),
        ]
        
        for cmd, desc in commands:
            print(f"   🔧 {cmd:<20} - {desc}")
        
        print(f"\n🌟 Example foraging session:")
        print(f"   🐜 codomyrmex> explore")
        print(f"   🗺️  Shows overview of all 14 discovered modules")
        print(f"   ")
        print(f"   🐜 codomyrmex> forage visualization")
        print(f"   🔍 Finds all capabilities related to 'visualization'")
        print(f"   ")
        print(f"   🐜 codomyrmex> demo data_visualization") 
        print(f"   🚀 Runs live demo creating plots and charts")
        print(f"   ")
        print(f"   🐜 codomyrmex> dive ai_code_editing")
        print(f"   🤿 Shows detailed analysis of AI code editing capabilities")
        
        print(f"\n💡 The shell makes exploration fun and accessible!")
        print(f"   You're not just browsing code - you're foraging for knowledge!")
        
    except Exception as e:
        print(f"❌ Error demonstrating interactive features: {e}")


def demo_status_reporting():
    """Demonstrate status reporting capabilities.""" 
    demo_header("Status Reporting")
    
    print("📊 The orchestrator provides comprehensive system health monitoring")
    print("   and detailed status reports!")
    
    demo_pause("Generating status report...")
    
    try:
        from codomyrmex.system_discovery.status_reporter import StatusReporter
        
        reporter = StatusReporter()
        
        print("\n🏥 System Health Check:")
        
        # Check key components
        env_status = reporter.check_python_environment()
        print(f"   🐍 Python {env_status['version_string']}")
        print(f"   📦 Virtual Environment: {'✅' if env_status['virtual_env'] else '❌'}")
        
        project_status = reporter.check_project_structure()
        print(f"   📂 Project Structure: {'✅' if project_status['src_exists'] else '❌'}")
        print(f"   🧪 Testing Directory: {'✅' if project_status['testing_dir'] else '❌'}")
        
        deps_status = reporter.check_dependencies()
        success_rate = deps_status['success_rate']
        print(f"   📦 Dependencies: {deps_status['available_count']}/{deps_status['total_count']} ({success_rate:.1f}%)")
        
        git_status = reporter.check_git_status()
        print(f"   🌐 Git Repository: {'✅' if git_status['is_git_repo'] else '❌'}")
        
        tools_status = reporter.check_external_tools()
        available_tools = sum(tools_status.values())
        print(f"   🔧 External Tools: {available_tools}/{len(tools_status)} available")
        
        # Overall health
        checks = [
            env_status['virtual_env'],
            project_status['src_exists'], 
            success_rate > 80,
            git_status['is_git_repo'],
        ]
        health_score = (sum(checks) / len(checks)) * 100
        
        if health_score >= 90:
            health_emoji = "🎉"
            health_text = "Excellent"
        elif health_score >= 70:
            health_emoji = "✅" 
            health_text = "Good"
        else:
            health_emoji = "⚠️"
            health_text = "Needs Attention"
        
        print(f"\n{health_emoji} Overall Health: {health_text} ({health_score:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error in status reporting: {e}")


def demo_exports_and_reports():
    """Demonstrate export and reporting capabilities."""
    demo_header("Exports and Reports")
    
    print("📋 The orchestrator can generate comprehensive reports in JSON format")
    print("   for documentation, analysis, and integration with other tools!")
    
    demo_pause("Let's see what can be exported...")
    
    print("\n📊 Available Exports:")
    
    exports = [
        ("System Inventory", "codomyrmex_inventory.json", "Complete module and capability catalog"),
        ("Status Report", "codomyrmex_status_report_TIMESTAMP.json", "System health and diagnostics"),
        ("Capabilities Report", "codomyrmex_capabilities_TIMESTAMP.json", "Deep technical analysis"),
    ]
    
    for name, filename, description in exports:
        print(f"   📄 {name}")
        print(f"      📁 File: {filename}")
        print(f"      📝 Content: {description}")
        print()
    
    print("💡 These reports can be used for:")
    print("   • 📊 Project documentation and architecture reviews")
    print("   • 🔍 Code analysis and dependency mapping") 
    print("   • 📈 Progress tracking and capability evolution")
    print("   • 🤖 Integration with CI/CD and other automation tools")
    print("   • 📚 Onboarding new team members")


def main():
    """Run the complete orchestrator demonstration."""
    print("🎬" + "="*68 + "🎬")
    print("  🐜 CODOMYRMEX ORCHESTRATOR DEMONSTRATION 🐜")
    print("  The Epistemic Forager's Guide to Code Ecosystem Discovery")  
    print("🎬" + "="*68 + "🎬")
    
    print("\n🌟 Welcome to the Codomyrmex Orchestrator Demo!")
    print("   This demo will show you how to explore, discover, and analyze")
    print("   the entire Codomyrmex ecosystem like an epistemic forager!")
    
    demo_pause("Ready to start the demo?")
    
    # Run demo sections
    discovery = demo_system_discovery()
    
    demo_pause("Continue to capability analysis?")
    demo_capability_analysis(discovery)
    
    demo_pause("Continue to interactive features?")
    demo_interactive_features()
    
    demo_pause("Continue to status reporting?")
    demo_status_reporting()
    
    demo_pause("Continue to exports and reports?")  
    demo_exports_and_reports()
    
    # Final summary
    demo_header("Demo Complete!")
    
    print("🎉 Congratulations! You've seen the power of the Codomyrmex Orchestrator!")
    print("\n🚀 Next Steps:")
    print("   1. Run './start_here.sh' to launch the full orchestrator")
    print("   2. Choose option 7 for the Interactive Shell experience")
    print("   3. Use 'explore' and 'forage' to discover the ecosystem")
    print("   4. Try 'demo' to see working examples")
    print("   5. Use 'export' to generate comprehensive reports")
    
    print("\n🐜 Remember: You're not just using a tool - you're becoming an")
    print("   epistemic forager, exploring a vast and structured knowledge nest!")
    
    print("\n✨ Happy foraging! ✨")


if __name__ == "__main__":
    main()
