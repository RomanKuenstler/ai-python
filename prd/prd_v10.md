prd_v10.md — Local RAG System (Step 10)

⸻

1. Overview

1.1 Goal

Introduce a user-specific personalization system that:
	•	is configurable via the UI
	•	persists per user
	•	applies globally across all chats
	•	dynamically influences the assistant’s response style
	•	is integrated into the prompt-building pipeline

⸻

2. Step 10 Scope

This step introduces:
	•	personalization settings (user-scoped)
	•	UI implementation for personalization (Preferences → Personalization)
	•	prompt-building integration
	•	structured prompt templates
	•	dynamic prompt composition based on user choices

⸻

3. Core Concept

⸻

3.1 Personalization Scope
	•	personalization is user-specific
	•	applies to all chats of that user
	•	not chat-specific (no overrides per chat in this step)

⸻

3.2 Integration Point

Personalization must be applied during prompt construction, after assistant mode logic.

⸻

4. Personalization Options

⸻

4.1 Base Style and Tone

Options:
	•	default
	•	professional
	•	friendly
	•	direct
	•	quirky
	•	efficient
	•	sceptical

⸻

4.2 Characteristics

Warm
	•	more
	•	default
	•	less

⸻

Enthusiastic
	•	more
	•	default
	•	less

⸻

Headers and Lists
	•	more
	•	default
	•	less

⸻

4.3 Custom Instructions
	•	textarea
	•	free-form input
	•	optional

⸻

4.4 About You

Nickname
	•	input field
	•	placeholder:

What should the assistant call you?



⸻

Occupation
	•	input field
	•	placeholder:

What do you do?



⸻

More About You
	•	textarea
	•	placeholder:

Anything else that helps personalize responses



⸻

5. Prompt System

⸻

5.1 Prompt Files

All personalization prompts are stored in:

/prompts/


⸻

5.2 Available Prompt Types

Base Style Prompts

personalization-base-style-<type>.md


⸻

Characteristics Prompts

personalization-characteristic-<type>-<level>.md


⸻

Templates

personalization-template.md
personalization-custom-user-instructions-template.md
personalization-more-about-user-template.md
personalization-nickname-template.md
personalization-occupation-template.md


⸻

5.3 Prompt Building Process

⸻

Step 1 — Load Selected Prompts

Based on user settings:
	•	load base style prompt
	•	load characteristic prompts (3 types)
	•	include custom instructions (if present)
	•	include about user fields (if present)

⸻

Step 2 — Build Personalization Block

Use:

personalization-template.md

Insert:
	•	base style prompt
	•	characteristic prompts
	•	custom instructions
	•	user metadata

⸻

Step 3 — Final Personalization Output

Result:

[PERSONALIZATION PROMPT BLOCK]


⸻

6. Integration into Retrieval Pipeline

⸻

6.1 Placement in Prompt

Personalization must be inserted into prompt building as a system message.

⸻

6.2 Final Prompt Order

Simple Mode

SYSTEM: guardrails
SYSTEM: assistant
SYSTEM: personalization
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

Refine Mode

Draft Step

SYSTEM: guardrails
SYSTEM: assistant-refine-draft
SYSTEM: personalization
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

Refinement Step

SYSTEM: guardrails
SYSTEM: assistant-refine-refining
SYSTEM: personalization
SYSTEM: draft answer
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

6.3 Important Rules
	•	personalization must always be included
	•	must not break existing prompt structure
	•	must be inserted as a separate system block
	•	must not overwrite guardrails or assistant prompts

⸻

7. Backend Data Model

⸻

7.1 User Personalization Table

user_personalization
user_id
base_style
warm_level
enthusiasm_level
headers_lists_level
custom_instructions
nickname
occupation
more_about
updated_at


⸻

7.2 Default Values

If not set:

base_style = default
warm = default
enthusiastic = default
headers_lists = default

All optional fields = null

⸻

8. API Changes

⸻

8.1 Get Personalization

GET /api/user/personalization


⸻

8.2 Update Personalization

PATCH /api/user/personalization


⸻

9. Web UI Requirements

⸻

9.1 Preferences → Personalization Tab

Must match the provided design exactly.

⸻

9.2 UI Components

⸻

Base Style Dropdown
	•	single select
	•	shows current value

⸻

Characteristics Section

Each:
	•	dropdown with:
	•	more
	•	default
	•	less

⸻

Custom Instructions
	•	textarea
	•	persistent

⸻

About You Section

Inputs:
	•	nickname
	•	occupation
	•	more about you

⸻

9.3 Save Behavior
	•	changes must persist immediately or via save button
	•	reflect instantly in backend
	•	applied to next message

⸻

10. Backend Requirements

⸻

10.1 Prompt Builder Extension
	•	must support personalization injection
	•	must dynamically load prompt files
	•	must handle missing/invalid configs safely

⸻

10.2 Prompt Caching (Optional)
	•	cache loaded prompt files
	•	avoid repeated disk reads

⸻

10.3 Validation
	•	ensure valid enum values
	•	sanitize custom instructions

⸻

11. Frontend State Requirements

⸻

Must manage:
	•	personalization state
	•	form state
	•	loading state
	•	update state

⸻

12. Testing & Validation

⸻

12.1 Required Validation

Codex must verify:
	•	personalization settings save correctly
	•	prompt builder includes personalization
	•	different styles produce different outputs
	•	refine + personalization works together
	•	no regression from Step 1–9

⸻

12.2 Edge Cases

Test:
	•	empty personalization
	•	only custom instructions
	•	only base style
	•	all options filled
	•	long custom instructions

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
	•	docs/personalization.md
	•	docs/prompts.md
	•	docs/api.md
	•	docs/testing.md

⸻

14. Acceptance Criteria

⸻

Functionality
	•	personalization settings persist
	•	personalization applied to all chats
	•	prompt includes personalization correctly

⸻

UI
	•	matches design
	•	all fields work
	•	values reflect backend

⸻

Backend
	•	prompt building works correctly
	•	no conflicts with assistant modes

⸻

Quality
	•	tested
	•	debugged
	•	documented

⸻

15. Non-Goals

Do NOT implement:
	•	per-chat personalization
	•	AI-generated personalization
	•	auto-learning preferences
	•	UI preview of tone

⸻

16. Engineering Requirements
	•	clean prompt builder design
	•	modular prompt loading
	•	no hardcoded prompts
	•	maintainable structure
	•	strong typing
	•	validation
	•	changelog updates
	•	full system validation