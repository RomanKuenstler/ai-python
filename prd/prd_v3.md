prd_v3.md — Local RAG System (Step 3)

1. Overview

1.1 Goal

Extend the existing local RAG system with a modern web interface and API-based chat flow.

1.2 Step 3 Scope

This step introduces:
	•	a React.js web UI built with Vite
	•	a retriever API service for web communication
	•	multi-chat functionality
	•	a modern chat-style interface
	•	in-message Sources interaction for retrieved knowledge visibility

1.3 Step 3 Priorities
	1.	Convert retriever from CLI-only usage into an API-backed service
	2.	Build a clean and modern light-mode chat interface
	3.	Add multi-chat creation and switching
	4.	Preserve persistent chat history in PostgreSQL
	5.	Display retrieved knowledge metadata in the UI
	6.	Keep the implementation clean, modular, tested, and debugged before completion

⸻

2. Required Outcomes

After Step 3, the system must:
	•	provide a browser-based chat UI
	•	allow creation of multiple chats
	•	allow switching between chats
	•	persist chats and messages in PostgreSQL
	•	send chat requests from the web UI to the retriever API
	•	show loading state while the assistant response is being generated
	•	show a Sources button below final assistant answers
	•	open a dropdown/panel below the answer when Sources is clicked
	•	display retrieved knowledge metadata in that panel
	•	keep all Step 1 and Step 2 functionality working without regression

⸻

3. High-Level Architecture Changes

3.1 New/Updated Services

Service	Responsibility
webui	React + Vite frontend
retriever-api	HTTP API for chat requests, chat management, message retrieval
embedder	unchanged core responsibility from earlier steps
postgres	persistent storage for chats, messages, retrieval metadata
qdrant	vector database
model runner / LLM backend	unchanged inference backend

3.2 Architecture Flow

Web UI
→ Retriever API
→ Retrieval pipeline
→ Qdrant similarity search
→ Postgres chat/history/retrieval persistence
→ LLM call
→ API response
→ Web UI render

3.3 Retriever Evolution

The retriever must no longer be designed as CLI-first only.

Instead:
	•	the retriever core logic should be moved into reusable service modules
	•	the CLI may remain as an optional developer tool
	•	the primary interaction path for Step 3 is the HTTP API

⸻

4. Frontend Requirements

4.1 Frontend Stack

The web UI must use:
	•	React.js
	•	Vite
	•	modern component-based structure
	•	clean CSS architecture
	•	light mode only for now

TypeScript is recommended and preferred for maintainability.

4.2 Design Goals

The UI should feel:
	•	modern
	•	clean
	•	minimal
	•	spacious
	•	polished
	•	similar in interaction style to a contemporary chat product

The interface should follow the inspiration shown by the screenshots:
	•	left sidebar for chat navigation
	•	large main conversation area
	•	fixed bottom input
	•	clean rounded elements
	•	subtle borders and spacing
	•	source button below assistant answers
	•	source details in a small dropdown/panel

4.3 Layout Structure

The web UI should have two main areas:

Sidebar

Contains:
	•	app title / branding at the top
	•	New chat button
	•	list of all chats
	•	bottom placeholder area for a future user menu

Main Chat Area

Contains:
	•	current chat messages
	•	user and assistant messages
	•	loading/working state for assistant response
	•	fixed prompt input area at the bottom

⸻

5. Sidebar Requirements

5.1 New Chat Button

There must be a visible New chat button in the sidebar.

Behavior:
	•	clicking it creates a new empty chat
	•	the new chat becomes the active chat immediately
	•	the main panel should switch to that chat

5.2 Chat List

The sidebar must display all chats.

Requirements:
	•	one item per chat
	•	clicking a chat switches to it
	•	active chat should be visually highlighted
	•	list must be scrollable when many chats exist

5.3 Chat Naming

New chats should initially get a random/generated placeholder name.

Examples:
	•	chat-a1b2c3
	•	chat-89d55d

A generated random title is enough for Step 3.

Automatic AI-generated titles are not required yet.

5.4 Bottom Placeholder Area

At the bottom of the sidebar, reserve a placeholder area for a future user menu.

For Step 3, this can be a simple visual placeholder container.

⸻

6. Chat Page Requirements

6.1 Main Conversation Area

The main area must show the full message history for the selected chat.

Message order:
	•	oldest at top
	•	newest at bottom

6.2 Message Types

Support at minimum:
	•	user message
	•	assistant message
	•	assistant loading state / pending answer

6.3 User Message Display

User messages should appear clearly distinct from assistant messages.

6.4 Assistant Message Display

