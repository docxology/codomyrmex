#!/usr/bin/env python3
"""Documentation Audit Script.

Scans the repository for required documentation files (README.md, AGENTS.md, SPEC.md, PAI.md)
and reports on coverage and quality (stub detection).
"""

from pathlib import Path
from typing import Dict, List, Any
import os

from codomyrmex.utils import ScriptBase, ScriptConfig

class DocumentationAudit(ScriptBase):
    def __init__(self):
        super().__init__(
            name="doc_audit",
            description="Audits repository documentation coverage",
            version="1.0.0"
        )
        self.required_files = ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"]
        self.stub_threshold = 500  # Bytes

    def add_arguments(self, parser):
        parser.add_argument(
            "--target", type=Path, default=Path.cwd() / "src/codomyrmex",
            help="Target directory to scan"
        )
        parser.add_argument(
            "--fix", action="store_true",
            help="Attempt to create missing files (Dry run recommended first)"
        )

    def scan_directory(self, path: Path) -> Dict[str, Any]:
        """Scan a single directory for documentation status."""
        stats = {
            "path": str(path.relative_to(self.root_dir)),
            "files": {},
            "missing": [],
            "stubs": []
        }
        
        for filename in self.required_files:
            file_path = path / filename
            if file_path.exists():
                size = file_path.stat().st_size
                stats["files"][filename] = size
                if size < self.stub_threshold:
                    stats["stubs"].append(filename)
            else:
                stats["missing"].append(filename)
                
        return stats

    def calculate_score(self, stats: Dict[str, Any]) -> float:
        """Calculate a compliance score (0-100)."""
        total = len(self.required_files)
        present = total - len(stats["missing"])
        non_stubs = present - len(stats["stubs"])
        
        # 50% for presence, 50% for quality
        score = (present / total) * 50 + (non_stubs / total) * 50
        return score

    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """Generate a markdown report."""
        report_lines = [
            "# Documentation Audit Report",
            f"**Date**: {os.popen('date').read().strip()}",
            f"**Target**: {self.target_dir}",
            "",
            "## Summary",
            "",
            "| Module | Score | Missing | Stubs |",
            "| :--- | :---: | :--- | :--- |"
        ]
        
        total_score = 0
        
        for res in results:
            score = self.calculate_score(res)
            total_score += score
            
            missing_str = ", ".join(res["missing"]) if res["missing"] else "✅"
            stubs_str = ", ".join(res["stubs"]) if res["stubs"] else "✅"
            
            # Highlight poor scores
            icon = "🟢" if score > 80 else "🟡" if score > 50 else "🔴"
            
            report_lines.append(
                f"| {icon} **{res['path']}** | {score:.0f}% | {missing_str} | {stubs_str} |"
            )
            
        avg_score = total_score / len(results) if results else 0
        report_lines.insert(5, f"**Average Compliance**: {avg_score:.1f}%")
        report_lines.insert(6, "")
        
        report_content = "\n".join(report_lines)
        
        # Save report
        if self.output_path:
            report_file = self.output_path / "audit_report.md"
            with open(report_file, "w") as f:
                f.write(report_content)
            self.log_success(f"Report saved to {report_file}")
            
            # Also print to console
            print(report_content)

    def run(self, args, config):
        self.target_dir = args.target.resolve()
        self.root_dir = Path.cwd()
        
        self.log_info(f"Scanning target: {self.target_dir}")
        
        results = []
        
        # Walk through directories
        # We only care about modules (directories with __init__.py) or top-level dirs
        for root, dirs, files in os.walk(self.target_dir):
            path = Path(root)
            
            # Skip hidden dirs and pycache
            if path.name.startswith(".") or path.name == "__pycache__":
                continue
            
            # Check if it's a python module or has significant content
            if "__init__.py" in files or any(p.suffix == ".py" for p in path.iterdir()):
                stats = self.scan_directory(path)
                results.append(stats)
                
        self.generate_report(results)
        
        return {"scanned": len(results), "average_score": 0} # Simplified return

if __name__ == "__main__":
    import sys
    # Ensure src is in path for imports
    sys.path.append(str(Path.cwd() / "src"))
    
    audit = DocumentationAudit()
    sys.exit(audit.execute())
