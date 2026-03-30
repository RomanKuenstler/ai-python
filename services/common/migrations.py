from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def run_migrations(database_url: str) -> None:
    root_dir = Path(__file__).resolve().parents[2]
    config = Config()
    config.set_main_option("script_location", str(root_dir / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
