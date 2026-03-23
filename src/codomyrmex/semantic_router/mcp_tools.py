"""MCP tools for the Semantic Router module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="semantic_router")
def semantic_router_route(
    text: str = "What is the weather today?",
    routes: list[dict] | None = None,
    embedding_dim: int = 64,
) -> dict:
    """Route an input text to the best matching semantic route.

    Args:
        text: Input text to classify
        routes: list of route dicts, each with 'name' and 'utterances' keys.
                Default provides weather/greeting/help routes.
        embedding_dim: Dimension of the embedding vectors

    Returns:
        dict with: route_name, score, matched, all_routes
    """
    from .router import Route, SemanticRouter

    if routes is None:
        routes = [
            {
                "name": "weather",
                "utterances": [
                    "What is the weather?",
                    "How is the weather today?",
                    "Will it rain?",
                ],
            },
            {
                "name": "greeting",
                "utterances": ["Hello", "Hi there", "Good morning", "Hey"],
            },
            {
                "name": "help",
                "utterances": [
                    "I need help",
                    "Can you help me?",
                    "Help me please",
                ],
            },
        ]

    router = SemanticRouter(embedding_dim=embedding_dim)
    for r in routes:
        router.add_route(
            Route(
                name=r["name"],
                utterances=r["utterances"],
                threshold=r.get("threshold", 0.7),
            )
        )

    result = router.route(text)
    return {
        "route_name": result.route_name,
        "score": result.score,
        "matched": result.matched,
        "all_routes": list(router.routes.keys()),
        "status": "success",
    }
