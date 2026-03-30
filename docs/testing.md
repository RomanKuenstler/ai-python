# Testing

## Automated Checks

Create a local Python 3.12 virtualenv and run the backend tests:

```bash
/opt/homebrew/bin/python3.12 -m venv .venv312
. .venv312/bin/activate
python -m pip install -r services/retriever/requirements.txt -r services/embedder/requirements.txt
python -m pytest tests/test_retriever_api.py tests/test_step4_backend.py -q
python -m compileall services tests
```

Frontend build smoke check:

```bash
cd webui
npm install
npm run build
```

## Step 4 Checks Covered

- chat rename and delete API contracts
- library list, patch, and delete API contracts
- default tag normalization
- disabled-file retrieval filtering
- frontend TypeScript and production build

## Manual Smoke Test

1. Run `docker compose up --build`.
2. Open `http://localhost:5173`.
3. Open `Library` from the sidebar.
4. Upload one supported file with tags.
5. Upload one supported file with an empty tag field and confirm it becomes `default`.
6. Disable a file and confirm it stays visible in Library but no longer appears in retrieval-backed answers.
7. Re-enable the file and confirm it becomes available again.
8. Delete a file and confirm it disappears from the UI and `data/`.
9. Rename a chat from the sidebar hover menu.
10. Delete a chat and confirm the app falls back to another chat or creates a new one.
11. Refresh the page and confirm both chats and library state reload.
12. Send an assistant prompt that returns markdown and confirm headings, lists, inline code, and fenced code blocks render properly.

## Debugging Notes

- If upload endpoints fail at startup, confirm `python-multipart` is installed in the backend environment.
- If uploads appear in `data/` but not in Library, inspect backend logs for embedding or processor errors.
- If a disabled file still appears in sources, verify the `files.is_enabled` flag in PostgreSQL and rerun retrieval.
- If file deletion becomes inconsistent, compare the local `data/` folder, Postgres `files` and `chunks` rows, and Qdrant payloads for the same file path.
- If markdown renders as plain text, confirm the frontend bundle includes `react-markdown`, `remark-gfm`, and `rehype-sanitize`.
