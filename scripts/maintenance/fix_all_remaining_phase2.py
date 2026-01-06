#!/usr/bin/env python3
"""
Comprehensive fix script - Phase 2
Fixes all remaining broken links and examples migration issues.
"""
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

def fix_examples_documentation_readme():
    """Fix broken references in examples/documentation/README.md"""
    file_path = REPO_ROOT / "examples/documentation/README.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("../code.review/", "../code_review/")
        content = content.replace("../api/documentation/", "../api_documentation/")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_examples_database_readme():
    """Fix broken references in examples/database_management/README.md"""
    file_path = REPO_ROOT / "examples/database_management/README.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("../api/standardization/", "../api_standardization/")
        content = content.replace("](../security/)", "](../security_audit/)")
        content = content.replace("](../security)", "](../security_audit)")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_config_agents():
    """Fix examples references in config/AGENTS.md"""
    file_path = REPO_ROOT / "config/AGENTS.md"
    if file_path.exists():
        content = file_path.read_text()
        # These example files are in config/ directory, not examples/
        # Just remove the broken relative path
        content = content.replace("(examples/workflow-basic.json)", "(workflow-basic.json)")
        content = content.replace("(examples/docker-compose.yml)", "(docker-compose.yml)")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_spatial_three_d_docs_index():
    """Fix examples references in spatial/three_d/docs/index.md"""
    file_path = REPO_ROOT / "src/codomyrmex/spatial/three_d/docs/index.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("](../examples/)", "](../../../../examples/modeling_3d/)")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_physical_management_docs_index():
    """Fix examples references in physical_management/docs/index.md"""
    file_path = REPO_ROOT / "src/codomyrmex/physical_management/docs/index.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("](../examples/)", "](../../../examples/physical_management/)")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_scripts_project_orchestration():
    """Fix examples references in scripts/project_orchestration/"""
    files = [
        REPO_ROOT / "scripts/project_orchestration/README.md",
        REPO_ROOT / "scripts/project_orchestration/AGENTS.md"
    ]
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            content = content.replace("(../examples/README.md)", "(../examples/project_orchestration/README.md)")
            content = content.replace("(../examples/AGENTS.md)", "(../examples/project_orchestration/AGENTS.md)")
            content = content.replace("(examples/comprehensive_workflow_demo.py)", "(../examples/project_orchestration/example_basic.py)")
            file_path.write_text(content)
            print(f"Fixed: {file_path}")

def fix_scripts_fpf():
    """Fix examples references in scripts/fpf/"""
    files = [
        REPO_ROOT / "scripts/fpf/README.md",
        REPO_ROOT / "scripts/fpf/AGENTS.md"
    ]
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            content = content.replace("(../examples/README.md)", "(../examples/README.md)")
            content = content.replace("(../examples/AGENTS.md)", "(../examples/AGENTS.md)")
            file_path.write_text(content)
            print(f"Fixed: {file_path}")

def fix_maintenance_agents():
    """Fix security.py reference in scripts/maintenance/AGENTS.md"""
    file_path = REPO_ROOT / "scripts/maintenance/AGENTS.md"
    if file_path.exists():
        content = file_path.read_text()
        # Remove or fix the reference to security.py
        content = content.replace("`security.py`", "`security_checks.py`")
        content = re.sub(r'\[security\.py\]\(security\.py\)', 'security checks', content)
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_documentation_modules():
    """Fix documentation/docs/modules references"""
    files = [
        REPO_ROOT / "src/codomyrmex/documentation/docs/modules/README.md",
        REPO_ROOT / "src/codomyrmex/documentation/docs/modules/AGENTS.md"
    ]
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            # Remove the broken children references
            content = re.sub(r'\s+- \[(?:agents/)?ai_code_editing\]\(agents/ai_code_editing/(?:README|AGENTS)\.md\)\n', '\n', content)
            content = re.sub(r'\s+- \[code\]\(code/(?:README|AGENTS)\.md\)\n', '', content)
            file_path.write_text(content)
            print(f"Fixed: {file_path}")

def fix_docs_modules_agents():
    """Fix docs/modules/AGENTS.md broken link"""
    file_path = REPO_ROOT / "docs/modules/AGENTS.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("(llm/ollama.md)", "(llm/README.md)")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_docs_reference_api():
    """Fix docs/reference/api.md broken link"""
    file_path = REPO_ROOT / "docs/reference/api.md"
    if file_path.exists():
        content = file_path.read_text()
        content = content.replace("../../src/codomyrmex/coding/API_SPECIFICATION.md", "../../src/codomyrmex/coding/README.md")
        file_path.write_text(content)
        print(f"Fixed: {file_path}")

def fix_template_files():
    """Mark template files as intentional placeholders - just add comments"""
    file_path = REPO_ROOT / "src/template/AGENTS_TEMPLATE.md"
    if file_path.exists():
        content = file_path.read_text()
        if "<!-- Template file" not in content:
            content = "<!-- Template file: Links below are intentional placeholder examples -->\n" + content
            file_path.write_text(content)
            print(f"Fixed: {file_path}")

def main():
    print("Starting comprehensive fix - Phase 2...")
    
    fix_examples_documentation_readme()
    fix_examples_database_readme()
    fix_config_agents()
    fix_spatial_three_d_docs_index()
    fix_physical_management_docs_index()
    fix_scripts_project_orchestration()
    fix_scripts_fpf()
    fix_maintenance_agents()
    fix_documentation_modules()
    fix_docs_modules_agents()
    fix_docs_reference_api()
    fix_template_files()
    
    print("\nDone! Re-run the audit to check remaining issues.")

if __name__ == "__main__":
    main()
