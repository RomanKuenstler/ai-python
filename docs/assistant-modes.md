# Assistant Modes

Step 6 adds per-message assistant mode selection.

## Available Modes

- `simple`: the existing one-pass RAG flow using `prompts/assistant.md`
- `refine`: a two-step flow using `prompts/assistant-refine-draft.md` and `prompts/assistant-refine-refining.md`

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

## Configuration

- `DEFAULT_ASSISTANT_MODE=simple`
- `ENABLE_REFINE_MODE=true`
