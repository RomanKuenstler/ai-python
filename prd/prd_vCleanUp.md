prd_vCleanUp.md — Local RAG System

1. Overview

1.1 Goal

Stabilize and professionalize the project by cleaning up the codebase, refactoring where needed, updating tests and migrations, improving setup/start documentation, and preparing a production-oriented container setup alongside the existing development setup.

1.2 Step Scope

This step focuses on:
	•	project cleanup
	•	refactoring
	•	file/module splitting where needed
	•	removing dead or duplicated code
	•	updating and extending tests
	•	reviewing and fixing migrations if needed
	•	updating setup/start/run documentation
	•	adding production Dockerfiles
	•	adding a prod-compose.yml
	•	preparing the project for a more production-like deployment model

1.3 Explicit Non-Goal

This step is not for adding major new product features.
The main focus is quality, maintainability, correctness, and production readiness.

Small supporting improvements are allowed if they are needed to complete the cleanup and production preparation properly.

⸻

2. Required Outcomes

After this Step, the project must:
	•	have a cleaner, more maintainable code structure
	•	have large or overly complex files split into clearer modules where appropriate
	•	remove stale, duplicate, and unused code where safe
	•	have tests updated to match the current system behavior
	•	have migrations reviewed and corrected if needed
	•	have clearer startup/setup/development docs
	•	include production-oriented Dockerfiles
	•	include a prod-compose.yml
	•	keep the current development workflow unchanged and working
	•	keep all implemented Step 1–12 functionality working without regression

⸻

3. High-Level Priorities

3.1 Maintainability

Improve the project structure so future steps are easier and safer to implement.

3.2 Stability

Verify that cleanup/refactor work does not break existing behavior.

3.3 Production Preparation

Add a clean production container setup without replacing the development setup.

3.4 Documentation

Ensure new contributors or future-you can start, run, migrate, and deploy the system without confusion.

⸻

4. Cleanup and Refactoring Requirements

4.1 General Cleanup

Codex must review the project and clean up where appropriate, including:
	•	duplicated logic
	•	stale files
	•	dead code
	•	unused imports
	•	inconsistent naming
	•	outdated helper functions
	•	obsolete styles/components
	•	old temporary scaffolding no longer needed

Cleanup must be done carefully and only when safe.

4.2 Refactoring Scope

Codex should refactor areas that have become hard to maintain due to previous step-by-step growth.

Typical targets may include:
	•	large API route files
	•	prompt building logic
	•	retriever pipeline orchestration
	•	embedder processors
	•	frontend component trees
	•	dialog/menu state handling
	•	shared config loading
	•	filtering and settings logic
	•	GPT and user-config separation
	•	auth/session handling modules

4.3 Split Large Files

If files have become too large or too mixed in responsibility, split them into smaller modules.

This should especially apply where one file currently mixes several responsibilities such as:
	•	route definitions + business logic + persistence
	•	React UI + local state + API calls + formatting logic
	•	prompt loading + prompt composition + mode selection + personalization merging

4.4 Preserve Behavior

Refactoring must not silently change product behavior unless a bug fix is intentionally being made.

Any intentional behavior changes must be:
	•	justified
	•	tested
	•	documented
	•	added to changelog.md

⸻

5. Architecture Review Requirements

5.1 Backend Structure Review

Review whether the backend is cleanly separated into concerns such as:
	•	routes/controllers
	•	schemas
	•	services
	•	repositories/data access
	•	auth/security
	•	prompt building
	•	retrieval orchestration
	•	embedder processing
	•	config management

Refactor toward a more maintainable structure if needed.

5.2 Frontend Structure Review

Review whether the frontend is cleanly separated into concerns such as:
	•	layout
	•	pages
	•	domain-specific components
	•	dialogs
	•	menus
	•	hooks
	•	API client
	•	state management
	•	shared UI primitives
	•	type definitions
	•	style tokens or design system utilities

Refactor toward a clearer structure if needed.

5.3 Shared Logic Review

