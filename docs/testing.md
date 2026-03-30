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

## Step 5 Checks Covered

- attachment-aware chat API contracts
- existing retrieval and processor regressions
- frontend production build
- migration module importability

## Manual Validation

1. Run `docker compose up --build`.
2. Open `http://localhost:5173`.
3. Upload a library file and confirm it appears in Library.
4. Send a plain chat message and confirm grounded sources still work.
5. Send a message with a `.csv` attachment and confirm the answer reflects row content.
6. Send a message with a `.png` or `.jpg` attachment and confirm OCR-derived context is used.
7. Confirm user messages with attachments display attachment chips in chat history.
8. Inspect PostgreSQL and confirm attachment content is not stored, only metadata.
9. Restart the stack and confirm migrations apply cleanly.

## Debugging Notes

- If startup fails before the API boots, confirm `alembic` is installed in the active environment.
- If image attachments fail, verify Tesseract is available in the embedder container.
- If attachment context seems missing, inspect the retriever logs and confirm `ATTACHMENT_MAX_TOTAL_CHARS` is not overly restrictive.
