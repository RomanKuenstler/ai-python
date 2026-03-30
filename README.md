# Local AI System

Local, containerized Retrieval-Augmented Generation for indexing your own files and chatting with grounded, citation-ready answers.

## Step 5 Scope

This repository now includes the Step 5 PRD implementation:

- reference-style React web UI refresh with disabled placeholders for not-yet-implemented controls
- per-message chat attachments with preview, validation, and backend multipart support
- ephemeral attachment extraction through the embedder service for text, PDF, EPUB, CSV, and OCR-backed image inputs
- attachment-aware prompt construction with message-level attachment metadata persistence
- Alembic-backed database migrations for schema management
- updated docs, tests, and repo hygiene for a cleaner GitHub push surface

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- web UI: `http://localhost:5173`
- retriever API: `http://localhost:8000`

Detailed setup and architecture notes live in [docs/setup.md](/Users/rknstlr/Workspace/ai-python/docs/setup.md), [docs/api.md](/Users/rknstlr/Workspace/ai-python/docs/api.md), [docs/frontend.md](/Users/rknstlr/Workspace/ai-python/docs/frontend.md), [docs/attachments.md](/Users/rknstlr/Workspace/ai-python/docs/attachments.md), and [docs/migrations.md](/Users/rknstlr/Workspace/ai-python/docs/migrations.md).
