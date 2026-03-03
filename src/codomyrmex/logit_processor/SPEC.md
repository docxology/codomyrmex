# Logit Processor Module Specification

## 1. Objective

Provide a robust, composable, and efficient set of logit processors for language model token generation.

## 2. Core Components

### 2.1 Processors

*   `TemperatureProcessor(temperature: float)`: Scales logits by `1/temperature`.
*   `TopKProcessor(top_k: int)`: Keeps the `k` largest logits, setting others to `-inf`.
*   `TopPProcessor(top_p: float)`: Nucleus sampling; keeps the minimal set of tokens whose cumulative probability exceeds `p`.
*   `RepetitionPenaltyProcessor(penalty: float)`: Scales logits based on whether they appear in the `input_ids`.
*   `LogitProcessorList(processors: list)`: Sequentially applies processors.

### 2.2 Functional API

*   `greedy_decode(logits: np.ndarray) -> int`: Returns the argmax token index.
*   `sample_token(logits, temperature, top_k, top_p, repetition_penalty, input_ids, seed)`: Chain application of processors followed by multinomial sampling.

### 2.3 MCP Integration

*   `process_logits`: MCP tool wrapper around `sample_token`, providing additional metadata like entropy and top-5 tokens.
