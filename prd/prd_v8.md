prd_v8.md — Local RAG System (Step 8)

⸻

1. Overview

1.1 Goal

Introduce authentication, multi-user support, and role-based access control into the system.

1.2 Step 8 Scope

This step introduces:
	•	user authentication (username + password)
	•	multi-user system
	•	user roles (user, admin)
	•	user lifecycle management
	•	session/token handling
	•	per-user data isolation
	•	admin UI for user management
	•	users bootstrap via users.json

⸻

2. High-Level Changes

⸻

2.1 System Evolution

User → Login → Authenticated Session
→ WebUI (user-scoped)
→ Retriever API (user-scoped)
→ Postgres (user-specific data)
→ Qdrant (shared, but filtered per user settings)


⸻

3. Authentication System

⸻

3.1 Login Mechanism
	•	username + password login
	•	no signup functionality
	•	users must exist via system provisioning

⸻

3.2 Password Security

Passwords must:
	•	never be stored in plain text
	•	be hashed using a secure hashing function (e.g. bcrypt or argon2)

Additionally:
	•	include salt string:

%vSp3$


	•	hashing input:

hash(password + "%vSp3$")



⸻

3.3 Session Strategy

Use JWT-based authentication (recommended).

Token Rules:
	•	valid duration: 2 hours
	•	sliding refresh:
	•	if user is actively using the system → refresh token after ~1 hour
	•	hard expiration:
	•	after 12 hours total, force re-login

⸻

3.4 Session Definition

“Active user” means:
	•	sending messages
	•	navigating UI
	•	interacting with API

Not just idle logged-in state.

⸻

3.5 Logout
	•	must invalidate session (client-side + backend awareness)
	•	token removal on client

⸻

4. User Bootstrap via users.json

⸻

4.1 File Location

/users.json


⸻

4.2 Structure

[
  {
    "username": "admin",
    "displayname": "Admin User",
    "role": "admin"
  },
  {
    "username": "john",
    "displayname": "John Doe",
    "role": "user"
  },
  {
    "username": "anna",
    "displayname": "Anna Smith",
    "role": "user"
  }
]


⸻

4.3 Startup Behavior

On system startup:

For each user in users.json:
	•	if user does NOT exist in DB:
	•	create user
	•	set password = "Passw0rd!" (hashed)
	•	set:
	•	force_password_change = true
	•	status = active
	•	if user exists:
	•	ensure:
	•	role matches
	•	displayname updated

⸻

Users NOT in users.json:
	•	do NOT delete
	•	set:
	•	status = inactive

⸻

5. User Model

⸻

5.1 Users Table

id
username UNIQUE
displayname
password_hash
role (user | admin)
status (active | inactive)
force_password_change BOOLEAN
created_at
updated_at


⸻

6. Authentication Flow

⸻

6.1 Login Flow
	1.	user enters username + password
	2.	system:
	•	checks user exists
	•	checks status = active
	•	verifies password hash
	3.	returns JWT token

⸻

6.2 Forced Password Change

If:

force_password_change = true

Then:
	•	user must be redirected to password change screen
	•	cannot access app until completed

⸻

6.3 Password Change Rules
	•	must confirm new password
	•	must not be empty
	•	must replace existing password hash
	•	set:
	•	force_password_change = false

⸻

7. Web UI — Authentication Pages

⸻

7.1 Login Page

Must include:
	•	username input
	•	password input
	•	login button
	•	error handling

⸻

7.2 Password Change Page

Shown when required.

Includes:
	•	new password input
	•	confirm password input
	•	submit button

⸻

7.3 Logout

Accessible from user menu.

⸻

8. Multi-User Data Isolation

⸻

8.1 User-Scoped Data

Each user must have isolated:
	•	chats
	•	messages
	•	retrieval logs
	•	settings
	•	preferences
	•	archived chats

⸻

8.2 Database Changes

All relevant tables must include:

user_id


⸻

9. Library Behavior (Global + Per User)

⸻

9.1 Global Library
	•	files are global
	•	stored once

⸻

9.2 Per-User File State

Each user can:
	•	disable files (for retrieval)

Stored per user:

user_file_settings
user_id
file_id
is_enabled


⸻

