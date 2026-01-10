import os
import re

from fix_src_doubling import FunctionName, ClassName

from codomyrmex.logging_monitoring import get_logger









"""

logger = get_logger(__name__)

def fix_src_doubling(directory):
    # Matches [label](.../src/README.md)
    # We want to change it to [label](.../README.md)
    
    pattern = re.compile(r'\[([^\]]+)\]\(((\.\./)+)src/README\.md\)')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = pattern.sub(r'[\1](\2README.md)', content)
                    
                    if new_content != content:
                        print(f"Fixing src doubling in {path}")
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    # Target the documentation module's docs
    fix_src_doubling("src/codomyrmex/documentation/docs/")
    # Also check the root docs
    fix_src_doubling("docs/")
