prd_v9.md — Local RAG System (Step 9)

⸻

1. Overview

1.1 Goal

Introduce user-scoped knowledge filtering through:
	•	file enable/disable controls
	•	tag-based filtering
	•	global (user-wide) filters
	•	chat-specific filters

This step gives users fine-grained control over which knowledge is used during retrieval.

⸻

2. Step 9 Scope

This step introduces:
	•	user-specific file enable/disable (global + chat-level)
	•	tag-based filtering (global + chat-level)
	•	filter precedence rules
	•	UI for managing filters
	•	integration into retrieval pipeline

⸻

3. Core Concepts

⸻

3.1 File Enable / Disable

A file can be:
	•	enabled → allowed for retrieval
	•	disabled → excluded from retrieval

Scope:
	•	global (all chats of a user)
	•	chat-specific

⸻

3.2 Tag Filtering

A tag can be:
	•	enabled → allowed
	•	disabled → excluded

If a tag is disabled:
	•	all files using this tag are excluded
	•	even if file itself is enabled

⸻

3.3 Filtering Levels

There are two independent filtering levels:

1. Global (User-wide)

Applies to all chats of the user.

2. Chat-specific

Applies only to a single chat.

⸻

3.4 Precedence Rules

File Filtering

Final file availability:

file is usable IF:
  global_file_enabled == true
  AND chat_file_enabled == true


⸻

Tag Filtering

Final tag availability:

tag is usable IF:
  global_tag_enabled == true
  AND chat_tag_enabled == true


⸻

Critical Rule

If a tag is disabled globally:

→ it cannot be enabled in chat-specific filter

⸻

3.5 Final Retrieval Rule

A chunk is usable only if:

file_enabled (global + chat)
AND tag_enabled (global + chat)


⸻

4. Backend Data Model

⸻

4.1 User Global File Settings

user_file_settings
user_id
file_id
is_enabled


⸻

4.2 Chat File Settings

chat_file_settings
chat_id
file_id
is_enabled


⸻

4.3 User Global Tag Settings

user_tag_settings
user_id
tag
is_enabled


⸻

4.4 Chat Tag Settings

chat_tag_settings
chat_id
tag
is_enabled


⸻

5. Retrieval Pipeline Changes

⸻

5.1 Filtering Step

Before similarity search results are finalized:
	1.	retrieve candidates from Qdrant
	2.	apply filtering:

	•	filter by file enable/disable
	•	filter by tag enable/disable

⸻

5.2 Filtering Logic

For each candidate chunk:
	•	get file_id
	•	get file tags

Then:

if file disabled → discard
if any tag disabled → discard


⸻

5.3 Performance Consideration

Filtering should be efficient:
	•	preload user + chat filter configs
	•	avoid per-chunk DB calls

⸻

6. Web UI Changes

⸻

6.1 Library Page (Global File Control)

The Library page becomes:

→ global file enable/disable control for user

Each file row must:
	•	show enable/disable toggle
	•	reflect user-specific state

⸻

6.2 Preferences Dialog → Filter Tab (NEW)

Add new tab:

Preferences → Filter


⸻

6.3 Global Tag Filtering UI

Table:

| Tag | File Count | Enabled |

Features:
	•	one row per tag
	•	count = number of files using this tag
	•	toggle switch (default enabled)

⸻

6.4 Chat Menu → Filter Option

Each chat gets new menu option:

Filter


⸻

7. Chat-Specific Filter Dialog

⸻

7.1 Structure

Dialog contains two tables:

⸻

Table 1 — Tags

| Tag | File Count | Enabled |

Rules:
	•	default: enabled
	•	if globally disabled → switch disabled (locked)

⸻

Table 2 — Files

| File Name | Tags | Enabled |

Features:
	•	one row per file
	•	tags displayed
	•	toggle enable/disable (same behavior as library page but scoped to chat)

⸻

7.2 Behavior Rules

Tag Table
	•	reflects all tags in system
	•	disabled tags globally cannot be enabled here

⸻

File Table
	•	reflects all files
	•	respects global file disable state

⸻

8. UI Behavior Rules

⸻

8.1 Toggle Behavior

File Toggle
	•	immediate UI update
	•	persisted to backend

⸻

Tag Toggle
	•	immediate UI update
	•	persisted

⸻

8.2 Visual Indicators
	•	disabled tags clearly marked
	•	disabled files visually distinct
	•	locked (globally disabled) tags should appear disabled and non-interactive

⸻

9. API Changes

⸻

9.1 Global File Settings

GET    /api/user/files
PATCH  /api/user/files/{file_id}


⸻

9.2 Chat File Settings

GET    /api/chats/{chat_id}/files
PATCH  /api/chats/{chat_id}/files/{file_id}


⸻

9.3 Global Tag Settings

GET    /api/user/tags
PATCH  /api/user/tags/{tag}


⸻

9.4 Chat Tag Settings

GET    /api/chats/{chat_id}/tags
PATCH  /api/chats/{chat_id}/tags/{tag}


⸻

10. Backend Requirements

⸻

10.1 Default Behavior

If no setting exists:
	•	file = enabled
	•	tag = enabled

⸻

10.2 Data Integrity
	•	deleting a file must clean related settings
	•	deleting a tag must clean related settings

⸻

10.3 Security
	•	all settings must be user-scoped
	•	no cross-user access

⸻

11. Frontend State Requirements

⸻

Must manage:
	•	global file state
	•	global tag state
	•	chat file state
	•	chat tag state
	•	locked tags
	•	UI sync with backend

⸻

12. Testing & Validation

⸻

12.1 Required Validation

Codex must verify:
	•	global file disable works
	•	chat file disable works
	•	global tag disable works
	•	chat tag disable works
	•	globally disabled tags cannot be enabled in chat
	•	filtering correctly affects retrieval
	•	combinations behave correctly
	•	no regression from Step 1–8.5

⸻

12.2 Edge Cases

Test:
	•	file enabled but tag disabled → excluded
	•	tag enabled but file disabled → excluded
	•	both enabled → included
	•	global disabled overrides chat

⸻

12.3 Debugging Loop
	1.	identify
	2.	fix
	3.	retest
	4.	document

⸻

13. Documentation Requirements

⸻

Create/update:
	•	docs/filtering.md
	•	docs/api.md
	•	docs/frontend.md
	•	docs/testing.md

⸻

14. Acceptance Criteria

⸻

Filtering
	•	works correctly for files and tags
	•	respects global + chat scope
	•	precedence rules enforced

⸻

UI
	•	library page controls global file state
	•	preferences filter tab works
	•	chat filter dialog works

⸻

Backend
	•	filtering applied before retrieval
	•	efficient execution

⸻

Quality
	•	tested
	•	debugged
	•	documented

⸻

15. Non-Goals

Do NOT implement:
	•	advanced tag hierarchies
	•	tag editing UI
	•	bulk operations
	•	auto-tagging improvements

⸻

16. Engineering Requirements
	•	clean separation of filtering logic
	•	reusable filtering functions
	•	no duplication
	•	efficient queries
	•	maintainable schema
	•	strong typing
	•	changelog updates
	•	full validation before completion