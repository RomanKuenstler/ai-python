prd_v2.md — Local RAG System (Step 2)

1. Overview

1.1 Goal

Extend the existing Step 1 local RAG system with richer document ingestion and improved retrieval transparency.

1.2 Step 2 Scope

This step adds support for embedding:
	•	.html
	•	.htm
	•	.pdf
	•	.epub

It also improves the retriever CLI by showing the metadata of the retrieved knowledge used for each answer.

1.3 Step 2 Priorities
	1.	High-quality text extraction
	2.	Strong file-type-specific normalization before chunking
	3.	Preservation of meaningful semantic structure
	4.	Reliable fallback behavior for weak extraction
	5.	Better visibility of retrieved sources in the terminal
	6.	Clean maintainable processor architecture
	7.	Strong verification, testing, and debugging before considering implementation finished

⸻

2. Required Outcomes

After Step 2, the system must:
	•	ingest and embed .html, .htm, .pdf, and .epub
	•	normalize extracted text appropriately per file type
	•	preserve semantic structure where useful
	•	avoid embedding markup, layout noise, boilerplate, and repeated chrome where possible
	•	support OCR fallback for PDFs with poor extracted text
	•	enrich chunk metadata for these new file types
	•	display retrieval metadata below each assistant response in the CLI
	•	keep all Step 1 functionality working without regression

⸻

3. High-Level Design Changes

3.1 Processor-Based Architecture

The embedder must use a processor-based design where each supported file type has a specialized processor.

Suggested structure:

services/embedder/
├── processors/
│   ├── base_processor.py
│   ├── txt_processor.py
│   ├── markdown_processor.py
│   ├── html_processor.py
│   ├── pdf_processor.py
│   ├── epub_processor.py
│   ├── shared_normalization.py
│   ├── extraction_quality.py
│   └── processor_registry.py

3.2 Common Processing Pipeline

For every supported file type, the pipeline should be:

file discovery
→ file type detection
→ specialized extraction
→ specialized normalization
→ semantic block building
→ chunking
→ embedding
→ qdrant upsert
→ postgres state update

3.3 Common Processor Contract

Each processor should return a structured extraction result object, not just raw text.

Example logical shape:

{
    "text": "...",
    "document_title": "...",
    "sections": [...],
    "metadata": {...},
    "quality": {...},
    "processing_flags": {...}
}

This allows a common interface while preserving file-type-specific metadata.

⸻

4. Shared Requirements for All New File Types

4.1 Base Text Normalization

All extracted text must go through shared normalization before chunking.

At minimum:
	•	Unicode normalization using NFKC
	•	normalize line endings to \n
	•	replace non-breaking spaces with standard spaces
	•	collapse repeated blank lines
	•	trim trailing whitespace
	•	preserve block boundaries
	•	avoid merging unrelated semantic blocks

4.2 Do Not Over-Normalize

Normalization must not destroy:
	•	headings
	•	chapter boundaries
	•	list structure
	•	tables
	•	blockquotes
	•	code/preformatted text
	•	page boundaries where relevant

4.3 Useful-Text Validation

Every processor must validate whether extracted text is actually useful.

The system should be able to detect at least:
	•	empty extraction
	•	extremely short extraction
	•	mostly broken symbols
	•	obviously corrupted encoding
	•	mostly repetitive garbage
	•	text too weak to be useful for indexing

If extraction is not useful, the processor must either:
	•	try a fallback path, or
	•	fail cleanly and log the reason

4.4 Metadata Enrichment

Each chunk should carry as much useful metadata as possible, depending on file type.

Examples:
	•	source file name
	•	source file path
	•	extension
	•	content type
	•	document title
	•	chapter
	•	section
	•	heading path
	•	page number
	•	extraction method
	•	tags
	•	normalized content hash
	•	processor version
	•	schema version

4.5 Reindex Triggers

A file must be reprocessed not only when the source file changes, but also when one of these changes:
	•	processor version
	•	index schema version
	•	chunk size
	•	chunk overlap
	•	normalization strategy version
	•	extraction strategy version

⸻

5. HTML / HTM Processing Requirements

5.1 Goal

Extract clean meaningful visible content while preserving semantic structure and avoiding embedding markup or page chrome.

