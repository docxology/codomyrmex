import hashlib
import timeit

def using_hexdigest(shingles):
    res = set()
    for s in shingles:
        res.add(int(hashlib.md5(s.encode(), usedforsecurity=False).hexdigest(), 16))
    return res

def using_digest(shingles):
    res = set()
    for s in shingles:
        res.add(int.from_bytes(hashlib.md5(s.encode(), usedforsecurity=False).digest(), 'big'))
    return res

shingles = ["hello", "world", "this", "is", "a", "test", "of", "minhash", "speed"] * 1000

print("hexdigest:", timeit.timeit(lambda: using_hexdigest(shingles), number=100))
print("digest:", timeit.timeit(lambda: using_digest(shingles), number=100))

# correctness
assert using_hexdigest(shingles) == using_digest(shingles)
