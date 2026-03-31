# Database

The PostgreSQL schema is initialized automatically on service startup.

## Tables

### `files`

- `id`
- `file_path`
- `file_name`
- `hash`
- `content_hash`
- `file_type`
- `processing_status`
- `processing_error`
- `last_extraction_method`
- `document_title`
- `author`
- `detected_language`
- `index_schema_version`
- `processor_version`
- `normalization_version`
- `extraction_strategy_version`
- `chunk_size`
- `chunk_overlap`
- `processing_signature`
- `extraction_quality`
- `processing_flags`
- `ocr_used`
- `tags`
- `last_processed_at`
- `created_at`
- `updated_at`

### `chunks`

- `id`
- `file_id`
- `chunk_id`
- `text`
- `title`
- `chapter`
- `section`
- `heading_path`
- `page_number`
- `extraction_method`
- `content_type`
- `quality_flags`
- `metadata`
- `tags`
- `created_at`
- `updated_at`

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

### `retrieval_logs`

- `id`
- `assistant_message_id`
- `user_message_id`
- `session_id`
- `source_file_name`
- `source_file_path`
- `chunk_id`
- `chunk_text`
- `chunk_title`
- `chapter`
- `section`
- `page_number`
- `tags`
- `retrieval_score`
- `retrieved_at`

## Persistence Notes

- `files` captures both the indexed source state and the processing configuration that produced it.
- `chunks` stores semantic metadata so retrieval sources can be rendered in the CLI and stale chunks can be recreated safely.
- `chats` stores chat metadata for the Step 3 multi-chat UI.
- `chat_messages` stores both Step 3 web conversations and the optional CLI transcript.
- `retrieval_logs` stores only chunks that were actually inserted into the final RAG context for an answer.