5.2 Required Cleaning

The HTML processor must remove non-content and high-noise elements before extraction.

At minimum remove:
	•	script
	•	style
	•	noscript
	•	svg
	•	canvas
	•	iframe
	•	nav
	•	footer
	•	aside
	•	form
	•	button
	•	input
	•	select
	•	textarea
	•	img
	•	picture
	•	video
	•	audio
	•	source
	•	meta
	•	link
	•	object
	•	embed

Also ignore hidden or non-visible content when detectable.

5.3 Main Content Root Detection

The processor should prefer extracting from the most likely content root in this order:
	1.	<main>
	2.	<article>
	3.	[role="main"]
	4.	<body>
	5.	full document fallback

5.4 Semantic Preservation

Preserve useful document structure and convert it into markdown-like plain text.

Supported structures include:
	•	headings h1 to h6
	•	paragraphs
	•	list items
	•	blockquotes
	•	preformatted/code blocks
	•	tables

5.5 Markdown-Like Plain Text Conversion

Convert extracted content into a semantic plain-text representation such as:
	•	headings → #, ##, etc.
	•	list items → - item
	•	blockquotes → > quote
	•	code/preformatted blocks → fenced code blocks
	•	tables → row-based plain text with consistent delimiters

5.6 Noise and Boilerplate Handling

Implement safeguards for:
	•	repeated navigation boilerplate
	•	duplicate consecutive blocks
	•	empty blocks
	•	trivial short blocks with no semantic value

5.7 HTML Metadata

Each HTML-derived chunk should include where available:
	•	file name
	•	file path
	•	document title
	•	nearest heading / section title
	•	heading path
	•	tags
	•	extension
	•	content type = html

⸻

6. PDF Processing Requirements

6.1 Goal

Extract useful text from standard PDFs and use OCR fallback when direct extraction is weak or empty.

6.2 Extraction Flow

The PDF processor must support this flow:

direct text extraction
→ extraction quality evaluation
→ OCR fallback if needed
→ normalization
→ page/section-aware semantic chunking

6.3 Direct PDF Extraction

Use a robust PDF text extraction library first.

Preferred stack:
	•	pdfplumber and/or PyMuPDF

The implementation should be page-aware.

6.4 Reading Order Preservation

For PDFs with multiple text blocks, the processor should preserve a sensible reading order as much as possible.

This includes:
	•	top-to-bottom ordering
	•	left-to-right within normal layouts
	•	basic support for two-column detection where feasible

6.5 Page-Level Handling

Each page should be processed independently before being merged into the final normalized document text.

The processor should:
	•	preserve page numbers in metadata
	•	optionally mark page boundaries in semantic text
	•	skip pages with no useful text

6.6 Direct Extraction Quality Evaluation

After direct extraction, evaluate text quality before deciding whether to use it.

At minimum evaluate:
	•	total extracted characters
	•	average extracted characters per page
	•	printable character ratio
	•	alphabetic character ratio
	•	average word length
	•	ratio of broken fragments
	•	obvious encoding corruption

6.7 OCR Fallback

If direct extraction quality is weak, use OCR fallback.

Suggested stack:
	•	pytesseract
	•	Pillow
	•	pdf2image or pypdfium2

6.8 OCR Modes

Support these OCR modes via config:
	•	off
	•	fallback
	•	ocr_only

6.9 OCR Preprocessing

Before OCR, page images should support basic preprocessing when enabled:
	•	grayscale conversion
	•	thresholding / binarization
	•	contrast improvement
	•	optional denoise
	•	optional DPI/render scale adjustment

Keep preprocessing configurable so it can be tuned later.

6.10 OCR Quality Evaluation

OCR output must also be evaluated for usefulness.

If OCR still produces unusable text:
	•	log the failure clearly
	•	do not index garbage text
	•	mark the file as processed with failure or no-useful-text status in Postgres

6.11 Extraction Method Metadata

Each PDF chunk must store:
	•	file name
	•	file path
	•	page number
	•	inferred section title if available
	•	tags
	•	extraction method: text, ocr, or mixed
	•	OCR performed: true/false
	•	extension
	•	content type = pdf

6.12 PDF Failure Handling

