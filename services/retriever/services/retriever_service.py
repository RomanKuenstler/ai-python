from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from services.common.config import Settings
from services.common.models import UserAccount
from services.embedder.chunking import Chunker
from services.embedder.embedding import EmbeddingClient
from services.embedder.postgres_client import EmbedderPostgresClient
from services.embedder.processor import FileProcessor
from services.embedder.qdrant_client import EmbedderQdrantClient
from services.retriever.attachment_client import AttachmentProcessingClient
from services.retriever.auth import AuthContext, AuthManager
from services.retriever.chat_history import ChatHistoryService
from services.retriever.llm_client import LlmClient
from services.retriever.prompt_builder import PromptBuilder
from services.retriever.qdrant_client import RetrieverQdrantClient
from services.retriever.repositories.chat_repository import ChatRepository
from services.retriever.retriever import RetrievalService
from services.retriever.schemas.auth import AdminUserRead, AuthLoginResponse, AuthMeResponse, PasswordChangeResponse
from services.retriever.schemas.chat import (
    ChatDownloadMessageRead,
    ChatDownloadResponse,
    PersonalizationRead,
    PersonalizationUpdateRequest,
    SettingsRead,
    SettingsUpdateRequest,
)
from services.retriever.services.chat_naming import generate_chat_name
from services.retriever.services.library_manager import LibraryManager, UploadFilePayload
from services.retriever.services.message_mapper import map_attachment, map_chat, map_filter_file, map_filter_tag, map_message, map_source

RUNTIME_SETTING_KEYS = {
    "chat_history_messages_count",
    "max_similarities",
    "min_similarities",
    "similarity_score_threshold",
}

PERSONALIZATION_DEFAULTS = {
    "base_style": "default",
    "warm": "default",
    "enthusiastic": "default",
    "headers_and_lists": "default",
    "custom_instructions": "",
    "nickname": "",
    "occupation": "",
    "more_about_user": "",
}

PERSONALIZATION_SETTING_KEYS = set(PERSONALIZATION_DEFAULTS)
logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RetrieverDependencies:
    chat_repository: ChatRepository
    history_service: ChatHistoryService
    retrieval_service: RetrievalService
    prompt_builder: PromptBuilder
    llm_client: LlmClient
    library_manager: LibraryManager
    attachment_client: AttachmentProcessingClient
    settings: Settings
    auth_manager: AuthManager | None = None


