# Preferences

The shared preferences dialog is opened from the header or user menu.

## Tabs

- `General`: lists the currently available assistant modes
- `Personalization`: user-scoped tone, style, custom instruction, and profile fields that apply to all chats
- `Settings`: live retrieval tuning form
- `Filter`: global tag filters
- `Archive`: archived chat management

## User Menu

The sidebar user block now opens a dropdown with:

- `Info`
- `Help`
- `Preferences`
- `Personalization`

`Preferences` and `Personalization` open the same dialog on different tabs.

## Personalization

Personalization is stored per user and injected into the prompt pipeline as a separate system message after the assistant-mode prompt and before RAG context.

Available controls:

- base style: `default`, `professional`, `friendly`, `direct`, `quirky`, `efficient`, `sceptical`
- characteristics: `warm`, `enthusiastic`, `headers and lists` with `more`, `default`, and `less`
- custom instructions
- nickname
- occupation
- more about you
