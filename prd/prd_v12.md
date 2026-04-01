prd_v12.md — Local RAG System (Step 12)

⸻

1. Overview

1.1 Goal

Introduce user-owned GPTs (custom assistants) that:
	•	behave like preconfigured chats
	•	have fully isolated configuration
	•	include their own:
	•	personalization
	•	assistant mode
	•	filters
	•	file settings
	•	system instructions
	•	are persistent and reusable
	•	are only accessible by their owner

⸻

2. Step 12 Scope

This step introduces:
	•	GPT entity (custom assistant)
	•	GPT creation & editing UI
	•	GPT-specific configuration system
	•	GPT preview mode (non-persistent chat)
	•	GPT-based chat sessions (persistent)
	•	GPT navigation in sidebar
	•	GPT management actions

⸻

3. Core Concept

⸻

3.1 What is a GPT

A GPT is:

A preconfigured assistant instance with its own full configuration


⸻

3.2 GPT Characteristics
	•	owned by a user
	•	not shared (for now)
	•	fully isolated from user settings
	•	reusable across sessions
	•	persistent
	•	has its own chat history

⸻

3.3 Configuration Isolation

A GPT must NOT:
	•	inherit user settings
	•	modify user settings

A GPT MUST:
	•	use only its own configuration
	•	behave consistently regardless of user defaults

⸻

4. Web UI — Sidebar Changes

⸻

4.1 New Section: GPTs

Add a new section above chat list:

GPTs


⸻

4.2 GPT List
	•	displays all GPTs created by the user
	•	one GPT per row
	•	clickable

⸻

4.3 Create Button

Below GPT list:

+ New GPT


⸻

5. GPT Creation / Editing Page

⸻

5.1 Navigation Behavior
	•	no sidebar visible
	•	full-width page

⸻

5.2 Header

Left:
	•	back button → returns to previous page

Center:

New GPT / Edit GPT / <GPT Name>

Right:
	•	Create / Save button

⸻

5.3 Layout

Split view:

Left (50%) → Configuration
Right (50%) → Preview Chat


⸻

6. Configuration Panel (Left Side)

⸻

6.1 Basic Fields

Name
	•	input
	•	label: Name
	•	placeholder: Name your GPT

⸻

Description
	•	textarea
	•	label: Description
	•	placeholder:

Add a short description about what this GPT does



⸻

Instructions
	•	textarea
	•	label: Instructions
	•	placeholder:

What does this GPT? How does it behave? What should it avoid doing?



⸻

6.2 Configuration Sections

Must include:
	•	personalization (without About You + without custom instructions)
	•	settings
	•	filter
	•	files (enable/disable)
	•	assistant mode

⸻

6.3 Important Rules
	•	all fields must reflect current GPT config in edit mode
	•	changes must update preview behavior immediately

⸻

7. Preview Chat (Right Side)

⸻

7.1 Purpose

Allows user to test GPT behavior live.

⸻

7.2 Behavior
	•	behaves like normal chat UI
	•	uses GPT configuration only
	•	NOT persistent

⸻

7.3 Reset Behavior

On ANY config change:

preview chat must be cleared


⸻

7.4 Important Rules
	•	no data stored in DB
	•	no history persisted
	•	purely temporary

⸻

8. GPT Chat Usage

⸻

8.1 Opening a GPT

When user clicks a GPT:
	•	open a chat view
	•	this is a persistent GPT chat

⸻

8.2 GPT Chat Behavior
	•	uses GPT configuration ONLY
	•	ignores user global settings
	•	stores chat history

⸻

8.3 GPT Chat Ownership
	•	chat belongs to GPT
	•	GPT belongs to user

⸻

9. GPT Menu (Sidebar)

⸻

Each GPT must have menu options:

⸻

9.1 Edit
	•	opens edit page

⸻

9.2 Clear
	•	clears entire GPT chat history

⸻

9.3 Download
	•	downloads GPT chat as .json

⸻

9.4 Delete
	•	opens confirm dialog
	•	deletes:
	•	GPT
	•	associated chat history

⸻

10. Backend Data Model

⸻

10.1 GPT Table

gpts
id
user_id
name
description
instructions
assistant_mode
created_at
updated_at


⸻

10.2 GPT Configuration Tables

Separate tables or structured JSON:

⸻

GPT Personalization

gpt_personalization
gpt_id
base_style
warm_level
enthusiasm_level
headers_lists_level


⸻

GPT Settings

gpt_settings
gpt_id
history_limit
max_similarities
min_similarities
similarity_score


⸻

GPT File Settings

gpt_file_settings
gpt_id
file_id
is_enabled


⸻

GPT Tag Settings

gpt_tag_settings
gpt_id
tag
is_enabled


⸻

10.3 GPT Chat Table

gpt_chats
id
gpt_id
created_at


⸻

10.4 GPT Messages

Reuse messages table with:

gpt_id (nullable)
chat_id (nullable)


⸻

11. Retrieval Changes

⸻

11.1 GPT Context

When GPT chat is active:
	•	use GPT config instead of user config

⸻

11.2 Prompt Building

Add:

SYSTEM: GPT instructions

Inserted after:

SYSTEM: assistant
SYSTEM: personalization


⸻

11.3 Priority Order

guardrails
assistant mode
GPT instructions
personalization (GPT)
filters (GPT)
rag context
chat history
user prompt


⸻

12. API Changes

⸻

12.1 GPT CRUD

GET    /api/gpts
POST   /api/gpts
GET    /api/gpts/{id}
PATCH  /api/gpts/{id}
DELETE /api/gpts/{id}


⸻

12.2 GPT Chat

GET  /api/gpts/{id}/chat
POST /api/gpts/{id}/messages
DELETE /api/gpts/{id}/chat


⸻

13. Frontend State Requirements

⸻

Must manage:
	•	GPT list
	•	GPT config state
	•	preview state
	•	GPT chat state
	•	edit mode vs create mode

⸻

14. Testing & Validation

⸻

14.1 Required Validation

Codex must verify:
	•	GPT creation works
	•	GPT editing works
	•	preview resets on config change
	•	preview uses correct config
	•	GPT chat persists correctly
	•	GPT chat uses GPT config (not user config)
	•	GPT deletion removes all data
	•	GPT menu actions work
	•	no regression from Step 1–11

⸻

14.2 Edge Cases

Test:
	•	empty GPT config
	•	long instructions
	•	switching between GPT and normal chat
	•	file/tag filters in GPT

⸻

14.3 Debugging Loop
	1.	identify
	2.	fix
	3.	retest
	4.	document

⸻

15. Documentation Requirements

⸻

Create/update:
	•	docs/gpts.md
	•	docs/frontend.md
	•	docs/api.md
	•	docs/testing.md

⸻

16. Acceptance Criteria

⸻

Functionality
	•	GPTs can be created, edited, deleted
	•	GPT preview works
	•	GPT chats persist
	•	GPT config fully applied

⸻

UI
	•	GPT section visible
	•	create/edit page works
	•	preview works
	•	menu works

⸻

Backend
	•	GPT config stored correctly
	•	retrieval uses GPT config

⸻

Quality
	•	tested
	•	debugged
	•	documented

⸻

17. Non-Goals

Do NOT implement:
	•	GPT sharing
	•	GPT marketplace
	•	GPT versioning
	•	collaborative GPTs

⸻

18. Engineering Requirements
	•	clean separation GPT vs user config
	•	reusable config system
	•	modular prompt builder
	•	maintainable schema
	•	no duplication
	•	strong typing
	•	changelog updates
	•	full validation before completion