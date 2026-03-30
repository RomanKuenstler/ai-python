prd_v4.md — Local RAG System (Step 4)

1. Overview

1.1 Goal

Extend the current local RAG system with library management and better chat management in the web UI.

1.2 Step 4 Scope

This step adds:
	•	a Library page in the web UI
	•	file management for embedded knowledge files
	•	file upload from the web UI
	•	file disable/enable behavior for retrieval
	•	file deletion from UI and backend
	•	chat item actions in the sidebar:
	•	rename
	•	delete

1.3 Step 4 Priorities
	1.	Add a clean and usable Library page
	2.	Allow managed upload of supported files from the UI
	3.	Allow disabling files without deleting embeddings permanently
	4.	Allow full file deletion from data folder, Qdrant, and Postgres
	5.	Improve sidebar chat management with rename/delete dialogs
	6.	Preserve existing chat workflow and navigation
	7.	Validate, test, and debug the result before considering Step 4 complete

⸻

2. Required Outcomes

After Step 4, the system must:
	•	show a Library button in the sidebar directly below New chat
	•	open a dedicated Library page when clicked
	•	keep the same sidebar visible on the Library page
	•	allow switching from Library back to any chat by clicking New chat or a chat item
	•	display all embedded files in a Library table with useful metadata
	•	allow disabling a file so it stays indexed but is ignored during retrieval
	•	allow deleting a file completely from:
	•	vector database
	•	PostgreSQL
	•	local data/ folder
	•	allow uploading supported files from the web UI
	•	allow adding per-file tags during upload
	•	default missing tags to default
	•	show sidebar chat actions on hover:
	•	rename
	•	delete
	•	use dialogs for chat rename and chat delete confirmation
	•	keep all Step 1–3 functionality working without regression

⸻

3. High-Level Design Changes

3.1 Frontend

The web UI gains:
	•	a new Library route/page
	•	a file table view
	•	an upload dialog
	•	sidebar chat item action menu
	•	rename dialog
	•	delete confirmation dialog

3.2 Backend/API

The backend must gain endpoints for:
	•	listing files in the library
	•	uploading files
	•	storing upload tags
	•	disabling/enabling files for retrieval
	•	deleting files fully
	•	renaming chats
	•	deleting chats

3.3 Embedder Behavior

The embedder must support:
	•	defaulting file tags to default when no tags exist
	•	respecting file disabled state during retrieval integration
	•	safe file deletion sync
	•	processing files uploaded by the web UI into the shared data/ folder

⸻

4. Sidebar Requirements

4.1 Sidebar Structure

The sidebar must now contain, in order:
	1.	application title / branding
	2.	New chat button
	3.	Library button
	4.	chat list
	5.	bottom placeholder/user menu area

4.2 Library Button

The Library button must appear directly below New chat.

Behavior:
	•	clicking it navigates to the Library page
	•	Library becomes the active main view
	•	sidebar remains visible

4.3 Navigation from Library Back to Chat

While on the Library page:
	•	clicking New chat creates a new chat and opens it in the normal chat page
	•	clicking an existing chat in the sidebar switches to that chat and opens the normal chat page directly

⸻

4.x Assistant Message Rendering

Markdown Rendering Requirement

Assistant messages returned by the backend are markdown-formatted text and must be rendered in the web UI as markdown, not as plain raw text.

Requirements

The web UI must render assistant messages with proper formatting support for at least:
	•	paragraphs
	•	headings
	•	bold and italic text
	•	ordered and unordered lists
	•	inline code
	•	fenced code blocks
	•	blockquotes
	•	links
	•	tables if present
	•	horizontal rules

Styling Requirements

Markdown-rendered assistant messages should be styled clearly and consistently with the rest of the UI.

At minimum:
	•	readable typography
	•	proper spacing between blocks
	•	visually distinct code blocks
	•	proper list indentation
	•	good heading hierarchy
	•	links visually recognizable

Security Requirement

Markdown rendering must be implemented safely.

