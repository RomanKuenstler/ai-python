# API

## Base URL

The retriever API listens on `http://localhost:8000` by default.

## Core Endpoints

### `GET /api/health`

Returns:

```json
{
  "status": "ok"
}
```

### `POST /api/chats`

Creates a new chat with a generated placeholder name such as `chat-a1b2c3`.

### `GET /api/chats`

Returns all chats ordered by most recently updated first.

### `GET /api/chats/{chat_id}`

Returns one chat record or `404`.

### `PATCH /api/chats/{chat_id}`

Renames a chat.

Request body:

```json
{
  "chat_name": "Docker Notes"
}
```

### `DELETE /api/chats/{chat_id}`

Deletes the chat plus its stored messages and retrieval logs.

### `GET /api/chats/{chat_id}/messages`

Returns the full message history for a chat. Assistant messages include persisted source metadata.

### `POST /api/chats/{chat_id}/messages`

Request body:

```json
{
  "content": "What does the Docker book say about volumes?"
}
```

Response body:

```json
{
  "chat_id": "chat-id",
  "user_message": {
    "id": "1",
    "chat_id": "chat-id",
    "role": "user",
    "content": "What does the Docker book say about volumes?",
    "status": "completed",
    "created_at": "2026-03-29T20:00:00Z",
    "sources": []
  },
  "assistant_message": {
    "id": "2",
    "chat_id": "chat-id",
    "role": "assistant",
    "content": "…",
    "status": "completed",
    "created_at": "2026-03-29T20:00:01Z",
    "sources": []
  },
  "sources": [
    {
      "chunk_id": "manual-12",
      "file_name": "Deployment with Docker.epub",
      "file_path": "/app/data/Deployment with Docker.epub",
      "title": "Storage",
      "chapter": "Chapter 4",
      "section": "Volumes",
      "page_number": null,
      "score": 0.742,
      "tags": ["docker", "storage"]
    }
  ]
}
```

## Library Endpoints

### `GET /api/library/files`

Returns all known library files plus upload constraints used by the UI.

Example response:

```json
{
  "files": [
    {
      "id": 1,
      "file_name": "Deployment with Docker.epub",
      "file_path": "Deployment with Docker.epub",
      "file_type": "epub",
      "extension": ".epub",
      "size_bytes": 3560000,
      "chunk_count": 1656,
      "tags": ["container", "docker"],
      "is_embedded": true,
      "is_enabled": true,
      "processing_status": "processed",
      "updated_at": "2026-03-29T20:00:00Z"
    }
  ],
  "summary": {
    "total_files": 1,
    "embedded_files": 1,
    "total_chunks": 1656
  },
  "allowed_extensions": [".epub", ".html", ".htm", ".md", ".pdf", ".txt"],
  "max_upload_files": 5,
  "upload_max_file_size_mb": 50,
  "default_tag": "default"
}
```

### `POST /api/library/files/upload`

Multipart upload endpoint used by the web UI.

Contract:

- one or more `files` parts
- optional `tags_by_file` form field containing JSON

Example `tags_by_file` payload:

```json
{
  "notes.md": ["docker", "containers"],
  "manual.pdf": ["default"]
}
```

Rules:

- maximum file count is controlled by `MAX_UPLOAD_FILES`
- allowed extensions are controlled by `ALLOWED_UPLOAD_EXTENSIONS`
- empty or missing tags are normalized to `DEFAULT_TAG`
- duplicate filenames are rejected
- existing library filenames are rejected

### `PATCH /api/library/files/{file_id}`

Updates persistent file state.

Request body:

```json
{
  "is_enabled": false
}
```

`is_enabled=false` keeps the file in Postgres, Qdrant, and `data/`, but removes it from retrieval results.

### `DELETE /api/library/files/{file_id}`

Deletes the file from:

- local `data/`
- PostgreSQL file and chunk metadata
- Qdrant chunk vectors
- `tags.json` if present

## Error Responses

The API returns structured JSON errors:

```json
{
  "detail": "Chat not found"
}
```

## Local Usage

```bash
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/chats
curl -X PATCH http://localhost:8000/api/chats/<chat_id> \
  -H "Content-Type: application/json" \
  -d '{"chat_name":"Docker Notes"}'
curl http://localhost:8000/api/library/files
curl -X PATCH http://localhost:8000/api/library/files/1 \
  -H "Content-Type: application/json" \
  -d '{"is_enabled":false}'
curl -X POST http://localhost:8000/api/library/files/upload \
  -F 'files=@data/AI_IPS.md' \
  -F 'tags_by_file={"AI_IPS.md":["security","default"]}'
```
