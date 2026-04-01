# Prompts

## Core Prompt Files

- `prompts/guardrails.md`: shared system guardrails used by every assistant mode
- `prompts/ragcontext.md`: shared retrieved-evidence template
- `prompts/assistant.md`: single-pass `simple` mode prompt

## Refine Mode Prompt Files

- `prompts/assistant-refine-draft.md`
- `prompts/assistant-refine-refining.md`

`refine` uses the draft output from the first file as an additional system block for the second file.

## Thinking Mode Prompt Files

- `prompts/assistant-thinking-analyse-plan.md`
- `prompts/assistant-thinking-draft.md`
- `prompts/assistant-thinking-refining.md`

`thinking` uses:

- `planning_result` from the planning prompt in the drafting and refining prompts
- `draft_result` from the drafting prompt in the refining prompt

## Shared Prompt Composition

The prompt builder composes prompts in this order:

1. guardrails
2. mode-specific prompt
3. personalization block
4. previous step outputs, when present
5. RAG context
6. attachment context
7. chat history
8. user prompt

This keeps retrieval evidence, personalization, and chat context consistent across `simple`, `refine`, and `thinking`.