Check for duplicated logic across:
	•	user vs GPT configuration handling
	•	chat vs GPT chat behavior
	•	file filtering vs tag filtering
	•	settings validation
	•	auth guards
	•	markdown rendering
	•	source rendering
	•	upload validation

Consolidate where appropriate.

⸻

6. Tests Requirements

6.1 Test Review

Review the current test suite and bring it in line with the current functionality of the project.

Codex should identify:
	•	outdated tests
	•	missing tests
	•	broken tests
	•	flaky tests
	•	duplicated tests

6.2 Update Tests

Existing tests must be updated to reflect the current code structure and current supported behavior.

6.3 Add Missing Tests Where Important

Add tests where practical and especially where refactoring or production prep touches critical areas.

Priority areas include:
	•	authentication and route protection
	•	assistant mode pipelines
	•	personalization prompt composition
	•	filtering logic
	•	library file state logic
	•	GPT configuration isolation
	•	admin role enforcement
	•	upload validation and limits
	•	retrieval source handling
	•	settings persistence
	•	archive/download behavior

6.4 Test Categories

Where appropriate, maintain or improve separation between:
	•	unit tests
	•	integration tests
	•	API tests
	•	frontend component or interaction tests
	•	smoke tests

6.5 Production-Relevant Tests

Add or improve tests around:
	•	startup/config loading
	•	migrations
	•	environment handling
	•	auth/session behavior
	•	permission checks

⸻

7. Database and Migration Requirements

7.1 Migration Review

Review all existing migrations and ensure they are consistent with the actual code and schema expectations.

Check for:
	•	missing migrations
	•	schema drift
	•	duplicate or conflicting migrations
	•	obsolete migration assumptions
	•	invalid defaults
	•	missing indexes or constraints where needed

7.2 Fix Migrations If Needed

If migrations are inconsistent or incomplete, Codex must correct them.

Rules:
	•	do not silently break existing migration history
	•	preserve upgradeability
	•	document any migration repair clearly
	•	update docs accordingly

7.3 Migration Reliability

The project must support a reliable migration flow for both:
	•	development environments
	•	production-like environments

7.4 Seed / Bootstrap Compatibility

Ensure that migrations work correctly alongside:
	•	users.json bootstrap
	•	file/library state
	•	auth/user tables
	•	GPT-related tables
	•	settings/filter/personalization tables

⸻

8. Documentation Requirements

8.1 Setup/Start Docs Must Be Updated

Update setup and run documentation so it reflects the real current state of the project.

At minimum document:
	•	project overview
	•	development startup
	•	production-like startup
	•	environment files
	•	migrations
	•	auth bootstrap behavior
	•	data folder behavior
	•	OCR/runtime dependencies
	•	common troubleshooting steps

8.2 Required Documentation Updates

Codex must update or create at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/migrations.md
	•	docs/testing.md
	•	docs/architecture.md

8.3 README Goals

The root README.md should become a reliable starting point for the project.

It should clearly explain:
	•	what the project is
	•	major services
	•	how to run in development
	•	how to run migrations
	•	where docs are
	•	how production setup differs from development

8.4 Setup Documentation

docs/setup.md should explain initial setup including:
	•	required tools
	•	env configuration
	•	Docker setup
	•	data folders
	•	prompt files
	•	users bootstrap file
	•	first startup
	•	migration workflow

8.5 Development Documentation

docs/development.md should explain:
	•	normal development startup flow
	•	dev compose usage
	•	how to rebuild services
	•	how to run tests
	•	how hot reload or frontend dev mode works if applicable
	•	how to debug common issues

8.6 Production Documentation

docs/production.md should explain:
	•	purpose of production Dockerfiles and prod-compose.yml
	•	build/run workflow
	•	required env variables
	•	migration handling for production
	•	persistent volumes
	•	secrets considerations
	•	reverse proxy or deployment notes if relevant

⸻

9. Production Containerization Requirements

9.1 Keep Development Setup Intact

