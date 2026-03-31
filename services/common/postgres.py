from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from services.common.migrations import run_migrations
from services.common.models import (
    ChatMessage,
    ChatSession,
    ChunkRecord,
    FileRecord,
    MessageAttachment,
    RetrievalLog,
    SettingRecord,
    UserAccount,
    UserFileSetting,
    UserSessionRecord,
)
from services.common.retry import retry


class PostgresClient:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        retry(lambda: run_migrations(self.database_url))

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_files(self) -> list[FileRecord]:
        with self.session() as session:
            rows = session.scalars(select(FileRecord).order_by(FileRecord.updated_at.desc(), FileRecord.file_name.asc()))
            records = list(rows)
            chunk_counts = self.chunk_counts_by_file_ids([record.id for record in records])
            for record in records:
                if not record.extension:
                    record.extension = Path(record.file_name).suffix.lower()
                resolved_chunk_count = chunk_counts.get(record.id, record.chunk_count)
                if not record.chunk_count and resolved_chunk_count:
                    record.chunk_count = resolved_chunk_count
                if resolved_chunk_count and not record.is_embedded:
                    record.is_embedded = True
            return records

    def list_files_for_user(self, *, user_id: int, is_admin: bool) -> list[FileRecord]:
        with self.session() as session:
            records = list(
                session.scalars(select(FileRecord).order_by(FileRecord.updated_at.desc(), FileRecord.file_name.asc()))
            )
            file_ids = [record.id for record in records]
            chunk_counts = self.chunk_counts_by_file_ids(file_ids)
            settings = self._user_file_settings_map(session, user_id=user_id, file_ids=file_ids)
            for record in records:
                if not record.extension:
                    record.extension = Path(record.file_name).suffix.lower()
                resolved_chunk_count = chunk_counts.get(record.id, record.chunk_count)
                if not record.chunk_count and resolved_chunk_count:
                    record.chunk_count = resolved_chunk_count
                if resolved_chunk_count and not record.is_embedded:
                    record.is_embedded = True
                if record.is_system and not is_admin:
                    record.is_enabled = True
                else:
                    record.is_enabled = settings.get(record.id, True)
            return records

    def get_file(self, file_path: str) -> FileRecord | None:
        with self.session() as session:
            return session.scalar(select(FileRecord).where(FileRecord.file_path == file_path))

    def get_file_by_id(self, file_id: int) -> FileRecord | None:
        with self.session() as session:
            return session.get(FileRecord, file_id)

    def upsert_file_with_chunks(
        self,
        *,
        file_payload: dict,
        chunks: list[dict],
    ) -> FileRecord:
        file_path = str(file_payload["file_path"])
        with self.session() as session:
            record = session.scalar(select(FileRecord).where(FileRecord.file_path == file_path))
            if record is None:
                record = FileRecord(**file_payload)
                session.add(record)
                session.flush()
            else:
                for key, value in file_payload.items():
                    if key == "is_enabled" and value is None:
                        continue
                    setattr(record, key, value)
                record.last_processed_at = datetime.now(timezone.utc)
                session.execute(delete(ChunkRecord).where(ChunkRecord.file_id == record.id))
                session.flush()

            for chunk in chunks:
                chunk_payload = dict(chunk)
                if "metadata" in chunk_payload:
                    chunk_payload["chunk_metadata"] = chunk_payload.pop("metadata")
                session.add(ChunkRecord(file_id=record.id, **chunk_payload))

            session.flush()
            session.refresh(record)
            return record

    def delete_file(self, file_path: str) -> FileRecord | None:
        with self.session() as session:
            record = session.scalar(select(FileRecord).where(FileRecord.file_path == file_path))
            if record is None:
                return None
            session.delete(record)
            return record

    def set_file_enabled(self, file_id: int, is_enabled: bool) -> FileRecord | None:
        with self.session() as session:
            record = session.get(FileRecord, file_id)
            if record is None:
                return None
            record.is_enabled = is_enabled
            record.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(record)
            return record

    def set_file_enabled_for_user(self, *, user_id: int, file_id: int, is_enabled: bool, is_admin: bool) -> FileRecord | None:
        with self.session() as session:
            record = session.get(FileRecord, file_id)
            if record is None:
                return None
            if record.is_system and not is_admin:
                raise PermissionError("System files cannot be disabled by normal users")
            setting = session.scalar(
                select(UserFileSetting).where(UserFileSetting.user_id == user_id, UserFileSetting.file_id == file_id)
            )
            if setting is None:
                setting = UserFileSetting(user_id=user_id, file_id=file_id, is_enabled=is_enabled)
                session.add(setting)
            else:
                setting.is_enabled = is_enabled
                setting.updated_at = datetime.now(timezone.utc)
            record.is_enabled = is_enabled if (is_admin or not record.is_system) else True
            session.flush()
            session.refresh(record)
            return record

    def enabled_file_paths_for_candidates(self, file_paths: list[str], *, user_id: int, is_admin: bool) -> set[str]:
        if not file_paths:
            return set()
        with self.session() as session:
            records = list(session.scalars(select(FileRecord).where(FileRecord.file_path.in_(file_paths))))
            settings = self._user_file_settings_map(
                session,
                user_id=user_id,
                file_ids=[record.id for record in records],
            )
            enabled: set[str] = set()
            for record in records:
                if record.is_system and not is_admin:
                    enabled.add(record.file_path)
                    continue
                if settings.get(record.id, True):
                    enabled.add(record.file_path)
            return enabled

    def chunk_counts_by_file_ids(self, file_ids: list[int]) -> dict[int, int]:
        if not file_ids:
            return {}
        with self.session() as session:
            rows = session.execute(
                select(ChunkRecord.file_id, func.count(ChunkRecord.id)).where(ChunkRecord.file_id.in_(file_ids)).group_by(ChunkRecord.file_id)
            )
            return {int(file_id): int(count) for file_id, count in rows}

    def ensure_chat(self, user_id: int, chat_id: str, chat_name: str) -> ChatSession:
        with self.session() as session:
            chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
            if chat is None:
                chat = ChatSession(id=chat_id, user_id=user_id, chat_name=chat_name)
                session.add(chat)
                session.flush()
                session.refresh(chat)
            return chat

    def create_chat(self, user_id: int, chat_name: str, chat_id: str | None = None) -> ChatSession:
        with self.session() as session:
            chat = ChatSession(id=chat_id or None, user_id=user_id, chat_name=chat_name)
            session.add(chat)
            session.flush()
            session.refresh(chat)
            return chat

    def list_chats(self, *, user_id: int, archived: bool = False) -> list[ChatSession]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatSession)
                .where(ChatSession.user_id == user_id, ChatSession.is_archived.is_(archived))
                .order_by(ChatSession.updated_at.desc(), ChatSession.created_at.desc())
            )
            return list(rows)

    def get_chat(self, chat_id: str, *, user_id: int) -> ChatSession | None:
        with self.session() as session:
            return session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))

    def rename_chat(self, chat_id: str, *, user_id: int, chat_name: str) -> ChatSession | None:
        with self.session() as session:
            chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
            if chat is None:
                return None
            chat.chat_name = chat_name
            chat.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(chat)
            return chat

    def delete_chat(self, chat_id: str, *, user_id: int) -> ChatSession | None:
        with self.session() as session:
            chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
            if chat is None:
                return None
            session.execute(delete(RetrievalLog).where(RetrievalLog.session_id == chat_id, RetrievalLog.user_id == user_id))
            session.execute(delete(ChatMessage).where(ChatMessage.session_id == chat_id, ChatMessage.user_id == user_id))
            session.delete(chat)
            return chat

    def set_chat_archived(self, chat_id: str, *, user_id: int, is_archived: bool) -> ChatSession | None:
        with self.session() as session:
            chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
            if chat is None:
                return None
            chat.is_archived = is_archived
            chat.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(chat)
            return chat

    def touch_chat(self, chat_id: str, *, user_id: int) -> None:
        with self.session() as session:
            chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
            if chat is not None:
                chat.updated_at = datetime.now(timezone.utc)

    def add_chat_message(
        self,
        session_id: str,
        user_id: int,
        role: str,
        content: str,
        status: str = "completed",
        *,
        has_attachments: bool = False,
    ) -> ChatMessage:
        with self.session() as session:
            message = ChatMessage(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                status=status,
                has_attachments=has_attachments,
            )
            session.add(message)
            self._touch_chat_in_session(session, session_id, user_id=user_id)
            session.flush()
            session.refresh(message)
            return message

    def get_chat_messages(self, chat_id: str, *, user_id: int) -> list[ChatMessage]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == chat_id, ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            )
            return list(rows)

    def add_message_attachments(self, message_id: int, attachments: list[dict[str, object]]) -> list[MessageAttachment]:
        with self.session() as session:
            records: list[MessageAttachment] = []
            for attachment in attachments:
                record = MessageAttachment(
                    message_id=message_id,
                    file_name=str(attachment["file_name"]),
                    file_type=str(attachment["type"]),
                    extraction_method=str(attachment.get("extraction_method") or "") or None,
                    quality=dict(attachment.get("quality") or {}),
                )
                session.add(record)
                records.append(record)
            session.flush()
            for record in records:
                session.refresh(record)
            return records

    def get_attachments_by_message_ids(self, message_ids: list[int]) -> dict[int, list[MessageAttachment]]:
        if not message_ids:
            return {}
        with self.session() as session:
            rows = session.scalars(
                select(MessageAttachment)
                .where(MessageAttachment.message_id.in_(message_ids))
                .order_by(MessageAttachment.message_id.asc(), MessageAttachment.id.asc())
            )
            grouped: dict[int, list[MessageAttachment]] = {}
            for row in rows:
                grouped.setdefault(row.message_id, []).append(row)
            return grouped

    def get_recent_chat_history(self, session_id: str, *, user_id: int, limit: int) -> list[ChatMessage]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id, ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
                .limit(limit * 2)
            )
            return list(reversed(list(rows)))

    def get_retrieval_logs_for_assistant_messages(self, assistant_message_ids: list[int], *, user_id: int) -> dict[int, list[RetrievalLog]]:
        if not assistant_message_ids:
            return {}
        with self.session() as session:
            rows = session.scalars(
                select(RetrievalLog)
                .where(RetrievalLog.assistant_message_id.in_(assistant_message_ids), RetrievalLog.user_id == user_id)
                .order_by(RetrievalLog.assistant_message_id.asc(), RetrievalLog.id.asc())
            )
            grouped: dict[int, list[RetrievalLog]] = {}
            for row in rows:
                grouped.setdefault(row.assistant_message_id, []).append(row)
            return grouped

    def add_retrieval_logs(
        self,
        *,
        assistant_message_id: int,
        user_message_id: int,
        session_id: str,
        user_id: int,
        used_chunks: list[dict[str, str | float]],
    ) -> None:
        with self.session() as session:
            for chunk in used_chunks:
                session.add(
                    RetrievalLog(
                        user_id=user_id,
                        assistant_message_id=assistant_message_id,
                        user_message_id=user_message_id,
                        session_id=session_id,
                        source_file_name=str(chunk["file_name"]),
                        source_file_path=str(chunk["file_path"]),
                        chunk_id=str(chunk["chunk_id"]),
                        chunk_text=str(chunk["text"]),
                        chunk_title=str(chunk.get("title") or "") or None,
                        chapter=str(chunk.get("chapter") or "") or None,
                        section=str(chunk.get("section") or "") or None,
                        page_number=chunk.get("page_number"),
                        tags=list(chunk.get("tags", [])),
                        retrieval_score=float(chunk["score"]),
                    )
                )
            self._touch_chat_in_session(session, session_id, user_id=user_id)

    def _touch_chat_in_session(self, session: Session, chat_id: str, *, user_id: int) -> None:
        chat = session.scalar(select(ChatSession).where(ChatSession.id == chat_id, ChatSession.user_id == user_id))
        if chat is not None:
            chat.updated_at = datetime.now(timezone.utc)

    def list_settings(self, *, user_id: int) -> list[SettingRecord]:
        with self.session() as session:
            rows = session.scalars(
                select(SettingRecord).where(SettingRecord.user_id == user_id).order_by(SettingRecord.key.asc())
            )
            return list(rows)

    def upsert_setting(self, *, user_id: int, key: str, value: str) -> SettingRecord:
        with self.session() as session:
            record = session.scalar(
                select(SettingRecord).where(SettingRecord.user_id == user_id, SettingRecord.key == key)
            )
            if record is None:
                record = SettingRecord(user_id=user_id, key=key, value=value)
                session.add(record)
            else:
                record.value = value
                record.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(record)
            return record

    def get_user_by_id(self, user_id: int) -> UserAccount | None:
        with self.session() as session:
            return session.get(UserAccount, user_id)

    def get_user_by_username(self, username: str) -> UserAccount | None:
        with self.session() as session:
            return session.scalar(select(UserAccount).where(UserAccount.username == username))

    def list_users(self) -> list[UserAccount]:
        with self.session() as session:
            rows = session.scalars(select(UserAccount).order_by(UserAccount.username.asc()))
            return list(rows)

    def create_user(
        self,
        *,
        username: str,
        displayname: str,
        role: str,
        password_hash: str,
        status: str = "active",
        force_password_change: bool = True,
    ) -> UserAccount:
        with self.session() as session:
            user = UserAccount(
                username=username,
                displayname=displayname,
                role=role,
                password_hash=password_hash,
                status=status,
                force_password_change=force_password_change,
            )
            session.add(user)
            session.flush()
            session.refresh(user)
            return user

    def update_user(self, user_id: int, **fields: object) -> UserAccount | None:
        with self.session() as session:
            user = session.get(UserAccount, user_id)
            if user is None:
                return None
            for key, value in fields.items():
                if value is not None:
                    setattr(user, key, value)
            user.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(user)
            return user

    def delete_user(self, user_id: int) -> UserAccount | None:
        with self.session() as session:
            user = session.get(UserAccount, user_id)
            if user is None:
                return None
            session.delete(user)
            return user

    def upsert_bootstrap_user(
        self,
        *,
        username: str,
        displayname: str,
        role: str,
        password_hash: str,
    ) -> UserAccount:
        with self.session() as session:
            user = session.scalar(select(UserAccount).where(UserAccount.username == username))
            if user is None:
                user = UserAccount(
                    username=username,
                    displayname=displayname,
                    role=role,
                    status="active",
                    force_password_change=True,
                    password_hash=password_hash,
                )
                session.add(user)
            else:
                user.displayname = displayname
                user.role = role
                user.status = "active"
                user.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(user)
            return user

    def deactivate_users_not_in(self, usernames: set[str]) -> None:
        with self.session() as session:
            session.execute(
                update(UserAccount)
                .where(UserAccount.username.not_in(usernames))
                .values(status="inactive", updated_at=datetime.now(timezone.utc))
            )

    def assign_orphaned_records_to_user(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        with self.session() as session:
            session.execute(update(ChatSession).where(ChatSession.user_id.is_(None)).values(user_id=user_id, updated_at=now))
            session.execute(update(ChatMessage).where(ChatMessage.user_id.is_(None)).values(user_id=user_id))
            session.execute(update(RetrievalLog).where(RetrievalLog.user_id.is_(None)).values(user_id=user_id))
            session.execute(update(SettingRecord).where(SettingRecord.user_id.is_(None)).values(user_id=user_id, updated_at=now))

    def create_user_session(
        self,
        *,
        session_id: str,
        user_id: int,
        issued_at: datetime,
        last_refreshed_at: datetime,
        last_activity_at: datetime,
        expires_at: datetime,
        max_expires_at: datetime,
    ) -> UserSessionRecord:
        with self.session() as session:
            record = UserSessionRecord(
                id=session_id,
                user_id=user_id,
                issued_at=issued_at,
                last_refreshed_at=last_refreshed_at,
                last_activity_at=last_activity_at,
                expires_at=expires_at,
                max_expires_at=max_expires_at,
            )
            session.add(record)
            session.flush()
            session.refresh(record)
            return record

    def get_user_session(self, session_id: str) -> UserSessionRecord | None:
        with self.session() as session:
            return session.get(UserSessionRecord, session_id)

    def update_user_session_activity(self, session_id: str, *, last_activity_at: datetime) -> UserSessionRecord | None:
        with self.session() as session:
            record = session.get(UserSessionRecord, session_id)
            if record is None:
                return None
            record.last_activity_at = last_activity_at
            record.updated_at = last_activity_at
            session.flush()
            session.refresh(record)
            return record

    def refresh_user_session(
        self,
        session_id: str,
        *,
        last_refreshed_at: datetime,
        last_activity_at: datetime,
        expires_at: datetime,
    ) -> UserSessionRecord | None:
        with self.session() as session:
            record = session.get(UserSessionRecord, session_id)
            if record is None:
                return None
            record.last_refreshed_at = last_refreshed_at
            record.last_activity_at = last_activity_at
            record.expires_at = expires_at
            record.updated_at = last_activity_at
            session.flush()
            session.refresh(record)
            return record

    def revoke_user_session(self, session_id: str, *, revoked_at: datetime) -> UserSessionRecord | None:
        with self.session() as session:
            record = session.get(UserSessionRecord, session_id)
            if record is None:
                return None
            record.revoked_at = revoked_at
            record.updated_at = revoked_at
            session.flush()
            session.refresh(record)
            return record

    def revoke_all_user_sessions(self, user_id: int, *, revoked_at: datetime) -> None:
        with self.session() as session:
            session.execute(
                update(UserSessionRecord)
                .where(UserSessionRecord.user_id == user_id, UserSessionRecord.revoked_at.is_(None))
                .values(revoked_at=revoked_at, updated_at=revoked_at)
            )

    def _user_file_settings_map(self, session: Session, *, user_id: int, file_ids: list[int]) -> dict[int, bool]:
        if not file_ids:
            return {}
        rows = session.scalars(
            select(UserFileSetting).where(UserFileSetting.user_id == user_id, UserFileSetting.file_id.in_(file_ids))
        )
        return {row.file_id: row.is_enabled for row in rows}