Requirements:
	•	do not allow unsafe raw HTML rendering by default
	•	sanitize rendered output appropriately
	•	avoid XSS-prone rendering behavior

Recommended Implementation

A safe markdown renderer should be used in the frontend, such as a React markdown rendering library with appropriate sanitization and optional syntax highlighting later.

Syntax highlighting is optional for Step 4, but code blocks must still render clearly even without it.

⸻

5. Library Page Requirements

5.1 General Layout

The Library page must:
	•	use the same shell layout as the chat page
	•	keep the sidebar visible
	•	show a clean main content area
	•	focus on file overview and file actions

5.2 Main Content Sections

The page should contain:
	1.	optional summary/statistics section
	2.	files table
	3.	upload area/button below the table

A summary section is recommended and may include:
	•	total files
	•	embedded files
	•	total chunks

5.3 Files Table

The Library page must show a table of all embedded files with metadata.

Each row represents one file.

5.3.1 Required Columns

At minimum include:
	•	file name
	•	status
	•	tags
	•	size
	•	chunks
	•	extension
	•	embedded
	•	updated
	•	actions

5.3.2 Metadata Meaning
	•	status: whether the file is active or disabled for retrieval
	•	tags: current tags associated with the file
	•	size: original file size
	•	chunks: number of embedded chunks
	•	extension: file extension badge
	•	embedded: whether the file is currently indexed successfully
	•	updated: last processed / updated timestamp

5.4 File Extension Color Coding

File extension badges must use color coding:
	•	.pdf and .epub → red
	•	.txt and .md → grey
	•	.html and .htm → blue

Styling should be consistent, modern, and easy to scan.

5.5 File Status / Disable Behavior

Each file row must support a disable action.

When a file is disabled:
	•	it remains in PostgreSQL
	•	it remains in Qdrant
	•	it remains in the data/ folder
	•	it is ignored during similarity search / retrieval
	•	the Library table reflects disabled state clearly

This is a logical disable, not a physical delete.

5.6 File Delete Behavior

Each file row must support a delete action.

When deleting a file, the system must remove it from:
	•	Qdrant
	•	PostgreSQL
	•	local data/ folder

Deletion should fully remove the file from the knowledge base.

A confirmation dialog is recommended and preferred before actual deletion.

5.7 Empty Library State

If no files exist, the Library page should show a clean empty state and still show the upload button.

⸻

6. Upload Workflow Requirements

6.1 Upload Button Placement

Below the files table there must be an Upload button.

6.2 Upload Dialog

Clicking Upload opens a small dialog.

The dialog must contain:
	•	title or clear purpose
	•	Cancel action button
	•	Upload action button
	•	centered + Add files button initially

6.2.1 Initial State

Initially:
	•	Upload button inside the dialog is disabled
	•	only + Add files is available for file selection
	•	no file rows shown yet

6.3 File Selection Rules

Clicking + Add files must open local file selection.

Requirements:
	•	user can select up to 5 files
	•	only valid embedding extensions are allowed
	•	supported extensions at this stage:
	•	.txt
	•	.md
	•	.html
	•	.htm
	•	.pdf
	•	.epub

If invalid files are selected, the UI should reject them clearly.

6.4 Upload Dialog File Rows

After files are selected:
	•	the + Add files button is replaced by a list of selected files
	•	one file per row
	•	each row shows:
	•	file name
	•	an input field for tags

6.4.1 Tag Input Rules

The tag input field must:
	•	allow comma-separated tags
	•	trim whitespace around tags
	•	ignore empty tag segments
	•	use default if no tags are entered

Examples:
	•	input: docker, container, docs
	•	stored as ["docker", "container", "docs"]
	•	input: empty
	•	stored as ["default"]

6.5 Upload Button Enablement

Inside the dialog:
	•	before files are added, Upload is disabled
	•	after at least one valid file is added, Upload becomes enabled

6.6 Upload Action

