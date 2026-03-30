# API

## Base URLs

- Retriever API: `http://localhost:8000`
- Internal embedder attachment API: `http://embedder:8001`

## Chats

### `POST /api/chats`

Creates a new chat with a generated placeholder name.

### `GET /api/chats`

Returns chats ordered by most recently updated first.

### `GET /api/chats/{chat_id}`

Returns one chat record or `404`.

### `PATCH /api/chats/{chat_id}`

Renames a chat.

### `DELETE /api/chats/{chat_id}`

Deletes the chat, messages, attachment metadata, and retrieval logs.

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
  "message": "What does the Docker book say about volumes?"
}
```

Multipart request:

- `message`: text field
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
