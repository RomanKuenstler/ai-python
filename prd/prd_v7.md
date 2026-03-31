prd_v7.md — Local RAG System (Step 7)

1. Overview

1.1 Goal

Refine the current web UI so it matches the reference UI in look, feel, layout, spacing, behavior, and visual polish as closely as possible.

1.2 Step 7 Scope

This step is web UI restyling only.

It is focused on:
	•	exact visual restyling
	•	exact layout alignment
	•	exact component styling
	•	exact interaction styling
	•	exact states styling
	•	exact dialog/dropdown styling
	•	exact typography, spacing, sizing, borders, and colors

1.3 Explicit Non-Goal

This step must not introduce new product features.

Do not add new backend features, retrieval features, embedder features, or database features unless a tiny UI-support adjustment is strictly necessary for existing functionality already implemented.

⸻

2. Core Requirement

2.1 Reference Parity Requirement

The web UI must be reworked so it looks and feels exactly like the reference UI in other webui.

This means Codex must deeply analyze the reference implementation and then restyle the existing UI to match it as closely as possible.

This includes at minimum:
	•	overall page layout
	•	sidebar proportions
	•	top/bottom spacing
	•	typography scale
	•	font weight usage
	•	color palette
	•	surface colors
	•	borders
	•	shadows
	•	rounded corners
	•	hover states
	•	active states
	•	disabled states
	•	focus states
	•	dropdown styling
	•	dialog styling
	•	button styling
	•	input styling
	•	table styling
	•	message styling
	•	markdown content styling
	•	source button and source panel styling
	•	icon sizing and alignment
	•	transitions and micro-interactions
	•	empty states
	•	scroll behavior and scroll container styling

⸻

3. Strict Implementation Rules

3.1 Do Not Copy-Paste

Do not copy-paste the reference code directly into the project.

Instead:
	•	keep the existing app architecture
	•	keep the existing functionality
	•	rework components and styling intentionally
	•	refactor where necessary
	•	preserve maintainability

3.2 Rebuild Styling Properly

The implementation must use the current project’s own structure and codebase, but visually reproduce the reference UI as closely as possible.

3.3 Existing Features Must Keep Working

All currently implemented UI features must continue to work after the restyle, including:
	•	chat list
	•	new chat
	•	library page
	•	upload dialog
	•	chat rename/delete
	•	archive-related UI already implemented
	•	preferences dialogs already implemented
	•	assistant mode selector
	•	attachments UI
	•	sources dropdown/panel
	•	markdown rendering

⸻

4. Design Analysis Requirement

4.1 Deep Analysis First

Before changing the UI, Codex must first analyze the reference UI thoroughly.

The implementation should explicitly inspect and reproduce:
	•	global layout grid
	•	component spacing rhythm
	•	width constraints
	•	message container widths
	•	sidebar width and internal padding
	•	button heights and corner radius
	•	table row heights
	•	line heights
	•	font sizing hierarchy
	•	menu/dropdown positioning
	•	modal sizing and structure
	•	hover opacity and color shifts
	•	icon usage patterns
	•	empty-state composition
	•	input area height and spacing
	•	source panel visual treatment
	•	subtle visual hierarchy differences between primary and secondary UI elements

4.2 Restyle From Largest to Smallest

Recommended restyling order:
	1.	app shell layout
	2.	sidebar
	3.	main chat layout
	4.	prompt input area
	5.	message cards / message typography
	6.	dialogs and dropdowns
	7.	library page table
	8.	buttons, icons, badges, tags
	9.	micro-interactions and transitions
	10.	final visual polish

⸻

5. Global Styling Requirements

5.1 Visual Target

The UI must match the reference styling as closely as possible in:
	•	modern minimal look
	•	clean light theme
	•	soft neutral palette
	•	polished spacing
	•	subtle contrast
	•	restrained shadows
	•	balanced visual density

5.2 Styling Consistency

All pages and components must feel like one unified design system.

There should be no mix of old and new visual language.

5.3 Typography

Typography must be adjusted to match the reference UI closely:
	•	font family
	•	font sizes
	•	font weights
	•	line heights
	•	text color hierarchy
	•	heading emphasis
	•	secondary text style
	•	muted text style

5.4 Surfaces

All surfaces must match the reference in terms of:
	•	background color
	•	section separation
	•	border treatment
	•	corner radius
	•	elevation / shadow

5.5 Motion and Interaction

Use subtle transitions where appropriate for:
	•	hover states
	•	dropdowns
	•	dialogs
	•	button states
	•	source panel expansion
	•	chat item menu appearance

Animations should be polished and restrained, not flashy.

⸻

6. Sidebar Restyling Requirements

6.1 Sidebar Layout

