import time
import re
from codomyrmex.api.standardization.rest_api import APIRouter

# Compiled at class level like we would do
_PARAM_PATTERN = re.compile(r"\{([^}]+)\}")

class BetterAPIRouter(APIRouter):
    def _path_to_regex(self, path: str) -> tuple:
        param_names = _PARAM_PATTERN.findall(path)
        regex_pattern = _PARAM_PATTERN.sub(r"(?P<\1>[^/]+)", path)
        regex_pattern = f"^{regex_pattern}$"
        return re.compile(regex_pattern), param_names

def test_perf():
    router = BetterAPIRouter()

    # Pre-warm
    router._path_to_regex("/users/{id}/posts/{post_id}")

    start = time.perf_counter()
    for _ in range(100000):
        router._path_to_regex("/users/{id}/posts/{post_id}")
    end = time.perf_counter()

    print(f"Time taken: {end - start:.6f}s")

test_perf()
