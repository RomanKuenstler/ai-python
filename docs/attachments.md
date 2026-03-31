# Attachments

## Supported Message Attachments

Text-like:

- `.txt`
- `.md`
- `.html`
- `.htm`
- `.pdf`
- `.epub`
- `.csv`

OCR-only images:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

## Flow

1. The web UI sends `message` plus up to 3 files to `POST /api/chats/{chat_id}/messages`.
2. The retriever validates extensions and count.
3. The retriever forwards files to the embedder internal attachment endpoint.
4. The embedder extracts text using the existing processor stack, including OCR preprocessing for image files.
5. The retriever injects truncated attachment context into the prompt.
6. Only attachment metadata is persisted with the user message. Raw file bytes and extracted content are not stored permanently.

## CSV Handling

CSV rows are rendered into readable text blocks:

```text
Row 1:
name: Alice
score: 42
```

## Limits

- `ATTACHMENT_MAX_FILES`
- `ATTACHMENT_MAX_TOTAL_CHARS`
- `ATTACHMENT_ALLOWED_EXTENSIONS`
- `ENABLE_ATTACHMENT_OCR`

## Persistence Rules

- no permanent attachment vectors
- no permanent attachment file storage
- metadata-only storage in `message_attachments`