The current normal Dockerfiles / compose flow for development must stay available and remain the default for development work.

Do not replace the development workflow.

9.2 Add Production-Oriented Setup

Create a separate production-oriented container setup.

Required deliverables:
	•	prod-compose.yml
	•	production Dockerfiles for relevant services

Suggested naming:
	•	Dockerfile.prod per service, or
	•	clear equivalent naming convention

The naming should be consistent and easy to understand.

9.3 Production Setup Goals

The production-oriented setup should be more suitable for real usage than the dev setup.

This should include where appropriate:
	•	smaller/more focused images
	•	multi-stage builds
	•	fewer dev-only dependencies
	•	production server/runtime commands
	•	minimized debug behavior
	•	stable startup flow
	•	explicit environment usage

9.4 Services Covered

Prepare production-oriented container definitions for at least the services that matter operationally, such as:
	•	web UI
	•	retriever/backend API
	•	embedder
	•	any supporting service wrappers if needed

External services like Postgres and Qdrant may still use official images, but the production compose should define them clearly for production-like usage.

9.5 Production Build Behavior

Production Dockerfiles should avoid development-only behavior such as:
	•	auto-reload servers
	•	debug commands
	•	unnecessary dev packages
	•	mounting source code as the normal runtime model

9.6 Production Runtime Considerations

Production setup should consider:
	•	persistent volumes
	•	environment variable handling
	•	port exposure
	•	startup order / readiness
	•	migration execution strategy
	•	restart policies
	•	logs
	•	health checks where useful

9.7 Security / Sensible Defaults

Production setup should avoid obviously unsafe defaults where practical.

At minimum consider:
	•	non-debug runtime mode
	•	secrets via env, not hardcoded
	•	minimal container privileges where reasonable
	•	persistent data isolation
	•	stable network definitions

⸻

10. Production Compose Requirements

10.1 prod-compose.yml

Create a dedicated prod-compose.yml for a production-like deployment.

It should be clearly separate from the dev compose file.

10.2 Purpose

This file should allow a user to bring up the application stack in a way that is more production-suitable, while still being local/self-hostable.

10.3 Required Considerations

The file should handle or document:
	•	backend API service
	•	embedder service
	•	web UI service
	•	Postgres
	•	Qdrant
	•	persistent volumes
	•	environment files
	•	migration execution strategy
	•	service dependencies
	•	health checks where useful

10.4 Do Not Break Dev Flow

Adding prod-compose.yml must not interfere with the current development compose setup.

⸻

11. Production Dockerfile Requirements

11.1 General Rules

Production Dockerfiles should:
	•	be clean
	•	be clearly separated from dev Dockerfiles
	•	use multi-stage builds where appropriate
	•	avoid unnecessary packages
	•	use production commands
	•	be documented

11.2 Frontend Production Build

The web UI production Dockerfile should:
	•	build the frontend assets
	•	serve them in a production-appropriate way
	•	avoid running the dev server in production mode

11.3 Backend Production Build

The backend/retriever production Dockerfile should:
	•	install only needed runtime dependencies
	•	run with a production server process
	•	avoid development reload mode

11.4 Embedder Production Build

The embedder production Dockerfile should:
	•	include required runtime dependencies
	•	include OCR/runtime libraries if needed
	•	avoid dev-only tools unless genuinely needed at runtime

⸻

12. Environment and Config Requirements

12.1 Environment Review

Review current env usage and clean up where helpful.

Possible improvements include:
	•	clearer naming
	•	separating dev vs production env docs
	•	documenting required vs optional variables
	•	documenting defaults
	•	removing obsolete config keys

12.2 Production Env Documentation

Document all required production-related variables clearly.

This includes at minimum:
	•	auth/JWT config
	•	DB connection config
	•	Qdrant config
	•	OCR config if applicable
	•	upload/file config
	•	runtime mode config
	•	migration config if needed

⸻

13. Operational Readiness Requirements

13.1 Startup Reliability

The system should have a clearer and more reliable startup story.