If both direct extraction and OCR fail to produce useful text:
	•	do not insert chunks into Qdrant
	•	store failure status in Postgres
	•	store reason for failure
	•	allow future reprocessing after config or implementation changes

⸻

7. EPUB Processing Requirements

7.1 Goal

Extract book content in reading order, preserve chapter and section structure, and avoid indexing front matter and repeated book chrome when possible.

7.2 Required EPUB Support

Use a proper EPUB parsing approach that understands container/package structure and reading order.

Preferred library:
	•	ebooklib

7.3 Reading Order

The EPUB processor must prefer package spine order over arbitrary file order.

7.4 Supported Internal Content

Extract text from document-like entries only, such as XHTML/HTML reading content.

Skip non-reading assets such as:
	•	images
	•	fonts
	•	stylesheets
	•	media assets

7.5 Navigation and Front Matter Skipping

The EPUB processor should skip or strongly down-prioritize likely non-content sections such as:
	•	cover
	•	title page
	•	copyright page
	•	table of contents
	•	contents
	•	front matter
	•	half title
	•	navigation documents

7.6 XHTML Content Extraction

EPUB chapter documents should be processed similarly to HTML:
	•	remove non-content tags
	•	preserve headings
	•	preserve lists
	•	preserve blockquotes
	•	preserve code/pre blocks
	•	preserve tables
	•	convert to markdown-like plain text

7.7 Repeated Book Chrome Removal

The EPUB processor should detect and remove repeated lines that appear across many sections when they look like running headers, footers, or repeated book chrome.

7.8 Fallback Discovery

If spine traversal is incomplete or yields little usable text, the processor may fall back to scanning XHTML/HTML entries directly.

7.9 EPUB Metadata

Each EPUB chunk should store where available:
	•	book title
	•	author
	•	chapter title
	•	section title
	•	heading path
	•	source file name
	•	source file path
	•	tags
	•	extension
	•	content type = epub

7.10 EPUB Chunk Semantics

Chunk boundaries should prefer:
	1.	chapter boundaries
	2.	section/subheading boundaries
	3.	paragraph boundaries
	4.	token-based fallback chunking

7.11 EPUB Failure Handling

If EPUB metadata or package structure is malformed:
	•	log a structured warning
	•	attempt best-effort fallback extraction
	•	fail only if no useful text can be recovered

⸻

8. Chunking Requirements

8.1 Shared Chunking Rules

Continue using:
	•	semantic chunking first
	•	then size-based chunking
	•	chunk size = 600
	•	overlap = 100

8.2 File-Type-Specific Semantic Units

Use these semantic boundaries before token chunking:
	•	HTML: headings, paragraphs, lists, tables, blockquotes, pre/code blocks
	•	PDF: pages, headings if inferred, paragraphs
	•	EPUB: chapters, headings, sections, paragraphs

8.3 Oversized Semantic Blocks

If a semantic block is too large:
	•	split it recursively
	•	preserve the parent title/heading metadata
	•	never silently drop text

8.4 Chunk Titles

Each chunk should have a best-effort title when possible, derived from:
	•	nearest heading
	•	chapter title
	•	section title
	•	page marker fallback

This will help later for UI display and source transparency.

⸻

9. Database Changes

9.1 files Table Extensions

Add fields such as:

file_type
processing_status
processing_error
last_extraction_method
document_title
author
detected_language
content_hash
index_schema_version
processor_version
normalization_version
extraction_quality
ocr_used

9.2 chunks Table Extensions

Add fields such as:

title
chapter
section
heading_path
page_number
extraction_method
content_type
quality_flags

9.3 retrieval_logs Table Extensions

Add fields such as:

source_file_name
source_file_path
chunk_id
chunk_title
chapter
section
page_number
score
tags
retrieved_at

9.4 Index Consistency

The system should store enough indexing metadata so that stale chunks can be safely re-created when extraction logic or schema changes.

⸻

10. Retriever CLI Enhancements

10.1 Source Display Requirement

After each assistant answer, print a source section in the CLI showing the metadata for the retrieved knowledge actually used.

Example:

AI:
<assistant answer>

--- Sources ---
Used similarities: 3
[1] file=notes.html | title=Install Guide | score=0.88 | tags=[docker, setup]
[2] file=book.epub | chapter=Chapter 4 | section=Volumes | score=0.84 | tags=[docker]
[3] file=manual.pdf | page=18 | title=Storage Classes | score=0.81 | tags=[kubernetes]

