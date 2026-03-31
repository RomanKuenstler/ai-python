from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260330_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in set(inspect(op.get_bind()).get_table_names())


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if _has_table("chats") and not _has_column("chats", "is_archived"):
        op.add_column("chats", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))

    if not _has_table("settings"):
        op.create_table(
            "settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=128), nullable=False, unique=True),
            sa.Column("value", sa.Text(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    if _has_table("chats"):
        op.execute("UPDATE chats SET is_archived = FALSE WHERE is_archived IS NULL")


def downgrade() -> None:
    if _has_table("settings"):
        op.drop_table("settings")
