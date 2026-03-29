# Frontend

## Stack

- React 18
- TypeScript
- Vite
- plain modular CSS

## Layout

The Step 3 UI is split into two areas:

- a left sidebar with branding, a `New chat` action, the chat list, and a footer placeholder
- a main chat surface with the conversation history, error/loading feedback, and a fixed bottom input

## Major Components

- `AppShell` handles the two-column layout
- `Sidebar` renders chat creation and switching
- `ChatView` coordinates the main conversation view
- `MessageList` and `MessageBubble` render user and assistant messages
- `SourcesPanel` shows retrieval metadata below assistant answers
- `ChatInput` handles Enter-to-send and disabled/loading states

## State Handling

`useChatApp` keeps the frontend state intentionally lightweight:

- chat list
- active chat id
- messages keyed by chat id
- loading/sending state
- current application error

The hook also persists the last active chat id in `localStorage` and uses optimistic message placeholders while the API request is in flight.

## Local Run

Install and run from [webui/package.json](/Users/rknstlr/Workspace/ai-python/webui/package.json):

```bash
cd webui
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` and defaults to `http://localhost:8000`.
