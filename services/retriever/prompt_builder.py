from __future__ import annotations

from pathlib import Path
from typing import Any


class PromptBuilder:
    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = prompts_dir
        self.guardrails = (prompts_dir / "guardrails.md").read_text(encoding="utf-8").strip()
        self.assistant = (prompts_dir / "assistant.md").read_text(encoding="utf-8").strip()
        self.assistant_refine_draft = (prompts_dir / "assistant-refine-draft.md").read_text(encoding="utf-8").strip()
        self.assistant_refine_refining = (prompts_dir / "assistant-refine-refining.md").read_text(encoding="utf-8").strip()
        self.assistant_thinking_plan = (prompts_dir / "assistant-thinking-analyse-plan.md").read_text(encoding="utf-8").strip()
        self.assistant_thinking_draft = (prompts_dir / "assistant-thinking-draft.md").read_text(encoding="utf-8").strip()
        self.assistant_thinking_refining = (prompts_dir / "assistant-thinking-refining.md").read_text(encoding="utf-8").strip()
        self.rag_template = (prompts_dir / "ragcontext.md").read_text(encoding="utf-8").strip()
        self.personalization_template = (prompts_dir / "personalization-template.md").read_text(encoding="utf-8").strip()
        self.personalization_custom_instructions_template = (
            prompts_dir / "personalization-custom-user-instructions-template.md"
        ).read_text(encoding="utf-8").strip()
        self.personalization_more_about_user_template = (
            prompts_dir / "personalization-more-about-user-template.md"
        ).read_text(encoding="utf-8").strip()
        self.personalization_nickname_template = (
            prompts_dir / "personalization-nickname-template.md"
        ).read_text(encoding="utf-8").strip()
        self.personalization_occupation_template = (
            prompts_dir / "personalization-occupation-template.md"
        ).read_text(encoding="utf-8").strip()
        self.personalization_base_style_prompts = {
            style: (prompts_dir / f"personalization-base-style-{style}.md").read_text(encoding="utf-8").strip()
            for style in ("default", "professional", "friendly", "direct", "quirky", "efficient", "sceptical")
        }
        self.personalization_characteristic_prompts = {
            characteristic: {
                level: (prompts_dir / f"personalization-characteristic-{characteristic}-{level}.md")
                .read_text(encoding="utf-8")
                .strip()
                for level in ("more", "default", "less")
            }
            for characteristic in ("warm", "enthusiastic", "headers-and-lists")
        }

    def build_simple_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )

    def build_refine_draft_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant_refine_draft,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
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
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
        ) -> list[tuple[str, str]]:
        messages = self._build_messages(
            assistant_prompt=self.assistant_refine_refining,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
            previous_step_outputs=[("draft answer", draft_answer)],
        )
        return messages

    def build_thinking_plan_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant_thinking_plan,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )

    def build_thinking_draft_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        planning_result: str,
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant_thinking_draft,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
            previous_step_outputs=[("planning result", planning_result)],
        )

    def build_thinking_final_messages(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        planning_result: str,
        draft_answer: str,
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
    ) -> list[tuple[str, str]]:
        return self._build_messages(
            assistant_prompt=self.assistant_thinking_refining,
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
            previous_step_outputs=[("planning result", planning_result), ("draft answer", draft_answer)],
        )

    def _build_messages(
        self,
        *,
        assistant_prompt: str,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str]]],
        personalization: dict[str, Any] | None = None,
        attachments: list[dict[str, object]] | None = None,
        attachment_char_limit: int = 15000,
        previous_step_outputs: list[tuple[str, str]] | None = None,
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
            ("system", self.build_personalization_block(personalization or {})),
        ]
        for label, content in previous_step_outputs or []:
            messages.append(("system", f"[{label}]\n{content.strip()}"))
        messages.append(("system", rag_context))
        messages.append(("system", self._build_attachment_context(attachments or [], attachment_char_limit)))
        if history:
            history_text = "\n".join(f"{role.upper()}: {content}" for role, content in history)
            messages.append(("system", f"[chat history]\n{history_text}"))
        messages.append(("user", user_message))
        return messages

    def build_personalization_block(self, personalization: dict[str, Any]) -> str:
        base_style = str(personalization.get("base_style") or "default").strip().lower()
        warm = str(personalization.get("warm") or "default").strip().lower()
        enthusiastic = str(personalization.get("enthusiastic") or "default").strip().lower()
        headers_and_lists = str(personalization.get("headers_and_lists") or "default").strip().lower()
        custom_instructions = str(personalization.get("custom_instructions") or "").strip()
        nickname = str(personalization.get("nickname") or "").strip()
        occupation = str(personalization.get("occupation") or "").strip()
        more_about_user = str(personalization.get("more_about_user") or "").strip()

        base_style_text = self.personalization_base_style_prompts.get(
            base_style,
            self.personalization_base_style_prompts["default"],
        )
        characteristics = "\n\n".join(
            [
                "\n".join(
                    [
                        "Warm:",
                        self.personalization_characteristic_prompts["warm"].get(
                            warm,
                            self.personalization_characteristic_prompts["warm"]["default"],
                        ),
                    ]
                ),
                "\n".join(
                    [
                        "Enthusiastic:",
                        self.personalization_characteristic_prompts["enthusiastic"].get(
                            enthusiastic,
                            self.personalization_characteristic_prompts["enthusiastic"]["default"],
                        ),
                    ]
                ),
                "\n".join(
                    [
                        "Headers and Lists:",
                        self.personalization_characteristic_prompts["headers-and-lists"].get(
                            headers_and_lists,
                            self.personalization_characteristic_prompts["headers-and-lists"]["default"],
                        ),
                    ]
                ),
            ]
        )

        if custom_instructions:
            custom_instructions_text = self.personalization_custom_instructions_template.replace(
                "{USER_CUSTOM_INSTRUCTIONS}",
                custom_instructions,
            )
        else:
            custom_instructions_text = "No additional custom instructions provided."

        about_user_parts: list[str] = []
        if nickname:
            about_user_parts.append(self.personalization_nickname_template.replace("{NICKNAME}", nickname))
        if occupation:
            about_user_parts.append(self.personalization_occupation_template.replace("{OCCUPATION}", occupation))
        if more_about_user:
            about_user_parts.append(
                self.personalization_more_about_user_template.replace("{ABOUT_USER_TEXT}", more_about_user)
            )
        about_user_text = "\n\n".join(about_user_parts) if about_user_parts else "No additional user background provided."

        return (
            self.personalization_template.replace("{BASE_STYLE}", base_style_text)
            .replace("{CHARACTERISTICS}", characteristics)
            .replace("{CUSTOM_INSTRUCTIONS}", custom_instructions_text)
            .replace("{ABOUT_USER}", about_user_text)
        )

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
