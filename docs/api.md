# API

## Base URLs

- Retriever API: `http://localhost:8000`
- Internal embedder attachment API: `http://embedder:8001`

## Chats

### `POST /api/chats`

Creates a new chat with a generated placeholder name.

### `GET /api/chats`

Returns non-archived chats ordered by most recently updated first.

### `GET /api/chats/archived`

Returns archived chats ordered by most recently updated first.

### `GET /api/chats/{chat_id}`

Returns one chat record or `404`.

### `PATCH /api/chats/{chat_id}`

Renames a chat.

### `DELETE /api/chats/{chat_id}`

Deletes the chat, messages, attachment metadata, and retrieval logs.

### `PATCH /api/chats/{chat_id}/archive`

Sets `is_archived=true` for the chat.

### `PATCH /api/chats/{chat_id}/unarchive`

Sets `is_archived=false` for the chat.

### `GET /api/chats/{chat_id}/download`

Returns a JSON export payload and includes a download filename in `Content-Disposition`.

### `GET /api/chats/{chat_id}/messages`

Returns full chat history. Messages now include:

- `has_attachments`
- `attachments`
- `sources`

### `POST /api/chats/{chat_id}/messages`

Supports either JSON or multipart form data.

JSON request:

```json
{
  "message": "What does the Docker book say about volumes?",
  "assistant_mode": "simple"
}
```

Multipart request:

- `message`: text field
- `assistant_mode`: `simple` or `refine`
- `files`: up to 3 file parts

Response:

```json
{
  "chat_id": "chat-id",
  "user_message": {
    "id": "1",
    "chat_id": "chat-id",
    "role": "user",
    "content": "Explain the attachment",
    "status": "completed",
    "has_attachments": true,
    "created_at": "2026-03-30T12:00:00Z",
    "sources": [],
    "attachments": [
      {
        "file_name": "diagram.png",
        "file_type": "png",
        "extraction_method": "ocr",
        "quality": {
          "score": 0.91
        }
      }
    ]
  },
  "assistant_message": {
    "id": "2",
    "chat_id": "chat-id",
    "role": "assistant",
    "content": "...",
    "status": "completed",
    "has_attachments": false,
    "created_at": "2026-03-30T12:00:01Z",
    "sources": [],
    "attachments": []
  },
  "assistant_mode": "simple",
  "sources": [],
  "attachments_used": [
    {
      "file_name": "diagram.png",
      "file_type": "png",
      "extraction_method": "ocr",
      "quality": {
        "score": 0.91
      }
    }
  ]
}
```

## Settings

### `GET /api/settings`

Returns live retriever settings and available assistant modes.

### `PATCH /api/settings`

Updates retriever settings immediately and persists them.

Request:

```json
{
  "chat_history_messages_count": 5,
  "max_similarities": 8,
  "min_similarities": 2,
  "similarity_score_threshold": 0.7
}
```

## Library

### `GET /api/library/files`

Returns embedded library files and upload constraints.

### `POST /api/library/files/upload`

Multipart upload endpoint used by the web UI.

Rules:

- max file count comes from `MAX_UPLOAD_FILES`
- allowed extensions come from `ALLOWED_UPLOAD_EXTENSIONS`
- tags default to `DEFAULT_TAG`
- duplicate names are rejected

### `PATCH /api/library/files/{file_id}`

Toggles `is_enabled` without deleting vectors.

### `DELETE /api/library/files/{file_id}`

Deletes the library file from local storage, PostgreSQL, Qdrant, and tag metadata.

## Internal Embedder Attachment Job

### `POST /internal/process-attachments`

Used only by the retriever service.

Request payload:

```json
{
  "type": "attachment_processing",
  "files": [
    {
      "file_name": "table.csv",
      "content_base64": "..."
    }
  ]
}
```

This endpoint extracts text and returns ephemeral attachment metadata. It does not persist vectors or file content.
