from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260401_0004"
down_revision = "20260331_0003"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    if not _has_table("chat_file_settings"):
        op.create_table(
            "chat_file_settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("chat_id", sa.String(length=128), sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
            sa.Column("file_id", sa.Integer(), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("chat_id", "file_id", name="uq_chat_file_settings_chat_file"),
        )
        op.create_index("ix_chat_file_settings_chat_id", "chat_file_settings", ["chat_id"])
        op.create_index("ix_chat_file_settings_file_id", "chat_file_settings", ["file_id"])

    if not _has_table("user_tag_settings"):
        op.create_table(
            "user_tag_settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tag", sa.String(length=255), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("user_id", "tag", name="uq_user_tag_settings_user_tag"),
        )
        op.create_index("ix_user_tag_settings_user_id", "user_tag_settings", ["user_id"])

    if not _has_table("chat_tag_settings"):
        op.create_table(
            "chat_tag_settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("chat_id", sa.String(length=128), sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tag", sa.String(length=255), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("chat_id", "tag", name="uq_chat_tag_settings_chat_tag"),
        )
        op.create_index("ix_chat_tag_settings_chat_id", "chat_tag_settings", ["chat_id"])


def downgrade() -> None:
    if _has_table("chat_tag_settings"):
        op.drop_table("chat_tag_settings")
    if _has_table("user_tag_settings"):
        op.drop_table("user_tag_settings")
    if _has_table("chat_file_settings"):
        op.drop_table("chat_file_settings")
