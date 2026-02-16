import os
import re

MAPPINGS = {
    'coding': ['static_analysis', 'pattern_matching'],
    'telemetry': ['metrics', 'dashboard'],
    'model_ops': ['evaluation', 'registry', 'optimization', 'feature_store'],
    'testing': ['workflow', 'chaos'],
    'orchestrator': ['scheduler'],
    'events': ['streaming', 'notification'],
    'networking': ['service_mesh'],
    'database_management': ['migration', 'lineage'],
    'ci_cd_automation': ['build'],
    'api': ['rate_limiting'],
    'prompt_engineering': ['testing'],
    'data_visualization': ['visualization'],
    'cloud': ['cost_management'],
    'validation': ['schemas'],
    'security': ['governance'],
    'wallet': ['contracts'],
    'utils': ['i18n'],
    'documentation': ['education'],
    'website': ['accessibility'],
    'llm': ['multimodal', 'safety']
}

SRC_DIR = 'src/codomyrmex'

def update_init_files():
    for host, subs in MAPPINGS.items():
        init_path = os.path.join(SRC_DIR, host, '__init__.py')
        if not os.path.exists(init_path):
            print(f"  [SKIP] {init_path} not found")
            continue
            
        with open(init_path, 'r') as f:
            content = f.read()
            
        new_content = content
        
        # 1. Standardize/Update docstring
        docstring_match = re.search(r'^\"\"\"(.*?)\"\"\"', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1)
            original_docstring = docstring
            
            # Ensure Submodules section header exists
            if 'Submodules:' not in docstring:
                # Add it before Examples or at the end
                if 'Example:' in docstring:
                    docstring = docstring.replace('Example:', 'Submodules:\n\nExample:')
                elif 'Integration:' in docstring:
                    docstring = docstring.replace('Integration:', 'Submodules:\n\nIntegration:')
                else:
                    docstring += '\n\nSubmodules:'
            
            # Add missing submodules to docstring
            for sub in subs:
                if f'\n    {sub}:' not in docstring and f'    - {sub}:' not in docstring:
                    sub_line = f"\n    {sub}: Consolidated {sub.replace('_', ' ')} capabilities."
                    docstring = docstring.replace('Submodules:', f'Submodules:{sub_line}')
            
            if docstring != original_docstring:
                new_content = new_content.replace(f'\"\"\"{original_docstring}\"\"\"', f'\"\"\"{docstring}\"\"\"')

        # 2. Ensure imports exist
        # We'll insert them before __all__ or at the end of imports
        for sub in subs:
            if f'from . import {sub}' not in new_content and f'import {sub}' not in new_content:
                # Find a good place to insert- before __all__
                if '__all__ = [' in new_content:
                    new_content = new_content.replace('__all__ = [', f'from . import {sub}\n\n__all__ = [')
                else:
                    new_content += f"\nfrom . import {sub}\n"

        # 3. Ensure they are in __all__
        if '__all__ = [' in new_content:
            for sub in subs:
                if f'\"{sub}\"' not in new_content and f"'{sub}'" not in new_content:
                    new_content = new_content.replace('__all__ = [', f'__all__ = [\n    \"{sub}\",')

        if new_content != content:
            with open(init_path, 'w') as f:
                f.write(new_content)
            print(f"  [UPDATED] {init_path}")
        else:
            print(f"  [OK] {init_path}")

if __name__ == "__main__":
    update_init_files()
