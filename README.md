# Local AI System

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Node](https://img.shields.io/badge/node.js-20+-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Beginner Friendly](https://img.shields.io/badge/beginner-friendly-success)

Local, containerized Retrieval-Augmented Generation (RAG) for indexing your own files and chatting with grounded, citation-ready answers.

## Step 3 Scope

This repository now includes the Step 3 PRD implementation:

- processor-based ingestion for `.md`, `.txt`, `.html`, `.htm`, `.pdf`, and `.epub`
- file-type-aware normalization, quality validation, metadata enrichment, and reindex triggers
- PDF OCR fallback support in the embedder runtime
- Qdrant vector storage
- PostgreSQL persistence for file state, chats, messages, and retrieval logs
- FastAPI retriever API for multi-chat browser access
- React + Vite web UI with chat switching, optimistic messaging, loading states, and per-answer source panels
- CLI retriever retained as an optional developer tool
- prompt layering from the `prompts/` directory

Detailed setup and architecture notes live in [docs/setup.md](/Users/rknstlr/Workspace/ai-python/docs/setup.md), [docs/frontend.md](/Users/rknstlr/Workspace/ai-python/docs/frontend.md), and [docs/api.md](/Users/rknstlr/Workspace/ai-python/docs/api.md).
