# Local AI System

Local, containerized Retrieval-Augmented Generation for indexing your own files and chatting with grounded, citation-ready answers.

## Step 8 Scope

This repository now includes the Step 8 PRD implementation:

- JWT-based authentication with forced password change flow
- multi-user chat, retrieval log, and settings isolation
- admin user management UI and API
- bootstrap provisioning from `users.json`
- per-user library enablement plus uploader/admin delete restrictions
- updated docs, tests, and Docker validation for the Step 8 rollout

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:

- web UI: `http://localhost:5173`
- retriever API: `http://localhost:8000`

Detailed setup and architecture notes live in [docs/setup.md](/Users/rknstlr/Workspace/ai-python/docs/setup.md), [docs/api.md](/Users/rknstlr/Workspace/ai-python/docs/api.md), [docs/authentication.md](/Users/rknstlr/Workspace/ai-python/docs/authentication.md), [docs/users.md](/Users/rknstlr/Workspace/ai-python/docs/users.md), [docs/admin.md](/Users/rknstlr/Workspace/ai-python/docs/admin.md), and [docs/security.md](/Users/rknstlr/Workspace/ai-python/docs/security.md).
