
import tokenize
import sys

filename = 'src/codomyrmex/agents/core.py'
print(f"Tokenizing {filename}...")

try:
    with open(filename, 'rb') as f:
        for token in tokenize.tokenize(f.readline):
            pass
    print("Tokenization successful!")
except tokenize.TokenError as e:
    print(f"TokenError: {e}")
except Exception as e:
    print(f"Error: {e}")
