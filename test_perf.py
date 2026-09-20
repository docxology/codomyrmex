import time
from codomyrmex.cache.stats import CacheStats

stats = CacheStats()

# Add 1 million hits
print("Adding 1M hits...")
for _ in range(1000000):
    stats.record_hit("foo")

start = time.time()
rate = stats.hit_rate_window(60.0)
end = time.time()
print(f"Hit rate: {rate}")
print(f"Time: {end - start:.4f} seconds")
