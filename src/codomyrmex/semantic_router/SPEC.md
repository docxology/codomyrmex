# Semantic Router -- Technical Specification

## Architecture

### Routing Pipeline

```
Input text -> Embedding function -> Query vector (embedding_dim,)
    -> Cosine similarity against each route's example embeddings
    -> Max similarity per route
    -> Best route above threshold -> RouteMatch
```

### Cosine Similarity

```
sim(a, b) = (a . b) / (||a|| * ||b||)
```

Each route stores pre-computed embeddings for its example utterances. During routing, the query is compared against all examples in all routes.

### Default Embedding

Hash-based deterministic embedding:
1. Initialize zero vector of size `embedding_dim`
2. For each character in lowercased text: `vec[i % dim] += ord(char) / 100`
3. L2-normalize the vector

This produces consistent embeddings without external dependencies. Similar texts produce similar vectors due to character overlap.

### Route Selection

1. For each route, compute cosine similarity between query and every example
2. Take the maximum similarity score for each route
3. Select the route with highest max-similarity
4. If best score >= route's threshold, return as matched
5. Otherwise return "no_match"

## Limitations

- Hash-based embeddings are not semantic (character-level only)
- No support for route priorities or fallback chains
- Single embedding function for all routes
