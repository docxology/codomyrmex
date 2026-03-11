import time
import re
from codomyrmex.api.standardization.rest_api import APIRouter, APIEndpoint, HTTPMethod

class FastAPIRouter(APIRouter):
    def __init__(self, prefix: str = ""):
        super().__init__(prefix)
        self._compiled_regexes = {}
        self._param_pattern = re.compile(r"\{([^}]+)\}")

    def _path_to_regex(self, path: str) -> tuple:
        if path in self._compiled_regexes:
            return self._compiled_regexes[path]

        param_names = self._param_pattern.findall(path)
        regex_pattern = self._param_pattern.sub(r"(?P<\1>[^/]+)", path)
        regex_pattern = f"^{regex_pattern}$"
        compiled = re.compile(regex_pattern)

        self._compiled_regexes[path] = (compiled, param_names)
        return compiled, param_names

router = FastAPIRouter()

def handler(req): return req

router.add_endpoint(APIEndpoint(path="/users/{id}/posts/{post_id}", method=HTTPMethod.GET, handler=handler, summary=""))
router.add_endpoint(APIEndpoint(path="/users/{id}", method=HTTPMethod.GET, handler=handler, summary=""))
router.add_endpoint(APIEndpoint(path="/articles/{year}/{month}/{day}", method=HTTPMethod.GET, handler=handler, summary=""))

start = time.perf_counter()
for _ in range(10000):
    router.match_endpoint(HTTPMethod.GET, "/users/123/posts/456")
    router.match_endpoint(HTTPMethod.GET, "/articles/2023/10/25")
end = time.perf_counter()

print(f"Time taken matching endpoints fast: {end - start:.6f}s")