The sidebar must match the reference closely in:
	•	width
	•	internal padding
	•	spacing between sections
	•	alignment of buttons and list items
	•	bottom user area placement

6.2 Sidebar Elements

Restyle all sidebar elements to match the reference:
	•	brand/title area
	•	new chat button
	•	library button
	•	chat list
	•	active chat item
	•	hovered chat item
	•	chat menu trigger
	•	bottom user placeholder/menu

6.3 Chat List Item Styling

Chat items must match the reference in:
	•	height
	•	padding
	•	text truncation
	•	active state background
	•	hover treatment
	•	icon/menu alignment

6.4 Chat Menu Styling

The three-dot menu and its dropdown must match the reference in:
	•	trigger visibility behavior
	•	positioning
	•	width
	•	menu item spacing
	•	icon alignment
	•	destructive action styling

⸻

7. Main Chat Page Restyling Requirements

7.1 Chat Layout

The main chat page must match the reference in:
	•	conversation width
	•	horizontal centering
	•	top spacing
	•	message spacing
	•	bottom input placement
	•	empty-state positioning

7.2 Messages

Restyle user and assistant messages to match the reference:
	•	message block width
	•	typography
	•	spacing inside messages
	•	spacing between messages
	•	visual distinction between roles
	•	markdown content treatment

7.3 Assistant Markdown Styling

Assistant messages are markdown and must continue to render as markdown, but now styled to match the reference exactly.

This includes:
	•	headings
	•	paragraphs
	•	lists
	•	inline code
	•	fenced code blocks
	•	blockquotes
	•	tables
	•	links
	•	separators

7.4 Sources Button and Panel

The Sources button and dropdown/panel below assistant messages must be visually aligned with the reference.

This includes:
	•	button shape
	•	button text/icon treatment
	•	spacing below message
	•	panel width
	•	panel padding
	•	item layout
	•	score/tag metadata styling
	•	divider usage
	•	scroll behavior if many sources exist

⸻

8. Prompt Input Area Restyling Requirements

8.1 Input Container

The bottom prompt input area must match the reference in:
	•	width
	•	max width
	•	padding
	•	border radius
	•	border color
	•	background
	•	alignment
	•	spacing between controls

8.2 Input Field

The input itself must match the reference in:
	•	font size
	•	placeholder styling
	•	padding
	•	multiline behavior
	•	disabled state styling
	•	focus state styling

8.3 Controls in Input Area

Restyle all controls in the input area to match the reference:
	•	send button
	•	attachment button
	•	assistant mode selector
	•	any placeholder controls already present
	•	disabled states for non-active controls

⸻

9. Library Page Restyling Requirements

9.1 Overall Page

The Library page must be visually brought into the same design language as the reference UI.

9.2 Summary Section

If a summary/statistics section exists, it must match the visual structure and spacing of the reference style.

9.3 Files Table

The files table must be restyled carefully, including:
	•	table container
	•	header row
	•	row height
	•	text alignment
	•	metadata presentation
	•	extension badges
	•	action icons/buttons
	•	scroll area
	•	hover state
	•	disabled file appearance

9.4 Upload Area and Dialog

The upload button and upload dialog must match the reference’s visual quality and patterns for:
	•	button treatment
	•	modal size
	•	modal spacing
	•	file rows
	•	tags inputs
	•	action buttons
	•	disabled upload state

⸻

10. Dialog and Dropdown Restyling Requirements

10.1 Dialogs

All dialogs must be restyled to match the reference:
	•	rename chat dialog
	•	delete chat dialog
	•	upload dialog
	•	info/help dialog
	•	preferences dialog
	•	archive delete confirmation dialog
	•	any other current modal

10.2 Dialog Structure

Match the reference in:
	•	modal width
	•	corner radius
	•	overlay treatment
	•	title styling
	•	body spacing
	•	footer layout
	•	action button sizing

10.3 Dropdowns / Popovers

All dropdowns/popovers must match the reference in:
	•	elevation
	•	padding
	•	divider usage
	•	item hover state
	•	item spacing
	•	visual density
	•	positioning

⸻

11. Preferences and Settings UI Restyling Requirements

11.1 Preferences Dialog

The preferences/personalization dialog must match the reference closely in:
	•	tab navigation appearance
	•	section spacing
	•	input styling
	•	table styling
	•	save button styling
	•	archive list styling

11.2 Archive Tab

Archived chats list and icon-only actions must match the reference in:
	•	row spacing
	•	icon sizes
	•	alignment
	•	destructive action styling
	•	empty-state styling

⸻

12. Disabled / Not Yet Available UI Elements

12.1 Keep Existing Rule

Any UI elements already present for functionality not fully active must remain visually integrated and properly disabled.

12.2 Disabled Styling

