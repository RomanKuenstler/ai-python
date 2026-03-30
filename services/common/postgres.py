from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, delete, func, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker

from services.common.models import Base, ChatMessage, ChatSession, ChunkRecord, FileRecord, RetrievalLog
from services.common.retry import retry


class PostgresClient:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        retry(lambda: Base.metadata.create_all(self.engine))
        self._ensure_legacy_columns()

    def _ensure_legacy_columns(self) -> None:
        inspector = inspect(self.engine)
        table_names = set(inspector.get_table_names())
        if not table_names:
            return

        column_specs: dict[str, dict[str, str]] = {
            "files": {
                "extension": "VARCHAR(16) DEFAULT ''",
                "size_bytes": "INTEGER DEFAULT 0",
                "chunk_count": "INTEGER DEFAULT 0",
                "content_hash": "VARCHAR(64) DEFAULT ''",
                "file_type": "VARCHAR(32) DEFAULT 'unknown'",
                "processing_status": "VARCHAR(64) DEFAULT 'processed'",
                "is_embedded": "BOOLEAN DEFAULT FALSE",
                "is_enabled": "BOOLEAN DEFAULT TRUE",
                "processing_error": "TEXT",
                "last_extraction_method": "VARCHAR(64)",
                "document_title": "VARCHAR(1024)",
                "author": "VARCHAR(512)",
                "detected_language": "VARCHAR(64)",
                "index_schema_version": "INTEGER DEFAULT 1",
                "processor_version": "INTEGER DEFAULT 1",
                "normalization_version": "INTEGER DEFAULT 1",
                "extraction_strategy_version": "INTEGER DEFAULT 1",
                "chunk_size": "INTEGER DEFAULT 600",
                "chunk_overlap": "INTEGER DEFAULT 100",
                "processing_signature": "VARCHAR(2048) DEFAULT ''",
                "extraction_quality": "JSON",
                "processing_flags": "JSON",
                "ocr_used": "BOOLEAN DEFAULT FALSE",
            },
            "chunks": {
                "title": "VARCHAR(1024)",
                "chapter": "VARCHAR(1024)",
                "section": "VARCHAR(1024)",
                "heading_path": "JSON",
                "page_number": "INTEGER",
                "extraction_method": "VARCHAR(64)",
                "content_type": "VARCHAR(64)",
                "quality_flags": "JSON",
                "metadata": "JSON",
            },
            "chat_messages": {
                "status": "VARCHAR(32) DEFAULT 'completed'",
            },
            "retrieval_logs": {
                "chunk_title": "VARCHAR(1024)",
                "chapter": "VARCHAR(1024)",
                "section": "VARCHAR(1024)",
                "page_number": "INTEGER",
                "tags": "JSON",
            },
        }

        with self.engine.begin() as connection:
            for table_name, specs in column_specs.items():
                if table_name not in table_names:
                    continue
                existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
                for column_name, ddl in specs.items():
                    if column_name in existing_columns:
                        continue
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))

            if "chat_messages" in table_names:
                connection.execute(text("UPDATE chat_messages SET status = 'completed' WHERE status IS NULL"))
            if "files" in table_names:
                connection.execute(text("UPDATE files SET extension = '' WHERE extension IS NULL"))
                connection.execute(text("UPDATE files SET size_bytes = 0 WHERE size_bytes IS NULL"))
                connection.execute(text("UPDATE files SET chunk_count = 0 WHERE chunk_count IS NULL"))
                connection.execute(text("UPDATE files SET is_embedded = FALSE WHERE is_embedded IS NULL"))
                connection.execute(text("UPDATE files SET is_enabled = TRUE WHERE is_enabled IS NULL"))

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

    def set_file_tags(self, file_id: int, tags: list[str]) -> FileRecord | None:
        with self.session() as session:
            record = session.get(FileRecord, file_id)
            if record is None:
                return None
            record.tags = tags
            record.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(record)
            return record

    def enabled_file_paths_for_candidates(self, file_paths: list[str]) -> set[str]:
        if not file_paths:
            return set()
        with self.session() as session:
            rows = session.scalars(
                select(FileRecord.file_path).where(FileRecord.file_path.in_(file_paths), FileRecord.is_enabled.is_(True))
            )
            return set(rows)

    def chunk_counts_by_file_ids(self, file_ids: list[int]) -> dict[int, int]:
        if not file_ids:
            return {}
        with self.session() as session:
            rows = session.execute(
                select(ChunkRecord.file_id, func.count(ChunkRecord.id)).where(ChunkRecord.file_id.in_(file_ids)).group_by(ChunkRecord.file_id)
            )
            return {int(file_id): int(count) for file_id, count in rows}

    def ensure_chat(self, chat_id: str, chat_name: str) -> ChatSession:
        with self.session() as session:
            chat = session.get(ChatSession, chat_id)
            if chat is None:
                chat = ChatSession(id=chat_id, chat_name=chat_name)
                session.add(chat)
                session.flush()
                session.refresh(chat)
            return chat

    def create_chat(self, chat_name: str, chat_id: str | None = None) -> ChatSession:
        with self.session() as session:
            chat = ChatSession(id=chat_id or None, chat_name=chat_name)
            session.add(chat)
            session.flush()
            session.refresh(chat)
            return chat

    def list_chats(self) -> list[ChatSession]:
        with self.session() as session:
            rows = session.scalars(select(ChatSession).order_by(ChatSession.updated_at.desc(), ChatSession.created_at.desc()))
            return list(rows)

    def get_chat(self, chat_id: str) -> ChatSession | None:
        with self.session() as session:
            return session.get(ChatSession, chat_id)

    def rename_chat(self, chat_id: str, chat_name: str) -> ChatSession | None:
        with self.session() as session:
            chat = session.get(ChatSession, chat_id)
            if chat is None:
                return None
            chat.chat_name = chat_name
            chat.updated_at = datetime.now(timezone.utc)
            session.flush()
            session.refresh(chat)
            return chat

    def delete_chat(self, chat_id: str) -> ChatSession | None:
        with self.session() as session:
            chat = session.get(ChatSession, chat_id)
            if chat is None:
                return None
            session.execute(delete(RetrievalLog).where(RetrievalLog.session_id == chat_id))
            session.execute(delete(ChatMessage).where(ChatMessage.session_id == chat_id))
            session.delete(chat)
            return chat

    def touch_chat(self, chat_id: str) -> None:
        with self.session() as session:
            chat = session.get(ChatSession, chat_id)
            if chat is not None:
                chat.updated_at = datetime.now(timezone.utc)

    def add_chat_message(self, session_id: str, role: str, content: str, status: str = "completed") -> ChatMessage:
        with self.session() as session:
            message = ChatMessage(session_id=session_id, role=role, content=content, status=status)
            session.add(message)
            self._touch_chat_in_session(session, session_id)
            session.flush()
            session.refresh(message)
            return message

    def get_chat_messages(self, chat_id: str) -> list[ChatMessage]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatMessage).where(ChatMessage.session_id == chat_id).order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            )
            return list(rows)

    def get_recent_chat_history(self, session_id: str, limit: int) -> list[ChatMessage]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
                .limit(limit * 2)
            )
            return list(reversed(list(rows)))

    def get_retrieval_logs_for_assistant_messages(self, assistant_message_ids: list[int]) -> dict[int, list[RetrievalLog]]:
        if not assistant_message_ids:
            return {}
        with self.session() as session:
            rows = session.scalars(
                select(RetrievalLog)
                .where(RetrievalLog.assistant_message_id.in_(assistant_message_ids))
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
        used_chunks: list[dict[str, str | float]],
    ) -> None:
        with self.session() as session:
            for chunk in used_chunks:
                session.add(
                    RetrievalLog(
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
            self._touch_chat_in_session(session, session_id)

    def _touch_chat_in_session(self, session: Session, chat_id: str) -> None:
        chat = session.get(ChatSession, chat_id)
        if chat is not None:
            chat.updated_at = datetime.now(timezone.utc)
