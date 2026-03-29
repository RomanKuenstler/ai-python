# Embedder

The embedder is responsible for keeping the indexed knowledge base synchronized with the local `data/` directory.

## Supported Files

- `.html`
- `.htm`
- `.pdf`
- `.epub`
- `.md`
- `.txt`

## File Tracking

Each processed file is tracked with:

- relative file path
- file name
- SHA256 hash
- normalized content hash
- processing status and error reason
- processor/schema/normalization versions
- extraction quality summary
- OCR usage flag
- tags
- last processed timestamp

On each poll cycle the watcher compares on-disk files against PostgreSQL state:

- new file: embed and store
- changed file: re-embed and replace prior vectors and chunk rows
- changed processing settings: re-embed and replace prior vectors and chunk rows
- deleted file: remove vectors from Qdrant and metadata from PostgreSQL

## Processor Architecture

Processors live under `services/embedder/processors/` and return structured extraction results containing:

- normalized document text
- document title
- semantic blocks
- extraction quality details
- file-type-specific metadata
- processing flags such as OCR usage and failure state

## Processing Notes By Type

- Markdown and text keep the Step 1 path, but now emit structured blocks and metadata.
- HTML and HTM remove chrome such as scripts, styles, navigation, forms, media, and hidden content before converting visible structure into markdown-like plain text.
- PDF is page-aware, uses direct extraction first, evaluates quality, and can fall back to OCR depending on config.
- EPUB follows spine order, skips likely front matter, reuses the HTML extraction logic for XHTML content, and removes repeated book chrome when possible.

## Text Processing

1. Normalize Unicode, line endings, whitespace, and blank-line structure.
2. Validate extraction quality and stop cleanly if the result is not useful.
3. Build semantic blocks per file type.
4. Split semantic blocks into final chunks with configurable chunk size and overlap.
5. Persist enriched chunk metadata into Qdrant and PostgreSQL.

## Tags

Tags come from `data/tags.json`. The loader supports either a relative path key such as `notes/project.md` or a file-name key such as `project.md`.

The embedder stores tags in both PostgreSQL and Qdrant payload metadata.
