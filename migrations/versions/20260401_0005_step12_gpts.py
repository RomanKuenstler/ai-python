from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260401_0005"
down_revision = "20260401_0004"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("gpts"):
        op.create_table(
            "gpts",
            sa.Column("id", sa.String(length=128), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False, server_default=""),
            sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
            sa.Column("assistant_mode", sa.String(length=32), nullable=False, server_default="simple"),
            sa.Column("personalization", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("file_settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("tag_settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_gpts_user_id", "gpts", ["user_id"])

    if not _has_table("gpt_chats"):
        op.create_table(
            "gpt_chats",
            sa.Column("id", sa.String(length=128), primary_key=True),
            sa.Column("gpt_id", sa.String(length=128), sa.ForeignKey("gpts.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("gpt_id", name="uq_gpt_chats_gpt_id"),
        )
        op.create_index("ix_gpt_chats_gpt_id", "gpt_chats", ["gpt_id"])

    if _has_table("chat_messages") and not _has_column("chat_messages", "gpt_id"):
        op.add_column("chat_messages", sa.Column("gpt_id", sa.String(length=128), nullable=True))
        op.create_foreign_key("fk_chat_messages_gpt_id", "chat_messages", "gpts", ["gpt_id"], ["id"], ondelete="CASCADE")

    if _has_table("chat_messages") and "ix_chat_messages_gpt_id_created_at" not in _index_names("chat_messages"):
        op.create_index("ix_chat_messages_gpt_id_created_at", "chat_messages", ["gpt_id", "created_at"])


def downgrade() -> None:
    if _has_table("chat_messages") and "ix_chat_messages_gpt_id_created_at" in _index_names("chat_messages"):
        op.drop_index("ix_chat_messages_gpt_id_created_at", table_name="chat_messages")
    if _has_table("chat_messages") and _has_column("chat_messages", "gpt_id"):
        with op.batch_alter_table("chat_messages") as batch_op:
            batch_op.drop_column("gpt_id")
    if _has_table("gpt_chats"):
        op.drop_table("gpt_chats")
    if _has_table("gpts"):
        op.drop_table("gpts")
