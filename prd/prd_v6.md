prd_v6.md — Local RAG System (Step 6)

⸻

1. Overview

1.1 Goal

Extend the system with:
	•	multi-stage retrieval (refine mode)
	•	user-selectable assistant modes per message
	•	chat archiving and export
	•	user menu with dialogs
	•	preferences system with live configuration

⸻

2. Step 6 Scope

This step introduces:
	•	Assistant modes
	•	simple (existing behavior)
	•	refine (new two-step pipeline)
	•	assistant mode selection in UI
	•	chat archive system
	•	chat download (.json)
	•	user menu dropdown
	•	preferences dialog with tabs
	•	live configurable retrieval settings

⸻

3. Assistant Modes

⸻

3.1 Mode: simple

Description

This is the current behavior.
	•	single-step retrieval
	•	uses prompts/assistant.md

⸻

3.2 Mode: refine (NEW)

Description

Two-step retrieval + generation process.

⸻

3.3 Refine Pipeline

Step 1 — Draft

Retriever builds prompt:

SYSTEM:
[guardrails]

SYSTEM:
[assistant-refine-draft.md]

SYSTEM:
[RAG context]

SYSTEM:
[chat history]

USER:
[user prompt]

→ produces draft answer

⸻

Step 2 — Refinement

Retriever builds second prompt:

SYSTEM:
[guardrails]

SYSTEM:
[assistant-refine-refining.md]

SYSTEM:
[draft answer]

SYSTEM:
[RAG context]

SYSTEM:
[chat history]

USER:
[user prompt]

→ produces final answer

⸻

3.4 Important Rules
	•	only final answer is returned to UI
	•	draft is NOT persisted as assistant message
	•	draft may optionally be logged (debug only)
	•	retrieval should be performed once (recommended) and reused for both steps

⸻

3.5 Configuration

Add:

DEFAULT_ASSISTANT_MODE=simple
ENABLE_REFINE_MODE=true


⸻

4. Web UI — Assistant Mode Selection

⸻

4.1 Placement

Inside the prompt input component.

Replace placeholder like:
	•	“Deep research”
	•	or similar

With:

→ Assistant mode selector

⸻

4.2 UI Behavior
	•	dropdown or segmented control
	•	options:
	•	simple
	•	refine

⸻

4.3 Per-Message Mode
	•	selected mode applies to the current message only
	•	must be sent to backend with request

⸻

4.4 Backend Requirement

Message endpoint must accept:

{
  "message": "...",
  "assistant_mode": "simple" | "refine"
}


⸻

5. Chat Menu Enhancements

⸻

5.1 New Options in Chat Menu

Add:
	•	Rename (existing)
	•	Delete (existing)
	•	Archive (NEW)
	•	Download (NEW)

⸻

5.2 Archive Behavior

When archiving a chat:
	•	remove from sidebar list
	•	keep in database
	•	accessible in archive tab (preferences)
	•	retrieval history remains intact

⸻

5.3 Download Behavior

When clicking download:
	•	generate .json file
	•	include:
	•	chat metadata
	•	all messages
	•	assistant responses
	•	retrieval sources per message

⸻

5.4 JSON Structure Example

{
  "chat_id": "...",
  "chat_name": "...",
  "messages": [
    {
      "role": "user",
      "content": "...",
      "created_at": "..."
    },
    {
      "role": "assistant",
      "content": "...",
      "sources": [...]
    }
  ]
}


⸻

6. User Menu (Sidebar Bottom)

⸻

6.1 Behavior

User placeholder becomes clickable.

Opens dropdown menu with:
	•	Info
	•	Help
	•	Preferences
	•	Personalization

⸻

6.2 Info Dialog
	•	simple modal dialog
	•	content placeholder (static)

⸻

6.3 Help Dialog
	•	simple modal dialog
	•	content placeholder

⸻

6.4 Preferences & Personalization

Both open same dialog system with tabs

⸻

7. Preferences Dialog

⸻

7.1 Tabs

Tabs:
	•	General
	•	Personalization
	•	Settings
	•	Archive

⸻

7.2 General Tab

