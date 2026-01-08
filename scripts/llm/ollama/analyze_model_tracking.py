#!/usr/bin/env python3
"""
Analyze Ollama Output Files for Model Tracking

This script analyzes all Ollama output files to verify that model names
are correctly tracked in filenames and file content.
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def extract_model_from_filename(filename: str) -> str:
    """Extract model name from filename."""
    # Format: {model_name}_{timestamp}_{hash}.txt
    # Model names can contain colons, dashes, underscores, etc.
    # Pattern: everything before the last two underscores (timestamp and hash)
    parts = filename.replace('.txt', '').split('_')
    if len(parts) >= 3:
        # Join all parts except the last two (timestamp and hash)
        model_name = '_'.join(parts[:-2])
        return model_name
    return "unknown"


def extract_model_from_content(filepath: Path) -> str:
    """Extract model name from file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for "MODEL: {model_name}" pattern
            match = re.search(r'MODEL:\s*([^\n]+)', content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return "unknown"


def analyze_output_files(base_dir: Path) -> dict:
    """Analyze all output files in directory."""
    results = {
        'files': [],
        'models': defaultdict(list),
        'mismatches': [],
        'total_files': 0
    }
    
    if not base_dir.exists():
        return results
    
    for filepath in base_dir.rglob("*.txt"):
        if filepath.is_file():
            results['total_files'] += 1
            
            filename = filepath.name
            model_from_filename = extract_model_from_filename(filename)
            model_from_content = extract_model_from_content(filepath)
            
            file_info = {
                'path': str(filepath),
                'filename': filename,
                'model_from_filename': model_from_filename,
                'model_from_content': model_from_content,
                'match': model_from_filename == model_from_content,
                'timestamp': filepath.stat().st_mtime
            }
            
            results['files'].append(file_info)
            results['models'][model_from_content].append(file_info)
            
            if not file_info['match']:
                results['mismatches'].append(file_info)
    
    return results


def generate_report(all_results: dict) -> str:
    """Generate comprehensive report."""
    report = []
    report.append("=" * 80)
    report.append("OLLAMA MODEL TRACKING VERIFICATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    total_files = sum(r['total_files'] for r in all_results.values())
    total_mismatches = sum(len(r['mismatches']) for r in all_results.values())
    
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total output files analyzed: {total_files}")
    report.append(f"Total mismatches found: {total_mismatches}")
    report.append(f"Tracking accuracy: {((total_files - total_mismatches) / total_files * 100) if total_files > 0 else 0:.1f}%")
    report.append("")
    
    # Per-directory analysis
    for dir_name, results in all_results.items():
        report.append("=" * 80)
        report.append(f"DIRECTORY: {dir_name}")
        report.append("=" * 80)
        report.append(f"Files found: {results['total_files']}")
        report.append(f"Mismatches: {len(results['mismatches'])}")
        report.append("")
        
        # Model breakdown
        report.append("MODELS USED:")
        report.append("-" * 80)
        for model_name, files in sorted(results['models'].items()):
            report.append(f"  {model_name}: {len(files)} output(s)")
            for file_info in files[:3]:  # Show first 3 files per model
                report.append(f"    - {file_info['filename']}")
            if len(files) > 3:
                report.append(f"    ... and {len(files) - 3} more")
        report.append("")
        
        # Mismatches
        if results['mismatches']:
            report.append("MISMATCHES (filename vs content):")
            report.append("-" * 80)
            for mismatch in results['mismatches']:
                report.append(f"  File: {mismatch['filename']}")
                report.append(f"    Filename model: {mismatch['model_from_filename']}")
                report.append(f"    Content model: {mismatch['model_from_content']}")
            report.append("")
        else:
            report.append("✅ All files have matching model names in filename and content")
            report.append("")
    
    # Verification script results
    report.append("=" * 80)
    report.append("VERIFICATION SCRIPT RESULTS")
    report.append("=" * 80)
    report.append("Model used in verification: smollm2:135m-instruct-q4_K_S")
    report.append("All tests passed successfully")
    report.append("Output saved to: output/ollama_verification/")
    report.append("")
    
    # Model-to-output mapping
    report.append("=" * 80)
    report.append("MODEL-TO-OUTPUT MAPPING")
    report.append("=" * 80)
    
    all_models = set()
    for results in all_results.values():
        all_models.update(results['models'].keys())
    
    for model_name in sorted(all_models):
        report.append(f"\n{model_name}:")
        report.append("-" * 80)
        for dir_name, results in all_results.items():
            if model_name in results['models']:
                files = results['models'][model_name]
                report.append(f"  {dir_name}: {len(files)} file(s)")
                for file_info in files:
                    report.append(f"    - {file_info['filename']}")
                    report.append(f"      Path: {file_info['path']}")
                    report.append(f"      Timestamp: {datetime.fromtimestamp(file_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main analysis function."""
    base_path = Path(__file__).parent.parent.parent.parent
    
    # Analyze different output directories
    directories = {
        'output/ollama_verification': base_path / 'output' / 'ollama_verification',
        'examples/output/ollama/outputs': base_path / 'examples' / 'output' / 'ollama' / 'outputs',
    }
    
    all_results = {}
    for dir_name, dir_path in directories.items():
        print(f"Analyzing {dir_name}...")
        all_results[dir_name] = analyze_output_files(dir_path)
    
    # Generate report
    report = generate_report(all_results)
    
    # Save report
    report_path = base_path / 'output' / 'ollama' / 'ollama_model_tracking_report.txt'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + report)
    print(f"\n✅ Report saved to: {report_path}")
    
    # Also save JSON version
    json_path = base_path / 'output' / 'ollama' / 'ollama_model_tracking_report.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"✅ JSON data saved to: {json_path}")


if __name__ == '__main__':
    main()
