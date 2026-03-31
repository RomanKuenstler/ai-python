# Testing

## Automated Checks

Create a Python 3.11 virtualenv and run:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r services/retriever/requirements.txt -r services/embedder/requirements.txt
python -m pytest tests -q
python3 -m compileall services migrations tests webui/src
```

Frontend build smoke check:

```bash
cd webui
npm install
npm run build
```

## Step 7 Checks Covered

- frontend production build after the Step 7 restyle
- existing retrieval and processor regressions
- frontend production build
- migration module importability

## Visual Verification Process

1. Start the stack with `docker compose up --build`.
2. Open the current app and the reference app side by side.
3. Compare the shell first: top bar height, sidebar width, content centering, and bottom composer placement.
4. Compare state styling next: neutral hover, active chat row, disabled controls, menus, dialogs, and empty states.
5. Compare typography and spacing in assistant markdown, user bubbles, table headers, dialogs, and tab navigation.
6. Iterate on any mismatch before calling Step 7 complete.

## Side-by-Side Checklist

- Sidebar proportions, internal padding, and bottom user row match the reference closely.
- Chat layout width and conversation centering match the reference closely.
- Composer width, border, radius, controls, and fixed positioning match the reference closely.
- Assistant messages, user messages, attachment chips, and markdown blocks share the same visual language.
- Sources trigger and sources panel match the reference popover treatment.
- Library summary, table, upload dialog, and action controls feel like the same product.
- Preferences modal, tabs, archive rows, and settings fields follow the same modal design system.

## Interaction Regression Checklist

- Create, open, rename, archive, download, and delete chats.
- Open Library, upload files, toggle file state, and delete files.
- Send messages with and without attachments.
- Change assistant mode from the composer.
- Open and close sources panels.
- Open Info, Help, Preferences, and Archive-related dialogs.
- Confirm archived chat actions still work.

## Known Styling Decisions

- The implementation keeps the existing React architecture and current product functionality intact instead of copying the reference code.
- A single tokenized stylesheet is still used, but the rules are grouped by shared UI patterns to keep the restyle maintainable.
- Desktop parity is the main target; mobile behavior is preserved with compact responsive fallbacks rather than a separate design.

## Debugging Notes

- If startup fails before the API boots, confirm `alembic` is installed in the active environment.
- If image attachments fail, verify Tesseract is available in the embedder container.
- If attachment context seems missing, inspect the retriever logs and confirm `ATTACHMENT_MAX_TOTAL_CHARS` is not overly restrictive.
- If the Step 7 visuals look inconsistent, inspect the fixed composer width, sidebar padding, and modal variants first because they establish most of the reference rhythm.