Contains:
	•	assistant mode selection configuration
	•	ability to enable/disable modes (optional future)

For now:
	•	show available modes:
	•	simple
	•	refine

⸻

7.3 Personalization Tab
	•	empty for now
	•	placeholder UI

⸻

7.4 Settings Tab

7.4.1 Table Fields

Display editable inputs:
	•	chat history messages count
	•	max similarities
	•	min similarities
	•	similarity score threshold

⸻

7.4.2 Input Requirements

Each field:
	•	prefilled with current value
	•	validated
	•	numeric constraints enforced

⸻

7.4.3 Save Button
	•	updates settings live
	•	persists to backend
	•	affects retrieval immediately

⸻

7.4.4 Backend Config Update

Settings must update:
	•	runtime config
	•	optionally persisted in DB

⸻

7.5 Archive Tab

⸻

7.5.1 Content

List of archived chats

⸻

7.5.2 Per Chat Actions

Each archived chat must have:
	•	download (icon)
	•	unarchive (icon)
	•	delete (icon)

⸻

7.5.3 Unarchive Behavior
	•	restore chat to sidebar
	•	remove from archive list

⸻

7.5.4 Delete Behavior
	•	opens confirmation dialog
	•	permanently deletes chat

⸻

8. Backend Changes

⸻

8.1 Chat Table Update

Add:

is_archived BOOLEAN DEFAULT false


⸻

8.2 Settings Storage

Add table:

settings
id
key
value
updated_at


⸻

8.3 API Endpoints

Add:

Chat Actions

PATCH /api/chats/{id}/archive
PATCH /api/chats/{id}/unarchive
GET   /api/chats/archived
GET   /api/chats/{id}/download


⸻

Settings

GET  /api/settings
PATCH /api/settings


⸻

8.4 Retriever Changes
	•	accept assistant_mode
	•	route to correct pipeline
	•	implement refine pipeline logic

⸻

9. Frontend State Requirements

⸻

Must handle:
	•	assistant mode selection state
	•	archived chats list
	•	preferences state
	•	settings form state
	•	dialog states

⸻

10. UI/UX Requirements

⸻

Archive
	•	archived chats invisible in sidebar
	•	accessible only via preferences

Settings
	•	clean table UI
	•	validation feedback
	•	save confirmation

Dialogs
	•	consistent design
	•	smooth transitions

⸻

11. Testing & Validation

⸻

11.1 Required Validation

Codex must verify:
	•	assistant mode selection works
	•	refine pipeline works correctly
	•	archive hides chats
	•	unarchive restores chats
	•	download JSON works
	•	preferences dialog works
	•	settings update live
	•	validation prevents invalid input
	•	no regression from Step 1–5

⸻

11.2 Debugging Loop

If issues:
	1.	identify
	2.	fix
	3.	retest
	4.	document

⸻

12. Documentation Requirements

Create/update:
	•	docs/assistant-modes.md
	•	docs/preferences.md
	•	docs/archive.md
	•	docs/api.md
	•	docs/settings.md

⸻

13. Acceptance Criteria

⸻

Assistant Modes
	•	simple mode works
	•	refine mode works (2-step pipeline)

UI
	•	mode selector exists
	•	preferences dialog works
	•	archive tab works

Chat Management
	•	archive/unarchive works
	•	download works
	•	delete works

Settings
	•	editable
	•	validated
	•	persisted
	•	applied live

Quality
	•	tested
	•	debugged
	•	documented

⸻

14. Non-Goals

Do NOT implement yet:
	•	AI-generated chat titles
	•	multi-user accounts
	•	cloud sync
	•	streaming refine steps

⸻

15. Engineering Requirements
	•	clean modular design
	•	no duplicated logic between modes
	•	reusable pipeline functions
	•	strong typing
	•	maintainable code
	•	proper separation frontend/backend
	•	continuous refactoring
	•	changelog updates
	•	full validation before completion

⸻

16. Future (Step 7 Preview)
	•	streaming responses
	•	tool usage
	•	advanced reranking
	•	multimodal reasoning
	•	user accounts