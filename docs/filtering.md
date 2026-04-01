# Filtering

## Step 9 Scope

Step 9 adds user-scoped knowledge filtering at two levels:

- global per-user filters
- chat-specific filters

Both files and tags default to enabled when no explicit setting exists.

## Precedence

Retrieval accepts a chunk only when both checks pass:

- the source file is enabled globally and for the active chat
- every chunk tag is enabled globally and for the active chat

Global disables always win. A tag disabled globally is exposed as locked in chat-level filtering and stays disabled there.

## Data Model

- `user_file_settings`
- `chat_file_settings`
- `user_tag_settings`
- `chat_tag_settings`

File rows are deleted automatically with the parent file or chat through foreign-key cascades. Tag settings are pruned when tags no longer exist in the indexed file set.

## Retrieval Flow

1. Run the Qdrant similarity search.
2. Gather the candidate file paths and tags.
3. Load user and chat filter state in bulk from PostgreSQL.
4. Drop candidates with a disabled file or any disabled tag.
5. Apply score threshold and min/max result rules.

This keeps filter enforcement out of the prompt layer and avoids per-chunk database calls.

## UI Surfaces

- `Library` continues to manage global file enable or disable state.
- `Preferences -> Filter` manages global file and tag filters.
- `Chat menu -> Filter` manages chat-specific file and tag filters for one chat.

Locked rows are shown when a global disable prevents a chat-level override.
