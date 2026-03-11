import time
from codomyrmex.api.standardization.rest_api import APIRouter, APIEndpoint, HTTPMethod

router = APIRouter()

def handler(req): return req

router.add_endpoint(APIEndpoint(path="/users/{id}/posts/{post_id}", method=HTTPMethod.GET, handler=handler, summary=""))
router.add_endpoint(APIEndpoint(path="/users/{id}", method=HTTPMethod.GET, handler=handler, summary=""))
router.add_endpoint(APIEndpoint(path="/articles/{year}/{month}/{day}", method=HTTPMethod.GET, handler=handler, summary=""))

start = time.perf_counter()
for _ in range(10000):
    router.match_endpoint(HTTPMethod.GET, "/users/123/posts/456")
    router.match_endpoint(HTTPMethod.GET, "/articles/2023/10/25")
end = time.perf_counter()

print(f"Time taken matching endpoints: {end - start:.6f}s")