10.2 Required Display Fields

Display where available:
	•	number of used similarities
	•	file name
	•	chunk title or nearest heading
	•	chapter
	•	section
	•	page number
	•	score
	•	tags

10.3 Ordering

Display sources in the same order they were selected for the final RAG context, usually highest score first.

10.4 No-Source Case

If no retrieved knowledge passed threshold, clearly show that no sources were used.

⸻

11. Configuration Requirements

Update .env with Step 2 options:

CHUNK_SIZE=600
CHUNK_OVERLAP=100
WATCH_INTERVAL=10

RETRIEVAL_SCORE_THRESHOLD=0.70
RETRIEVAL_MIN_RESULTS=2
RETRIEVAL_MAX_RESULTS=8
CHAT_HISTORY_LIMIT=5

ENABLE_OCR=true
PDF_OCR_MODE=fallback
PDF_MIN_EXTRACTED_CHARS=500
PDF_MIN_AVG_CHARS_PER_PAGE=150
PDF_ENABLE_COLUMN_DETECTION=true
PDF_RENDER_SCALE=2.0

OCR_LANGUAGE=eng
OCR_ENABLE_PREPROCESSING=true
OCR_PREPROCESS_GRAYSCALE=true
OCR_PREPROCESS_THRESHOLD=true
OCR_PREPROCESS_DENOISE=false
OCR_PREPROCESS_CONTRAST=true

HTML_CLEANING_STRICT=true

EPUB_SKIP_FRONT_MATTER=true
EPUB_REMOVE_REPEATED_CHROME=true
EPUB_FALLBACK_SCAN_ENABLED=true

INDEX_SCHEMA_VERSION=2
PROCESSOR_VERSION=2
NORMALIZATION_VERSION=2
LOG_LEVEL=INFO

11.1 Config Meaning
	•	PDF_OCR_MODE: off, fallback, or ocr_only
	•	PDF_MIN_EXTRACTED_CHARS: minimum acceptable extracted text before fallback is considered
	•	PDF_MIN_AVG_CHARS_PER_PAGE: guard against weak extraction on longer PDFs
	•	PDF_ENABLE_COLUMN_DETECTION: attempt basic reading-order improvement for multi-column pages
	•	PDF_RENDER_SCALE: page render scale for OCR
	•	OCR_LANGUAGE: default OCR language
	•	OCR_ENABLE_PREPROCESSING: master switch for OCR preprocessing
	•	EPUB_SKIP_FRONT_MATTER: skip likely non-content front matter
	•	EPUB_REMOVE_REPEATED_CHROME: remove repeated running headers/footers
	•	EPUB_FALLBACK_SCAN_ENABLED: scan XHTML/HTML entries if spine extraction is weak
	•	INDEX_SCHEMA_VERSION: bump when embedding schema changes
	•	PROCESSOR_VERSION: bump when extraction/processing logic changes
	•	NORMALIZATION_VERSION: bump when normalization behavior changes

⸻

12. Docker / Runtime Requirements

12.1 OCR Dependencies

The embedder container must include OCR-related runtime dependencies when OCR is enabled.

Expected packages may include:
	•	tesseract-ocr
	•	appropriate language packs
	•	poppler-utils and/or other PDF rendering dependencies

12.2 Optionality

OCR should remain configurable, but the default Step 2 environment should support it.

⸻

13. Logging and Observability

13.1 Structured Logs

The embedder should log per file:
	•	processor chosen
	•	extraction success/failure
	•	extraction method
	•	extracted text length
	•	OCR triggered or not
	•	extraction quality result
	•	number of semantic blocks
	•	number of final chunks
	•	reindex reason

13.2 Useful Warnings

Warn clearly for:
	•	malformed HTML
	•	malformed EPUB package/container
	•	empty chapter extraction
	•	weak PDF extraction
	•	OCR failure
	•	skipped file due to no useful text

⸻

14. Documentation Requirements

Codex must update or create:
	•	docs/embedder.md
	•	docs/retriever.md
	•	docs/parsers.md
	•	docs/ocr.md
	•	docs/metadata.md
	•	docs/testing.md

