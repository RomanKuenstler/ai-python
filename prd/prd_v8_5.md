prd_v8_5.md — Local RAG System (Step 8.5)

1. Overview

1.1 Goal

Harden the system so that all protected backend APIs and all protected web UI pages can only be used when the user is properly authenticated.

1.2 Step 8.5 Scope

This step focuses only on access protection and auth enforcement.

It introduces:
	•	strict API authentication enforcement
	•	strict frontend route protection
	•	redirect handling for unauthenticated users
	•	session expiration handling in the UI
	•	backend authorization guards for authenticated-only access
	•	consistent handling of invalid, missing, expired, or revoked authentication

1.3 Explicit Non-Goal

This step does not add new product features.
It only secures access to the existing system.

⸻

2. Required Outcomes

After Step 8.5, the system must:
	•	reject all protected API calls when authentication is missing or invalid
	•	prevent direct access to protected web UI pages when not authenticated
	•	allow access only to the login page without authentication
	•	redirect unauthenticated users to the login page
	•	handle expired sessions consistently
	•	prevent protected data from loading in the frontend before auth is confirmed
	•	prevent role-protected pages from being accessed by unauthorized users
	•	keep Step 8 behavior working without regression

⸻

3. Protection Requirements

3.1 Protected Web UI Pages

All web UI pages must require authentication except the login page.

Protected pages include at minimum:
	•	chat page
	•	library page
	•	admin page
	•	preferences-related pages/dialogs if they depend on authenticated data
	•	archive views
	•	any other internal application route

Only the login page may be accessible without authentication.

3.2 Protected APIs

All backend APIs must require valid authentication unless explicitly marked as public.

Public endpoints should be kept to the absolute minimum.

Expected public endpoints:
	•	POST /api/auth/login
	•	possibly a minimal auth/session bootstrap endpoint if needed
	•	optionally a health endpoint if intentionally public

All other endpoints must be protected.

⸻

4. Backend API Protection Requirements

4.1 Authentication Middleware

The backend must enforce authentication centrally through middleware or dependency-based guards.

Requirements:
	•	validate token presence
	•	validate token integrity/signature
	•	validate token expiration
	•	validate user still exists
	•	validate user status is active
	•	reject inactive users
	•	attach authenticated user context to request handling

4.2 Default-Secure Rule

Backend routing should follow a default-secure model:
	•	endpoints are protected by default
	•	public access must be explicitly declared

4.3 Failure Responses

If authentication fails, the API must return appropriate error responses.

At minimum handle:
	•	missing token
	•	malformed token
	•	expired token
	•	invalid token
	•	inactive user
	•	insufficient role

Recommended response codes:
	•	401 Unauthorized for missing/invalid/expired auth
	•	403 Forbidden for authenticated but unauthorized access

4.4 Authenticated User Context

Every protected API request should expose authenticated user context to the handler, including at minimum:
	•	user id
	•	username
	•	role
	•	active/inactive state if useful

4.5 Role Enforcement

Role-based endpoints must also be protected after authentication.

For example:
	•	admin endpoints must require authenticated user with role admin
	•	normal authenticated users must not access admin-only APIs

Server-side role checks are mandatory.
Frontend-only hiding is not sufficient.

⸻

5. Frontend Route Protection Requirements

5.1 Route Guards

The web UI must implement route guards so that protected routes cannot be used without valid authentication.

Behavior:
	•	if user is not authenticated, redirect to login page
	•	if token/session is invalid or expired, redirect to login page
	•	protected content must not briefly flash before redirect

5.2 Initial App Load

On app startup or page refresh, the frontend must determine auth state before rendering protected app content.

Requirements:
	•	block protected route rendering until auth state is resolved
	•	show a loading/splash state if needed during auth check
	•	avoid rendering user-specific content before auth validation completes

5.3 Unauthorized Role Handling

If a logged-in user accesses a route they are not allowed to use, such as the admin page without admin role:
	•	do not render the protected page
	•	redirect to a safe allowed page or show a proper unauthorized state

Preferred behavior:
	•	redirect non-admin users away from admin routes to the main chat page

⸻

6. Session and Expiration Handling

6.1 Expired Session Behavior

If a token/session expires:
	•	backend must reject requests
	•	frontend must detect this
	•	user must be logged out or redirected to login
	•	protected pages must become inaccessible immediately

6.2 Active Session Refresh

If the system already supports refresh/sliding validity from Step 8, Step 8.5 must ensure that protection logic works correctly with it.

That means:
	•	requests with valid refreshed auth continue working
	•	requests after hard expiration fail and force re-login

6.3 Session Loss Recovery

If the frontend loses session state or token storage becomes invalid:
	•	app must fall back to unauthenticated state
	•	user must be redirected to login
	•	stale protected data must not remain interactable

⸻

7. Frontend Auth State Requirements

7.1 Auth State Model

Frontend must reliably track at minimum:
	•	whether auth state is still loading
	•	whether user is authenticated
	•	current user info
	•	current token/session validity
	•	current role

7.2 Protected App Shell

The protected app shell must not mount as fully usable until authentication succeeds.

This includes:
	•	sidebar
	•	chats
	•	library data
	•	admin data
	•	preferences data

7.3 Request Interceptor Handling

Frontend API calls should consistently include auth credentials and handle auth failures centrally.

Recommended behavior:
	•	attach token automatically
	•	intercept 401 responses
	•	clear invalid session state
	•	redirect to login when appropriate

