
import ast
import os
import sys

def check_syntax(directory):
    print(f"Checking syntax in {directory}...")
    error_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    print(f"❌ SyntaxError in {path}: {e}")
                    error_count += 1
                except IndentationError as e:
                    print(f"❌ IndentationError in {path}: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"⚠️ Could not parse {path}: {e}")
    return error_count

if __name__ == "__main__":
    src_errors = check_syntax("src/codomyrmex")
    scripts_errors = check_syntax("scripts")
    
    total_errors = src_errors + scripts_errors
    if total_errors == 0:
        print("\n✅ All files are syntactically valid!")
        sys.exit(0)
    else:
        print(f"\n❌ Found {total_errors} syntax errors.")
        sys.exit(1)
