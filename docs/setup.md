# Setup

## Prerequisites

- Docker and Docker Compose
- A local OpenAI-compatible chat model endpoint
- A local OpenAI-compatible embedding endpoint

The repository defaults point to Docker Model Runner on `http://host.docker.internal:12434/v1`. If your local model runner uses a different endpoint, update `.env`.

## Run

1. Copy `.env.example` to `.env`.
2. Review the model endpoint and model-name settings.
3. Add `.md` and `.txt` files to `data/`.
4. Optionally map tags in `data/tags.json`.
5. Start indexing and infrastructure:

```bash
docker compose up --build embedder postgres qdrant
```

6. In a second terminal, start the CLI retriever:

```bash
docker compose run --rm retriever
```

## Important Environment Variables

- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `WATCH_INTERVAL`
- `RETRIEVAL_SCORE_THRESHOLD`
- `RETRIEVAL_MIN_RESULTS`
- `RETRIEVAL_MAX_RESULTS`
- `HISTORY_LIMIT`
- `QDRANT_COLLECTION`
- `EMBEDDING_MODEL`
- `EMBEDDING_BASE_URL`
- `LLM_MODEL`
- `LLM_BASE_URL`
