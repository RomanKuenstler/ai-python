# Metadata

## File Metadata

The `files` table now tracks:

- file identity: path, name, file hash, normalized content hash
- file type and document-level metadata such as title and author
- processing state: status, error reason, OCR used
- indexing provenance: schema version, processor version, normalization version, extraction strategy version
- reindex triggers: chunk size, chunk overlap, processing signature
- extraction quality summary and processing flags

## Chunk Metadata

Each chunk carries retrieval-facing metadata where available:

- source file name and path
- title
- chapter
- section
- heading path
- page number
- extraction method
- content type
- quality flags
- tags

## Retrieval Metadata

The retriever logs and CLI source display use the same metadata fields so the answer can show what knowledge was actually used.
