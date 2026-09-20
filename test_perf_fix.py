import time
import bisect
from codomyrmex.cache.stats import CacheStats

class CacheStatsFast(CacheStats):
    def hit_rate_window(self, seconds: float = 60.0) -> float:
        cutoff = time.time() - seconds

        # Binary search for the first element >= cutoff using bisect.bisect_left
        # We can just extract the timestamps, or do custom binary search.
        # Custom binary search is fast enough and avoids creating a new list.
        left, right = 0, len(self._timestamps)
        while left < right:
            mid = (left + right) // 2
            if self._timestamps[mid][0] < cutoff:
                left = mid + 1
            else:
                right = mid

        # left is the index of the first valid timestamp
        # Truncate the list to free memory and make future searches faster
        self._timestamps = self._timestamps[left:]

        if not self._timestamps:
            return 0.0

        hits = sum(1 for _, hit in self._timestamps if hit)
        return hits / len(self._timestamps)

stats = CacheStatsFast()

# Add 1 million hits
print("Adding 1M hits...")
for _ in range(1000000):
    stats.record_hit("foo")

start = time.time()
rate = stats.hit_rate_window(60.0)
end = time.time()
print(f"Hit rate: {rate}")
print(f"Time: {end - start:.4f} seconds")
