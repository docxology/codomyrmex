# Agent Guidelines - Rate Limiting

Use `SlidingWindowLimiter` for accurate limiting. Use `TokenBucketLimiter` for burst tolerance. Always handle `RateLimitExceeded` gracefully with retry logic.

## Integration Points

- **api**: Protect endpoints
- **llm**: Limit API calls
- **cloud**: Provider rate limits
