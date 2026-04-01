# Thinking Mode

Step 11 adds the `thinking` assistant mode for higher-latency, higher-quality responses.

## Pipeline

`thinking` runs three sequential LLM calls:

1. planning
2. drafting
3. refining

The retriever performs vector search once at the beginning and reuses the same retrieved chunks for all three steps.

## Prompt Order

Each stage keeps the same high-level prompt layout:

1. guardrails
2. mode-specific instructions
3. personalization
4. previous step outputs, when applicable
5. shared RAG context
6. attachment context
7. chat history
8. user prompt

## Data Flow

- `planning_result` feeds the drafting step
- `planning_result` and `draft_result` feed the refining step
- only the final refining output is returned to the UI and persisted as the assistant message

## Debugging

The retriever can log `planning_result` and `draft_result` at debug level for backend troubleshooting.

Those intermediate artifacts are never returned by the API and never rendered by the frontend.

## Failure Handling

If the thinking pipeline raises an exception, the retriever logs the failure and falls back to the `simple` mode prompt flow so the user still gets a grounded response.