When the dialog’s Upload button is clicked:
	1.	selected files are uploaded to the backend
	2.	backend stores files into the shared data/ folder
	3.	backend stores or merges the tags for those files
	4.	embedder is triggered or detects the new files
	5.	files go through normal embedding flow
	6.	Library view updates when processing completes or refreshes

6.7 Upload Processing State

The UI should show an upload/processing state after upload starts.

At minimum:
	•	prevent duplicate submissions
	•	disable dialog actions while upload is in progress
	•	show visible feedback that upload is happening

6.8 Upload Limits and Safety

Recommended validations:
	•	max 5 files per upload action
	•	file size checks may be added
	•	duplicate filename behavior must be defined clearly

Preferred duplicate behavior for Step 4:
	•	reject duplicate filenames in the same upload request
	•	if a filename already exists in the library, either:
	•	reject with a clear message, or
	•	replace by explicit policy only if implemented intentionally

Safer default for Step 4: reject duplicates unless replacement is explicitly supported.

⸻

7. Tags Requirements

7.1 Default Tags for Uploaded Files

If the user uploads a file and provides no tags, the file must receive the tag:
	•	default

7.2 Default Tags in data/ Folder

For files already present in data/, if no tags are specified in tags.json, the embedder must also use:
	•	default

7.3 Tag Persistence

Tags must be persisted consistently in:
	•	PostgreSQL
	•	vector metadata where used
	•	any tags.json or equivalent file-state mechanism if still part of the design

7.4 Tag Normalization

Tags should be normalized by:
	•	trimming whitespace
	•	removing empty tags
	•	optionally deduplicating repeated tags
	•	preserving user intent without over-normalizing

⸻

8. Retrieval Integration Requirements

8.1 Disabled Files Must Be Ignored

Retriever similarity search must ignore files marked as disabled.

This means disabled files must not contribute chunks to:
	•	similarity search results
	•	RAG context construction
	•	source metadata shown in responses

8.2 Embedded but Disabled

A disabled file is still considered embedded, but unavailable for retrieval.

This distinction must be clear in backend logic and UI display.

⸻

9. Chat List Hover Menu Requirements

9.1 Hover Interaction

In the sidebar chat list, when hovering a chat item:
	•	a menu button with three dots should appear on the far right of that chat row

The button should stay hidden or subtle when not hovered, except optionally for the active item.

9.2 Chat Item Menu

Clicking the three-dot button opens a small dropdown menu for that chat.

The menu must contain:
	•	Rename
	•	Delete

The Delete option must be styled in red.

9.3 Menu Behavior

The menu should:
	•	align to the clicked chat item
	•	close on outside click
	•	close on escape
	•	not accidentally trigger chat switching when clicking the menu button

⸻

10. Rename Chat Dialog Requirements

10.1 Rename Flow

When the user clicks Rename, a small dialog opens.

The dialog must contain:
	•	input field
	•	current chat name prefilled
	•	Cancel button
	•	Save button

10.2 Rename Validation

Requirements:
	•	empty chat names are not allowed
	•	leading/trailing whitespace should be trimmed
	•	Save should be disabled if resulting name is empty
	•	renaming should update sidebar immediately after success

10.3 Rename Persistence

New chat name must be persisted in PostgreSQL.

⸻

11. Delete Chat Dialog Requirements

11.1 Delete Flow

When the user clicks Delete, a confirmation dialog opens.

The dialog must display:
	•	the current chat name
	•	Keep button
	•	Delete button

The delete action should be clearly destructive.

11.2 Delete Behavior

When confirmed:
	•	the chat is removed from persistent storage
	•	all messages for that chat are removed or logically deleted according to existing design
	•	related retrieval logs should be removed or handled consistently
	•	sidebar updates immediately

11.3 Active Chat Deletion

If the deleted chat is currently open:
	•	after deletion, the UI should navigate to a sensible fallback:
	•	another existing chat if available, or
	•	a newly created chat, or
	•	an empty chat state

Preferred behavior:
	•	switch to the most recent remaining chat
	•	if none remain, create a new empty chat

