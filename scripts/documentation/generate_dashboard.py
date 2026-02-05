#!/usr/bin/env python3
"""Generate HTML dashboard from validation results.

Combines all validation outputs into a single HTML dashboard.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_dashboard(repo_root: Path, output_dir: Path = None) -> int:
    """Generate HTML dashboard from validation results."""
    print("📊 Generating validation dashboard...\n")
    
    if output_dir is None:
        output_dir = repo_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect data from validation outputs
    data = {
        'generated': datetime.now().isoformat(),
        'links': {},
        'quality': {},
        'agents': {}
    }
    
    # Load link validation results
    links_path = output_dir / "link_validation.json"
    if links_path.exists():
        with open(links_path) as f:
            link_data = json.load(f)
            data['links'] = {
                'total': len(link_data),
                'broken': len([l for l in link_data if l['status'] == 'broken']),
                'valid': len([l for l in link_data if l['status'] == 'ok']),
                'external': len([l for l in link_data if l['status'] == 'external'])
            }
    
    # Load quality results
    quality_path = output_dir / "content_quality.json"
    if quality_path.exists():
        with open(quality_path) as f:
            quality_data = json.load(f)
            scores = [q['score'] for q in quality_data]
            data['quality'] = {
                'files': len(quality_data),
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            }
    
    # Load agents validation results
    agents_path = output_dir / "agents_validation.json"
    if agents_path.exists():
        with open(agents_path) as f:
            agents_data = json.load(f)
            data['agents'] = {
                'total': len(agents_data),
                'valid': len([a for a in agents_data if a['valid']]),
                'avg_score': sum(a['score'] for a in agents_data) / len(agents_data) if agents_data else 0
            }
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Quality Dashboard</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #f5f5f5; padding: 20px; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #34495e; font-size: 1.2rem; margin-bottom: 15px; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-value {{ font-weight: bold; font-size: 1.1rem; }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .danger {{ color: #e74c3c; }}
        .timestamp {{ text-align: center; color: #7f8c8d; margin-top: 20px; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Documentation Quality Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>🔗 Link Validation</h2>
                <div class="metric">
                    <span>Total Links</span>
                    <span class="metric-value">{data['links'].get('total', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Valid Links</span>
                    <span class="metric-value success">{data['links'].get('valid', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Broken Links</span>
                    <span class="metric-value {'danger' if data['links'].get('broken', 0) > 0 else 'success'}">{data['links'].get('broken', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>External Links</span>
                    <span class="metric-value">{data['links'].get('external', 'N/A')}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📝 Content Quality</h2>
                <div class="metric">
                    <span>Files Analyzed</span>
                    <span class="metric-value">{data['quality'].get('files', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Average Score</span>
                    <span class="metric-value {'success' if data['quality'].get('avg_score', 0) >= 70 else 'warning'}">{data['quality'].get('avg_score', 0):.1f}/100</span>
                </div>
                <div class="metric">
                    <span>Lowest Score</span>
                    <span class="metric-value">{data['quality'].get('min_score', 'N/A')}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 AGENTS.md Validation</h2>
                <div class="metric">
                    <span>Total Files</span>
                    <span class="metric-value">{data['agents'].get('total', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Valid Files</span>
                    <span class="metric-value success">{data['agents'].get('valid', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Average Score</span>
                    <span class="metric-value">{data['agents'].get('avg_score', 0):.1f}/100</span>
                </div>
            </div>
        </div>
        
        <p class="timestamp">Generated: {data['generated']}</p>
    </div>
</body>
</html>'''
    
    # Write dashboard
    dashboard_path = output_dir / "dashboard.html"
    with open(dashboard_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard generated: {dashboard_path}")
    
    # Also write JSON data
    json_path = output_dir / "dashboard_data.json"
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"📄 Dashboard data: {json_path}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Generate validation dashboard")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    
    args = parser.parse_args()
    return generate_dashboard(args.repo_root, args.output)


if __name__ == "__main__":
    sys.exit(main())
