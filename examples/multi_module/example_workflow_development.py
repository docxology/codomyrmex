#!/usr/bin/env python3
"""
Multi-Module Workflow: Development Pipeline

This workflow demonstrates integration of multiple modules:
- AI Code Editing: Code generation and refactoring
- Code Review: Automated code analysis and suggestions
- Git Operations: Version control and repository management
- Static Analysis: Code quality checking
- Logging Monitoring: Development activity logging
- Events: Development event tracking

This example shows a real-world scenario: AI-assisted development workflow
with automated quality checks and version control integration.
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.agents.ai_code_editing.openai_codex import generate_code_snippet
from codomyrmex.code.review import CodeReviewer, analyze_file
from codomyrmex.git_operations.git_manager import get_status, commit_changes
from codomyrmex.static_analysis.code_analyzer import analyze_file
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.events import get_event_bus, EventType, publish_event

from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, ensure_output_dir

def main():
    """Run the development workflow."""
    config = load_config(Path(__file__).parent / "config_workflow_development.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Multi-Module Development Workflow")

        # Setup logging
        setup_logging()
        logger = get_logger('workflow.development')

        # Initialize event bus
        event_bus = get_event_bus()

        # Get workflow configuration
        workflow_config = config.get('workflow', {})

        results = {
            'code_generated': 0,
            'reviews_performed': 0,
            'commits_made': 0,
            'analyses_completed': 0,
            'quality_score': 0
        }

        # Publish workflow start event
        publish_event(EventType.ANALYSIS_START, source='workflow', data={
            'workflow_name': 'development_pipeline',
            'stages': ['code_generation', 'code_review', 'static_analysis', 'git_commit']
        })

        # Create temporary workspace for development
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            print(f"Created development workspace: {workspace}")

            # Stage 1: AI Code Generation
            print("\n[1/4] AI Code Generation...")
            code_specs = workflow_config.get('code_generation', [])

            generated_files = []
            for spec in code_specs:
                try:
                    prompt = spec.get('prompt', '')
                    language = spec.get('language', 'python')
                    filename = spec.get('filename', f'generated_{len(generated_files)}.py')

                    # Generate code using AI
                    generated_code = generate_code_snippet(
                        prompt=prompt,
                        language=language,
                        model_name=spec.get('model', 'gpt-3.5-turbo')
                    )

                    if generated_code and generated_code.get('success'):
                        # Save generated code
                        file_path = workspace / filename
                        with open(file_path, 'w') as f:
                            f.write(generated_code.get('code', ''))

                        generated_files.append(str(file_path))
                        results['code_generated'] += 1

                        print(f"✓ Generated {filename} ({len(generated_code.get('code', ''))} chars)")
                        logger.info(f"Generated code file: {filename}")
                    else:
                        print(f"✗ Failed to generate code for {filename}")

                except Exception as e:
                    print(f"✗ Error in code generation: {e}")
                    logger.error(f"Code generation error: {e}")

            # Stage 2: Code Review
            print("\n[2/4] Automated Code Review...")
            review_results = []

            for file_path in generated_files:
                try:
                    file_obj = Path(file_path)
                    if file_obj.exists():
                        content = file_obj.read_text()

                        # Perform automated code review
                        review_results_list = analyze_file(str(file_obj))

                        if review_results_list:
                            issues_found = len(review_results_list)
                            # Calculate score from results
                            score = 100.0
                            for result in review_results_list:
                                if result.severity.value == "critical":
                                    score -= 10
                                elif result.severity.value == "error":
                                    score -= 5
                                elif result.severity.value == "warning":
                                    score -= 2
                            review_results.append({
                                'file': file_obj.name,
                                'issues': issues_found,
                                'score': max(0, score)
                            })

                            results['reviews_performed'] += 1
                            print(f"✓ Reviewed {file_obj.name}: {issues_found} issues found")
                        else:
                            print(f"✗ Failed to review {file_obj.name}")

                except Exception as e:
                    print(f"✗ Error reviewing file: {e}")
                    logger.error(f"Code review error: {e}")

            # Stage 3: Static Analysis
            print("\n[3/4] Static Analysis...")
            analysis_results = []

            for file_path in generated_files:
                try:
                    file_obj = Path(file_path)
                    if file_obj.exists():
                        # Run static analysis
                        analysis = analyze_file(str(file_obj))

                        if analysis:
                            analysis_results.append({
                                'file': file_obj.name,
                                'issues': len(analysis)
                            })

                            results['analyses_completed'] += 1
                            print(f"✓ Analyzed {file_obj.name}: {len(analysis)} issues found")
                        else:
                            print(f"Note: No issues found in {file_obj.name}")

                except Exception as e:
                    print(f"✗ Error analyzing file: {e}")
                    logger.error(f"Static analysis error: {e}")

            # Stage 4: Git Operations (simulated)
            print("\n[4/4] Version Control Integration...")

            # Initialize git repo (simulated)
            try:
                # In a real scenario, this would initialize a git repository
                # and commit the generated code
                if generated_files:
                    # Simulate git operations
                    git_status = get_status()  # This would check the actual repo status

                    # Simulate commit
                    commit_message = workflow_config.get('commit_message',
                                                        'AI-generated code from development workflow')
                    commit_result = commit_changes(commit_message, generated_files)

                    if commit_result:
                        results['commits_made'] = 1
                        print("✓ Code committed to version control")
                        logger.info("Code committed successfully")
                    else:
                        print("Note: Git commit simulated (would commit in real environment)")
                else:
                    print("Note: No files to commit")

            except Exception as e:
                print(f"Note: Git operations simulated: {e}")

        # Calculate overall quality score
        total_reviews = len(review_results)
        if total_reviews > 0:
            avg_score = sum(r.get('score', 0) for r in review_results) / total_reviews
            results['quality_score'] = avg_score

            if avg_score >= 8.0:
                quality_rating = "Excellent"
            elif avg_score >= 6.0:
                quality_rating = "Good"
            elif avg_score >= 4.0:
                quality_rating = "Fair"
            else:
                quality_rating = "Needs Improvement"

            results['quality_rating'] = quality_rating

        # Publish workflow complete event
        publish_event(EventType.ANALYSIS_COMPLETE, source='workflow', data={
            'workflow_name': 'development_pipeline',
            'results': results
        })

        # Final summary
        results['summary'] = {
            'workflow_stages': 4,
            'files_processed': len(generated_files),
            'total_quality_checks': (results['reviews_performed'] +
                                   results['analyses_completed']),
            'automation_level': 'high' if results['code_generated'] > 0 else 'manual'
        }

        print_section("Development Workflow Complete")
        print_results(results['summary'], "Development Pipeline Summary")

        runner.validate_results(results)
        runner.save_results(results)

        runner.complete("Development workflow completed successfully")

    except Exception as e:
        runner.error("Workflow failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

