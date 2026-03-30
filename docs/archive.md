# Archive

Step 6 introduces soft-archive chat handling.

## Behavior

- archived chats are hidden from the main sidebar chat list
- archived chats stay in PostgreSQL with messages and retrieval history intact
- archived chats appear in the `Archive` tab inside Preferences

## Actions

Active chat menu:

- `Archive`
- `Download`

Archived chat actions:

- `Download`
- `Unarchive`
- `Delete`

## Download Format

Downloads are JSON exports containing:

- chat metadata
- all messages in order
- assistant retrieval sources per message
- attachment metadata per message
