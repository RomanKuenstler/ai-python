# Assistant Modes

Step 11 keeps per-message assistant mode selection and adds a third multi-step pipeline.

## Available Modes

- `simple`: the existing one-pass RAG flow using `prompts/assistant.md`
- `refine`: a two-step flow using `prompts/assistant-refine-draft.md` and `prompts/assistant-refine-refining.md`
- `thinking`: a three-step flow using `prompts/assistant-thinking-analyse-plan.md`, `prompts/assistant-thinking-draft.md`, and `prompts/assistant-thinking-refining.md`

## Refine Pipeline

1. Retrieve evidence once.
2. Build a draft prompt with guardrails, refine-draft instructions, RAG context, attachment context, and chat history.
3. Generate a draft answer.
4. Build a second prompt with guardrails, refine-refining instructions, the draft answer, the same RAG context, attachment context, and chat history.
5. Generate the final answer returned to the UI.

Rules:

- only the final answer is stored as the assistant message
- the draft is not persisted
- the same retrieved chunks are reused for both stages

## Thinking Pipeline

1. Retrieve evidence once.
2. Build a planning prompt with guardrails, thinking-plan instructions, personalization, the shared RAG context, attachment context, and chat history.
3. Generate `planning_result`.
4. Build a drafting prompt with the same evidence plus `planning_result`.
5. Generate `draft_result`.
6. Build a refining prompt with the same evidence plus `planning_result` and `draft_result`.
7. Generate the final answer returned to the UI.

Rules:

- only the final answer is stored as the assistant message
- `planning_result` and `draft_result` are never exposed in the UI
- the same retrieved chunks are reused for all three stages
- if the thinking pipeline fails, the backend falls back to the simple pipeline for a graceful response

## Configuration

- `DEFAULT_ASSISTANT_MODE=simple`
- `ENABLE_REFINE_MODE=true`
- `ENABLE_THINKING_MODE=true`
