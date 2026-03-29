from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.embedder.embedding import EmbeddingClient
from services.retriever.chat_history import ChatHistoryService
from services.retriever.llm_client import LlmClient
from services.retriever.prompt_builder import PromptBuilder
from services.retriever.qdrant_client import RetrieverQdrantClient
from services.retriever.repositories.chat_repository import ChatRepository
from services.retriever.retriever import RetrievalService
from services.retriever.services.chat_naming import generate_chat_name
from services.retriever.services.message_mapper import map_chat, map_message, map_source


@dataclass(slots=True)
class RetrieverDependencies:
    chat_repository: ChatRepository
    history_service: ChatHistoryService
    retrieval_service: RetrievalService
    prompt_builder: PromptBuilder
    llm_client: LlmClient


class RetrieverAppService:
    def __init__(self, deps: RetrieverDependencies) -> None:
        self.chat_repository = deps.chat_repository
        self.history_service = deps.history_service
        self.retrieval_service = deps.retrieval_service
        self.prompt_builder = deps.prompt_builder
        self.llm_client = deps.llm_client

    def create_chat(self):
        chat = self.chat_repository.create_chat(generate_chat_name())
        return map_chat(chat)

    def list_chats(self):
        return [map_chat(chat) for chat in self.chat_repository.list_chats()]

    def get_chat(self, chat_id: str):
        chat = self.chat_repository.get_chat(chat_id)
        if chat is None:
            return None
        return map_chat(chat)

    def get_chat_messages(self, chat_id: str):
        messages = self.chat_repository.list_messages(chat_id)
        assistant_ids = [message.id for message in messages if message.role == "assistant"]
        sources_by_message = self.chat_repository.get_sources_by_assistant_message(assistant_ids)
        return [map_message(message, sources_by_message.get(message.id)) for message in messages]

    def send_message(self, chat_id: str, user_content: str):
        chat = self.chat_repository.get_chat(chat_id)
        if chat is None:
            return None

        user_message = self.chat_repository.create_message(chat_id, "user", user_content)
        history = self.history_service.fetch(chat_id, exclude_message_id=user_message.id)
        retrieved_chunks = self.retrieval_service.retrieve(user_content)
        prompt_messages = self.prompt_builder.build_messages(
            user_message=user_content,
            history=history,
            retrieved_chunks=retrieved_chunks,
        )
        response = self.llm_client.invoke(prompt_messages)
        assistant_message = self.chat_repository.create_message(chat_id, "assistant", response)
        self.chat_repository.create_retrieval_logs(
            assistant_message_id=assistant_message.id,
            user_message_id=user_message.id,
            chat_id=chat_id,
            used_chunks=retrieved_chunks,
        )

        return {
            "chat_id": chat_id,
            "user_message": map_message(user_message),
            "assistant_message": map_message(assistant_message),
            "sources": [map_source_from_chunk(chunk) for chunk in retrieved_chunks],
        }


def build_retriever_app_service(
    *,
    database_url: str,
    embedding_model: str,
    embedding_base_url: str,
    embedding_api_key: str,
    embedding_max_input_tokens: int,
    qdrant_url: str,
    qdrant_collection: str,
    retrieval_score_threshold: float,
    retrieval_min_results: int,
    retrieval_max_results: int,
    llm_model: str,
    llm_base_url: str,
    llm_api_key: str,
    prompts_dir: Path,
    history_limit: int,
) -> RetrieverAppService:
    from services.retriever.postgres_client import RetrieverPostgresClient

    postgres_client = RetrieverPostgresClient(database_url)
    postgres_client.initialize()
    chat_repository = ChatRepository(postgres_client)
    deps = RetrieverDependencies(
        chat_repository=chat_repository,
        history_service=ChatHistoryService(postgres_client, history_limit),
        retrieval_service=RetrievalService(
            embedding_client=EmbeddingClient(
                model=embedding_model,
                base_url=embedding_base_url,
                api_key=embedding_api_key,
                max_input_tokens=embedding_max_input_tokens,
            ),
            qdrant_store=RetrieverQdrantClient(qdrant_url, qdrant_collection),
            score_threshold=retrieval_score_threshold,
            min_results=retrieval_min_results,
            max_results=retrieval_max_results,
        ),
        prompt_builder=PromptBuilder(prompts_dir),
        llm_client=LlmClient(model=llm_model, base_url=llm_base_url, api_key=llm_api_key),
    )
    return RetrieverAppService(deps)


def map_source_from_chunk(chunk: dict[str, str | float | list[str] | None]):
    return map_source(
        RetrievalLogProxy(
            chunk_id=str(chunk.get("chunk_id", "")),
            source_file_name=str(chunk.get("file_name", "")),
            source_file_path=str(chunk.get("file_path", "")),
            chunk_title=_to_optional_str(chunk.get("title")),
            chapter=_to_optional_str(chunk.get("chapter")),
            section=_to_optional_str(chunk.get("section")),
            page_number=chunk.get("page_number"),
            tags=list(chunk.get("tags", []) or []),
            retrieval_score=float(chunk.get("score", 0.0) or 0.0),
        )
    )


class RetrievalLogProxy:
    def __init__(
        self,
        *,
        chunk_id: str,
        source_file_name: str,
        source_file_path: str,
        chunk_title: str | None,
        chapter: str | None,
        section: str | None,
        page_number: int | None,
        tags: list[str],
        retrieval_score: float,
    ) -> None:
        self.chunk_id = chunk_id
        self.source_file_name = source_file_name
        self.source_file_path = source_file_path
        self.chunk_title = chunk_title
        self.chapter = chapter
        self.section = section
        self.page_number = page_number
        self.tags = tags
        self.retrieval_score = retrieval_score


def _to_optional_str(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None