⸻

12. Backend/API Requirements

12.1 New/Updated File Management Endpoints

At minimum add endpoints for:
	•	GET /api/library/files
	•	list library files with metadata
	•	POST /api/library/files/upload
	•	upload up to 5 files with per-file tags
	•	PATCH /api/library/files/{file_id}
	•	update file state such as enabled/disabled
	•	DELETE /api/library/files/{file_id}
	•	fully delete file from system

12.2 Chat Management Endpoints

At minimum add endpoints for:
	•	PATCH /api/chats/{chat_id}
	•	rename chat
	•	DELETE /api/chats/{chat_id}
	•	delete chat

12.3 Upload Request Contract

Upload API should support multipart upload.

Each uploaded file should be accompanied by tags data.

One acceptable design:
	•	multipart files
	•	JSON field mapping file names to tags

Or equivalent typed form structure.

The contract must be documented clearly in docs/api.md.

12.4 File List Response

Library file list response should include enough data for UI rendering.

Example shape:

[
  {
    "id": "uuid",
    "file_name": "Deployment with Docker.epub",
    "file_path": "/app/data/Deployment with Docker.epub",
    "file_type": "epub",
    "extension": ".epub",
    "size_bytes": 3560000,
    "chunk_count": 1656,
    "tags": ["container", "docker"],
    "is_embedded": true,
    "is_enabled": true,
    "processing_status": "completed",
    "updated_at": "2026-03-26T12:50:00Z"
  }
]

12.5 Disable/Enable Semantics

The backend must provide a persistent flag such as:
	•	is_enabled or equivalent

Behavior:
	•	true → file is available for retrieval
	•	false → file is ignored for retrieval

12.6 File Delete Semantics

Deleting a file must coordinate:
	1.	remove physical file from data/
	2.	remove file metadata and chunk metadata from Postgres
	3.	remove vectors/chunks from Qdrant
	4.	update UI-facing file list state

Deletion must be safe and consistent.

⸻

13. Database Requirements

13.1 File Table Extensions

Ensure the file metadata model supports at minimum:

id
file_name
file_path
file_type
extension
size_bytes
chunk_count
tags
is_embedded
is_enabled
processing_status
created_at
updated_at

13.2 Chat Table

Ensure chats support rename and delete cleanly.

Suggested fields remain:

id
chat_name
created_at
updated_at

13.3 Message and Retrieval Cleanup

When deleting chats or files, related dependent records must be handled consistently.

This should be done via:
	•	cascade delete, or
	•	explicit service-layer cleanup

The behavior must be documented and implemented intentionally.

⸻

14. Frontend State Requirements

14.1 Library State

Frontend must manage at minimum:
	•	library file list
	•	upload dialog open/closed
	•	selected files for upload
	•	tag inputs per selected file
	•	upload loading state
	•	file action loading states

14.2 Chat Menu State

Frontend must manage:
	•	which chat action menu is open
	•	rename dialog state
	•	delete dialog state
	•	currently targeted chat

14.3 Refresh Behavior

After file upload, disable, delete, rename, or chat delete:
	•	relevant UI data must refresh or update immediately
	•	avoid requiring full page reload

⸻

15. UI/UX Requirements

15.1 Library Visual Style

The Library page should match the existing clean, modern, light-mode style.

Use:
	•	clear spacing
	•	compact but readable tables
	•	subtle borders
	•	status icons/badges
	•	rounded elements

15.2 Action Buttons

Disable and delete actions should be visually distinct.

Recommended:
	•	disable → neutral/warning style
	•	delete → red/destructive style

15.3 Dialog Style

All dialogs should be:
	•	compact
	•	modern
	•	centered
	•	accessible
	•	visually consistent

15.4 Table Responsiveness

Desktop is priority, but table overflow should be handled gracefully.

Acceptable approaches:
	•	horizontal scroll
	•	truncated cells with tooltip
	•	scrollable table region

⸻

16. Error Handling Requirements

16.1 Upload Errors

