# Security

## Password Security

- Argon2 hashes are stored in the database.
- The configured salt is appended before hashing.
- Default credentials are only for bootstrap and must be rotated on first use.

## Session Security

- JWTs are signed with `JWT_SECRET`.
- Each JWT maps to a server-side session row.
- Revoked or expired sessions are rejected even if an old token is still presented.

## Authorization

- Role checks are enforced server-side.
- User-scoped queries filter chats, messages, retrieval logs, and settings by `user_id`.
- Normal users cannot disable system files.
- Normal users can delete only files they uploaded.
- Admins can delete any file, including system files under `/data`.
