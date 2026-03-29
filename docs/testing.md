# Testing

## Automated Checks

Run the local test suite from a virtualenv:

```bash
/opt/homebrew/bin/python3.11 -m venv .venv311
. .venv311/bin/activate
python -m pip install -r services/embedder/requirements.txt -r services/retriever/requirements.txt
pytest -q
```

The current test coverage focuses on:

- HTML cleanup and semantic preservation
- extraction quality heuristics
- EPUB front matter and repeated chrome handling
- retriever source formatting

## Smoke Checks

Useful smoke checks during development:

```bash
. .venv311/bin/activate
python -m compileall services tests
```

And a direct processor smoke run against sample data:

```bash
. .venv311/bin/activate
python - <<'PY'
from pathlib import Path
from services.common.config import Settings
from services.embedder.processors.processor_registry import ProcessorRegistry

root = Path("data")
settings = Settings(data_dir=str(root.resolve()))
registry = ProcessorRegistry(settings=settings, data_dir=root.resolve())
for rel in ["AI_IPS.md", "Developing with Docker.pdf", "Deployment with Docker.epub"]:
    result = registry.for_path(root / rel).process(file_path=(root / rel).resolve(), relative_path=rel, tags=[])
    print(rel, result.processing_flags["processing_status"], result.metadata.get("extraction_method"), len(result.semantic_blocks))
PY
```

## What Was Verified

- `.html` and `.htm` extraction logic through unit coverage
- markdown/text regression behavior through shared processors and smoke extraction
- direct PDF extraction on the sample digital PDF
- EPUB spine-order extraction and front-matter cleanup on the sample EPUB
- CLI source rendering format

## Debugging Tips

- If retrieval sources are empty, inspect `RETRIEVAL_SCORE_THRESHOLD`.
- If a file keeps reprocessing, compare the stored processing signature fields in `files`.
- If a PDF produces no chunks, inspect the stored `processing_status`, `processing_error`, and `extraction_quality`.
- If OCR is required, validate the embedder Docker image rather than the host Python environment.