If upload fails:
	•	show clear error feedback
	•	do not silently close the dialog
	•	allow retry after failure

16.2 Disable/Delete File Errors

If a file action fails:
	•	show clear error feedback
	•	keep UI state consistent
	•	do not incorrectly remove/update row visually unless action succeeded

16.3 Chat Rename/Delete Errors

If rename or delete fails:
	•	show clear error feedback
	•	keep dialogs or state recoverable
	•	avoid corrupting the sidebar state

16.4 Partial Failure Handling

For file deletion in particular, backend must guard against partial failure.

If one deletion step fails, behavior must be explicit and logged.
The service should aim for consistency and may need rollback or compensating cleanup where practical.

⸻

17. Suggested Project Structure Changes

webui/src/
├── components/
│   ├── sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── ChatList.tsx
│   │   ├── ChatListItem.tsx
│   │   ├── ChatItemMenu.tsx
│   │   ├── RenameChatDialog.tsx
│   │   └── DeleteChatDialog.tsx
│   ├── library/
│   │   ├── LibraryPage.tsx
│   │   ├── LibraryTable.tsx
│   │   ├── LibraryRow.tsx
│   │   ├── UploadDialog.tsx
│   │   └── FileTagInputRow.tsx
│   └── common/
│       └── ConfirmDialog.tsx

Backend/API may add modules such as:

services/retriever/api/
├── routes/
│   ├── chats.py
│   ├── messages.py
│   └── library.py
├── schemas/
├── services/
├── repositories/


⸻

18. Configuration Requirements

Add config as needed for upload and file handling.

Suggested additions:

MAX_UPLOAD_FILES=5
ALLOWED_UPLOAD_EXTENSIONS=.txt,.md,.html,.htm,.pdf,.epub
UPLOAD_MAX_FILE_SIZE_MB=50
DEFAULT_TAG=default

18.1 Config Rules
	•	upload constraints must be configurable
	•	default tag must be configurable
	•	allowed extensions must be configurable
	•	frontend should ideally get relevant limits from backend or shared config, not hardcode them blindly

⸻

19. Testing, Validation, and Debugging Requirements

19.1 Implementation Is Not Finished Without Verification

Step 4 is not complete when code only exists.
It is complete only after the result has been checked, validated, and debugged where necessary.

19.2 Required Validation

Codex must verify at minimum:
	•	Library button appears and opens Library page
	•	sidebar remains visible on Library page
	•	clicking New chat from Library opens a new chat page
	•	clicking a chat from Library opens that chat page directly
	•	file table loads correctly
	•	extension color coding is correct
	•	disable action works and disabled files are ignored in retrieval
	•	delete file action removes from Qdrant, Postgres, and data/
	•	upload dialog works
	•	upload allows up to 5 valid files
	•	tag input works correctly
	•	empty tags become default
	•	uploaded files are stored and embedded
	•	existing data/ files without tags also receive default
	•	chat hover menu appears correctly
	•	rename dialog works and persists changes
	•	delete dialog works and removes chat correctly
	•	Step 1–3 functionality is not broken

19.3 Required Debugging Loop

If issues are found during implementation or validation, Codex must:
	1.	identify the cause
	2.	debug and fix the issue
	3.	rerun validation
	4.	update docs if behavior changed
	5.	update changelog.md

19.4 Recommended Tests

Codex should add tests where practical, especially for:
	•	library file listing
	•	file enable/disable behavior
	•	file deletion workflow
	•	upload validation rules
	•	default tag behavior
	•	chat rename API
	•	chat delete API
	•	sidebar menu interaction
	•	dialog component behavior

19.5 Manual Smoke Test Checklist

Codex should perform and document a smoke test covering:
	•	open Library page
	•	upload one file with tags
	•	upload one file without tags and verify default
	•	disable a file and verify it is not used in retrieval
	•	re-enable if supported or verify disable persistence
	•	delete a file and verify full removal
	•	rename a chat
	•	delete a chat
	•	switch from Library back to a selected chat
	•	verify chats and library still work after page refresh

