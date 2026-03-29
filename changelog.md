# Changelog

## 2026-03-29 00:00 UTC

- Added a full Step 1 local RAG scaffold with dedicated `embedder` and `retriever` services.
- Added shared configuration, logging, retry, PostgreSQL schema, and Qdrant integration modules.
- Implemented polling-based file ingestion for `.md` and `.txt` files with normalization, chunking, hashing, tag loading, embedding, and delete handling.
- Implemented CLI retrieval flow with prompt assembly, chat history persistence, retrieval score filtering, and retrieval evidence logging.
- Added Dockerfiles, Compose service wiring, `.env.example`, and starter `data/tags.json`.
- Added Step 1 documentation for architecture, embedder behavior, retriever behavior, database schema, and setup.
