## 🔄 CI/CD Integration

### **GitHub Actions Integration**

```python
# github_integration.py - GitHub Actions and API integration
import aiohttp
import asyncio
from typing import Dict, List, Optional
import base64
import json

class GitHubIntegration:
    """Integration with GitHub API and Actions."""

    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Codomyrmex-Integration/1.0'
        }

    async def create_pull_request_analysis(self, pr_number: int) -> Dict:
        """Analyze pull request and create detailed analysis."""
        from codomyrmex.coding.static_analysis import analyze_diff
        from codomyrmex.agents import review_code_changes

        async with aiohttp.ClientSession() as session:
            # Get PR details
            pr_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
            async with session.get(pr_url, headers=self.headers) as response:
                pr_data = await response.json()

            # Get PR diff
            diff_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/files"
            async with session.get(diff_url, headers=self.headers) as response:
                files_data = await response.json()

            # Analyze changes
            analysis_tasks = []
            for file_data in files_data:
                if file_data['status'] in ['added', 'modified']:
                    # Get file content
                    content_url = file_data['contents_url']
                    async with session.get(content_url, headers=self.headers) as response:
                        content_data = await response.json()

                        if content_data['encoding'] == 'base64':
                            file_content = base64.b64decode(content_data['content']).decode()

                            # Schedule analysis
                            analysis_tasks.append(
                                self._analyze_file_changes(
                                    file_data['filename'],
                                    file_content,
                                    file_data.get('patch', ''),
                                    session
                                )
                            )

            # Execute all analyses in parallel
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # Compile comprehensive review
            review = {
                'pr_number': pr_number,
                'title': pr_data['title'],
                'author': pr_data['user']['login'],
                'files_analyzed': len([r for r in analysis_results if not isinstance(r, Exception)]),
                'analysis_results': [r for r in analysis_results if not isinstance(r, Exception)],
                'errors': [str(r) for r in analysis_results if isinstance(r, Exception)],
                'summary': self._generate_review_summary(analysis_results),
                'recommendations': self._generate_recommendations(analysis_results)
            }

            return review

    async def _analyze_file_changes(self, filename: str, content: str,
                                  patch: str, session: aiohttp.ClientSession) -> Dict:
        """Analyze individual file changes."""
        from codomyrmex.coding.static_analysis import analyze_code_quality
        from codomyrmex.coding.pattern_matching import find_code_patterns

        try:
            # Static analysis
            quality_analysis = analyze_code_quality(content, filename)

            # Pattern analysis
            pattern_analysis = find_code_patterns(content, filename)

            # AI review (if enabled)
            ai_review = None
            if os.getenv('ENABLE_AI_REVIEW', 'false').lower() == 'true':
                from codomyrmex.agents import review_code_changes
                ai_review = await review_code_changes(content, patch, filename)

            return {
                'filename': filename,
                'quality_score': quality_analysis.overall_score,
                'issues': quality_analysis.issues,
                'patterns': pattern_analysis.patterns_found,
                'ai_review': ai_review,
                'recommendations': self._file_recommendations(quality_analysis, pattern_analysis)
            }

        except Exception as e:
            logger.error(f"Analysis failed for {filename}: {e}")
            return {
                'filename': filename,
                'error': str(e)
            }

    async def post_review_comment(self, pr_number: int, analysis_result: Dict) -> str:
        """Post comprehensive analysis as PR comment."""
        comment_body = self._format_analysis_comment(analysis_result)

        async with aiohttp.ClientSession() as session:
            comment_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{pr_number}/comments"

            async with session.post(
                comment_url,
                headers=self.headers,
                json={'body': comment_body}
            ) as response:
                comment_data = await response.json()
                return comment_data['html_url']

    async def trigger_workflow(self, workflow_id: str, ref: str, inputs: Dict = None) -> str:
        """Trigger GitHub Actions workflow."""
        async with aiohttp.ClientSession() as session:
            workflow_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_id}/dispatches"

            payload = {
                'ref': ref,
                'inputs': inputs or {}
            }

            async with session.post(
                workflow_url,
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 204:
                    return f"Workflow {workflow_id} triggered successfully"
                else:
                    error_data = await response.json()
                    raise Exception(f"Workflow trigger failed: {error_data}")

    def _format_analysis_comment(self, analysis_result: Dict) -> str:
        """Format analysis result as markdown comment."""
        comment_parts = [
            "## 🤖 Codomyrmex Analysis Report
",
            f"**Files Analyzed**: {analysis_result['files_analyzed']}
",
            f"**Author**: @{analysis_result['author']}

"
        ]

        # Summary
        if analysis_result.get('summary'):
            comment_parts.append("### 📊 Summary
")
            for key, value in analysis_result['summary'].items():
                comment_parts.append(f"- **{key.title()}**: {value}
")
            comment_parts.append("
")

        # File-by-file analysis
        if analysis_result.get('analysis_results'):
            comment_parts.append("### 📁 File Analysis

")

            for file_result in analysis_result['analysis_results']:
                if file_result.get('error'):
                    comment_parts.append(f"❌ **{file_result['filename']}**: Analysis failed - {file_result['error']}

")
                    continue

                comment_parts.append(f"#### {file_result['filename']}
")
                comment_parts.append(f"- **Quality Score**: {file_result.get('quality_score', 'N/A')}/100
")

                if file_result.get('issues'):
                    comment_parts.append(f"- **Issues Found**: {len(file_result['issues'])}
")
                    for issue in file_result['issues'][:3]:  # Top 3 issues
                        comment_parts.append(f"  - {issue['severity']}: {issue['message']}
")

                if file_result.get('ai_review'):
                    comment_parts.append(f"- **AI Insights**: {file_result['ai_review']['summary']}
")

                comment_parts.append("
")

        # Recommendations
        if analysis_result.get('recommendations'):
            comment_parts.append("### 💡 Recommendations

")
            for rec in analysis_result['recommendations']:
                comment_parts.append(f"- {rec}
")
            comment_parts.append("
")

        comment_parts.append("---
*This analysis was generated by Codomyrmex. For more details, check the full CI/CD pipeline.*")

        return "".join(comment_parts)

# GitHub Actions workflow file
github_workflow_content = """
# .github/workflows/codomyrmex-analysis.yml
name: Codomyrmex Code Analysis

on:
  pull_request:
    types: [opened, synchronize]
  push:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      analysis_type:
        description: 'Type of analysis to run'
        required: true
        default: 'comprehensive'
        type: choice
        options:
        - comprehensive
        - static-only
        - ai-review-only

jobs:
  codomyrmex-analysis:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for comprehensive analysis

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install Codomyrmex
      run: |
        uv sync --all-extras
        # Or install from source
        # uv sync

    - name: Run Static Analysis
      if: ${{ github.event.inputs.analysis_type != 'ai-review-only' }}
      run: |
        codomyrmex analyze --path . --output-format json --output-file analysis.json

    - name: Run AI Code Review
      if: ${{ github.event.inputs.analysis_type != 'static-only' }}
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        codomyrmex ai-review --path . --pr-number ${{ github.event.number }}

    - name: Generate Visualizations
      run: |
        codomyrmex visualize --analysis-file analysis.json --output-dir ./analysis-output

    - name: Upload Analysis Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: codomyrmex-analysis-${{ github.sha }}
        path: |
          analysis.json
          analysis-output/
        retention-days: 30

    - name: Post PR Comment
      if: github.event_name == 'pull_request'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python scripts/documentation/post_analysis_comment.py \\
          --pr-number ${{ github.event.number }} \\
          --analysis-file analysis.json \\
          --repo ${{ github.repository }}

    - name: Check Quality Gates
      run: |
        python scripts/maintenance/check_quality_gates.py \\
          --analysis-file analysis.json \\
          --fail-on-error \\
          --min-quality-score 80
"""
```