⸻

8. Page-Level Requirements

8.1 Login Page

The login page remains public.

Behavior:
	•	unauthenticated users can access it
	•	authenticated users should not stay there unnecessarily

Preferred behavior:
	•	if already authenticated and valid, redirect from login page to main app

8.2 Chat Page

Must require valid authentication.

8.3 Library Page

Must require valid authentication.

8.4 Admin Page

Must require:
	•	valid authentication
	•	admin role

8.5 Other App UI

Any future authenticated page should inherit the same protection pattern.

⸻

9. API-Level Requirements

9.1 Protected Endpoints

At minimum, the following classes of endpoints must be protected:
	•	chats
	•	messages
	•	retrieval
	•	library
	•	uploads
	•	settings
	•	preferences
	•	archive
	•	download/export
	•	admin
	•	user profile / auth me endpoints except login/logout semantics as appropriate

9.2 Public Endpoints

Only explicitly public endpoints may remain open.

Recommended public endpoints:
	•	login
	•	possibly health if intentionally public

Everything else must be authenticated.

9.3 File Upload Protection

Upload endpoints must also require authentication.

Unauthenticated users must not be able to upload files, trigger embedding, or manipulate library content.

⸻

10. Security Requirements

10.1 No Trust in Frontend Alone

The backend must never rely on hidden buttons or protected routes alone.

All protections must be enforced server-side.

10.2 No Data Leakage

Protected API endpoints must not leak sensitive data to unauthenticated users.

This includes:
	•	chat lists
	•	message history
	•	user details
	•	settings
	•	library state
	•	admin data

10.3 Inactive Users

If a user is marked inactive:
	•	they must not be able to log in
	•	existing sessions should be rejected when checked
	•	protected APIs must deny access

⸻

11. Suggested Implementation Approach

11.1 Backend

Recommended:
	•	central auth dependency or middleware for FastAPI
	•	helper for current authenticated user
	•	helper for admin-only access
	•	standardized auth error responses

11.2 Frontend

Recommended:
	•	authenticated layout wrapper
	•	protected route component
	•	auth provider/context
	•	centralized request client with auth interceptor
	•	redirect-on-401 behavior

⸻

12. Testing, Validation, and Debugging Requirements

12.1 Implementation Is Not Finished Without Verification

Step 8.5 is not complete when guards merely exist in code.
It is complete only after protection has been tested and verified.

12.2 Required Validation

Codex must verify at minimum:
	•	unauthenticated user can access only login page
	•	unauthenticated user cannot open chat page directly by URL
	•	unauthenticated user cannot open library page directly by URL
	•	unauthenticated user cannot open admin page directly by URL
	•	unauthenticated API requests are rejected
	•	expired tokens are rejected
	•	invalid tokens are rejected
	•	inactive users are rejected
	•	authenticated users can access allowed pages
	•	non-admin authenticated users cannot access admin page or admin APIs
	•	authenticated users are redirected away from login page if already validly logged in
	•	protected content does not flash before redirect
	•	Step 8 auth behavior is not broken

12.3 Required Debugging Loop

If issues are found during verification, Codex must:
	1.	identify the cause
	2.	debug and fix it
	3.	rerun validation
	4.	update docs if needed
	5.	update changelog.md

12.4 Recommended Tests

Codex should add tests where practical, especially for:
	•	protected API access without token
	•	protected API access with invalid token
	•	protected API access with expired token
	•	frontend protected route redirect behavior
	•	admin route authorization behavior
	•	authenticated redirect-away-from-login behavior

⸻

13. Documentation Requirements

Codex must update or create:
	•	docs/authentication.md
	•	docs/api.md
	•	docs/frontend.md
	•	docs/testing.md

13.1 docs/authentication.md

Must document:
	•	which routes are public
	•	which routes are protected
	•	how token validation works
	•	how expired/inactive users are handled

13.2 docs/api.md

Must document:
	•	auth requirements for endpoints
	•	expected 401 and 403 behavior
	•	admin-only endpoint protection

13.3 docs/frontend.md

Must document:
	•	protected route handling
	•	redirect logic
	•	auth loading state handling

13.4 docs/testing.md

Must document:
	•	how auth protection was verified
	•	route protection test cases
	•	API protection test cases
	•	common debugging steps

13.5 changelog.md

Must be updated for all Step 8.5 changes.

⸻

14. Acceptance Criteria

14.1 API Protection
	•	all protected APIs reject unauthenticated access
	•	invalid and expired auth is rejected
	•	admin APIs require admin role

14.2 Web UI Protection
	•	all protected pages require authentication
	•	only login page is publicly accessible
	•	protected content does not render for unauthenticated users
	•	non-admin users cannot access admin page

14.3 Session Handling
	•	expired sessions force login again
	•	invalid sessions are cleared cleanly
	•	authenticated users can continue using allowed routes

14.4 Quality Gate
	•	protection has been tested
	•	issues found have been debugged and fixed
	•	docs updated
	•	changelog updated

⸻

15. Engineering Requirements

Codex must follow these implementation rules:
	•	use backend-enforced protection as the source of truth
	•	keep auth logic centralized
	•	avoid duplicate route-guard logic scattered across the app
	•	keep frontend protection predictable and maintainable
	•	preserve existing functionality
	•	validate carefully
	•	debug regressions before considering Step 8.5 complete