14.1 docs/parsers.md

Must document:
	•	HTML extraction rules
	•	PDF extraction flow
	•	OCR decision flow
	•	EPUB parsing flow
	•	file-type-specific metadata
	•	chunking behavior by type

14.2 docs/testing.md

Must document:
	•	how processor tests are run
	•	what fixture files are used
	•	how extraction quality is verified
	•	how OCR fallback is tested
	•	how CLI source display is verified
	•	common debugging steps

14.3 changelog.md

Must be updated for every Step 2 change.

⸻

15. Testing, Validation, and Debugging Requirements

15.1 Implementation Is Not Complete Without Verification

Step 2 must not be considered finished when the code compiles only. It is only finished after the result has been checked, validated, and debugged where necessary.

15.2 Required Validation

Codex must verify at minimum:
	•	HTML extraction works on representative files
	•	.htm and .html both work
	•	scripts/styles/navigation noise are not embedded
	•	PDF direct extraction works on text PDFs
	•	OCR fallback activates on weak/empty PDFs
	•	EPUB reading-order extraction works
	•	front matter skipping behaves reasonably
	•	repeated EPUB chrome removal works reasonably
	•	metadata is stored correctly in Postgres
	•	chunks are stored correctly in Qdrant
	•	retriever CLI displays source metadata correctly
	•	no regression of Step 1 functionality

15.3 Required Debugging Loop

If tests or manual verification reveal problems, Codex must:
	1.	identify the cause
	2.	debug and fix it
	3.	rerun validation
	4.	document the fix
	5.	update changelog and docs if needed

15.4 Required Tests

Codex should add tests where practical, especially for:
	•	HTML normalization
	•	PDF extraction quality evaluation
	•	OCR fallback decision logic
	•	EPUB section extraction
	•	repeated-chrome removal
	•	retrieval source formatting

15.5 Manual Smoke Test Checklist

Codex should also perform and document a practical smoke test covering:
	•	add one HTML file and confirm indexed chunks
	•	add one PDF with good text and confirm no OCR needed
	•	add one PDF that requires OCR and confirm fallback works
	•	add one EPUB and confirm chapter-based extraction
	•	run retriever and confirm sources are printed below answer

⸻

16. Acceptance Criteria

16.1 HTML / HTM
	•	scripts, styles, and page chrome are not embedded
	•	meaningful visible content is extracted
	•	headings/lists/quotes/tables/code blocks are preserved in text form
	•	raw HTML tags are not embedded

16.2 PDF
	•	digital PDFs extract useful text
	•	weak extraction triggers OCR fallback when configured
	•	page-aware metadata is stored
	•	unusable PDFs fail gracefully without indexing garbage

16.3 EPUB
	•	reading order follows spine when available
	•	navigation/front matter is skipped where appropriate
	•	chapter/section structure is preserved
	•	repeated book chrome is reduced
	•	metadata like chapter/section/title is stored where available

16.4 Retriever
	•	CLI answer is followed by a source section
	•	source section includes filename, title/chapter/section/page where available, score, and tags
	•	no-source case is handled clearly

16.5 Reindexing
	•	files are reprocessed when source content changes
	•	files are also reprocessed when processor/schema/normalization settings change

16.6 Quality Gate
	•	implementation has been tested
	•	issues found during verification have been debugged and fixed
	•	docs and changelog have been updated

⸻

17. Nice-to-Haves for Step 2

Allowed if they do not slow delivery too much:
	•	language detection in metadata
	•	extraction quality score stored in Postgres
	•	MIME sniffing instead of extension-only detection
	•	fixture-based tests for each processor
	•	benchmark logging for large files

⸻

18. Explicit Non-Goals for Step 2

Do not add yet:
	•	UI
	•	tag-based retrieval filtering
	•	rerankers
	•	multimodal image understanding inside PDFs/EPUBs
	•	advanced session management beyond current scope

⸻

19. Engineering Requirements

Codex must follow these implementation rules:
	•	use clean modular architecture
	•	split code into maintainable files
	•	use type hints
	•	use docstrings where useful
	•	use structured logging
	•	use best practices
	•	refactor when needed
	•	avoid large monolithic files
	•	update docs continuously
	•	update changelog.md continuously