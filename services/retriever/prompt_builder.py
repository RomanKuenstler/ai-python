from __future__ import annotations

from pathlib import Path


class PromptBuilder:
    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = prompts_dir
        self.guardrails = (prompts_dir / "guardrails.md").read_text(encoding="utf-8").strip()
        self.assistant = (prompts_dir / "assistant.md").read_text(encoding="utf-8").strip()
        self.assistant_refine_draft = (prompts_dir / "assistant-refine-draft.md").read_text(encoding="utf-8").strip()
        self.assistant_refine_refining = (prompts_dir / "assistant-refine-refining.md").read_text(encoding="utf-8").strip()
        self.rag_template = (prompts_dir / "ragcontext.md").read_text(encoding="utf-8").strip()

    def build_simple_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )

    def build_refine_draft_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant_refine_draft,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )

    def build_refine_final_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        draft_answer: str,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        messages = self._build_messages(
            assistant_prompt=self.assistant_refine_refining,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )
        messages.insert(2, ("system", f"[draft answer]\n{draft_answer.strip()}"))
        return messages

    def _build_messages(
        self,
        *,
        assistant_prompt: str,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        evidence_quality = "weak"
        if len(retrieved_chunks) >= 4:
            evidence_quality = "strong"
        elif retrieved_chunks:
            evidence_quality = "moderate"

        evidence_block = "\n\n".join(
            [
                (
                    f"Source: {chunk['file_name']} ({chunk['file_path']})\n"
                    f"Score: {float(chunk['score']):.4f}\n"
                    f"Tags: {', '.join(chunk['tags']) if chunk['tags'] else 'none'}\n"
                    f"Chunk ID: {chunk['chunk_id']}\n"
                    f"Content:\n{chunk['text']}"
                )
                for chunk in retrieved_chunks
            ]
        )

        rag_context = (
            self.rag_template.replace("${evidenceQuality}", evidence_quality)
            .replace("${evidenceBlock || \"No evidence retrieved.\"}", evidence_block or "No evidence retrieved.")
            .replace("${userMessage}", user_message)
        )
        messages: list[tuple[str, str]] = [
            ("system", self.guardrails),
            ("system", assistant_prompt),
            ("system", rag_context),
        ]
        messages.append(("system", self._build_attachment_context(attachments or [], attachment_char_limit)))
        if history:
            history_text = "\n".join(f"{role.upper()}: {content}" for role, content in history)
            messages.append(("system", f"[chat history]\n{history_text}"))
        messages.append(("user", user_message))
        return messages

    def _build_attachment_context(self, attachments: list[dict[str, object]], char_limit: int) -> str:
        if not attachments:
            return "[ATTACHMENT CONTEXT]\nNo attachments provided."

        remaining = max(char_limit, 0)
        rendered: list[str] = []
        for attachment in attachments:
            content = str(attachment.get("content") or "").strip()
            if not content or remaining <= 0:
                continue
            excerpt = content[:remaining]
            remaining -= len(excerpt)
            rendered.append(
                "\n".join(
                    [
                        f"File: {attachment.get('file_name', 'unknown')}",
                        f"Type: {attachment.get('type', 'unknown')}",
                        f"Extraction: {attachment.get('extraction_method') or 'unknown'}",
                        f"Quality: {attachment.get('quality') or {}}",
                        "Content:",
                        excerpt,
                    ]
                )
            )
        if not rendered:
            return "[ATTACHMENT CONTEXT]\nAttachments were provided but no usable text could be extracted."
        return "[ATTACHMENT CONTEXT]\n\n" + "\n\n---\n\n".join(rendered)