9.3 Restrictions

Users:
	•	can delete ONLY files they uploaded

Admins:
	•	can delete ALL files
	•	including system files from /data

⸻

9.4 System Files

Files placed directly in /data:
	•	marked as system files
	•	cannot be disabled by normal users

⸻

10. Admin Page

⸻

10.1 Access
	•	visible only for admin role
	•	located in sidebar above Library

⸻

10.2 Content

Users Table

Columns:
	•	username
	•	displayname
	•	role
	•	status
	•	actions

⸻

10.3 Actions

Activate / Deactivate
	•	toggle switch

Force Password Change
	•	toggle switch

Delete User
	•	opens confirm dialog

⸻

10.4 Restrictions
	•	admin cannot delete own account

⸻

10.5 Add User

Button below table.

Opens dialog:
	•	username
	•	displayname
	•	role dropdown

Creates:
	•	password = "Passw0rd!"
	•	force_password_change = true
	•	status = active

⸻

11. Preferences Changes

⸻

Preferences now must be:
	•	user-specific
	•	stored per user

⸻

12. API Changes

⸻

12.1 Auth Endpoints

POST /api/auth/login
POST /api/auth/logout
POST /api/auth/change-password
GET  /api/auth/me


⸻

12.2 User Management (Admin)

GET    /api/admin/users
POST   /api/admin/users
PATCH  /api/admin/users/{id}
DELETE /api/admin/users/{id}


⸻

12.3 Middleware

All endpoints must:
	•	validate JWT
	•	extract user context

⸻

13. Frontend State Changes

⸻

Frontend must manage:
	•	auth state
	•	current user
	•	token
	•	session expiration
	•	role-based UI visibility

⸻

14. UI/UX Requirements

⸻

Authentication
	•	clean login page
	•	clear error states
	•	smooth redirect flow

⸻

Admin Page
	•	table layout consistent with Library
	•	switches styled like rest of UI
	•	dialogs consistent

⸻

User Menu
	•	now fully functional
	•	includes logout

⸻

15. Security Requirements

⸻

Must ensure:
	•	password hashing secure
	•	no plaintext passwords anywhere
	•	JWT validated properly
	•	role checks enforced server-side
	•	user cannot access other user data

⸻

16. Configuration

⸻


JWT_SECRET=supersecretkey
JWT_EXPIRATION_MINUTES=120
JWT_REFRESH_THRESHOLD_MINUTES=60
JWT_MAX_LIFETIME_MINUTES=720

PASSWORD_SALT=%vSp3$


⸻

17. Testing & Validation

⸻

17.1 Required Validation

Codex must verify:
	•	login works
	•	password hashing works
	•	forced password change works
	•	logout works
	•	token expiration works
	•	refresh works correctly
	•	user isolation works
	•	admin page works
	•	role restrictions enforced
	•	file permissions enforced
	•	no regression from Step 1–7

⸻

17.2 Debugging Loop

If issues:
	1.	identify
	2.	fix
	3.	retest
	4.	document

⸻

18. Documentation Requirements

⸻

Create/update:
	•	docs/authentication.md
	•	docs/users.md
	•	docs/admin.md
	•	docs/security.md
	•	docs/api.md

⸻

19. Acceptance Criteria

⸻

Authentication
	•	login works
	•	logout works
	•	password change enforced when required

Multi-User
	•	users isolated
	•	settings isolated
	•	chats isolated

Admin
	•	admin page accessible only for admins
	•	user management works

Security
	•	passwords hashed
	•	JWT works correctly

Library
	•	per-user file disable works
	•	permissions enforced

Quality
	•	tested
	•	debugged
	•	documented

⸻

20. Non-Goals

Do NOT implement:
	•	signup
	•	OAuth/social login
	•	multi-tenant scaling
	•	RBAC beyond user/admin

⸻

21. Engineering Requirements
	•	clean modular auth layer
	•	middleware-based security
	•	no duplicated auth logic
	•	maintainable DB schema
	•	proper migrations
	•	strict validation
	•	changelog updates
	•	full system validation before completion

⸻

22. Future (Step 9 Preview)
	•	teams / organizations
	•	permissions system
	•	audit logs
	•	SSO
	•	API keys