Assistant responses should be rendered in a clean readable message block.

Support:
	•	multiline text
	•	paragraphs
	•	basic markdown rendering is recommended

6.5 Empty Chat State

If a chat has no messages yet, show a clean empty state with a prompt encouraging the user to ask something.

⸻

7. Prompt Input Requirements

7.1 Input Placement

The user prompt input must be fixed at the bottom of the main chat area.

7.2 Input Behavior

The input area must include:
	•	text input / textarea
	•	send button with icon only

7.3 Send Button State

Behavior rules:
	•	if input is empty, the send button must be disabled
	•	once the user enters text, the send button becomes enabled
	•	when sending starts:
	•	input field becomes disabled
	•	send button becomes disabled
	•	when the response finishes or errors:
	•	input field becomes enabled again
	•	send button becomes enabled again if text is present

7.4 On Send

When the user submits a prompt:
	1.	the prompt is immediately shown in the chat as a user message
	2.	an assistant placeholder/loading message appears
	3.	request is sent to the retriever API
	4.	when response arrives, loading placeholder is replaced with final assistant message

7.5 Input UX

Recommended behavior:
	•	Enter sends
	•	Shift+Enter creates newline
	•	input auto-expands to a reasonable max height

⸻

8. Multi-Chat Functionality

8.1 Core Requirement

The system must support multiple chats.

8.2 Chat Switching

When the user switches between chats:
	•	the selected chat becomes active
	•	its message history is loaded and displayed
	•	input operates on that chat only

8.3 Persistence

Chats and their messages must persist in PostgreSQL.

A page refresh must not lose chat history.

8.4 Independent Histories

Each chat must have its own isolated history and retrieval context.

The retriever must use the currently selected chat’s history only.

⸻

9. Retriever API Requirements

9.1 API Goal

Expose retriever functionality over HTTP so the web UI can create chats, fetch chats, fetch messages, and send prompts.

9.2 Suggested Stack

The API should use Python and a modern framework such as:
	•	FastAPI preferred

9.3 API Design Principles

The API should be:
	•	clean
	•	versionable
	•	typed
	•	documented
	•	modular
	•	easy to extend later

9.4 Required Endpoints

Chat Endpoints

At minimum:
	•	POST /api/chats
	•	create a new chat
	•	GET /api/chats
	•	list all chats
	•	GET /api/chats/{chat_id}
	•	get chat metadata
	•	GET /api/chats/{chat_id}/messages
	•	get all messages for a chat

Message / Retrieval Endpoint

At minimum:
	•	POST /api/chats/{chat_id}/messages
	•	submit user prompt
	•	perform retrieval
	•	call LLM
	•	persist user + assistant messages
	•	persist retrieval logs
	•	return assistant response plus source metadata

Health Endpoint

At minimum:
	•	GET /api/health

Optional:
	•	GET /api/config for safe frontend-readable config if useful

9.5 Chat Request Behavior

When the frontend submits a prompt, the API must:
	1.	validate chat exists
	2.	save user message
	3.	perform retrieval
	4.	build prompt using existing system logic
	5.	call model
	6.	save assistant response
	7.	save retrieval metadata
	8.	return structured response

⸻

10. API Response Requirements

10.1 Assistant Response Payload

The API response for a sent message must include:
	•	assistant message id
	•	assistant content
	•	chat id
	•	created timestamp
	•	source metadata for the chunks actually used

Example shape:

{
  "chat_id": "uuid",
  "user_message": {
    "id": "uuid",
    "content": "..."
  },
  "assistant_message": {
    "id": "uuid",
    "content": "...",
    "created_at": "..."
  },
  "sources": [
    {
      "chunk_id": "uuid",
      "file_name": "Deployment with Docker.epub",
      "file_path": "/app/data/Deployment with Docker.epub",
      "title": "Summary",
      "chapter": "Chapter 4",
      "section": "Volumes",
      "page_number": null,
      "score": 0.742,
      "tags": ["container", "docker"]
    }
  ]
}

10.2 Source Metadata Rules

Each returned source should include as much as available:
	•	file name
	•	file path if stored
	•	chunk title
	•	chapter
	•	section
	•	page number
	•	score
	•	tags

If some fields do not apply, return null or omit consistently.

⸻

11. Sources UI Requirements

11.1 Source Button Placement

Under each final assistant message, show a Sources button.

11.2 Source Button Behavior

When clicked:
	•	open a small dropdown, popover, or expandable panel below the assistant message
	•	show the retrieved knowledge metadata used for that answer
	•	allow closing by clicking again or clicking outside

