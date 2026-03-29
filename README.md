# Local AI System

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Node](https://img.shields.io/badge/node.js-20+-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Beginner Friendly](https://img.shields.io/badge/beginner-friendly-success)

Local, containerized Retrieval-Augmented Generation (RAG) for indexing your own files and chatting with grounded, citation-ready answers.

## Step 1 Scope

This repository now includes the first end-to-end PRD implementation:

- polling embedder for `.md` and `.txt` files
- Qdrant vector storage
- PostgreSQL persistence for file state, chunks, chat history, and retrieval logs
- CLI retriever with configurable score threshold and result limits
- prompt layering from the `prompts/` directory

Detailed setup and architecture notes live in [docs/setup.md](/Users/rknstlr/Workspace/ai-python/docs/setup.md) and [docs/architecture.md](/Users/rknstlr/Workspace/ai-python/docs/architecture.md).
