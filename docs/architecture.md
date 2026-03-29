# Architecture

Step 1 delivers a local RAG pipeline with four runtime components:

- `embedder`: polls `data/`, normalizes supported files, chunks them, creates embeddings, and synchronizes Qdrant plus PostgreSQL state
- `retriever`: CLI chat loop that embeds user questions, retrieves scored chunks, builds the RAG prompt, calls the local chat model, and stores history plus retrieval evidence
- `postgres`: stores file metadata, chunks, chat messages, and retrieval logs
- `qdrant`: stores chunk embeddings and retrieval payload metadata

The system is intentionally split into small modules so later UI, multi-user, and streaming work can extend the current services instead of replacing them.

## Data Flow

1. The embedder scans `data/` on an interval.
2. New or changed `.md` and `.txt` files are normalized, semantically split, then token-chunked.
3. Chunk vectors and metadata are written to Qdrant, while file and chunk state are written to PostgreSQL.
4. The retriever embeds each user query and performs a cosine-similarity search in Qdrant.
5. Retrieved candidates are normalized into an internal `score` field where higher is always better.
6. Chunks that meet the configured threshold are inserted into the RAG context.
7. The assistant response, chat history, and retrieval evidence are persisted in PostgreSQL.
