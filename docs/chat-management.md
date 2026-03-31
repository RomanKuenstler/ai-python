# Chat Management

## Sidebar Menu

Each chat row now exposes a hover menu on the right side with:

- `Rename`
- `Archive`
- `Download`
- `Delete`

The menu closes on outside click or `Escape`.

## Rename Flow

1. Hover a chat in the sidebar.
2. Open the `...` menu.
3. Select `Rename`.
4. Edit the name in the dialog and click `Save`.

Rules:

- leading and trailing whitespace is trimmed
- empty names are rejected
- the sidebar updates immediately after a successful rename

## Delete Flow

1. Hover a chat in the sidebar.
2. Open the `...` menu.
3. Select `Delete`.
4. Confirm in the dialog.

Delete removes:

- the chat row
- all messages for that chat
- retrieval logs tied to that chat

## Archive Flow

1. Hover a chat in the sidebar.
2. Open the `...` menu.
3. Select `Archive`.
4. The chat disappears from the main sidebar list and appears in Preferences > Archive.

Archived chats retain:

- chat metadata
- message history
- retrieval logs
- attachment metadata

## Active Chat Fallback

If the deleted chat was open:

- the UI switches to the most recent remaining chat
- if no chats remain, the app creates a new empty chat automatically
