import time
from codomyrmex.api.standardization.rest_api import APIRouter

def test_perf():
    router = APIRouter()

    # Pre-warm
    router._path_to_regex("/users/{id}/posts/{post_id}")

    start = time.perf_counter()
    for _ in range(100000):
        router._path_to_regex("/users/{id}/posts/{post_id}")
    end = time.perf_counter()

    print(f"Time taken: {end - start:.6f}s")

test_perf()
