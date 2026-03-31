# Settings

Step 6 adds a live retrieval settings form backed by the new `settings` table.

## Stored Keys

- `chat_history_messages_count`
- `max_similarities`
- `min_similarities`
- `similarity_score_threshold`

## Runtime Behavior

When `PATCH /api/settings` succeeds, the retriever service updates its in-memory runtime values immediately:

- chat history depth
- retrieval max results
- retrieval min results
- retrieval score threshold

The updated values are also persisted in PostgreSQL and loaded again when the retriever service starts.

## Validation

- history count: `1..50`
- max similarities: `1..50`
- min similarities: `1..50`
- threshold: `0.0..1.0`
- `min_similarities` must not be greater than `max_similarities`