class RetrieverAppService:
    def __init__(self, deps: RetrieverDependencies) -> None:
        self.chat_repository = deps.chat_repository
        self.history_service = deps.history_service
        self.retrieval_service = deps.retrieval_service
        self.prompt_builder = deps.prompt_builder
        self.llm_client = deps.llm_client
        self.library_manager = deps.library_manager
        self.attachment_client = deps.attachment_client
        self.auth_manager = deps.auth_manager
        self.settings = deps.settings
        if self.auth_manager is not None:
            self.auth_manager.bootstrap_users()

    def login(self, username: str, password: str) -> AuthLoginResponse:
        assert self.auth_manager is not None
        return self.auth_manager.login(username, password)

    def me(self, auth: AuthContext) -> AuthMeResponse:
        assert self.auth_manager is not None
        return self.auth_manager.me(auth)

    def logout(self, auth: AuthContext) -> None:
        assert self.auth_manager is not None
        self.auth_manager.logout(auth.session.id)

    def change_password(self, auth: AuthContext, *, current_password: str | None, new_password: str, confirm_password: str) -> PasswordChangeResponse:
        assert self.auth_manager is not None
        return self.auth_manager.change_password(
            auth=auth,
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password,
        )

    def list_admin_users(self, auth: AuthContext) -> list[AdminUserRead]:
        assert self.auth_manager is not None
        self.auth_manager.require_admin(auth)
        return self.auth_manager.list_users()

    def create_admin_user(self, auth: AuthContext, *, username: str, displayname: str, role: str) -> AdminUserRead:
        assert self.auth_manager is not None
        self.auth_manager.require_admin(auth)
        return self.auth_manager.create_user(username=username, displayname=displayname, role=role)

    def update_admin_user(self, auth: AuthContext, user_id: int, **fields: object) -> AdminUserRead | None:
        assert self.auth_manager is not None
        self.auth_manager.require_admin(auth)
        if auth.user.id == user_id and fields.get("status") == "inactive":
            raise ValueError("Admin cannot deactivate own account")
        return self.auth_manager.update_user(user_id, **fields)

    def delete_admin_user(self, auth: AuthContext, user_id: int) -> AdminUserRead | None:
        assert self.auth_manager is not None
        self.auth_manager.require_admin(auth)
        return self.auth_manager.delete_user(actor=auth, user_id=user_id)

    def create_chat(self, user: UserAccount):
        chat = self.chat_repository.create_chat(user.id, generate_chat_name())
        return map_chat(chat)

    def list_chats(self, user: UserAccount):
        return [map_chat(chat) for chat in self.chat_repository.list_chats(user.id, archived=False)]

    def list_archived_chats(self, user: UserAccount):
        return [map_chat(chat) for chat in self.chat_repository.list_chats(user.id, archived=True)]

    def get_chat(self, user: UserAccount, chat_id: str):
        chat = self.chat_repository.get_chat(user.id, chat_id)
        if chat is None:
            return None
        return map_chat(chat)

    def get_chat_messages(self, user: UserAccount, chat_id: str):
        messages = self.chat_repository.list_messages(user.id, chat_id)
        assistant_ids = [message.id for message in messages if message.role == "assistant"]
        message_ids = [message.id for message in messages]
        sources_by_message = self.chat_repository.get_sources_by_assistant_message(user.id, assistant_ids)
        attachments_by_message = self.chat_repository.get_attachments_by_message_ids(message_ids)
        return [
            map_message(message, sources_by_message.get(message.id)).model_copy(
                update={"attachments": [map_attachment(item) for item in attachments_by_message.get(message.id, [])]}
            )
            for message in messages
        ]

    def rename_chat(self, user: UserAccount, chat_id: str, chat_name: str):
        normalized_name = chat_name.strip()
        if not normalized_name:
            raise ValueError("Chat name cannot be empty")
        chat = self.chat_repository.rename_chat(user.id, chat_id, normalized_name)
        if chat is None:
            return None
        return map_chat(chat)

    def delete_chat(self, user: UserAccount, chat_id: str):
        chat = self.chat_repository.delete_chat(user.id, chat_id)
        if chat is None:
            return None
        return map_chat(chat)

    def archive_chat(self, user: UserAccount, chat_id: str):
        chat = self.chat_repository.set_chat_archived(user.id, chat_id, True)
        if chat is None:
            return None
        return map_chat(chat)

    def unarchive_chat(self, user: UserAccount, chat_id: str):
        chat = self.chat_repository.set_chat_archived(user.id, chat_id, False)
        if chat is None:
            return None
        return map_chat(chat)

    def download_chat(self, user: UserAccount, chat_id: str):
        chat = self.chat_repository.get_chat(user.id, chat_id)
        if chat is None:
            return None

        messages = self.chat_repository.list_messages(user.id, chat_id)
        assistant_ids = [message.id for message in messages if message.role == "assistant"]
        message_ids = [message.id for message in messages]
        sources_by_message = self.chat_repository.get_sources_by_assistant_message(user.id, assistant_ids)
        attachments_by_message = self.chat_repository.get_attachments_by_message_ids(message_ids)

        return ChatDownloadResponse(
            chat_id=chat.id,
            chat_name=chat.chat_name,
            is_archived=chat.is_archived,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages=[
                ChatDownloadMessageRead(
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                    sources=[map_source(log) for log in sources_by_message.get(message.id, [])],
                    attachments=[map_attachment(item) for item in attachments_by_message.get(message.id, [])],
                )
                for message in messages
            ],
        )

    def list_library_files(self, user: UserAccount):
        return self.library_manager.list_files(user)

    def update_library_file(self, user: UserAccount, file_id: int, *, is_enabled: bool):
        return self.library_manager.update_file_state(user, file_id, is_enabled=is_enabled)

    def delete_library_file(self, user: UserAccount, file_id: int):
        return self.library_manager.delete_file(user, file_id)

    def upload_library_files(self, user: UserAccount, uploads: list[UploadFilePayload], tags_by_file_raw: str | None):
        tags_by_file = self.library_manager.parse_tags_mapping(tags_by_file_raw)
        files = self.library_manager.upload_files(user, uploads, tags_by_file)
        return {"files": files}

    def list_user_file_filters(self, user: UserAccount):
        return {"files": [map_filter_file(item) for item in self.chat_repository.list_user_file_filters(user.id)]}

    def update_user_file_filter(self, user: UserAccount, file_id: int, *, is_enabled: bool):
        record = self.chat_repository.set_user_file_filter(user.id, file_id, is_enabled)
        if record is None:
            return None
        return map_filter_file(record)

    def list_chat_file_filters(self, user: UserAccount, chat_id: str):
        records = self.chat_repository.list_chat_file_filters(user.id, chat_id)
        if records is None:
            return None
        return {"files": [map_filter_file(item) for item in records]}

    def update_chat_file_filter(self, user: UserAccount, chat_id: str, file_id: int, *, is_enabled: bool):
        record = self.chat_repository.set_chat_file_filter(user.id, chat_id, file_id, is_enabled)
        if record is None:
            return None
        return map_filter_file(record)

    def list_user_tag_filters(self, user: UserAccount):
        return {"tags": [map_filter_tag(item) for item in self.chat_repository.list_user_tag_filters(user.id)]}

    def update_user_tag_filter(self, user: UserAccount, tag: str, *, is_enabled: bool):
        record = self.chat_repository.set_user_tag_filter(user.id, tag, is_enabled)
        if record is None:
            return None
        return map_filter_tag(record)

    def list_chat_tag_filters(self, user: UserAccount, chat_id: str):
        records = self.chat_repository.list_chat_tag_filters(user.id, chat_id)
        if records is None:
            return None
        return {"tags": [map_filter_tag(item) for item in records]}

    def update_chat_tag_filter(self, user: UserAccount, chat_id: str, tag: str, *, is_enabled: bool):
        record = self.chat_repository.set_chat_tag_filter(user.id, chat_id, tag, is_enabled)
        if record is None:
            return None
        return map_filter_tag(record)

    def get_settings(self, user: UserAccount) -> SettingsRead:
        self._load_runtime_settings(user)
        return SettingsRead(
            chat_history_messages_count=self.history_service.history_limit,
            max_similarities=self.retrieval_service.max_results,
            min_similarities=self.retrieval_service.min_results,
            similarity_score_threshold=self.retrieval_service.score_threshold,
            default_assistant_mode=self.settings.default_assistant_mode,
            available_assistant_modes=self.settings.available_assistant_modes,
        )

    def update_settings(self, user: UserAccount, payload: SettingsUpdateRequest) -> SettingsRead:
        if payload.min_similarities > payload.max_similarities:
            raise ValueError("min similarities cannot be greater than max similarities")

        self.history_service.history_limit = payload.chat_history_messages_count
        self.retrieval_service.max_results = payload.max_similarities
        self.retrieval_service.min_results = payload.min_similarities
        self.retrieval_service.score_threshold = payload.similarity_score_threshold

        persisted_values = {
            "chat_history_messages_count": payload.chat_history_messages_count,
            "max_similarities": payload.max_similarities,
            "min_similarities": payload.min_similarities,
            "similarity_score_threshold": payload.similarity_score_threshold,
        }
        for key, value in persisted_values.items():
            self.chat_repository.upsert_setting(user.id, key, json.dumps(value))
        return self.get_settings(user)

    def get_personalization(self, user: UserAccount) -> PersonalizationRead:
        stored_values = self._load_stored_setting_values(user)
        return PersonalizationRead(
            base_style=str(stored_values.get("base_style", PERSONALIZATION_DEFAULTS["base_style"])),
            warm=str(stored_values.get("warm", PERSONALIZATION_DEFAULTS["warm"])),
            enthusiastic=str(stored_values.get("enthusiastic", PERSONALIZATION_DEFAULTS["enthusiastic"])),
            headers_and_lists=str(
                stored_values.get("headers_and_lists", PERSONALIZATION_DEFAULTS["headers_and_lists"])
            ),
            custom_instructions=str(
                stored_values.get("custom_instructions", PERSONALIZATION_DEFAULTS["custom_instructions"])
            ),
            nickname=str(stored_values.get("nickname", PERSONALIZATION_DEFAULTS["nickname"])),
            occupation=str(stored_values.get("occupation", PERSONALIZATION_DEFAULTS["occupation"])),
            more_about_user=str(stored_values.get("more_about_user", PERSONALIZATION_DEFAULTS["more_about_user"])),
        )

    def update_personalization(self, user: UserAccount, payload: PersonalizationUpdateRequest) -> PersonalizationRead:
        for key, value in payload.model_dump().items():
            self.chat_repository.upsert_setting(user.id, key, json.dumps(str(value).strip()))
        return self.get_personalization(user)

    def send_message(
        self,
        user: UserAccount | str,
        chat_id: str | None = None,
        user_content: str | None = None,
        attachments: list[tuple[str, bytes]] | None = None,
        assistant_mode: str | None = None,
    ):
        if isinstance(user, UserAccount):
            return self._send_message_for_user(
                user,
                chat_id or "",
                user_content or "",
                attachments=attachments,
                assistant_mode=assistant_mode,
            )
        return self._send_message_legacy(
            user,
            chat_id or "",
            attachments=attachments,
            assistant_mode=assistant_mode,
        )

    def _send_message_for_user(
        self,
        user: UserAccount,
        chat_id: str,
        user_content: str,
        *,
        attachments: list[tuple[str, bytes]] | None = None,
        assistant_mode: str | None = None,
    ):
        chat = self.chat_repository.get_chat(user.id, chat_id)
        if chat is None:
            return None

        self._load_runtime_settings(user)
        resolved_mode = self._resolve_assistant_mode(assistant_mode)
        personalization = self.get_personalization(user)
        processed_attachments = self._process_attachments(attachments or [])
        user_message = self.chat_repository.create_message(
            user.id,
            chat_id,
            "user",
            user_content,
            has_attachments=bool(processed_attachments),
        )
        if processed_attachments:
            self.chat_repository.add_message_attachments(user_message.id, processed_attachments)
        history = self.history_service.fetch(chat_id, user_id=user.id, exclude_message_id=user_message.id)
        retrieved_chunks = self.retrieval_service.retrieve(
            user_content,
            user_id=user.id,
            chat_id=chat_id,
            is_admin=user.role == "admin",
        )
        response = self._generate_response(
            assistant_mode=resolved_mode,
            user_content=user_content,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization.model_dump(),
            processed_attachments=processed_attachments,
        )
        assistant_message = self.chat_repository.create_message(user.id, chat_id, "assistant", response)
        self.chat_repository.create_retrieval_logs(
            assistant_message_id=assistant_message.id,
            user_message_id=user_message.id,
            chat_id=chat_id,
            user_id=user.id,
            used_chunks=retrieved_chunks,
        )

        return {
            "chat_id": chat_id,
            "user_message": map_message(user_message).model_copy(
                update={"attachments": [map_attachment(item) for item in processed_attachments]}
            ),
            "assistant_message": map_message(assistant_message),
            "assistant_mode": resolved_mode,
            "sources": [map_source_from_chunk(chunk) for chunk in retrieved_chunks],
            "attachments_used": [map_attachment(item) for item in processed_attachments],
        }

    def _send_message_legacy(
        self,
        chat_id: str,
        user_content: str,
        *,
        attachments: list[tuple[str, bytes]] | None = None,
        assistant_mode: str | None = None,
    ):
        chat = self.chat_repository.get_chat(chat_id)
        if chat is None:
            return None

        resolved_mode = self._resolve_assistant_mode(assistant_mode)
        processed_attachments = self._process_attachments(attachments or [])
        user_message = self.chat_repository.create_message(
            chat_id,
            "user",
            user_content,
            has_attachments=bool(processed_attachments),
        )
        if processed_attachments:
            self.chat_repository.add_message_attachments(user_message.id, processed_attachments)
        history = self.history_service.fetch(chat_id, exclude_message_id=user_message.id)
        retrieved_chunks = self.retrieval_service.retrieve(user_content)
        response = self._generate_response(
            assistant_mode=resolved_mode,
            user_content=user_content,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=dict(PERSONALIZATION_DEFAULTS),
            processed_attachments=processed_attachments,
        )
        assistant_message = self.chat_repository.create_message(chat_id, "assistant", response)
        self.chat_repository.create_retrieval_logs(
            assistant_message_id=assistant_message.id,
            user_message_id=user_message.id,
            chat_id=chat_id,
            used_chunks=retrieved_chunks,
        )

        return {
            "chat_id": chat_id,
            "user_message": map_message(user_message).model_copy(
                update={"attachments": [map_attachment(item) for item in processed_attachments]}
            ),
            "assistant_message": map_message(assistant_message),
            "assistant_mode": resolved_mode,
            "sources": [map_source_from_chunk(chunk) for chunk in retrieved_chunks],
            "attachments_used": [map_attachment(item) for item in processed_attachments],
        }

    def _process_attachments(self, attachments: list[tuple[str, bytes]]) -> list[dict[str, object]]:
        if not attachments:
            return []
        if len(attachments) > self.settings.attachment_max_files:
            raise ValueError(f"Maximum {self.settings.attachment_max_files} attachments are allowed per message")

        validated: list[tuple[str, bytes]] = []
        for file_name, content in attachments:
            suffix = Path(file_name).suffix.lower()
            if suffix not in self.settings.attachment_allowed_extension_set:
                raise ValueError(f"Unsupported attachment type: {suffix or file_name}")
            validated.append((file_name, content))

        processed = self.attachment_client.process_files(validated)
        return [attachment for attachment in processed if str(attachment.get("content") or "").strip()]

    def _generate_response(
        self,
        *,
        assistant_mode: str,
        user_content: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str] | None]],
        personalization: dict[str, str],
        processed_attachments: list[dict[str, object]],
    ) -> str:
        common_kwargs = {
            "user_message": user_content,
            "history": history,
            "retrieved_chunks": retrieved_chunks,
            "personalization": personalization,
            "attachments": processed_attachments,
            "attachment_char_limit": self.settings.attachment_max_total_chars,
        }
        if assistant_mode == "refine":
            draft = self.llm_client.invoke(self.prompt_builder.build_refine_draft_messages(**common_kwargs))
            return self.llm_client.invoke(
                self.prompt_builder.build_refine_final_messages(draft_answer=draft, **common_kwargs)
            )
        if assistant_mode == "thinking":
            try:
                return self._run_thinking_pipeline(**common_kwargs)
            except Exception:
                logger.exception("Thinking mode failed; falling back to simple mode")
                return self.llm_client.invoke(self.prompt_builder.build_simple_messages(**common_kwargs))
        return self.llm_client.invoke(self.prompt_builder.build_simple_messages(**common_kwargs))

    def _run_thinking_pipeline(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str] | None]],
        personalization: dict[str, str],
        attachments: list[dict[str, object]],
        attachment_char_limit: int,
    ) -> str:
        planning_result = self._run_thinking_planning(
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )
        draft_result = self._run_thinking_drafting(
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            planning_result=planning_result,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )
        return self._run_thinking_refining(
            user_message=user_message,
            history=history,
            retrieved_chunks=retrieved_chunks,
            personalization=personalization,
            planning_result=planning_result,
            draft_result=draft_result,
            attachments=attachments,
            attachment_char_limit=attachment_char_limit,
        )

    def _run_thinking_planning(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str] | None]],
        personalization: dict[str, str],
        attachments: list[dict[str, object]],
        attachment_char_limit: int,
    ) -> str:
        planning_result = self.llm_client.invoke(
            self.prompt_builder.build_thinking_plan_messages(
                user_message=user_message,
                history=history,
                retrieved_chunks=retrieved_chunks,
                personalization=personalization,
                attachments=attachments,
                attachment_char_limit=attachment_char_limit,
            )
        )
        logger.debug("Thinking mode planning result: %s", planning_result)
        return planning_result

    def _run_thinking_drafting(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str] | None]],
        personalization: dict[str, str],
        planning_result: str,
        attachments: list[dict[str, object]],
        attachment_char_limit: int,
    ) -> str:
        draft_result = self.llm_client.invoke(
            self.prompt_builder.build_thinking_draft_messages(
                user_message=user_message,
                history=history,
                retrieved_chunks=retrieved_chunks,
                planning_result=planning_result,
                personalization=personalization,
                attachments=attachments,
                attachment_char_limit=attachment_char_limit,
            )
        )
        logger.debug("Thinking mode draft result: %s", draft_result)
        return draft_result

    def _run_thinking_refining(
        self,
        *,
        user_message: str,
        history: list[tuple[str, str]],
        retrieved_chunks: list[dict[str, str | float | list[str] | None]],
        personalization: dict[str, str],
        planning_result: str,
        draft_result: str,
        attachments: list[dict[str, object]],
        attachment_char_limit: int,
    ) -> str:
        return self.llm_client.invoke(
            self.prompt_builder.build_thinking_final_messages(
                user_message=user_message,
                history=history,
                retrieved_chunks=retrieved_chunks,
                planning_result=planning_result,
                draft_answer=draft_result,
                personalization=personalization,
                attachments=attachments,
                attachment_char_limit=attachment_char_limit,
            )
        )

    def _resolve_assistant_mode(self, assistant_mode: str | None) -> str:
        mode = (assistant_mode or self.settings.default_assistant_mode).strip().lower()
        if not mode:
            mode = "simple"
        if mode not in self.settings.available_assistant_modes:
            raise ValueError(f"Unsupported assistant mode: {mode}")
        return mode

    def _load_runtime_settings(self, user: UserAccount) -> None:
        stored_values = self._load_stored_setting_values(user)

        self.history_service.history_limit = max(
            1,
            int(stored_values.get("chat_history_messages_count", self.settings.history_limit)),
        )
        self.retrieval_service.min_results = max(
            1,
            int(stored_values.get("min_similarities", self.settings.retrieval_min_results)),
        )
        self.retrieval_service.max_results = max(
            self.retrieval_service.min_results,
            int(stored_values.get("max_similarities", self.settings.retrieval_max_results)),
        )
        self.retrieval_service.score_threshold = min(
            max(float(stored_values.get("similarity_score_threshold", self.settings.retrieval_score_threshold)), 0.0),
            1.0,
        )

    def _load_stored_setting_values(self, user: UserAccount) -> dict[str, object]:
        stored_values: dict[str, object] = {}
        supported_keys = RUNTIME_SETTING_KEYS | PERSONALIZATION_SETTING_KEYS
        for record in self.chat_repository.list_settings(user.id):
            if record.key not in supported_keys:
                continue
            try:
                stored_values[record.key] = json.loads(record.value)
            except json.JSONDecodeError:
                continue
        return stored_values


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
    settings: Settings,
) -> RetrieverAppService:
    from services.retriever.postgres_client import RetrieverPostgresClient

    postgres_client = RetrieverPostgresClient(database_url)
    postgres_client.initialize()
    embedder_postgres_client = EmbedderPostgresClient(database_url)
    embedder_postgres_client.initialize()
    chat_repository = ChatRepository(postgres_client)
    auth_manager = AuthManager(repository=chat_repository, settings=settings)
    data_dir = Path(settings.data_dir)
    library_processor = FileProcessor(
        data_dir=data_dir,
        chunker=Chunker(settings.chunk_size, settings.chunk_overlap),
        embedding_client=EmbeddingClient(
            model=embedding_model,
            base_url=embedding_base_url,
            api_key=embedding_api_key,
            max_input_tokens=embedding_max_input_tokens,
        ),
        postgres_client=embedder_postgres_client,
        qdrant_client=EmbedderQdrantClient(settings.qdrant_url, settings.qdrant_collection),
        tags_map={},
        settings=settings,
    )
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
            candidate_filter=postgres_client.filter_retrieval_candidates,
        ),
        prompt_builder=PromptBuilder(prompts_dir),
        llm_client=LlmClient(
            model=llm_model,
            base_url=llm_base_url,
            api_key=llm_api_key,
            timeout=settings.llm_timeout_seconds,
        ),
        library_manager=LibraryManager(data_dir=data_dir, processor=library_processor, settings=settings),
        attachment_client=AttachmentProcessingClient(settings.embedder_service_url),
        auth_manager=auth_manager,
        settings=settings,
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