11.3 Source Panel Content

The source panel should display:
	•	source count / number of similarities used
	•	optionally retrieval quality summary if available
	•	for each source:
	•	file name
	•	score
	•	title / chapter / section / page if available
	•	tags

11.4 Visual Design

The sources panel should be:
	•	compact
	•	readable
	•	styled consistently with the rest of the UI
	•	scrollable if many sources exist

11.5 No Sources Case

If no sources were used, the assistant message may either:
	•	hide the Sources button, or
	•	show it and display “No sources used”

For Step 3, showing the button only when sources exist is preferred.

⸻

12. Backend Persistence Requirements

12.1 Chats Table

Create or extend a chats table.

Suggested fields:

id
chat_name
created_at
updated_at

12.2 Messages Table

Use the existing message persistence or extend it to support chat-level storage cleanly.

Suggested fields:

id
chat_id
role
content
created_at
status

status may support:
	•	pending
	•	completed
	•	error

Optional but useful.

12.3 Retrieval Logs

Continue storing retrieval metadata for each assistant answer.

Retrieval logs must remain linked to the corresponding assistant message.

⸻

13. Frontend State Management Requirements

13.1 Required State Areas

Frontend state must handle at minimum:
	•	all chats list
	•	active chat id
	•	active chat messages
	•	loading state for current request
	•	input value
	•	sources panel open/closed state per assistant message

13.2 Recommended State Approach

Keep it simple and maintainable.

Acceptable options:
	•	React state + context
	•	lightweight client state library if needed

Do not over-engineer state management for Step 3.

13.3 Optimistic UI

On message send, the frontend should optimistically display:
	•	the user message immediately
	•	a pending assistant placeholder immediately

Then reconcile with API response.

⸻

14. Error Handling Requirements

14.1 Frontend Errors

If a request fails:
	•	remove or mark the pending assistant loading state
	•	show a visible error state in the chat
	•	re-enable the input and send button

14.2 API Errors

The API should return structured error responses.

At minimum handle:
	•	missing chat
	•	invalid input
	•	database failure
	•	vector retrieval failure
	•	model failure
	•	unexpected internal error

14.3 Recovery UX

The UI should recover cleanly after errors and allow the user to continue chatting.

⸻

15. Suggested Project Structure

.
├── webui/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── app/
│       ├── components/
│       │   ├── layout/
│       │   ├── sidebar/
│       │   ├── chat/
│       │   ├── messages/
│       │   ├── input/
│       │   └── sources/
│       ├── pages/
│       ├── hooks/
│       ├── api/
│       ├── types/
│       ├── utils/
│       └── styles/
├── services/
│   ├── retriever/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── main.py


⸻

16. Docker and Runtime Requirements

16.1 Docker Compose Update

Update docker-compose.yml to include:
	•	webui
	•	retriever API service if split separately from prior retriever container

16.2 Frontend Container

The web UI should run in Docker.

For development, Vite dev server is acceptable.
For a more stable local run mode, a production build + static serving approach may also be added.

16.3 Networking

The web UI must be able to call the retriever API through Docker networking and config-driven API base URLs.

⸻

17. Configuration Requirements

Add frontend/backend config as needed.

17.1 Backend

Suggested additions:

API_HOST=0.0.0.0
API_PORT=8000
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

17.2 Frontend

Suggested additions:

VITE_API_BASE_URL=http://localhost:8000

17.3 Config Rules

All URLs and ports should be configurable and not hardcoded.

⸻

18. UI/UX Requirements

18.1 Visual Style

The UI must be:
	•	light mode
	•	modern
	•	clean
	•	soft borders
	•	rounded corners
	•	consistent spacing
	•	subtle hover and active states

18.2 Accessibility

At minimum:
	•	keyboard navigable input and buttons
	•	visible focus states
	•	semantic button usage
	•	readable contrast
	•	loading state communicated clearly

18.3 Responsiveness

Basic responsive behavior is required.

Desktop is the priority for Step 3, but the layout should degrade reasonably on narrower screens.

⸻

19. Non-Functional Requirements

19.1 Clean Architecture

The implementation must:
	•	keep retriever logic separated from API transport code
	•	keep frontend UI components modular
	•	avoid giant files
	•	use reusable service and repository layers where useful

19.2 Code Quality

Use:
	•	clean code
	•	best practices
	•	refactoring where needed
	•	type hints in Python
	•	TypeScript preferred in frontend
	•	clear interfaces and schemas

19.3 Documentation

Codex must continue updating:
	•	changelog.md
	•	docs/

