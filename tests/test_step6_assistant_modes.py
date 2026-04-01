from __future__ import annotations

from pathlib import Path

from services.common.config import Settings
from services.retriever.services.retriever_service import RetrieverAppService, RetrieverDependencies


class StubChat:
    def __init__(self, chat_id: str = "chat-1", chat_name: str = "Chat", is_archived: bool = False) -> None:
        self.id = chat_id
        self.chat_name = chat_name
        self.is_archived = is_archived
        self.created_at = "2026-03-30T00:00:00Z"
        self.updated_at = "2026-03-30T00:00:00Z"


class StubMessage:
    def __init__(self, message_id: int, role: str, content: str, has_attachments: bool = False) -> None:
        self.id = message_id
        self.session_id = "chat-1"
        self.role = role
        self.content = content
        self.status = "completed"
        self.has_attachments = has_attachments
        self.created_at = "2026-03-30T00:00:00Z"


class StubRepository:
    def __init__(self) -> None:
        self.messages: list[StubMessage] = []
        self.retrieval_logs: list[dict] = []

    def list_settings(self):
        return []

    def upsert_setting(self, key: str, value: str):
        return None

    def get_chat(self, chat_id: str):
        return StubChat(chat_id=chat_id)

    def create_chat(self, chat_name: str):
        return StubChat(chat_name=chat_name)

    def list_chats(self, *, archived: bool = False):
        return []

    def list_messages(self, chat_id: str):
        return self.messages

    def create_message(self, chat_id: str, role: str, content: str, status: str = "completed", *, has_attachments: bool = False):
        message = StubMessage(len(self.messages) + 1, role, content, has_attachments=has_attachments)
        self.messages.append(message)
        return message

    def add_message_attachments(self, message_id: int, attachments: list[dict[str, object]]):
        return []

    def create_retrieval_logs(self, *, assistant_message_id: int, user_message_id: int, chat_id: str, used_chunks: list[dict]):
        self.retrieval_logs.append(
            {
                "assistant_message_id": assistant_message_id,
                "user_message_id": user_message_id,
                "chat_id": chat_id,
                "used_chunks": used_chunks,
            }
        )

    def get_sources_by_assistant_message(self, assistant_message_ids: list[int]):
        return {}

    def get_attachments_by_message_ids(self, message_ids: list[int]):
        return {}

    def rename_chat(self, chat_id: str, chat_name: str):
        return StubChat(chat_id=chat_id, chat_name=chat_name)

    def delete_chat(self, chat_id: str):
        return StubChat(chat_id=chat_id)

    def set_chat_archived(self, chat_id: str, is_archived: bool):
        return StubChat(chat_id=chat_id, is_archived=is_archived)


class StubHistoryService:
    history_limit = 5

    def fetch(self, session_id: str, exclude_message_id: int | None = None):
        return [("assistant", "Previous answer")]


class StubRetrievalService:
    def __init__(self) -> None:
        self.score_threshold = 0.7
        self.min_results = 2
        self.max_results = 8

    def retrieve(self, query: str):
        return [
            {
                "chunk_id": "chunk-1",
                "file_name": "manual.md",
                "file_path": "/app/data/manual.md",
                "text": "COPY copies files into the image.",
                "score": 0.91,
                "tags": ["docker"],
            }
        ]


class StubPromptBuilder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def build_simple_messages(self, **kwargs):
        self.calls.append(("simple", kwargs))
        return [("system", "simple"), ("user", kwargs["user_message"])]

    def build_refine_draft_messages(self, **kwargs):
        self.calls.append(("refine-draft", kwargs))
        return [("system", "draft"), ("user", kwargs["user_message"])]

    def build_refine_final_messages(self, **kwargs):
        self.calls.append(("refine-final", kwargs))
        return [("system", "final"), ("user", kwargs["user_message"])]

    def build_thinking_plan_messages(self, **kwargs):
        self.calls.append(("thinking-plan", kwargs))
        return [("system", "thinking-plan"), ("user", kwargs["user_message"])]

    def build_thinking_draft_messages(self, **kwargs):
        self.calls.append(("thinking-draft", kwargs))
        return [("system", "thinking-draft"), ("user", kwargs["user_message"])]

    def build_thinking_final_messages(self, **kwargs):
        self.calls.append(("thinking-final", kwargs))
        return [("system", "thinking-final"), ("user", kwargs["user_message"])]


