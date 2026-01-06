#!/usr/bin/env python3
"""
Comprehensive Workflow Demo for Codomyrmex Project Orchestration

This demo showcases how multiple Codomyrmex modules work together through
the orchestration system to perform complex analysis and improvement workflows.

Usage:
    python comprehensive_workflow_demo.py [--project-path PATH] [--output-dir DIR]
    
Example:
    python comprehensive_workflow_demo.py --project-path ./sample_project --output-dir ./results
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Codomyrmex imports (with graceful handling)
try:
    from codomyrmex.terminal_interface import TerminalFormatter, InteractiveShell
    from codomyrmex.performance import PerformanceMonitor, monitor_performance
    TERMINAL_AVAILABLE = True
except ImportError:
    print("Warning: Terminal interface not available, using basic output")
    TERMINAL_AVAILABLE = False

try:
    # Import available modules - we'll create mock versions if not available
    from codomyrmex.static_analysis.core import StaticAnalyzer
    from codomyrmex.data_visualization.visualizer import DataVisualizer  
    from codomyrmex.git_operations.git_manager import GitOperationsManager
    from codomyrmex.agents.ai_code_editing.ai_code_helpers import AICodeHelper
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
    MODULES_AVAILABLE = True
except ImportError:
    print("Warning: Some Codomyrmex modules not available - using simulation mode")
    MODULES_AVAILABLE = False


class WorkflowDemoRunner:
    """Runs comprehensive workflow demonstrations."""
    
    def __init__(self, project_path: str, output_dir: str, verbose: bool = False):
        self.project_path = Path(project_path)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # Set up logging
        self.setup_logging()
        
        # Initialize formatter and performance monitor
        self.formatter = TerminalFormatter() if TERMINAL_AVAILABLE else None
        self.perf_monitor = PerformanceMonitor() if 'PerformanceMonitor' in globals() else None
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize modules (real or mock)
        self.modules = self.initialize_modules()
        
        # Workflow results storage
        self.workflow_results = {}
    
    def setup_logging(self):
        """Set up logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.output_dir / 'workflow_demo.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_modules(self) -> Dict[str, Any]:
        """Initialize Codomyrmex modules or create mocks."""
        modules = {}
        
        if MODULES_AVAILABLE:
            try:
                modules['static_analyzer'] = StaticAnalyzer()
                modules['data_visualizer'] = DataVisualizer()
                modules['git_manager'] = GitOperationsManager()
                modules['ai_helper'] = AICodeHelper()
                modules['logger'] = LoggingManager()
                self.print_status("✅ Real Codomyrmex modules loaded", "success")
            except Exception as e:
                self.print_status(f"⚠️ Failed to load some modules: {e}", "warning")
                modules.update(self.create_mock_modules())
        else:
            modules.update(self.create_mock_modules())
            self.print_status("📦 Using simulated modules for demo", "info")
        
        return modules
    
    def create_mock_modules(self) -> Dict[str, Any]:
        """Create mock modules for demonstration purposes."""
        from unittest.mock import Mock
        
        # Mock Static Analyzer
        static_analyzer = Mock()
        static_analyzer.analyze_code_quality.return_value = {
            'overall_score': 8.2,
            'security_score': 7.5,
            'maintainability_score': 9.1,
            'complexity_score': 7.8,
            'issues': [
                {
                    'type': 'security',
                    'severity': 'medium',
                    'message': 'Potential SQL injection vulnerability',
                    'file': 'database.py',
                    'line': 45
                },
                {
                    'type': 'complexity',
                    'severity': 'low',
                    'message': 'Function has high cyclomatic complexity',
                    'file': 'utils.py',
                    'line': 123
                }
            ],
            'metrics': {
                'lines_of_code': 2500,
                'cyclomatic_complexity': 3.4,
                'maintainability_index': 78.9
            }
        }
        
        # Mock Data Visualizer
        data_visualizer = Mock()
        data_visualizer.create_bar_chart.return_value = {
            'success': True,
            'output_path': str(self.output_dir / 'quality_chart.png'),
            'chart_data': {
                'categories': ['Security', 'Maintainability', 'Complexity'],
                'values': [7.5, 9.1, 7.8]
            }
        }
        data_visualizer.create_dashboard.return_value = {
            'success': True,
            'output_path': str(self.output_dir / 'project_dashboard.html'),
            'dashboard_sections': ['overview', 'quality_metrics', 'trends', 'recommendations']
        }
        
        # Mock Git Manager
        git_manager = Mock()
        git_manager.analyze_repository.return_value = {
            'commit_count': 156,
            'contributor_count': 5,
            'branch_count': 8,
            'recent_activity': {
                'last_commit_date': '2024-01-15',
                'commits_last_month': 23
            },
            'file_changes': {
                'added': 45,
                'modified': 32,
                'deleted': 8
            },
            'hotspots': [
                {'file': 'main.py', 'changes': 18, 'complexity': 4.2},
                {'file': 'api.py', 'changes': 12, 'complexity': 3.8}
            ]
        }
        
        # Mock AI Helper
        ai_helper = Mock()
        ai_helper.generate_code_snippet.return_value = {
            'success': True,
            'generated_code': '''# AI-Generated Improvement Recommendations

## Security Enhancements
1. **SQL Injection Prevention**
   - Use parameterized queries instead of string concatenation
   - Implement input validation and sanitization
   - Consider using an ORM for database operations

## Code Quality Improvements
2. **Reduce Complexity**
   - Break down large functions into smaller, focused functions
   - Use early returns to reduce nesting levels
   - Consider extracting complex logic into separate classes

## Performance Optimizations  
3. **Caching Strategy**
   - Implement caching for frequently accessed data
   - Use connection pooling for database operations
   - Consider async operations for I/O intensive tasks

## Best Practices
4. **Documentation**
   - Add docstrings to all public functions and classes
   - Include type hints for better code maintainability
   - Create usage examples in README
''',
            'confidence': 0.89,
            'processing_time': 2.3
        }
        
        # Mock Logger
        logger = Mock()
        logger.get_performance_stats.return_value = {
            'total_operations': 1247,
            'average_response_time': 0.85,
            'error_rate': 0.02,
            'peak_memory_usage': '245 MB'
        }
        
        return {
            'static_analyzer': static_analyzer,
            'data_visualizer': data_visualizer,
            'git_manager': git_manager,
            'ai_helper': ai_helper,
            'logger': logger
        }
    
    def print_status(self, message: str, status: str = "info"):
        """Print formatted status message."""
        if self.formatter:
            if status == "success":
                print(self.formatter.success(message))
            elif status == "warning":
                print(self.formatter.warning(message))
            elif status == "error":
                print(self.formatter.error(message))
            else:
                print(self.formatter.info(message))
        else:
            # Simple formatting without TerminalFormatter
            emoji_map = {
                "success": "✅",
                "warning": "⚠️",
                "error": "❌",
                "info": "ℹ️"
            }
            print(f"{emoji_map.get(status, 'ℹ️')} {message}")
    
    def print_section_header(self, title: str, step_number: int):
        """Print formatted section header."""
        if self.formatter:
            print(f"\n{self.formatter.header(f'Step {step_number}: {title}')}")
        else:
            print(f"\n{'='*60}")
            print(f"Step {step_number}: {title}")
            print('='*60)
    
    @monitor_performance
    def run_comprehensive_analysis_workflow(self) -> Dict[str, Any]:
        """Run the comprehensive analysis workflow."""
        self.print_section_header("Comprehensive Code Analysis Workflow", 1)
        
        workflow_start_time = time.time()
        workflow_results = {}
        
        try:
            # Step 1: Static Code Analysis
            self.print_status("🔍 Running static code analysis...", "info")
            
            analysis_result = self.modules['static_analyzer'].analyze_code_quality(
                code_path=str(self.project_path),
                include_security=True,
                include_complexity=True,
                include_metrics=True
            )
            workflow_results['static_analysis'] = analysis_result
            
            self.print_status(f"✅ Code analysis complete - Quality Score: {analysis_result['overall_score']:.1f}/10", "success")
            self.print_status(f"   📊 {len(analysis_result['issues'])} issues found", "info")
            self.print_status(f"   📏 {analysis_result['metrics']['lines_of_code']:,} lines of code", "info")
            
            # Step 2: Git Repository Analysis
            self.print_status("📊 Analyzing git repository...", "info")
            
            git_result = self.modules['git_manager'].analyze_repository(
                repo_path=str(self.project_path)
            )
            workflow_results['git_analysis'] = git_result
            
            self.print_status(f"✅ Git analysis complete - {git_result['commit_count']} commits, {git_result['contributor_count']} contributors", "success")
            
            # Step 3: Create Visualizations
            self.print_status("📈 Creating data visualizations...", "info")
            
            # Quality metrics chart
            quality_chart = self.modules['data_visualizer'].create_bar_chart(
                categories=['Security', 'Maintainability', 'Complexity', 'Overall'],
                values=[
                    analysis_result['security_score'],
                    analysis_result['maintainability_score'],
                    analysis_result['complexity_score'],
                    analysis_result['overall_score']
                ],
                title="Code Quality Metrics",
                output_path=str(self.output_dir / 'quality_metrics.png')
            )
            
            # Project dashboard
            dashboard_result = self.modules['data_visualizer'].create_dashboard(
                data={
                    'code_analysis': analysis_result,
                    'git_analysis': git_result
                },
                output_path=str(self.output_dir / 'project_dashboard.html')
            )
            
            workflow_results['visualizations'] = {
                'quality_chart': quality_chart,
                'dashboard': dashboard_result
            }
            
            self.print_status(f"✅ Visualizations created:", "success")
            self.print_status(f"   📊 Quality chart: {os.path.basename(quality_chart['output_path'])}", "info")
            self.print_status(f"   📋 Dashboard: {os.path.basename(dashboard_result['output_path'])}", "info")
            
            # Step 4: AI-Powered Recommendations
            self.print_status("🤖 Generating AI-powered recommendations...", "info")
            
            ai_prompt = f"""
            Based on this code analysis, provide specific improvement recommendations:
            
            Code Quality Score: {analysis_result['overall_score']:.1f}/10
            Security Score: {analysis_result['security_score']:.1f}/10
            Issues Found: {len(analysis_result['issues'])}
            Lines of Code: {analysis_result['metrics']['lines_of_code']:,}
            
            Key Issues:
            {chr(10).join([f"- {issue['severity'].upper()}: {issue['message']}" for issue in analysis_result['issues'][:5]])}
            
            Git Activity:
            - Total commits: {git_result['commit_count']}
            - Recent activity: {git_result['recent_activity']['commits_last_month']} commits last month
            - Contributors: {git_result['contributor_count']}
            
            Provide actionable recommendations for improvement.
            """
            
            ai_recommendations = self.modules['ai_helper'].generate_code_snippet(
                prompt=ai_prompt,
                language="markdown",
                provider="openai"
            )
            workflow_results['ai_recommendations'] = ai_recommendations
            
            if ai_recommendations['success']:
                self.print_status(f"✅ AI recommendations generated (confidence: {ai_recommendations['confidence']:.1%})", "success")
                
                # Save recommendations to file
                recommendations_file = self.output_dir / 'ai_recommendations.md'
                with open(recommendations_file, 'w') as f:
                    f.write(ai_recommendations['generated_code'])
                
                self.print_status(f"   📝 Recommendations saved to: {recommendations_file.name}", "info")
            else:
                self.print_status("⚠️ AI recommendations generation failed", "warning")
            
            # Step 5: Generate Summary Report
            self.print_status("📋 Generating comprehensive report...", "info")
            
            report_data = {
                'project_path': str(self.project_path),
                'analysis_timestamp': datetime.now().isoformat(),
                'workflow_execution_time': time.time() - workflow_start_time,
                'analysis_results': analysis_result,
                'git_analysis': git_result,
                'ai_recommendations': ai_recommendations if ai_recommendations['success'] else None,
                'visualizations_created': list(workflow_results['visualizations'].keys()),
                'summary': {
                    'overall_health': 'Good' if analysis_result['overall_score'] >= 7.5 else 'Needs Improvement',
                    'priority_issues': len([i for i in analysis_result['issues'] if i['severity'] in ['high', 'critical']]),
                    'development_velocity': 'High' if git_result['recent_activity']['commits_last_month'] > 20 else 'Moderate'
                }
            }
            
            # Save detailed report
            report_file = self.output_dir / 'comprehensive_report.json'
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            workflow_results['report'] = {
                'success': True,
                'report_path': str(report_file),
                'data': report_data
            }
            
            self.print_status(f"✅ Comprehensive report saved to: {report_file.name}", "success")
            
            # Workflow summary
            execution_time = time.time() - workflow_start_time
            self.print_status(f"🎉 Comprehensive analysis workflow completed in {execution_time:.2f} seconds!", "success")
            
            return {
                'success': True,
                'execution_time': execution_time,
                'results': workflow_results,
                'summary': report_data['summary']
            }
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            self.print_status(f"❌ Workflow failed: {str(e)}", "error")
            return {
                'success': False,
                'error': str(e),
                'partial_results': workflow_results
            }
    
    @monitor_performance
    def run_ai_improvement_workflow(self) -> Dict[str, Any]:
        """Run the AI-driven code improvement workflow."""
        self.print_section_header("AI-Driven Code Improvement Workflow", 2)
        
        workflow_start_time = time.time()
        workflow_results = {}
        
        try:
            # Step 1: Initial Analysis
            self.print_status("🔍 Performing initial code analysis...", "info")
            
            initial_analysis = self.modules['static_analyzer'].analyze_code_quality(
                code_path=str(self.project_path),
                include_security=True,
                include_suggestions=True
            )
            workflow_results['initial_analysis'] = initial_analysis
            
            self.print_status(f"📊 Initial quality score: {initial_analysis['overall_score']:.1f}/10", "info")
            
            # Step 2: Generate Improvement Plan
            self.print_status("🧠 Generating AI improvement plan...", "info")
            
            improvement_prompt = f"""
            Create a detailed improvement plan for this codebase:
            
            Current State:
            - Quality Score: {initial_analysis['overall_score']:.1f}/10
            - Security Score: {initial_analysis['security_score']:.1f}/10
            - Issues: {len(initial_analysis['issues'])}
            - Lines of Code: {initial_analysis['metrics']['lines_of_code']:,}
            
            Priority Issues:
            {chr(10).join([f"- {issue['severity'].upper()}: {issue['message']} ({issue['file']}:{issue['line']})" for issue in initial_analysis['issues'][:3]])}
            
            Create a step-by-step improvement plan with:
            1. Security fixes (highest priority)
            2. Code quality improvements
            3. Performance optimizations
            4. Refactoring suggestions
            
            For each improvement, provide:
            - Specific code changes needed
            - Expected impact on quality score
            - Implementation difficulty (1-5)
            - Time estimate
            """
            
            improvement_plan = self.modules['ai_helper'].generate_code_snippet(
                prompt=improvement_prompt,
                language="markdown",
                provider="openai"
            )
            workflow_results['improvement_plan'] = improvement_plan
            
            if improvement_plan['success']:
                self.print_status(f"✅ Improvement plan generated (confidence: {improvement_plan['confidence']:.1%})", "success")
                
                # Save improvement plan
                plan_file = self.output_dir / 'improvement_plan.md'
                with open(plan_file, 'w') as f:
                    f.write(f"# AI-Generated Code Improvement Plan\n\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"**Project:** {self.project_path}\n")
                    f.write(f"**Initial Quality Score:** {initial_analysis['overall_score']:.1f}/10\n\n")
                    f.write(improvement_plan['generated_code'])
                
                self.print_status(f"   📝 Plan saved to: {plan_file.name}", "info")
            
            # Step 3: Simulate Code Improvements
            self.print_status("⚡ Simulating code improvements...", "info")
            
            # Simulate applying improvements
            improvements_applied = {
                'security_fixes': 2,
                'quality_improvements': 5,
                'performance_optimizations': 3,
                'refactoring_changes': 4,
                'files_modified': 8,
                'lines_changed': 156,
                'estimated_time_savings': '4.5 hours'
            }
            
            # Simulate improved analysis results
            improved_analysis = {
                'overall_score': min(10.0, initial_analysis['overall_score'] + 1.8),
                'security_score': min(10.0, initial_analysis['security_score'] + 2.5),
                'maintainability_score': min(10.0, initial_analysis['maintainability_score'] + 1.2),
                'complexity_score': min(10.0, initial_analysis['complexity_score'] + 0.8),
                'issues': [
                    issue for issue in initial_analysis['issues']
                    if issue['severity'] not in ['high', 'critical']  # High/critical issues resolved
                ],
                'metrics': {
                    'lines_of_code': initial_analysis['metrics']['lines_of_code'] + 45,  # Added documentation
                    'cyclomatic_complexity': max(1.0, initial_analysis['metrics']['cyclomatic_complexity'] - 0.4),
                    'maintainability_index': min(100.0, initial_analysis['metrics']['maintainability_index'] + 8.2)
                }
            }
            
            workflow_results['improvements_applied'] = improvements_applied
            workflow_results['improved_analysis'] = improved_analysis
            
            # Display improvement results
            improvement_delta = improved_analysis['overall_score'] - initial_analysis['overall_score']
            security_delta = improved_analysis['security_score'] - initial_analysis['security_score']
            issues_resolved = len(initial_analysis['issues']) - len(improved_analysis['issues'])
            
            self.print_status("✅ Code improvements applied:", "success")
            self.print_status(f"   📈 Quality score: {initial_analysis['overall_score']:.1f} → {improved_analysis['overall_score']:.1f} (+{improvement_delta:.1f})", "info")
            self.print_status(f"   🔒 Security score: {initial_analysis['security_score']:.1f} → {improved_analysis['security_score']:.1f} (+{security_delta:.1f})", "info")
            self.print_status(f"   🐛 Issues resolved: {issues_resolved}", "info")
            self.print_status(f"   📁 Files modified: {improvements_applied['files_modified']}", "info")
            self.print_status(f"   ⏰ Estimated time saved: {improvements_applied['estimated_time_savings']}", "info")
            
            # Step 4: Create Before/After Comparison
            self.print_status("📊 Creating before/after comparison...", "info")
            
            comparison_chart = self.modules['data_visualizer'].create_bar_chart(
                categories=['Overall', 'Security', 'Maintainability', 'Complexity'],
                values=[
                    [initial_analysis['overall_score'], improved_analysis['overall_score']],
                    [initial_analysis['security_score'], improved_analysis['security_score']],
                    [initial_analysis['maintainability_score'], improved_analysis['maintainability_score']],
                    [initial_analysis['complexity_score'], improved_analysis['complexity_score']]
                ],
                series_labels=['Before', 'After'],
                title="Code Quality Improvements",
                output_path=str(self.output_dir / 'improvement_comparison.png')
            )
            
            workflow_results['comparison_chart'] = comparison_chart
            
            self.print_status(f"✅ Comparison chart created: {os.path.basename(comparison_chart['output_path'])}", "success")
            
            # Step 5: Generate Improvement Report
            self.print_status("📋 Generating improvement report...", "info")
            
            improvement_report = {
                'project_path': str(self.project_path),
                'improvement_timestamp': datetime.now().isoformat(),
                'workflow_execution_time': time.time() - workflow_start_time,
                'before_analysis': initial_analysis,
                'after_analysis': improved_analysis,
                'improvements_applied': improvements_applied,
                'improvement_plan': improvement_plan if improvement_plan['success'] else None,
                'metrics': {
                    'quality_improvement': improvement_delta,
                    'security_improvement': security_delta,
                    'issues_resolved': issues_resolved,
                    'roi_estimate': f"${improvements_applied['estimated_time_savings']} × $75/hour = $337.50"
                },
                'recommendations': [
                    'Continue monitoring code quality with automated tools',
                    'Implement the remaining low-priority improvements',
                    'Set up pre-commit hooks to maintain code quality',
                    'Schedule regular AI-assisted code reviews'
                ]
            }
            
            # Save improvement report
            report_file = self.output_dir / 'improvement_report.json'
            with open(report_file, 'w') as f:
                json.dump(improvement_report, f, indent=2, default=str)
            
            workflow_results['improvement_report'] = improvement_report
            
            self.print_status(f"✅ Improvement report saved to: {report_file.name}", "success")
            
            # Workflow summary
            execution_time = time.time() - workflow_start_time
            self.print_status(f"🎉 AI improvement workflow completed in {execution_time:.2f} seconds!", "success")
            self.print_status(f"   📈 Net quality improvement: +{improvement_delta:.1f} points", "success")
            self.print_status(f"   💰 Estimated value: {improvement_report['metrics']['roi_estimate']}", "info")
            
            return {
                'success': True,
                'execution_time': execution_time,
                'results': workflow_results,
                'improvement_summary': improvement_report['metrics']
            }
            
        except Exception as e:
            self.logger.error(f"AI improvement workflow failed: {str(e)}")
            self.print_status(f"❌ AI improvement workflow failed: {str(e)}", "error")
            return {
                'success': False,
                'error': str(e),
                'partial_results': workflow_results
            }
    
    def run_performance_monitoring_demo(self) -> Dict[str, Any]:
        """Demonstrate performance monitoring across workflows."""
        self.print_section_header("Performance Monitoring Demo", 3)
        
        if not self.perf_monitor:
            self.print_status("⚠️ Performance monitor not available - skipping demo", "warning")
            return {'success': False, 'reason': 'Performance monitor not available'}
        
        # Start performance monitoring
        self.perf_monitor.start_monitoring()
        
        # Simulate some operations
        operations = [
            ('file_analysis', 2.3),
            ('data_processing', 1.8),
            ('visualization_creation', 3.2),
            ('ai_inference', 4.1),
            ('report_generation', 1.5)
        ]
        
        self.print_status("📊 Running performance monitoring demo...", "info")
        
        for operation_name, duration in operations:
            self.print_status(f"   ⏱️ Executing {operation_name}...", "info")
            
            # Simulate operation
            start_time = time.time()
            time.sleep(duration / 10)  # Scale down for demo
            end_time = time.time()
            
            # Record performance data
            if hasattr(self.perf_monitor, 'record_operation'):
                self.perf_monitor.record_operation(
                    operation_name,
                    end_time - start_time,
                    {'status': 'success'}
                )
            
            self.print_status(f"     ✅ {operation_name} completed in {end_time - start_time:.3f}s", "success")
        
        # Get performance statistics
        if hasattr(self.perf_monitor, 'get_statistics'):
            stats = self.perf_monitor.get_statistics()
            
            self.print_status("📊 Performance Statistics:", "info")
            self.print_status(f"   🔢 Total operations: {stats.get('total_operations', len(operations))}", "info")
            self.print_status(f"   ⏱️ Average execution time: {stats.get('average_time', 0.5):.3f}s", "info")
            self.print_status(f"   🚀 Operations per second: {stats.get('ops_per_second', 2.0):.1f}", "info")
            self.print_status(f"   💾 Peak memory usage: {stats.get('peak_memory', '45 MB')}", "info")
            
            return {
                'success': True,
                'statistics': stats,
                'operations_completed': len(operations)
            }
        
        return {
            'success': True,
            'message': 'Performance monitoring demo completed',
            'operations_completed': len(operations)
        }
    
    def generate_final_summary(self, workflow_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a final summary of all workflow executions."""
        self.print_section_header("Final Summary", 4)
        
        # Calculate summary statistics
        successful_workflows = [w for w in workflow_results if w.get('success', False)]
        total_execution_time = sum(w.get('execution_time', 0) for w in workflow_results)
        
        summary = {
            'demo_timestamp': datetime.now().isoformat(),
            'project_analyzed': str(self.project_path),
            'output_directory': str(self.output_dir),
            'workflows_executed': len(workflow_results),
            'successful_workflows': len(successful_workflows),
            'total_execution_time': total_execution_time,
            'files_created': list(self.output_dir.glob('*')),
            'key_achievements': []
        }
        
        # Extract key achievements
        for workflow in successful_workflows:
            if 'results' in workflow:
                results = workflow['results']
                if 'static_analysis' in results:
                    analysis = results['static_analysis']
                    summary['key_achievements'].append(
                        f"Code analysis completed - Quality score: {analysis['overall_score']:.1f}/10"
                    )
                if 'improvement_report' in results:
                    improvement = workflow['improvement_summary']
                    summary['key_achievements'].append(
                        f"Code improvements applied - Quality improved by {improvement['quality_improvement']:.1f} points"
                    )
        
        # Print summary
        self.print_status("🎉 Comprehensive Workflow Demo Summary:", "success")
        self.print_status(f"   📁 Project: {summary['project_analyzed']}", "info")
        self.print_status(f"   ⏱️ Total execution time: {total_execution_time:.2f} seconds", "info")
        self.print_status(f"   ✅ Successful workflows: {len(successful_workflows)}/{len(workflow_results)}", "success")
        self.print_status(f"   📄 Files created: {len(summary['files_created'])}", "info")
        
        self.print_status("\n🏆 Key Achievements:", "success")
        for achievement in summary['key_achievements']:
            self.print_status(f"   • {achievement}", "info")
        
        # List created files
        if summary['files_created']:
            self.print_status(f"\n📄 Generated Files in {self.output_dir}:", "info")
            for file_path in sorted(summary['files_created']):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    self.print_status(f"   • {file_path.name} ({file_size:,} bytes)", "info")
        
        # Save summary
        summary_file = self.output_dir / 'demo_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.print_status(f"\n📋 Demo summary saved to: {summary_file.name}", "success")
        
        return summary


def create_sample_project(project_path: Path) -> None:
    """Create a sample project for demonstration if it doesn't exist."""
    if project_path.exists() and any(project_path.iterdir()):
        return  # Project already exists with content
    
    print(f"📁 Creating sample project at {project_path}")
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create a sample Python file
    main_py = project_path / "main.py"
    main_py.write_text('''"""
Sample Python project for Codomyrmex demonstration.
"""
import os
import sys
from typing import List, Dict, Optional
import sqlite3  # Potential security issue


class DataProcessor:
    """Process data with various methods."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection = None
    
    def connect(self) -> None:
        """Connect to database."""
        self.connection = sqlite3.connect(self.database_path)
    
    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute SQL query - potential security vulnerability."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        
        # Security issue: Direct SQL execution without parameterization
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)  # Vulnerable to SQL injection
        
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        return [dict(zip(columns, row)) for row in results]
    
    def process_data(self, data: List[Dict]) -> Dict:
        """Process data with complex logic."""
        # High complexity function that could be refactored
        result = {
            'processed_items': 0,
            'errors': [],
            'summary': {}
        }
        
        for item in data:
            try:
                if isinstance(item, dict):
                    # Nested complexity
                    if 'value' in item:
                        if item['value'] is not None:
                            if isinstance(item['value'], (int, float)):
                                if item['value'] > 0:
                                    result['processed_items'] += 1
                                    if 'positive' not in result['summary']:
                                        result['summary']['positive'] = 0
                                    result['summary']['positive'] += item['value']
                                elif item['value'] < 0:
                                    if 'negative' not in result['summary']:
                                        result['summary']['negative'] = 0
                                    result['summary']['negative'] += item['value']
                                else:
                                    if 'zero' not in result['summary']:
                                        result['summary']['zero'] = 0
                                    result['summary']['zero'] += 1
                            else:
                                result['errors'].append(f"Invalid value type: {type(item['value'])}")
                        else:
                            result['errors'].append("Null value encountered")
                    else:
                        result['errors'].append("Missing 'value' key")
                else:
                    result['errors'].append(f"Invalid item type: {type(item)}")
            except Exception as e:
                result['errors'].append(f"Processing error: {str(e)}")
        
        return result


def unsafe_eval_function(expression: str):
    """Unsafe function that uses eval - security vulnerability."""
    try:
        return eval(expression)  # Major security vulnerability
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Main function with hardcoded values."""
    # Hardcoded database path - not ideal
    db_path = "/tmp/sample.db"
    
    processor = DataProcessor(db_path)
    
    # Sample data processing
    sample_data = [
        {"value": 10},
        {"value": -5},
        {"value": 0},
        {"value": "invalid"},
        {"missing": "value"}
    ]
    
    result = processor.process_data(sample_data)
    print(f"Processed {result['processed_items']} items")
    
    if result['errors']:
        print(f"Errors encountered: {len(result['errors'])}")
        for error in result['errors'][:3]:  # Show first 3 errors
            print(f"  - {error}")
    
    # Demonstrate unsafe eval usage
    user_input = "2 + 2"  # In reality, this could be malicious
    eval_result = unsafe_eval_function(user_input)
    print(f"Eval result: {eval_result}")


if __name__ == "__main__":
    main()
''')
    
    # Create requirements.txt
    requirements_txt = project_path / "requirements.txt"
    requirements_txt.write_text('''pandas>=1.3.0
numpy>=1.20.0
requests>=2.25.0
matplotlib>=3.3.0
''')
    
    # Create README.md
    readme_md = project_path / "README.md"
    readme_md.write_text('''# Sample Project for Codomyrmex Demo

This is a sample Python project created to demonstrate the Codomyrmex Project Orchestration capabilities.

## Features

- Data processing with database connectivity
- SQL query execution (with some security vulnerabilities for demo purposes)
- Complex data processing logic
- Error handling

## Known Issues (for demonstration)

- SQL injection vulnerabilities in query execution
- Use of eval() function - security risk
- High cyclomatic complexity in data processing
- Hardcoded values
- Missing type hints in some functions

## Usage

```python
from main import DataProcessor

processor = DataProcessor("/path/to/database.db")
result = processor.process_data(sample_data)
```

This project is intentionally created with some code quality and security issues to demonstrate Codomyrmex's analysis and improvement capabilities.
''')
    
    print(f"✅ Sample project created at {project_path}")


def main():
    """Main function to run the comprehensive workflow demo."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Workflow Demo for Codomyrmex Project Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python comprehensive_workflow_demo.py
  python comprehensive_workflow_demo.py --project-path ./my_project --output-dir ./demo_results
  python comprehensive_workflow_demo.py --verbose --create-sample-project
        """
    )
    
    parser.add_argument(
        '--project-path',
        default='./sample_project_for_demo',
        help='Path to the project to analyze (default: ./sample_project_for_demo)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./orchestration_demo_results',
        help='Directory to store demo results (default: ./orchestration_demo_results)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--create-sample-project',
        action='store_true',
        help='Create a sample project if the project path doesn\'t exist'
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    output_dir = Path(args.output_dir)
    
    # Create sample project if requested or if project doesn't exist
    if args.create_sample_project or not project_path.exists():
        create_sample_project(project_path)
    
    # Verify project exists
    if not project_path.exists():
        print(f"❌ Project path does not exist: {project_path}")
        print("   Use --create-sample-project to create a sample project for demonstration")
        sys.exit(1)
    
    # Initialize demo runner
    print("🚀 Starting Codomyrmex Comprehensive Workflow Demo")
    print("=" * 60)
    print(f"Project: {project_path}")
    print(f"Output: {output_dir}")
    print(f"Verbose: {args.verbose}")
    print("=" * 60)
    
    demo_runner = WorkflowDemoRunner(
        project_path=str(project_path),
        output_dir=str(output_dir),
        verbose=args.verbose
    )
    
    # Run workflows
    workflow_results = []
    
    try:
        # 1. Comprehensive Analysis Workflow
        analysis_result = demo_runner.run_comprehensive_analysis_workflow()
        workflow_results.append(analysis_result)
        
        # 2. AI-Driven Improvement Workflow
        improvement_result = demo_runner.run_ai_improvement_workflow()
        workflow_results.append(improvement_result)
        
        # 3. Performance Monitoring Demo
        performance_result = demo_runner.run_performance_monitoring_demo()
        workflow_results.append(performance_result)
        
        # 4. Generate Final Summary
        final_summary = demo_runner.generate_final_summary(workflow_results)
        
        # Print final status
        successful_workflows = len([w for w in workflow_results if w.get('success', False)])
        total_workflows = len(workflow_results)
        
        if successful_workflows == total_workflows:
            demo_runner.print_status(f"🎉 All workflows completed successfully! ({successful_workflows}/{total_workflows})", "success")
            sys.exit(0)
        else:
            demo_runner.print_status(f"⚠️ Some workflows had issues ({successful_workflows}/{total_workflows} successful)", "warning")
            sys.exit(1)
            
    except KeyboardInterrupt:
        demo_runner.print_status("🛑 Demo interrupted by user", "warning")
        sys.exit(130)
    except Exception as e:
        demo_runner.print_status(f"❌ Demo failed with unexpected error: {str(e)}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
