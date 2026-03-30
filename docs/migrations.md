# Migrations

## Tooling

The project now uses Alembic for schema management.

Directory layout:

```text
migrations/
  env.py
  script.py.mako
  versions/
```

## Runtime Behavior

`PostgresClient.initialize()` now runs Alembic upgrades to `head` instead of calling `Base.metadata.create_all()`.

This keeps:

- schema history in version control
- application startup aligned with the declared schema
- future schema changes additive and reviewable

## Creating a New Migration

Example:

```bash
.venv/bin/alembic revision -m "describe change"
```

Then apply:

```bash
.venv/bin/alembic upgrade head
```

Set `sqlalchemy.url` through the app config or the Alembic config object.