class StubLlmClient:
    def __init__(self) -> None:
        self.calls: list[list[tuple[str, str]]] = []

    def invoke(self, messages: list[tuple[str, str]]) -> str:
        self.calls.append(messages)
        if messages[0][1] == "draft":
            return "Draft answer"
        if messages[0][1] == "thinking-plan":
            return "Plan answer"
        if messages[0][1] == "thinking-draft":
            return "Draft from plan"
        return "Final answer"


class StubLibraryManager:
    def list_files(self):
        return {}


class StubAttachmentClient:
    def process_files(self, files):
        return []


def build_service() -> tuple[RetrieverAppService, StubRepository, StubPromptBuilder, StubLlmClient]:
    repository = StubRepository()
    prompt_builder = StubPromptBuilder()
    llm_client = StubLlmClient()
    settings = Settings(data_dir=str(Path("data")), enable_refine_mode=True, enable_thinking_mode=True, default_assistant_mode="simple")
    service = RetrieverAppService(
        RetrieverDependencies(
            chat_repository=repository,
            history_service=StubHistoryService(),
            retrieval_service=StubRetrievalService(),
            prompt_builder=prompt_builder,
            llm_client=llm_client,
            library_manager=StubLibraryManager(),
            attachment_client=StubAttachmentClient(),
            settings=settings,
        )
    )
    return service, repository, prompt_builder, llm_client


def test_simple_mode_uses_single_generation_pass() -> None:
    service, repository, prompt_builder, llm_client = build_service()

    response = service.send_message("chat-1", "Explain COPY", assistant_mode="simple")

    assert response["assistant_mode"] == "simple"
    assert response["assistant_message"].content == "Final answer"
    assert [call[0] for call in prompt_builder.calls] == ["simple"]
    assert len(llm_client.calls) == 1
    assert repository.messages[-1].role == "assistant"
    assert repository.messages[-1].content == "Final answer"


def test_refine_mode_uses_draft_and_final_passes_but_only_persists_final_message() -> None:
    service, repository, prompt_builder, llm_client = build_service()

    response = service.send_message("chat-1", "Explain COPY", assistant_mode="refine")

    assert response["assistant_mode"] == "refine"
    assert response["assistant_message"].content == "Final answer"
    assert [call[0] for call in prompt_builder.calls] == ["refine-draft", "refine-final"]
    assert len(llm_client.calls) == 2
    assert repository.messages[-1].role == "assistant"
    assert repository.messages[-1].content == "Final answer"
    assert all(message.content != "Draft answer" for message in repository.messages)


def test_thinking_mode_uses_three_generation_passes_and_only_persists_final_message() -> None:
    service, repository, prompt_builder, llm_client = build_service()

    response = service.send_message("chat-1", "Explain COPY", assistant_mode="thinking")

    assert response["assistant_mode"] == "thinking"
    assert response["assistant_message"].content == "Final answer"
    assert [call[0] for call in prompt_builder.calls] == ["thinking-plan", "thinking-draft", "thinking-final"]
    assert prompt_builder.calls[1][1]["planning_result"] == "Plan answer"
    assert prompt_builder.calls[2][1]["planning_result"] == "Plan answer"
    assert prompt_builder.calls[2][1]["draft_answer"] == "Draft from plan"
    assert len(llm_client.calls) == 3
    assert repository.messages[-1].role == "assistant"
    assert repository.messages[-1].content == "Final answer"
    assert all(message.content not in {"Plan answer", "Draft from plan"} for message in repository.messages)


def test_thinking_mode_falls_back_to_simple_when_pipeline_step_fails() -> None:
    service, _repository, prompt_builder, llm_client = build_service()

    def failing_build_thinking_draft_messages(**kwargs):
        prompt_builder.calls.append(("thinking-draft", kwargs))
        raise RuntimeError("draft step failed")

    prompt_builder.build_thinking_draft_messages = failing_build_thinking_draft_messages  # type: ignore[method-assign]

    response = service.send_message("chat-1", "Explain COPY", assistant_mode="thinking")

    assert response["assistant_mode"] == "thinking"
    assert response["assistant_message"].content == "Final answer"
    assert [call[0] for call in prompt_builder.calls] == ["thinking-plan", "thinking-draft", "simple"]
    assert len(llm_client.calls) == 2
