from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker

from services.common.models import Base, ChatMessage, ChunkRecord, FileRecord, RetrievalLog
from services.common.retry import retry


class PostgresClient:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        retry(lambda: Base.metadata.create_all(self.engine))

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
            return list(session.scalars(select(FileRecord)))

    def get_file(self, file_path: str) -> FileRecord | None:
        with self.session() as session:
            return session.scalar(select(FileRecord).where(FileRecord.file_path == file_path))

    def upsert_file_with_chunks(
        self,
        *,
        file_path: str,
        file_name: str,
        file_hash: str,
        tags: list[str],
        chunks: list[dict[str, str | list[str]]],
    ) -> FileRecord:
        with self.session() as session:
            record = session.scalar(select(FileRecord).where(FileRecord.file_path == file_path))
            if record is None:
                record = FileRecord(file_path=file_path, file_name=file_name, file_hash=file_hash, tags=tags)
                session.add(record)
                session.flush()
            else:
                record.file_name = file_name
                record.file_hash = file_hash
                record.tags = tags
                record.last_processed_at = datetime.now(timezone.utc)
                session.execute(delete(ChunkRecord).where(ChunkRecord.file_id == record.id))
                session.flush()

            for chunk in chunks:
                session.add(
                    ChunkRecord(
                        file_id=record.id,
                        chunk_id=str(chunk["chunk_id"]),
                        text=str(chunk["text"]),
                        tags=list(chunk["tags"]),
                    )
                )

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

    def add_chat_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        with self.session() as session:
            message = ChatMessage(session_id=session_id, role=role, content=content)
            session.add(message)
            session.flush()
            session.refresh(message)
            return message

    def get_recent_chat_history(self, session_id: str, limit: int) -> list[ChatMessage]:
        with self.session() as session:
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
                .limit(limit * 2)
            )
            return list(reversed(list(rows)))

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
                        retrieval_score=float(chunk["score"]),
                    )
                )
