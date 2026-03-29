from __future__ import annotations

from pathlib import Path


class PromptBuilder:
    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = prompts_dir
        self.guardrails = (prompts_dir / "guardrails.md").read_text(encoding="utf-8").strip()
        self.assistant = (prompts_dir / "assistant.md").read_text(encoding="utf-8").strip()
        self.rag_template = (prompts_dir / "ragcontext.md").read_text(encoding="utf-8").strip()

    def build_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
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
            ("system", self.assistant),
            ("system", rag_context),
        ]
        if history:
            history_text = "\n".join(f"{role.upper()}: {content}" for role, content in history)
            messages.append(("system", history_text))
        messages.append(("user", user_message))
        return messages
