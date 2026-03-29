# Database

Step 1 initializes the PostgreSQL schema automatically on service startup.

## Tables

### `files`

- `id`
- `file_path`
- `file_name`
- `hash`
- `tags`
- `last_processed_at`
- `created_at`
- `updated_at`

### `chunks`

- `id`
- `file_id`
- `chunk_id`
- `text`
- `tags`
- `created_at`
- `updated_at`

### `chat_messages`

- `id`
- `session_id`
- `role`
- `content`
- `created_at`

### `retrieval_logs`

- `id`
- `assistant_message_id`
- `user_message_id`
- `session_id`
- `source_file_name`
- `source_file_path`
- `chunk_id`
- `chunk_text`
- `retrieval_score`
- `retrieved_at`

## Persistence Notes

- `files` and `chunks` capture the indexed source state.
- `chat_messages` stores the CLI conversation transcript.
- `retrieval_logs` stores only chunks that were actually inserted into the final RAG context for an answer.
