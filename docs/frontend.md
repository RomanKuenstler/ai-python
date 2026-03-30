# Frontend

## Stack

- React 18
- TypeScript
- Vite
- `react-router-dom`
- `react-markdown` with `remark-gfm`
- `rehype-sanitize` for safe markdown rendering

## Layout

The Step 4 UI keeps a shared two-column shell:

- left sidebar with branding, `New chat`, `Library`, chat list, and footer placeholder
- right content area that switches between the chat page and the Library page

## Major Components

- `AppShell` handles the shared layout
- `Sidebar` renders chat navigation plus rename and delete dialogs
- `LibraryPage` renders summary cards, the files table, and destructive actions
- `UploadDialog` handles file selection and per-file tags
- `ChatView`, `MessageList`, and `MessageBubble` render the conversation
- `SourcesPanel` shows retrieval metadata below assistant answers
- `ChatInput` handles message entry

## State Handling

`useChatApp` now manages:

- chats
- active chat id
- messages by chat
- library file list and summary
- upload state
- per-file action busy state
- app and library errors

The hook still persists the last active chat id in `localStorage` and still uses optimistic message placeholders while the message request is in flight.

## Markdown Rendering

Assistant messages are rendered as markdown rather than raw text.

Supported markdown includes:

- paragraphs
- headings
- bold and italic text
- ordered and unordered lists
- inline code
- fenced code blocks
- blockquotes
- links
- tables
- horizontal rules

### Safety

- raw HTML is not enabled
- output is sanitized with `rehype-sanitize`
- the renderer avoids unsafe HTML injection paths by default

### Styling

- readable spacing between markdown blocks
- dark surfaced code blocks
- styled inline code
- table borders
- visible links
- blockquote accents

## Local Run

Install and run from [webui/package.json](/Users/rknstlr/Workspace/ai-python/webui/package.json):

```bash
cd webui
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` and defaults to `http://localhost:8000`.
