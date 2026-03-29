# Retriever

The retriever is a CLI-first chat service for Step 2.

## Runtime Flow

1. Start the service and open a new session id.
2. Accept a user question in the terminal.
3. Embed the query with the configured embedding model endpoint.
4. Search Qdrant for scored vector matches.
5. Drop candidates below `RETRIEVAL_SCORE_THRESHOLD`.
6. Sort the remaining candidates by descending score.
7. Keep up to `RETRIEVAL_MAX_RESULTS` chunks.
8. Build prompt layers from:
   - `prompts/guardrails.md`
   - `prompts/assistant.md`
   - `prompts/ragcontext.md`
   - recent chat history
   - the live user message
9. Call the configured local LLM endpoint.
10. Store user message, assistant message, and retrieval evidence in PostgreSQL.
11. Print a source section below the answer in the same order the chunks were used.

## Score Semantics

Qdrant is configured with cosine similarity. The implementation normalizes the returned similarity into an internal field named `score`, where higher is always better. Thresholding and sorting operate on this normalized value only.

## Empty Retrieval

If no chunk passes the threshold, the retriever still calls the LLM with a `No evidence retrieved.` context so the assistant can answer cautiously.

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