This includes:
	•	migration ordering
	•	bootstrap ordering
	•	service dependency handling
	•	clearer expected startup sequence

13.2 Health Checks

Add or improve health checks where useful, especially for production compose.

13.3 Failure Clarity

If production startup fails, logs and docs should make it reasonably clear what to inspect.

⸻

14. Changelog and Project Hygiene Requirements

14.1 Changelog

changelog.md must be updated for all Step changes.

14.2 Project Hygiene

Codex should also review and improve where reasonable:
	•	folder naming consistency
	•	file naming consistency
	•	doc naming consistency
	•	comments/docstrings in critical areas
	•	removal of abandoned temporary code paths

⸻

15. Testing, Validation, and Debugging Requirements

15.1 Implementation Is Not Finished Without Verification

The step is not complete when refactors and production files merely exist.
It is complete only after the result has been checked, validated, and debugged where necessary.

15.2 Required Validation

Codex must verify at minimum:
	•	development setup still works
	•	production compose builds successfully
	•	production-oriented containers start successfully
	•	migrations still work
	•	tests run successfully after refactoring
	•	authentication still works
	•	retriever still works
	•	embedder still works
	•	web UI still works
	•	library still works
	•	GPTs still work
	•	existing settings/filtering/personalization still work
	•	no regressions from Step 1–12

15.3 Refactor Safety Checks

Codex must verify that cleanup/refactoring did not break:
	•	routing
	•	prompt building
	•	settings persistence
	•	user isolation
	•	file filtering
	•	assistant modes
	•	uploads
	•	markdown rendering
	•	admin functionality

15.4 Production Validation

Codex should validate the production setup at minimum by checking:
	•	images build
	•	services run
	•	env handling is correct
	•	persistent storage is defined
	•	production docs match actual setup

15.5 Required Debugging Loop

If problems are found during cleanup, refactoring, migration review, testing, or production validation, Codex must:
	1.	identify the cause
	2.	debug and fix it
	3.	rerun the relevant validation
	4.	update docs if behavior or setup changed
	5.	update changelog.md

⸻

16. Acceptance Criteria

16.1 Cleanup and Refactor
	•	codebase is cleaner and easier to maintain
	•	overly large files are split where appropriate
	•	stale and duplicated code is reduced
	•	behavior remains correct

16.2 Tests and Migrations
	•	tests are updated and relevant
	•	migrations are reviewed and corrected if needed
	•	migration flow remains reliable

16.3 Documentation
	•	setup/start docs are updated
	•	README is accurate and useful
	•	development and production docs are clearly separated

16.4 Production Preparation
	•	prod-compose.yml exists
	•	production Dockerfiles exist
	•	production-oriented setup is documented
	•	development flow remains available and unchanged

16.5 Quality Gate
	•	refactors have been tested
	•	issues found have been debugged and fixed
	•	docs updated
	•	changelog updated

⸻

17. Nice-to-Haves

Allowed if they help maintainability or production readiness without expanding scope too much:
	•	better shared utility modules
	•	clearer domain folder structure
	•	stronger typed schemas
	•	improved health check endpoints
	•	startup helper scripts for migrations/bootstrap
	•	lint/format script improvements
	•	more explicit Makefile/task runner commands if already appropriate for the project

⸻

18. Explicit Non-Goals

Do not add major new product features in this step unless strictly needed to complete cleanup or production preparation.

Examples of non-goals:
	•	new assistant modes
	•	new retrieval strategies
	•	new personalization features
	•	new GPT features
	•	new library features
	•	new auth features beyond what is needed to keep current behavior working

⸻

19. Engineering Requirements

Codex must follow these implementation rules:
	•	prioritize maintainability and clarity
	•	refactor carefully, not recklessly
	•	avoid unnecessary architecture churn
	•	keep production and development concerns clearly separated
	•	do not break the existing dev workflow
	•	update tests, docs, and migrations together with code changes
	•	validate the final result carefully
	•	debug regressions before considering the step complete