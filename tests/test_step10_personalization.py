from __future__ import annotations

import json
from pathlib import Path

from services.common.config import Settings
from services.common.models import UserAccount
from services.retriever.prompt_builder import PromptBuilder
from services.retriever.services.retriever_service import RetrieverAppService, RetrieverDependencies


class SettingRecordStub:
    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value


class PersonalizationRepositoryStub:
    def __init__(self) -> None:
        self.settings: dict[tuple[int, str], str] = {}

    def list_settings(self, user_id: int):
        return [SettingRecordStub(key=key, value=value) for (stored_user_id, key), value in self.settings.items() if stored_user_id == user_id]

    def upsert_setting(self, user_id: int, key: str, value: str):
        self.settings[(user_id, key)] = value
        return SettingRecordStub(key=key, value=value)


class HistoryServiceStub:
    history_limit = 5


class RetrievalServiceStub:
    min_results = 2
    max_results = 8
    score_threshold = 0.7


class LlmClientStub:
    def invoke(self, messages):
        return "ok"


class LibraryManagerStub:
    pass


class AttachmentClientStub:
    def process_files(self, files):
        return []


def build_service(repository: PersonalizationRepositoryStub) -> RetrieverAppService:
    settings = Settings(data_dir=str(Path("data")), enable_refine_mode=True, enable_thinking_mode=True, default_assistant_mode="simple")
    return RetrieverAppService(
        RetrieverDependencies(
            chat_repository=repository,
            history_service=HistoryServiceStub(),
            retrieval_service=RetrievalServiceStub(),
            prompt_builder=PromptBuilder(Path("prompts")),
            llm_client=LlmClientStub(),
            library_manager=LibraryManagerStub(),
            attachment_client=AttachmentClientStub(),
            settings=settings,
        )
    )


def build_user() -> UserAccount:
    return UserAccount(
        id=1,
        username="john",
        displayname="John",
        password_hash="hash",
        role="user",
        status="active",
        force_password_change=False,
    )


def test_personalization_defaults_and_updates_round_trip() -> None:
    repository = PersonalizationRepositoryStub()
    service = build_service(repository)
    user = build_user()

    defaults = service.get_personalization(user)
    assert defaults.base_style == "default"
    assert defaults.nickname == ""

    updated = service.update_personalization(
        user,
        payload=defaults.model_copy(
            update={
                "base_style": "friendly",
                "warm": "more",
                "nickname": "Rik",
                "occupation": "Engineer",
                "custom_instructions": "Keep it practical.",
            }
        ),
    )

    assert updated.base_style == "friendly"
    assert updated.warm == "more"
    assert updated.nickname == "Rik"
    assert json.loads(repository.settings[(1, "custom_instructions")]) == "Keep it practical."


def test_prompt_builder_inserts_personalization_before_rag_context() -> None:
    builder = PromptBuilder(Path("prompts"))

    messages = builder.build_refine_final_messages(
        user_message="How does COPY work?",
        history=[("assistant", "Previous answer")],
        retrieved_chunks=[
            {
                "chunk_id": "chunk-1",
                "file_name": "manual.md",
                "file_path": "/app/data/manual.md",
                "text": "COPY copies files into the image.",
                "score": 0.91,
                "tags": ["docker"],
            }
        ],
        draft_answer="Draft response",
        personalization={
            "base_style": "professional",
            "warm": "less",
            "enthusiastic": "less",
            "headers_and_lists": "more",
            "custom_instructions": "Use concise examples.",
            "nickname": "Rik",
            "occupation": "Engineer",
            "more_about_user": "Works with Docker daily.",
        },
    )

    assert [message[0] for message in messages[:5]] == ["system", "system", "system", "system", "system"]
    assert messages[2][1].startswith("# Personalization")
    assert "Use a polished, precise, and professional tone." in messages[2][1]
    assert "The user prefers to be addressed as: Rik." in messages[2][1]
    assert messages[3][1] == "[draft answer]\nDraft response"
    assert "# Retrieved Evidence" in messages[4][1]


def test_thinking_prompt_builder_inserts_previous_step_outputs_before_rag_context() -> None:
    builder = PromptBuilder(Path("prompts"))

    messages = builder.build_thinking_final_messages(
        user_message="How does COPY work?",
        history=[("assistant", "Previous answer")],
        retrieved_chunks=[
            {
                "chunk_id": "chunk-1",
                "file_name": "manual.md",
                "file_path": "/app/data/manual.md",
                "text": "COPY copies files into the image.",
                "score": 0.91,
                "tags": ["docker"],
            }
        ],
        planning_result="Question\n- Explain COPY",
        draft_answer="COPY copies files into the image.",
        personalization={
            "base_style": "professional",
            "warm": "less",
            "enthusiastic": "less",
            "headers_and_lists": "more",
            "custom_instructions": "Use concise examples.",
            "nickname": "Rik",
            "occupation": "Engineer",
            "more_about_user": "Works with Docker daily.",
        },
    )

    assert [message[0] for message in messages[:6]] == ["system", "system", "system", "system", "system", "system"]
    assert messages[2][1].startswith("# Personalization")
    assert messages[3][1] == "[planning result]\nQuestion\n- Explain COPY"
    assert messages[4][1] == "[draft answer]\nCOPY copies files into the image."
    assert "# Retrieved Evidence" in messages[5][1]
