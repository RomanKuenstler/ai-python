# Admin

## Admin UI

Admins get an `Admin` entry in the left sidebar above `Personalization`.

The admin page supports:

- listing all users
- activating or deactivating users
- toggling `force_password_change`
- deleting users
- creating new users with the default password `Passw0rd!`

Admins cannot delete their own account, and the UI disables that action.

## Admin API

- `GET /api/admin/users`
- `POST /api/admin/users`
- `PATCH /api/admin/users/{id}`
- `DELETE /api/admin/users/{id}`

All admin endpoints require:

- a valid JWT
- an active session
- `role = admin`
- no pending forced password change on the acting admin