Disabled controls must match the reference disabled treatment closely:
	•	muted color
	•	cursor behavior
	•	opacity or contrast treatment
	•	no misleading active affordance

⸻

13. Styling Architecture Requirements

13.1 Do Not Create Styling Chaos

This step should improve styling quality, not make it harder to maintain.

Codex must clean up styling architecture as needed.

13.2 Recommended Styling Improvements

Allowed and recommended if useful:
	•	consolidate design tokens
	•	centralize colors
	•	centralize spacing scale
	•	centralize radii
	•	centralize shadows
	•	centralize typography scale
	•	standardize component variants
	•	remove old unused styles

13.3 Design Tokens

Introduce or improve shared design tokens for:
	•	colors
	•	typography
	•	spacing
	•	radius
	•	borders
	•	shadows
	•	z-index layers
	•	transitions

⸻

14. Responsiveness Requirements

14.1 Main Priority

Desktop parity is the primary target.

14.2 Basic Responsive Quality

Even though the main target is desktop, the UI should still behave reasonably on narrower widths.

Do not break layout integrity while matching the desktop reference.

⸻

15. What Must Not Change

This step must not change core product behavior unless necessary to preserve existing functionality during the restyle.

Do not add new features such as:
	•	new retriever capabilities
	•	new embedder capabilities
	•	new DB features
	•	new API endpoints
	•	new workflows
	•	new library logic
	•	new archive logic

This is a restyling and UX-polish step only.

⸻

16. Testing, Validation, and Debugging Requirements

16.1 Implementation Is Not Finished Without Verification

Step 7 is not complete when the UI merely looks “closer”.

It is complete only after the result has been carefully checked against the reference and debugged where necessary.

16.2 Required Validation

Codex must verify at minimum:
	•	sidebar styling matches the reference closely
	•	main chat layout matches the reference closely
	•	prompt input area matches the reference closely
	•	dialogs and dropdowns match the reference closely
	•	library page matches the same design language
	•	markdown-rendered assistant messages still display correctly
	•	sources button and sources panel still work and are styled correctly
	•	all existing UI interactions still function
	•	no regressions in Step 1–6 functionality caused by the restyle

16.3 Visual Comparison Requirement

Codex should perform side-by-side comparison against the reference UI and iterate until the result is very close.

This comparison should include:
	•	spacing
	•	sizing
	•	alignment
	•	typography
	•	colors
	•	state styling
	•	dialogs
	•	dropdowns
	•	sidebar
	•	chat page
	•	library page

16.4 Debugging Loop

If discrepancies or regressions are found, Codex must:
	1.	identify the mismatch or bug
	2.	fix it
	3.	compare again
	4.	retest affected interactions
	5.	update docs/changelog if needed

⸻

17. Documentation Requirements

Codex must update or create:
	•	docs/frontend.md
	•	docs/design-system.md
	•	docs/testing.md

17.1 docs/frontend.md

Must document:
	•	major layout structure
	•	major component structure
	•	styling approach
	•	any important restyling-related refactors

17.2 docs/design-system.md

Must document:
	•	shared color system
	•	spacing scale
	•	typography rules
	•	radius/shadow tokens
	•	component styling conventions

17.3 docs/testing.md

Must document:
	•	visual verification process
	•	side-by-side comparison checklist
	•	interaction regression checklist
	•	known styling decisions

17.4 changelog.md

Must be updated for all Step 7 changes.

⸻

18. Acceptance Criteria

18.1 Visual Parity
	•	the web UI visually matches the reference UI very closely
	•	layout, spacing, typography, colors, dialogs, dropdowns, and controls are aligned with the reference
	•	the result feels like the same product visually

18.2 No New Features
	•	no unnecessary new product features were introduced
	•	existing functionality remains intact

18.3 Existing Features Still Work
	•	chats still work
	•	library still works
	•	sources panel still works
	•	dialogs still work
	•	markdown messages still render correctly
	•	attachments UI still works
	•	preferences/archive UI still works

18.4 Quality Gate
	•	implementation has been visually checked carefully
	•	mismatches have been corrected
	•	regressions have been debugged and fixed
	•	docs updated
	•	changelog updated

⸻

19. Nice-to-Haves

Allowed if they help parity without changing product scope:
	•	cleaning up old styles
	•	unifying component variants
	•	improving design token structure
	•	refining spacing utilities
	•	polishing transitions

⸻

20. Engineering Requirements

Codex must follow these rules:
	•	keep architecture clean
	•	do not copy-paste the reference code
	•	rework existing UI intentionally
	•	preserve maintainability
	•	avoid giant style files if possible
	•	remove stale styling where appropriate
	•	validate carefully
	•	debug regressions
	•	update docs and changelog
	•	consider Step 7 complete only after close visual parity is achieved