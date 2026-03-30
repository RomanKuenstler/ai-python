# Uploads

## Supported Files

The Step 4 upload flow accepts:

- `.txt`
- `.md`
- `.html`
- `.htm`
- `.pdf`
- `.epub`

## Limits

- maximum files per request: `MAX_UPLOAD_FILES` default `5`
- maximum file size: `UPLOAD_MAX_FILE_SIZE_MB` default `50`
- duplicate filenames in the same request are rejected
- filenames already present in the library are rejected

## Web UI Flow

1. Open `Library`.
2. Click `Upload` below the file table.
3. Click `+ Add files`.
4. Enter comma-separated tags for each selected file.
5. Click `Upload`.

While the upload is running, dialog actions stay disabled and the button shows an uploading state.

## Tag Rules

- tags are comma-separated in the UI
- surrounding whitespace is trimmed
- empty tag segments are discarded
- repeated tags are deduplicated case-insensitively
- an empty tag field becomes `default`

Examples:

- `docker, container, docs` becomes `["docker", "container", "docs"]`
- empty input becomes `["default"]`

## Persistence

Uploaded files are written into the shared `data/` directory. Their tags are saved into `tags.json`, persisted in PostgreSQL, and stored with vector metadata during embedding.

Files already in `data/` with no explicit tags also fall back to the configured default tag.
