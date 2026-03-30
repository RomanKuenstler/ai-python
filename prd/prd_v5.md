prd_v5.md — Local RAG System (Step 5)

⸻

1. Overview

1.1 Goal

Upgrade the system to a polished, production-like application with:
	•	redesigned web UI (pixel-aligned to reference UI)
	•	file attachments in chat prompts
	•	improved retrieval pipeline for dynamic inputs
	•	database migration system for long-term maintainability

⸻

2. Step 5 Scope

This step introduces:
	•	full web UI redesign (visual + UX parity)
	•	attachment support per user message (max 3 files)
	•	retriever + embedder integration for dynamic files
	•	OCR support for images
	•	database migration system
	•	feature toggling (disable unimplemented UI features)

⸻

3. High-Level Changes

3.1 System Evolution

User (WebUI)
→ Chat Input + Attachments
→ Retriever API
→ (optional) Embedder job for attachments
→ Qdrant + Postgres
→ LLM
→ Response + Sources


⸻

4. Web UI Redesign

⸻

4.1 Design Requirement (STRICT)

The web UI must be visually and behaviorally identical to the reference UI located in:

/other webui

Critical Rules:
	•	Do NOT copy-paste code
	•	Rebuild using:
	•	existing architecture
	•	clean React structure
	•	Match exactly:
	•	layout
	•	spacing
	•	typography
	•	colors
	•	hover states
	•	animations
	•	component structure
	•	interaction patterns

⸻

4.2 Feature Parity Rules

The UI may contain features not yet implemented backend-side.

These MUST:
	•	exist visually
	•	be disabled
	•	show proper disabled state

Examples:
	•	archive chats
	•	preferences
	•	personalization
	•	settings panels

⸻

4.3 UI Behavior Requirements

Must match reference UI:
	•	transitions
	•	hover effects
	•	sidebar interactions
	•	message rendering
	•	dropdown behavior
	•	dialogs
	•	spacing and layout precision

⸻

5. Chat Attachments Feature

⸻

5.1 Core Requirement

Users must be able to attach files to a message.

Constraints:
	•	max 3 files per message
	•	attachments processed together with user prompt

⸻

5.2 Supported File Types

Text-based:
	•	.txt
	•	.md
	•	.html
	•	.htm
	•	.pdf
	•	.epub
	•	.csv

Images (OCR only):
	•	.png
	•	.jpg
	•	.jpeg
	•	.webp

⸻

5.3 UI Requirements

5.3.1 Attachment Button

In input area:
	•	add attachment button/icon
	•	opens file selector

⸻

5.3.2 Attachment Preview

After selection:
	•	show attached files above input
	•	each file row shows:
	•	filename
	•	remove button

⸻

5.3.3 Validation
	•	max 3 files
	•	only allowed extensions
	•	show error if invalid

⸻

5.3.4 Send Behavior

When sending:
	•	attachments are included in request
	•	UI disables input during processing

⸻

6. Attachment Processing (Backend)

⸻

6.1 Processing Strategy

Attachments must be processed before retrieval.

Two valid approaches:

Option A (Recommended)
Retriever sends attachments to embedder as a temporary processing job

Option B
Retriever processes files directly (less preferred)

⸻

6.2 Recommended Architecture

Retriever
→ sends files to Embedder
→ Embedder:
   - extracts text
   - normalizes
   - chunks
→ returns extracted content
→ Retriever injects into RAG context


⸻

6.3 Important Rule

Attached files:
	•	must NOT be permanently stored
	•	must NOT be embedded into Qdrant permanently
	•	must be treated as ephemeral context

⸻

6.4 OCR for Images

For image attachments:
	•	run OCR pipeline
	•	reuse existing OCR stack from embedder

Required:
	•	preprocessing (same as Step 2)
	•	text extraction
	•	normalization

⸻

6.5 CSV Handling

CSV files:
	•	parse rows
	•	convert to readable text format

Example:

Row 1:
column1: value
column2: value


⸻

6.6 Attachment Metadata

Each attachment must produce:

{
  "file_name": "...",
  "content": "...",
  "type": "...",
  "extraction_method": "...",
  "quality": {...}
}


⸻

7. Retriever Changes

⸻

7.1 Prompt Construction Update

Prompt must now include:

SYSTEM:
[guardrails]

SYSTEM:
[assistant]

SYSTEM:
[RAG context]

SYSTEM:
[ATTACHMENT CONTEXT]

SYSTEM:
[chat history]

