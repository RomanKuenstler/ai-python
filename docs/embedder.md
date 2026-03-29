# Embedder

The embedder is responsible for keeping the indexed knowledge base synchronized with the local `data/` directory.

## Supported Files

- `.md`
- `.txt`

## File Tracking

Each processed file is tracked with:

- relative file path
- file name
- SHA256 hash
- tags
- last processed timestamp

On each poll cycle the watcher compares on-disk files against PostgreSQL state:

- new file: embed and store
- changed file: re-embed and replace prior vectors and chunk rows
- deleted file: remove vectors from Qdrant and metadata from PostgreSQL

## Text Processing

1. Normalize line endings and whitespace, then strip invalid characters.
2. Perform semantic splitting:
   - markdown headers for `.md`
   - paragraph blocks for `.txt`
3. Perform token-aware chunking with configurable chunk size and overlap.

## Tags

Tags come from `data/tags.json`. The loader supports either a relative path key such as `notes/project.md` or a file-name key such as `project.md`.

The embedder stores tags in both PostgreSQL and Qdrant payload metadata.
