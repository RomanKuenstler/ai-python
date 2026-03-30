# Frontend

## Stack

- React 18
- TypeScript
- Vite
- `react-router-dom`
- `react-markdown` with `remark-gfm`
- `rehype-sanitize`

## Step 5 UI Changes

The UI now follows the Step 5 reference direction with:

- fixed top bar and fixed left navigation
- white, low-chrome workspace styling
- chat action menus for rename and delete
- disabled placeholders for archive and personalization/settings-adjacent controls
- attachment-capable composer with previews, removal, and validation

## Chat Experience

- optimistic user and assistant message placeholders
- markdown rendering for assistant responses
- per-message attachment chips for user messages
- collapsible source panels for assistant replies
- input disabled while a message is in flight

## Library Experience

- summary metrics row
- file management table
- upload dialog with extension-aware validation
- enable/disable and delete actions

## Attachment UX

- max 3 files per message
- supported extensions mirror backend config defaults
- invalid files surface inline errors
- attached files remain visible above the composer until send or removal

## Local Run

```bash
cd webui
npm install
npm run dev
```

`VITE_API_BASE_URL` defaults to `http://localhost:8000`.
