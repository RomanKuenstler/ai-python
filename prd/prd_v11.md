prd_v11.md — Local RAG System (Step 11)

⸻

1. Overview

1.1 Goal

Introduce a third assistant mode:

thinking

This mode implements a three-step reasoning pipeline:
	1.	planning (analysis)
	2.	drafting
	3.	refining

⸻

2. Step 11 Scope

This step introduces:
	•	new assistant mode: thinking
	•	multi-step reasoning pipeline (3 stages)
	•	new prompt templates for each stage
	•	integration into retriever pipeline
	•	UI support for selecting the new mode

⸻

3. Assistant Modes (Updated)

⸻

3.1 Existing Modes
	•	simple → single-step
	•	refine → two-step

⸻

3.2 New Mode: thinking

Description

A three-step reasoning pipeline:

planning → drafting → refining → final answer


⸻

4. Thinking Mode Pipeline

⸻

4.1 Step 1 — Planning (Analysis)

Prompt File

prompts/assistant-thinking-analyse-plan.md


⸻

Prompt Structure

SYSTEM: guardrails
SYSTEM: assistant-thinking-analyse-plan
SYSTEM: personalization
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

Output

planning_result

This is:
	•	structured reasoning
	•	analysis
	•	plan for answering

⸻

4.2 Step 2 — Drafting

Prompt File

prompts/assistant-thinking-draft.md


⸻

Prompt Structure

SYSTEM: guardrails
SYSTEM: assistant-thinking-draft
SYSTEM: personalization
SYSTEM: planning_result
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

Output

draft_result


⸻

4.3 Step 3 — Refining

Prompt File

prompts/assistant-thinking-refining.md


⸻

Prompt Structure

SYSTEM: guardrails
SYSTEM: assistant-thinking-refining
SYSTEM: personalization
SYSTEM: planning_result
SYSTEM: draft_result
SYSTEM: ragcontext
SYSTEM: chat history
USER: user prompt


⸻

Output

final_answer


⸻

4.4 Output Rules
	•	ONLY the final_answer is returned to the UI
	•	planning_result and draft_result are NOT shown to the user
	•	optional debug logging allowed (not exposed in UI)

⸻

5. Retrieval Strategy

⸻

5.1 Recommended Approach

Perform retrieval:
	•	once at the beginning
	•	reuse across all steps

⸻

5.2 RAG Context Consistency

The same retrieved knowledge must be:
	•	used in planning
	•	reused in drafting
	•	reused in refining

⸻

5.3 Important Rule

Do NOT re-run retrieval between steps unless explicitly required in future steps.

⸻

6. Prompt Integration Rules

⸻

6.1 Personalization

Personalization must be included in ALL three steps.

⸻

6.2 Guardrails

Guardrails must be included in ALL steps.

⸻

6.3 Prompt Order Consistency

Keep consistent structure:
	•	guardrails first
	•	mode-specific prompt
	•	personalization
	•	previous step outputs
	•	rag context
	•	chat history
	•	user prompt

⸻

7. Backend Changes

⸻

7.1 Retriever Pipeline

Extend retriever logic:

if mode == simple → existing
if mode == refine → existing
if mode == thinking → new pipeline


⸻

7.2 Pipeline Implementation

Create modular functions:

run_thinking_pipeline()
  → run_planning()
  → run_drafting()
  → run_refining()


⸻

7.3 Data Flow

planning_result → drafting → refining → final_answer


⸻

7.4 Error Handling

If a step fails:
	•	fail gracefully
	•	fallback to simpler pipeline OR return error

⸻

8. Web UI Changes

⸻

8.1 Assistant Mode Selector

Add new option:

thinking


⸻

8.2 Behavior
	•	selectable per message
	•	sent to backend as:

{
  "assistant_mode": "thinking"
}


⸻

8.3 UI Consistency
	•	same dropdown/selector as existing modes
	•	no new UI components needed

⸻

9. API Changes

⸻

9.1 Message Endpoint

Already supports:

{
  "assistant_mode": "simple | refine | thinking"
}

No structural change needed.

⸻

10. Logging & Debugging

⸻

10.1 Optional Debug Logs

System may log:
	•	planning_result
	•	draft_result

For debugging purposes.

⸻

10.2 Must NOT:
	•	expose intermediate steps to user
	•	leak internal reasoning in UI

⸻

11. Performance Considerations

⸻

11.1 Latency Impact

Thinking mode introduces:
	•	3 LLM calls instead of 1 or 2

⸻

11.2 Acceptable Tradeoff
	•	higher latency
	•	higher quality responses

⸻

11.3 Future Optimization (not in this step)
	•	streaming
	•	partial responses
	•	caching

⸻

12. Testing & Validation

⸻

12.1 Required Validation

Codex must verify:
	•	thinking mode executes all 3 steps
	•	planning feeds into drafting
	•	drafting feeds into refining
	•	final answer returned correctly
	•	intermediate outputs not exposed
	•	personalization applied correctly
	•	rag context applied consistently
	•	no regression from Step 1–10

⸻

12.2 Edge Cases

Test:
	•	empty rag context
	•	long planning outputs
	•	large chat history
	•	personalization + thinking combined

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
	•	docs/assistant-modes.md
	•	docs/thinking-mode.md
	•	docs/prompts.md
	•	docs/api.md
	•	docs/testing.md

⸻

14. Acceptance Criteria

⸻

Functionality
	•	thinking mode works end-to-end
	•	correct 3-step pipeline executed

⸻

Integration
	•	works with personalization
	•	works with rag retrieval
	•	works with chat history

⸻

UI
	•	mode selectable
	•	behaves like other modes

⸻

Quality
	•	tested
	•	debugged
	•	documented

⸻

15. Non-Goals

Do NOT implement:
	•	streaming intermediate steps
	•	UI for showing reasoning
	•	adaptive step skipping
	•	dynamic planning loops

⸻

16. Engineering Requirements
	•	modular pipeline design
	•	reusable prompt builder
	•	no duplicated logic
	•	clean separation of steps
	•	strong typing
	•	maintainable structure
	•	changelog updates
	•	full validation before completion