# Agent Guidelines - Streaming

## Module Context

The `streaming` module provides real-time event streaming for agent communication and live data feeds.

## Key Classes

- `Stream` - Base interface for all stream types
- `InMemoryStream` - Fast in-process communication
- `SSEStream` - Web client streaming via Server-Sent Events
- `TopicStream` - Route events by topic
- `StreamProcessor` - Transform and route events

## Integration Points

- **events**: Stream events for async event handling
- **notification**: Real-time notifications
- **agents**: Inter-agent communication
- **api**: WebSocket/SSE endpoints

## Best Practices

1. **Use topics** to organize event domains
2. **Handle errors** in event handlers gracefully
3. **Heartbeats** for long-lived SSE connections
4. **Buffer events** for late subscribers