Codex must verify at minimum:
	•	assistant markdown messages render correctly in the chat UI
	•	headings, lists, code blocks, and inline code display correctly
	•	markdown rendering is safe and does not expose raw unsafe HTML

Add to Recommended Tests

Codex should add tests where practical, especially for:
	•	markdown message rendering
	•	code block rendering
	•	safe markdown sanitization behavior

⸻

20. Documentation Requirements

Codex must update or create:
	•	docs/library.md
	•	docs/uploads.md
	•	docs/chat-management.md
	•	docs/api.md
	•	docs/testing.md

20.1 docs/library.md

Must document:
	•	Library page behavior
	•	file table columns
	•	disable vs delete behavior
	•	extension color rules

20.2 docs/uploads.md

Must document:
	•	upload flow
	•	file limits
	•	supported extensions
	•	tag entry rules
	•	default tag behavior

20.3 docs/chat-management.md

Must document:
	•	sidebar menu behavior
	•	rename flow
	•	delete flow
	•	fallback behavior after deleting active chat

20.4 docs/api.md

Must document:
	•	library endpoints
	•	upload contract
	•	disable endpoint
	•	delete endpoint
	•	chat rename/delete endpoints

20.5 docs/testing.md

Must document:
	•	library test steps
	•	upload test steps
	•	file deletion verification
	•	chat rename/delete verification
	•	common debugging notes

20.6 changelog.md

Must be updated for every Step 4 change.

20.7 docs/frontend.md

Must also document:
	•	how assistant markdown rendering works
	•	which markdown features are supported
	•	any rendering/sanitization constraints

⸻

21. Acceptance Criteria

21.1 Sidebar
	•	Library button exists below New chat
	•	Library opens as a separate page with sidebar still visible
	•	clicking New chat or a chat from Library opens normal chat page

21.2 Library Page
	•	file table displays embedded files with metadata
	•	extension badges use required colors
	•	files can be disabled for retrieval
	•	files can be deleted fully
	•	upload button exists below table

21.3 Upload
	•	upload dialog opens correctly
	•	add files supports up to 5 valid files
	•	selected files appear one per row
	•	each row has tag input
	•	Upload button is disabled until files exist
	•	missing tags become default
	•	upload stores files and triggers embedding

21.4 Retrieval Behavior
	•	disabled files remain embedded but are ignored during similarity search

21.5 Chat Management
	•	sidebar chat hover shows three-dot menu
	•	menu contains Rename and Delete
	•	Rename dialog prefills current name
	•	Delete dialog displays current chat name
	•	rename persists
	•	delete persists

21.6 Quality Gate
	•	implementation has been checked
	•	issues found have been debugged and fixed
	•	docs updated
	•	changelog updated

21.7 Assistant Message Rendering
	•	assistant messages are rendered as markdown in the web UI
	•	markdown formatting is displayed correctly
	•	code blocks, lists, headings, and links render properly
	•	markdown rendering is implemented safely

⸻

22. Nice-to-Haves for Step 4

Allowed if they do not slow delivery too much:
	•	enable toggle instead of disable-only action
	•	upload progress indication per file
	•	sortable library table
	•	filter/search in library
	•	file delete confirmation dialog
	•	optimistic UI updates with rollback on failure

⸻

23. Explicit Non-Goals for Step 4

Do not add yet unless truly necessary:
	•	drag-and-drop upload
	•	bulk multi-select file actions
	•	folder upload
	•	tag editing for existing files
	•	archive chats
	•	chat folders
	•	advanced file previews

⸻

24. Engineering Requirements

Codex must follow these implementation rules:
	•	use clean modular architecture
	•	split files for maintainability
	•	avoid monolithic frontend and backend files
	•	use best practices
	•	refactor where needed
	•	keep API schemas typed and clear
	•	keep UI interactions predictable
	•	update docs continuously
	•	update changelog.md continuously
	•	validate and debug the final result before considering Step 4 complete