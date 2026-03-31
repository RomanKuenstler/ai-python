from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260331_0003"
down_revision = "20260330_0002"
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


def _constraint_names(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return set()
    return {constraint["name"] for constraint in inspector.get_unique_constraints(table_name)}


def upgrade() -> None:
    if not _has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("username", sa.String(length=128), nullable=False, unique=True),
            sa.Column("displayname", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=512), nullable=False),
            sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
            sa.Column("force_password_change", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("user_sessions"):
        op.create_table(
            "user_sessions",
            sa.Column("id", sa.String(length=128), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("max_expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])

    if _has_table("files"):
        if not _has_column("files", "uploaded_by_user_id"):
            op.add_column("files", sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True))
            op.create_foreign_key("fk_files_uploaded_by_user_id", "files", "users", ["uploaded_by_user_id"], ["id"], ondelete="SET NULL")
        if not _has_column("files", "is_system"):
            op.add_column("files", sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))
            op.execute("UPDATE files SET is_system = CASE WHEN POSITION('/' IN file_path) = 0 THEN TRUE ELSE FALSE END")

    if _has_table("chats") and not _has_column("chats", "user_id"):
        op.add_column("chats", sa.Column("user_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_chats_user_id", "chats", "users", ["user_id"], ["id"], ondelete="CASCADE")
        op.create_index("ix_chats_user_id", "chats", ["user_id"])

    if _has_table("chat_messages"):
        if not _has_column("chat_messages", "user_id"):
            op.add_column("chat_messages", sa.Column("user_id", sa.Integer(), nullable=True))
            op.create_foreign_key("fk_chat_messages_user_id", "chat_messages", "users", ["user_id"], ["id"], ondelete="CASCADE")
        if "ix_chat_messages_user_id_created_at" not in _index_names("chat_messages"):
            op.create_index("ix_chat_messages_user_id_created_at", "chat_messages", ["user_id", "created_at"])

    if _has_table("retrieval_logs") and not _has_column("retrieval_logs", "user_id"):
        op.add_column("retrieval_logs", sa.Column("user_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_retrieval_logs_user_id", "retrieval_logs", "users", ["user_id"], ["id"], ondelete="CASCADE")
        op.create_index("ix_retrieval_logs_user_id", "retrieval_logs", ["user_id"])

    if _has_table("settings"):
        if not _has_column("settings", "user_id"):
            op.add_column("settings", sa.Column("user_id", sa.Integer(), nullable=True))
            op.create_foreign_key("fk_settings_user_id", "settings", "users", ["user_id"], ["id"], ondelete="CASCADE")
            op.create_index("ix_settings_user_id", "settings", ["user_id"])
        bind = op.get_bind()
        inspector = inspect(bind)
        if "key" in {constraint["column_names"][0] for constraint in inspector.get_unique_constraints("settings") if len(constraint["column_names"]) == 1}:
            with op.batch_alter_table("settings") as batch_op:
                for constraint in inspector.get_unique_constraints("settings"):
                    if constraint["column_names"] == ["key"]:
                        batch_op.drop_constraint(constraint["name"], type_="unique")
                        break
        if "uq_settings_user_key" not in _constraint_names("settings"):
            op.create_unique_constraint("uq_settings_user_key", "settings", ["user_id", "key"])

    if not _has_table("user_file_settings"):
        op.create_table(
            "user_file_settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("file_id", sa.Integer(), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("user_id", "file_id", name="uq_user_file_settings_user_file"),
        )
        op.create_index("ix_user_file_settings_user_id", "user_file_settings", ["user_id"])
        op.create_index("ix_user_file_settings_file_id", "user_file_settings", ["file_id"])


def downgrade() -> None:
    if _has_table("user_file_settings"):
        op.drop_table("user_file_settings")
    if _has_table("user_sessions"):
        op.drop_table("user_sessions")
