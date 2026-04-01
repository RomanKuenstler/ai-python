# GPTs

## Overview

Step 12 adds user-owned GPTs: reusable assistant presets with isolated configuration and their own persistent chat history.

Each GPT stores:

- name
- description
- instructions
- assistant mode
- GPT-only personalization
- GPT-only retrieval settings
- GPT-only file and tag filter overrides

GPTs do not inherit user personalization, user retrieval settings, or global user filter preferences at response time.

## Runtime Model

- `gpts` stores the GPT definition and JSON-backed config.
- `gpt_chats` stores the single persistent chat session owned by the GPT.
- `chat_messages.gpt_id` marks GPT-owned messages while normal chats keep `gpt_id = null`.
- Preview chat is non-persistent and never writes to PostgreSQL.

## Prompt Order

GPT requests build prompts in this order:

1. guardrails
2. assistant-mode prompt
3. personalization block
4. GPT instructions
5. RAG context
6. attachment context
7. chat history
8. user message

## Retrieval Isolation

Normal chats use:

- user retrieval settings
- user file filters
- chat file filters
- user tag filters
- chat tag filters

GPT chats use only:

- GPT retrieval settings
- GPT file filter overrides
- GPT tag filter overrides
- system file enablement

## UI Flow

- Sidebar shows a `GPTs` section above the normal chat list.
- `+ New GPT` opens a full-width editor without the main sidebar.
- The editor splits into configuration on the left and live preview on the right.
- Any config change clears preview history.
- Opening a GPT from the sidebar opens its persistent GPT chat.

## GPT Sidebar Actions

- `Edit`
- `Clear`
- `Download`
- `Delete`

`Clear` only removes the GPT chat history. `Delete` removes the GPT and its associated persistent chat data.
