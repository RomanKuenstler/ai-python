# Users

## Bootstrap

On retriever startup the app reads [`users.json`](/Users/rknstlr/Workspace/ai-python/users.json).

For every listed user:

- create the user if missing
- set default password to `Passw0rd!` when created
- mark `force_password_change = true` when created
- force `status = active`
- keep `role` and `displayname` aligned with the file

Users not present in `users.json` are not deleted, but they are marked `inactive` on startup.

## User Roles

- `user`: can use chat, preferences, and their user-scoped library settings
- `admin`: can do everything a user can do plus user lifecycle management and all library deletes

## User-Scoped Data

The following data is isolated per user in Postgres:

- chats
- chat messages
- retrieval logs
- runtime settings / preferences
- archived chat state
- file enablement preferences
