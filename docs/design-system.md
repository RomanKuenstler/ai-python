# Design System

## Design Direction

- Light, minimal, neutral UI
- Low-contrast surfaces with restrained shadows
- Tight spacing rhythm with rounded corners and soft hover states
- Shared component language across chat, library, dialogs, and preferences

## Tokens

Step 7 centralizes the main visual tokens in `webui/src/styles/index.css`.

### Colors

- `--bg`: primary white application background
- `--bg-soft`: soft surface fill for chips, code blocks, and placeholders
- `--bg-muted`: elevated header and tab background
- `--bg-hover`: hover fill for interactive neutral controls
- `--border`, `--border-soft`, `--border-mute`: default and subtle border tones
- `--text`, `--text-soft`, `--text-muted`: main, secondary, and muted text hierarchy
- `--danger`, `--danger-bg`, `--success`: semantic action and status colors

### Radius

- `--radius-sm`: row-level menus and compact controls
- `--radius-md`: standard neutral controls
- `--radius-lg`: cards, tables, and popovers
- `--radius-xl`: large modal surfaces
- `--radius-pill`: chips, badges, primary actions, and compact triggers

### Shadows

- `--shadow`: composer and light floating surfaces
- `--shadow-lg`: modal elevation

### Motion

- `--transition`: shared control hover and state transition timing

## Typography Rules

- Inter is used throughout the UI.
- Headings stay restrained; uppercase micro-headings are used for section framing.
- Primary content uses dark neutral text.
- Secondary and supporting metadata uses `--text-soft` or `--text-muted`.
- Markdown code and file path display use monospace fallbacks only where needed.

## Spacing Scale

- Tight inner component spacing sits mostly between `0.2rem` and `0.75rem`.
- Card and modal body padding is generally `0.7rem` to `1rem`.
- The app shell uses a fixed top offset and fixed sidebar width to match the reference proportions.
- The fixed composer uses a compact outer frame with slightly larger inner text padding.

## Component Conventions

- Neutral buttons are borderless white surfaces that fill on hover.
- Primary actions use dark filled pill shapes.
- Destructive actions use red text or red filled pills depending on emphasis.
- Menus and popovers use white backgrounds, subtle borders, small radii, and tight row spacing.
- Tables use muted uppercase headers with compact rows and light separators.
- User messages are right-aligned soft bubbles; assistant responses are full-width content blocks with separate evidence controls.
- Dialogs use muted headers, strong body separation, and shared footer actions.
