# Chat Model

## Tables

### `chats`

- `id`
- `chat_name`
- `created_at`
- `updated_at`

### `chat_messages`

- `id`
- `session_id`
- `role`
- `content`
- `status`
- `created_at`

`session_id` remains the persisted chat key for compatibility with the earlier CLI implementation, but the Step 3 API and UI treat it as the chat id.

### `retrieval_logs`

- `assistant_message_id`
- `user_message_id`
- `session_id`
- source file and chunk metadata
- retrieval score
- retrieval timestamp

## Persistence Flow

1. A new chat row is created in `chats`.
2. Each prompt creates a user message in `chat_messages`.
3. Retrieval uses only the selected chat's recent history.
4. The assistant answer is stored in `chat_messages`.
5. Retrieved chunks actually used for that answer are written to `retrieval_logs`.
6. Message history can be reconstructed per chat, including source metadata for assistant answers.

## Source Linking

`retrieval_logs.assistant_message_id` links source evidence directly to one assistant answer, which is what the frontend uses for the Sources panel.