USER:
[user prompt]


⸻

7.2 Attachment Context Rules
	•	include extracted text
	•	label clearly per file
	•	avoid overly large injection (truncate if needed)

⸻

7.3 Size Limits

Introduce config:

ATTACHMENT_MAX_TOTAL_CHARS=15000
ATTACHMENT_MAX_FILES=3


⸻

8. API Changes

⸻

8.1 Message Endpoint Update

POST /api/chats/{chat_id}/messages

Now supports:
	•	multipart/form-data
	•	files + JSON payload

⸻

8.2 Request Example

{
  "message": "Explain this file",
  "attachments": [...]
}


⸻

8.3 Response Update

Return:

{
  "assistant_message": {...},
  "sources": [...],
  "attachments_used": [...]
}


⸻

9. Database Changes

⸻

9.1 Message Table Extension

Add:

has_attachments BOOLEAN


⸻

9.2 Optional Attachment Table

message_attachments
id
message_id
file_name
file_type
extraction_method
created_at


⸻

10. Database Migrations (NEW)

⸻

10.1 Requirement

Introduce a database migration system.

⸻

10.2 Recommended Tool

Use:
	•	Alembic (with SQLAlchemy)

⸻

10.3 Migration Rules
	•	every schema change → migration file
	•	no manual schema drift
	•	version-controlled migrations

⸻

10.4 Required Setup

migrations/
├── versions/
├── env.py
├── script.py.mako


⸻

10.5 Developer Rules
	•	migrations must be generated and applied
	•	schema must always match code
	•	breaking changes must be handled carefully

⸻

11. Embedder Changes

⸻

11.1 New Capability

Embedder must support:
	•	on-demand processing jobs
	•	not only folder watching

⸻

11.2 Job Types
	•	persistent file embedding (existing)
	•	temporary attachment processing (new)

⸻

11.3 API (internal)

Retriever → Embedder:

{
  "type": "attachment_processing",
  "files": [...]
}


⸻

12. Configuration Updates

⸻


ATTACHMENT_MAX_FILES=3
ATTACHMENT_MAX_TOTAL_CHARS=15000

ENABLE_ATTACHMENT_OCR=true
ATTACHMENT_ALLOWED_EXTENSIONS=.txt,.md,.html,.htm,.pdf,.epub,.csv,.png,.jpg,.jpeg,.webp


⸻

13. UI/UX Requirements

⸻

Attachments
	•	visible before send
	•	removable
	•	clear error states

Disabled Features
	•	visually disabled
	•	no action triggered
	•	consistent styling

⸻

14. Testing & Validation

⸻

14.1 Mandatory Rule

Step 5 is NOT complete without:
	•	testing
	•	validation
	•	debugging

⸻

14.2 Required Validation

Codex must verify:
	•	UI matches reference visually
	•	attachments work correctly
	•	OCR works for images
	•	PDFs/EPUBs attach correctly
	•	retrieval includes attachment content
	•	attachments are NOT persisted
	•	migrations work
	•	DB schema matches code
	•	no regression from Step 1–4

⸻

14.3 Debugging Loop

If issues:
	1.	identify
	2.	fix
	3.	retest
	4.	document
	5.	update changelog

⸻

15. Documentation Requirements

Must update/create:
	•	docs/frontend.md (UI redesign)
	•	docs/attachments.md
	•	docs/migrations.md
	•	docs/api.md
	•	docs/testing.md

⸻

16. Acceptance Criteria

⸻

UI
	•	matches reference UI
	•	disabled features visible but inactive

Attachments
	•	max 3 files
	•	supported formats work
	•	OCR works for images
	•	content injected into RAG

Backend
	•	attachment processing works
	•	no persistence of attachments
	•	retriever integrates attachments

Database
	•	migrations implemented
	•	schema versioned

Quality
	•	tested
	•	debugged
	•	documented

⸻

17. Non-Goals

Do NOT implement yet:
	•	attachment persistence
	•	image understanding beyond OCR
	•	drag & drop uploads
	•	streaming responses
	•	user accounts

⸻

18. Engineering Requirements
	•	clean modular architecture
	•	no copy-paste UI code
	•	reusable components
	•	strong typing
	•	maintainable services
	•	proper separation of concerns
	•	continuous refactoring
	•	changelog updates
	•	full validation before completion

⸻

19. Future (Step 6 Preview)
	•	streaming responses
	•	citations inline
	•	tag filtering UI
	•	advanced ranking
	•	user accounts