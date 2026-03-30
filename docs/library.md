# Library

## Purpose

Step 4 adds a dedicated Library page to the web UI for managing embedded knowledge files without leaving the app shell.

## Page Behavior

- the sidebar stays visible while the Library page is open
- `Library` sits directly below `New chat`
- selecting `New chat` or a chat item leaves the Library view and opens the normal chat screen
- the Library view refreshes after uploads, enable or disable changes, and deletions

## File Table Columns

Each row shows:

- file name
- status
- tags
- size
- chunks
- extension
- embedded
- updated
- actions

## Status Semantics

- `Active`: file is enabled and can contribute chunks to retrieval
- `Disabled`: file remains indexed but is ignored during retrieval

## Disable vs Delete

Disable:

- keeps the physical file in `data/`
- keeps Postgres metadata and chunk rows
- keeps Qdrant vectors
- blocks the file from retrieval results

Delete:

- removes the physical file from `data/`
- removes Postgres metadata and chunk rows
- removes Qdrant vectors
- removes stored tags from `tags.json`

## Extension Colors

- `.pdf` and `.epub`: red badge
- `.txt` and `.md`: grey badge
- `.html` and `.htm`: blue badge
