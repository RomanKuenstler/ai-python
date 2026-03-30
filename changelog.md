# Changelog

## 2026-03-29 00:00 UTC

- Added a full Step 1 local RAG scaffold with dedicated `embedder` and `retriever` services.
- Added shared configuration, logging, retry, PostgreSQL schema, and Qdrant integration modules.
- Implemented polling-based file ingestion for `.md` and `.txt` files with normalization, chunking, hashing, tag loading, embedding, and delete handling.
- Implemented CLI retrieval flow with prompt assembly, chat history persistence, retrieval score filtering, and retrieval evidence logging.
- Added Dockerfiles, Compose service wiring, `.env.example`, and starter `data/tags.json`.
- Added Step 1 documentation for architecture, embedder behavior, retriever behavior, database schema, and setup.

## 2026-03-29 01:00 UTC

- Reworked the embedder into a processor-based pipeline for `.txt`, `.md`, `.html`, `.htm`, `.pdf`, and `.epub`.
- Added shared normalization, extraction quality validation, richer semantic chunk metadata, and reindex triggers tied to processing configuration.
- Added PDF page-aware extraction, OCR fallback configuration, EPUB spine-order parsing, HTML cleanup, and repeated chrome reduction.
- Extended PostgreSQL and Qdrant metadata payloads for Step 2 source transparency and indexing provenance.
- Updated the retriever CLI to print source metadata below each answer and expanded retrieval logging accordingly.
- Added Step 2 docs for parsers, OCR, metadata, testing, and refreshed the existing setup, architecture, embedder, retriever, and database docs.
- Added focused pytest coverage and smoke-test guidance for the Step 2 ingestion and source-formatting paths.

## 2026-03-29 02:00 UTC

- Refactored the retriever into reusable chat, repository, schema, and service layers and added a FastAPI entry point for Step 3.
- Added persisted chat metadata, chat-scoped message loading, assistant source lookups, and API responses tailored for the web UI.
- Added a React + Vite frontend with sidebar chat navigation, optimistic message sending, loading/error handling, and per-answer Sources panels.
- Updated Docker Compose, environment examples, and service images to run the web UI and retriever API together.
- Added Step 3 documentation for the frontend, API, chat model, setup, testing, and updated database/retriever notes.

## 2026-03-29 03:00 UTC

- Added Step 4 library management with backend file listing, upload, enable or disable, and full deletion endpoints.
- Extended file metadata persistence for extension, size, chunk count, embedded state, enabled state, and default-tag handling.
- Added synchronous upload processing into the shared `data/` directory plus `tags.json` persistence and duplicate upload guards.
- Updated retrieval to ignore disabled files even while their vectors remain indexed.
- Added chat rename and delete backend actions with message and retrieval-log cleanup.
- Reworked the web UI into routed chat and library views with sidebar `Library` navigation, upload dialogs, file actions, and chat hover menus.
- Added safe assistant markdown rendering with `react-markdown`, GitHub-flavored markdown support, and sanitization.
- Added Step 4 API and backend tests, refreshed frontend build validation, and documented library, upload, chat-management, frontend, API, and testing behavior.
