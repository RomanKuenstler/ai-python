from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260330_0001"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("files"):
        op.create_table(
            "files",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("file_path", sa.String(length=1024), nullable=False, unique=True),
            sa.Column("file_name", sa.String(length=512), nullable=False),
            sa.Column("extension", sa.String(length=16), nullable=False, server_default=""),
            sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("hash", sa.String(length=64), nullable=False),
            sa.Column("content_hash", sa.String(length=64), nullable=False, server_default=""),
            sa.Column("file_type", sa.String(length=32), nullable=False, server_default="unknown"),
            sa.Column("processing_status", sa.String(length=64), nullable=False, server_default="processed"),
            sa.Column("is_embedded", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("processing_error", sa.Text(), nullable=True),
            sa.Column("last_extraction_method", sa.String(length=64), nullable=True),
            sa.Column("document_title", sa.String(length=1024), nullable=True),
            sa.Column("author", sa.String(length=512), nullable=True),
            sa.Column("detected_language", sa.String(length=64), nullable=True),
            sa.Column("index_schema_version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("processor_version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("normalization_version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("extraction_strategy_version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("chunk_size", sa.Integer(), nullable=False, server_default="600"),
            sa.Column("chunk_overlap", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("processing_signature", sa.String(length=2048), nullable=False, server_default=""),
            sa.Column("extraction_quality", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
            sa.Column("processing_flags", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
            sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
            sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
            sa.Column("last_processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("chunks"):
        op.create_table(
            "chunks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("file_id", sa.Integer(), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
            sa.Column("chunk_id", sa.String(length=128), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("title", sa.String(length=1024), nullable=True),
            sa.Column("chapter", sa.String(length=1024), nullable=True),
            sa.Column("section", sa.String(length=1024), nullable=True),
            sa.Column("heading_path", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
            sa.Column("page_number", sa.Integer(), nullable=True),
            sa.Column("extraction_method", sa.String(length=64), nullable=True),
            sa.Column("content_type", sa.String(length=64), nullable=True),
            sa.Column("quality_flags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
            sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
            sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_index("chunks", "ix_chunks_file_id_chunk_id"):
        op.create_index("ix_chunks_file_id_chunk_id", "chunks", ["file_id", "chunk_id"], unique=True)

    if not _has_table("chats"):
        op.create_table(
            "chats",
            sa.Column("id", sa.String(length=128), primary_key=True),
            sa.Column("chat_name", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("chat_messages"):
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("session_id", sa.String(length=128), nullable=False),
            sa.Column("role", sa.String(length=32), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
            sa.Column("has_attachments", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_index("chat_messages", "ix_chat_messages_session_id_created_at"):
        op.create_index("ix_chat_messages_session_id_created_at", "chat_messages", ["session_id", "created_at"], unique=False)

    if not _has_table("retrieval_logs"):
        op.create_table(
            "retrieval_logs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("assistant_message_id", sa.Integer(), sa.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_message_id", sa.Integer(), sa.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("session_id", sa.String(length=128), nullable=False),
            sa.Column("source_file_name", sa.String(length=512), nullable=False),
            sa.Column("source_file_path", sa.String(length=1024), nullable=False),
            sa.Column("chunk_id", sa.String(length=128), nullable=False),
            sa.Column("chunk_text", sa.Text(), nullable=False),
            sa.Column("chunk_title", sa.String(length=1024), nullable=True),
            sa.Column("chapter", sa.String(length=1024), nullable=True),
            sa.Column("section", sa.String(length=1024), nullable=True),
            sa.Column("page_number", sa.Integer(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
            sa.Column("retrieval_score", sa.Float(), nullable=False),
            sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("message_attachments"):
        op.create_table(
            "message_attachments",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("message_id", sa.Integer(), sa.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("file_name", sa.String(length=512), nullable=False),
            sa.Column("file_type", sa.String(length=64), nullable=False),
            sa.Column("extraction_method", sa.String(length=64), nullable=True),
            sa.Column("quality", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    additions: dict[str, list[tuple[str, sa.Column]]] = {
        "chat_messages": [
            ("status", sa.Column("status", sa.String(length=32), nullable=False, server_default="completed")),
            ("has_attachments", sa.Column("has_attachments", sa.Boolean(), nullable=False, server_default=sa.text("FALSE"))),
        ],
        "retrieval_logs": [
            ("chunk_title", sa.Column("chunk_title", sa.String(length=1024), nullable=True)),
            ("chapter", sa.Column("chapter", sa.String(length=1024), nullable=True)),
            ("section", sa.Column("section", sa.String(length=1024), nullable=True)),
            ("page_number", sa.Column("page_number", sa.Integer(), nullable=True)),
            ("tags", sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"))),
        ],
    }
    for table_name, columns in additions.items():
        for column_name, column in columns:
            if not _has_column(table_name, column_name):
                op.add_column(table_name, column)

    file_columns = [
        ("extension", sa.Column("extension", sa.String(length=16), nullable=False, server_default="")),
        ("size_bytes", sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0")),
        ("chunk_count", sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0")),
        ("content_hash", sa.Column("content_hash", sa.String(length=64), nullable=False, server_default="")),
        ("file_type", sa.Column("file_type", sa.String(length=32), nullable=False, server_default="unknown")),
        ("processing_status", sa.Column("processing_status", sa.String(length=64), nullable=False, server_default="processed")),
        ("is_embedded", sa.Column("is_embedded", sa.Boolean(), nullable=False, server_default=sa.text("FALSE"))),
        ("is_enabled", sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE"))),
        ("processing_error", sa.Column("processing_error", sa.Text(), nullable=True)),
        ("last_extraction_method", sa.Column("last_extraction_method", sa.String(length=64), nullable=True)),
        ("document_title", sa.Column("document_title", sa.String(length=1024), nullable=True)),
        ("author", sa.Column("author", sa.String(length=512), nullable=True)),
        ("detected_language", sa.Column("detected_language", sa.String(length=64), nullable=True)),
        ("index_schema_version", sa.Column("index_schema_version", sa.Integer(), nullable=False, server_default="1")),
        ("processor_version", sa.Column("processor_version", sa.Integer(), nullable=False, server_default="1")),
        ("normalization_version", sa.Column("normalization_version", sa.Integer(), nullable=False, server_default="1")),
        ("extraction_strategy_version", sa.Column("extraction_strategy_version", sa.Integer(), nullable=False, server_default="1")),
        ("chunk_size", sa.Column("chunk_size", sa.Integer(), nullable=False, server_default="600")),
        ("chunk_overlap", sa.Column("chunk_overlap", sa.Integer(), nullable=False, server_default="100")),
        ("processing_signature", sa.Column("processing_signature", sa.String(length=2048), nullable=False, server_default="")),
        ("extraction_quality", sa.Column("extraction_quality", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"))),
        ("processing_flags", sa.Column("processing_flags", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"))),
        ("ocr_used", sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.text("FALSE"))),
    ]
    for column_name, column in file_columns:
        if _has_table("files") and not _has_column("files", column_name):
            op.add_column("files", column)

    chunk_columns = [
        ("title", sa.Column("title", sa.String(length=1024), nullable=True)),
        ("chapter", sa.Column("chapter", sa.String(length=1024), nullable=True)),
        ("section", sa.Column("section", sa.String(length=1024), nullable=True)),
        ("heading_path", sa.Column("heading_path", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"))),
        ("page_number", sa.Column("page_number", sa.Integer(), nullable=True)),
        ("extraction_method", sa.Column("extraction_method", sa.String(length=64), nullable=True)),
        ("content_type", sa.Column("content_type", sa.String(length=64), nullable=True)),
        ("quality_flags", sa.Column("quality_flags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"))),
        ("metadata", sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"))),
    ]
    for column_name, column in chunk_columns:
        if _has_table("chunks") and not _has_column("chunks", column_name):
            op.add_column("chunks", column)

    op.execute("UPDATE chat_messages SET status = 'completed' WHERE status IS NULL")
    op.execute("UPDATE chat_messages SET has_attachments = FALSE WHERE has_attachments IS NULL")


def downgrade() -> None:
    if _has_table("message_attachments"):
        op.drop_table("message_attachments")
