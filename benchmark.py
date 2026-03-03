import time
import statistics
import random
from collections import defaultdict

def old_way(query_types):
    analysis = {"query_types": {}}
    for query_type, times in query_types.items():
        if times:
            analysis["query_types"][query_type] = {
                "count": len(times),
                "avg_time_ms": statistics.mean(times),
                "median_time_ms": statistics.median(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "slow_queries": len([t for t in times if t > 1000])
            }
    return analysis

import bisect

def new_way(query_types):
    analysis = {"query_types": {}}
    for query_type, times in query_types.items():
        if times:
            times.sort()
            count = len(times)

            if count % 2 == 1:
                median_val = times[count // 2]
            else:
                median_val = (times[count // 2 - 1] + times[count // 2]) / 2.0

            slow_count = count - bisect.bisect_right(times, 1000)

            analysis["query_types"][query_type] = {
                "count": count,
                "avg_time_ms": sum(times) / count,
                "median_time_ms": median_val,
                "min_time_ms": times[0],
                "max_time_ms": times[-1],
                "slow_queries": slow_count
            }
    return analysis

# Generate test data
random.seed(42)
query_types = {
    "SELECT": [random.uniform(10, 2000) for _ in range(100000)],
    "INSERT": [random.uniform(5, 500) for _ in range(50000)],
    "UPDATE": [random.uniform(10, 1500) for _ in range(20000)],
}

# Copy data to avoid sorting affecting old_way
query_types_copy1 = {k: list(v) for k, v in query_types.items()}
query_types_copy2 = {k: list(v) for k, v in query_types.items()}

# Verify correctness
res1 = old_way(query_types_copy1)
res2 = new_way(query_types_copy2)

for k in res1["query_types"]:
    r1 = res1["query_types"][k]
    r2 = res2["query_types"][k]
    for metric in r1:
        diff = abs(r1[metric] - r2[metric])
        if diff > 1e-5:
            print(f"Mismatch in {k} {metric}: {r1[metric]} vs {r2[metric]}")

# Benchmark
import timeit

t1 = timeit.timeit("old_way(query_types_copy1)", globals={"old_way": old_way, "query_types_copy1": {k: list(v) for k, v in query_types.items()}}, number=10)
t2 = timeit.timeit("new_way(query_types_copy2)", globals={"new_way": new_way, "query_types_copy2": {k: list(v) for k, v in query_types.items()}}, number=10)

print(f"Old way: {t1:.4f}s")
print(f"New way: {t2:.4f}s")
print(f"Speedup: {t1/t2:.2f}x")