and add/update docs relevant to:
	•	frontend setup
	•	API usage
	•	chat data model
	•	running the system locally

⸻

20. Testing, Validation, and Debugging Requirements

20.1 Implementation Is Not Finished Without Verification

Step 3 is not complete when code merely exists.
It is complete only after the result has been checked, validated, and debugged where necessary.

20.2 Required Validation

Codex must verify at minimum:
	•	web UI starts correctly
	•	retriever API starts correctly
	•	new chat creation works
	•	chat switching works
	•	messages persist correctly per chat
	•	send button enable/disable logic works
	•	loading state appears while waiting for response
	•	assistant response replaces loading state correctly
	•	sources button appears under assistant answers when sources exist
	•	sources dropdown/panel opens and shows correct data
	•	page refresh keeps chats and messages
	•	prior retrieval functionality still works
	•	Step 1 and Step 2 behavior is not broken

20.3 Required Debugging Loop

If problems are found during implementation or validation, Codex must:
	1.	identify the cause
	2.	debug and fix the issue
	3.	rerun validation
	4.	update docs if behavior changed
	5.	update changelog.md

20.4 Recommended Tests

Codex should add tests where practical, especially for:
	•	API endpoint behavior
	•	chat creation and retrieval
	•	message send flow
	•	source metadata response formatting
	•	frontend component rendering for chat list, message list, input area, and sources panel

20.5 Manual Smoke Test Checklist

Codex should perform and document a smoke test covering:
	•	create multiple chats
	•	switch between chats
	•	send a message in chat A
	•	send a different message in chat B
	•	verify histories remain separate
	•	verify assistant loading state
	•	verify sources button and dropdown
	•	refresh page and confirm persistence

⸻

21. Documentation Requirements

Codex must update or create:
	•	docs/frontend.md
	•	docs/api.md
	•	docs/chat-model.md
	•	docs/testing.md
	•	docs/setup.md

21.1 docs/frontend.md

Must document:
	•	frontend stack
	•	layout structure
	•	major components
	•	state handling
	•	running locally

21.2 docs/api.md

Must document:
	•	endpoint list
	•	request/response shapes
	•	error responses
	•	local usage examples

21.3 docs/chat-model.md

Must document:
	•	chat data model
	•	how messages are persisted
	•	how sources are linked to assistant answers

21.4 docs/testing.md

Must document:
	•	frontend validation steps
	•	backend validation steps
	•	smoke test steps
	•	common debugging steps

⸻

22. Acceptance Criteria

22.1 Web UI
	•	React + Vite web UI exists and runs
	•	sidebar contains New chat button, chat list, and bottom placeholder area
	•	main area displays chat messages
	•	bottom fixed input exists with icon-only send button
	•	design is modern, clean, and light mode

22.2 Chat Interaction
	•	send button is disabled when input is empty
	•	send button becomes enabled when user enters text
	•	on send, input and button become disabled
	•	user message appears immediately
	•	assistant loading state appears immediately
	•	final assistant response replaces loading state

22.3 Multi-Chat
	•	multiple chats can be created
	•	chats can be switched
	•	each chat has isolated persistent history
	•	new chats get random/generated names

22.4 Retriever API
	•	retriever is accessible via HTTP API
	•	API supports chat creation, chat listing, message listing, and message sending
	•	API returns assistant response plus used source metadata

22.5 Sources UI
	•	assistant answers can show a Sources button
	•	clicking Sources opens a dropdown/panel below the answer
	•	panel shows retrieved knowledge information including score and tags

22.6 Quality Gate
	•	implementation has been checked
	•	issues found have been debugged and fixed
	•	docs updated
	•	changelog updated

⸻

23. Nice-to-Haves for Step 3

Allowed if they do not slow down delivery too much:
	•	markdown rendering for assistant answers
	•	auto-scroll to newest message
	•	chat rename support
	•	delete chat support
	•	subtle message animations
	•	keyboard shortcut focus on input

⸻

24. Explicit Non-Goals for Step 3

Do not add yet unless truly necessary:
	•	authentication
	•	user accounts
	•	advanced permissions
	•	streaming token output
	•	mobile-first redesign
	•	generated chat titles by AI
	•	chat search
	•	source citation highlighting inside assistant text

⸻

25. Engineering Requirements

Codex must follow these implementation rules:
	•	use clean modular architecture
	•	split files for maintainability
	•	avoid monolithic components and services
	•	use best practices
	•	refactor where needed
	•	use typed schemas for API payloads
	•	keep frontend and backend code organized
	•	continuously update docs and changelog
	•	validate the final result and debug it if needed before considering Step 3 complete