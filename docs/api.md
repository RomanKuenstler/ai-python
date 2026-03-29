# API

## Base URL

The retriever API listens on `http://localhost:8000` by default.

## Endpoints

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

Returns one chat record or a `404` error when the chat does not exist.

### `GET /api/chats/{chat_id}/messages`

Returns the full message history for a chat. Assistant messages include their persisted source metadata.

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
curl http://localhost:8000/api/chats
curl -X POST http://localhost:8000/api/chats/<chat_id>/messages \
  -H "Content-Type: application/json" \
  -d '{"content":"Summarize the Kubernetes EPUB"}'
```
