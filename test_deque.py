from collections import deque
import time

class DequeStats:
    def __init__(self):
        self._timestamps = deque()

    def record_hit(self):
        self._timestamps.append((time.time(), True))

    def hit_rate_window(self, seconds: float = 60.0) -> float:
        cutoff = time.time() - seconds

        # Pop from left until we reach timestamps >= cutoff
        while self._timestamps and self._timestamps[0][0] < cutoff:
            self._timestamps.popleft()

        if not self._timestamps:
            return 0.0

        hits = sum(1 for _, hit in self._timestamps if hit)
        return hits / len(self._timestamps)

stats = DequeStats()
print("Adding 1M hits...")
for _ in range(1000000):
    stats.record_hit()

start = time.time()
rate = stats.hit_rate_window(60.0)
end = time.time()
print(f"Hit rate: {rate}")
print(f"Time: {end - start:.4f} seconds")
