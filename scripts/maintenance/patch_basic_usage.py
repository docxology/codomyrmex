import os
import re

for folder, prompt_arg, default_prompt in [
    ("audio", "--text", "Hello! This is Codomyrmex."),
    (
        "video",
        "--prompt",
        "A timelapse of clouds moving over a mountain range, cinematic, golden hour",
    ),
    (
        "multimodal",
        "--prompt",
        "A photorealistic blue butterfly resting on a dandelion, morning light",
    ),
]:
    path = f"scripts/{folder}/examples/basic_usage.py"
    if not os.path.exists(path):
        continue

    with open(path) as f:
        content = f.read()

    # Fix outputs
    content = content.replace('"outputs" /', '"output" /')

    # Add argparse if not present
    if "import argparse" not in content:
        content = content.replace("import sys", "import argparse\nimport sys")

        argparse_code = f"""
def parse_args():
    parser = argparse.ArgumentParser(description=f"{folder.capitalize()} Basic Usage Example")
    parser.add_argument("{prompt_arg}", default="{default_prompt}", help="Input for generation")
    return parser.parse_args()
"""
        # Insert before main
        content = content.replace(
            "def main() -> int:", argparse_code + "\ndef main() -> int:"
        )

        # Parse args in main
        content = content.replace(
            "setup_logging()", "setup_logging()\n    args = parse_args()"
        )

        # Replace hardcoded strings
        if folder == "audio":
            content = re.sub(
                r'synthesize_to_file\(\s*"Hello!.*?",',
                "synthesize_to_file(\n                args.text,",
                content,
                count=1,
                flags=re.DOTALL,
            )
            content = re.sub(
                r'synthesize_to_file\(\s*"Hello! This is offline.*?",',
                "synthesize_to_file(\n                args.text,",
                content,
                count=1,
                flags=re.DOTALL,
            )
        else:
            prompt_var = "args.prompt"
            content = re.sub(
                r'prompt="A.*?",\n', f"prompt={prompt_var},\n", content, count=1
            )
            content = re.sub(
                r'prompt=".*?",\n',
                f'prompt={prompt_var} + " (alternative)",\n',
                content,
                count=1,
            )

    with open(path, "w") as f:
        f.write(content)

print("Updated basic_usage.py scripts with argparse and fixed output dir.")
