# Retriever

The retriever now has two entry points:

- a FastAPI service for the Step 3 web UI
- the earlier CLI flow for direct developer testing

## Runtime Flow

1. Resolve the active chat.
2. Persist the user prompt.
3. Embed the query with the configured embedding model endpoint.
4. Search Qdrant for scored vector matches.
5. Drop candidates below `RETRIEVAL_SCORE_THRESHOLD`.
6. Sort the remaining candidates by descending score.
7. Keep up to `RETRIEVAL_MAX_RESULTS` chunks.
8. Route the request by assistant mode:
   - `simple`: one prompt pass with `prompts/assistant.md`
   - `refine`: draft prompt plus refinement prompt
9. Call the configured local LLM endpoint.
10. Store only the final assistant message and retrieval evidence in PostgreSQL.
11. Return structured JSON to the web UI or print the formatted source section in the CLI.

## Score Semantics

Qdrant is configured with cosine similarity. The implementation normalizes the returned similarity into an internal field named `score`, where higher is always better. Thresholding and sorting operate on this normalized value only.

## Empty Retrieval

If no chunk passes the threshold, the retriever still calls the LLM with a `No evidence retrieved.` context so the assistant can answer cautiously.

## API Endpoints

- `GET /api/health`
- `POST /api/chats`
- `GET /api/chats`
- `GET /api/chats/archived`
- `GET /api/chats/{chat_id}`
- `PATCH /api/chats/{chat_id}/archive`
- `PATCH /api/chats/{chat_id}/unarchive`
- `GET /api/chats/{chat_id}/messages`
- `GET /api/chats/{chat_id}/download`
- `POST /api/chats/{chat_id}/messages`
- `GET /api/settings`
- `PATCH /api/settings`

## Source Display

The CLI source section shows, where available:

- number of used similarities
- file name
- chunk title
- chapter
- section
- page number
- similarity score
- tags
