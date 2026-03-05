import time
import re

content = "This is a test content that has a lot of Words in iT. " * 1000

terms = [
    "api", "method", "function", "class", "module", "parameter",
    "return", "exception", "error", "configuration"
]

start = time.time()
for _ in range(10000):
    found_terms = sum(1 for term in terms if term.lower() in content.lower())
print(f"Inside loop: {time.time() - start:.4f}s")

start = time.time()
for _ in range(10000):
    content_lower = content.lower()
    terms_lower = [t.lower() for t in terms]
    found_terms = sum(1 for term in terms_lower if term in content_lower)
print(f"Outside loop: {time.time() - start:.4f}s")
