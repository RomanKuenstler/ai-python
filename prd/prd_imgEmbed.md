Step: Add multimodal image/document retrieval with visual asset support using hf.co/Qwen/Qwen3-VL-Embedding-2B

Work on the existing project and implement a stable multimodal retrieval upgrade centered on image embeddings and visual asset handling. Use official model cards and official docs first. Do not guess APIs, processor behavior, or modality support. Before changing code, inspect the current codebase and current model, embedder, retriever, library, attachment, PDF, EPUB, OCR, and frontend source-display flows, then verify the correct usage from the official sources.

Objective

Extend the current system from text-first retrieval into multimodal knowledge retrieval with visual asset support, using:
	•	Embedding model: hf.co/Qwen/Qwen3-VL-Embedding-2B

This step should improve retrieval for:
	•	uploaded image files
	•	PDF pages and image-heavy PDFs
	•	scanned documents
	•	screenshots
	•	diagram-heavy content
	•	tables when text extraction is weak
	•	future-ready multimodal document retrieval

This step must also prepare the system so retrieved image-backed knowledge can later be shown in the chat UI as visual source previews.

Important design direction

Do not replace OCR/text extraction with image embeddings.

Implement a hybrid design:
	•	keep OCR and text extraction as first-class paths
	•	add visual embeddings as an additional retrieval path
	•	store extracted/stable image assets and link them to vector metadata
	•	keep the architecture ready for future multimodal retrieval expansion

This is important because the current answer model is still text-first, so image retrieval should improve retrieval quality and source display even when final generation still relies primarily on text/OCR-derived context. The official Qwen model card for Qwen3-VL-Embedding-2B explicitly describes it as a multimodal information retrieval model that accepts text, images, screenshots, videos, and mixed multimodal inputs, which supports this architecture.  ￼

Explicit non-goals for this step

Do not implement:
	•	full video embeddings
	•	figure/table region detection beyond a first simple pass
	•	vision-generation at answer time
	•	automatic multimodal reranking unless it fits very cleanly

Research requirements

Use official docs / official model cards / official library docs first to verify at minimum:
	1.	how Qwen/Qwen3-VL-Embedding-2B should be loaded and used for embeddings
	2.	whether it supports:
	•	text inputs
	•	image inputs
	•	mixed multimodal inputs
	3.	whether it requires a processor rather than a text-only tokenizer path
	4.	recommended inference/runtime usage for our stack
	5.	any model-specific embedding instructions, query/document formatting, or processor requirements
	6.	image preprocessing expectations
	7.	how multimodal inputs should be normalized before embedding
	8.	any performance or memory guidance relevant to a local deployment

Because multimodal models require processors that combine modality-specific preprocessing, do not force this into an old tokenizer-only abstraction if that is no longer correct. Hugging Face’s processor docs explicitly note that multimodal models use processors to handle text, image, and audio preprocessing together.  ￼

Scope of this step

Implement all of the following:

1. Image embedding support for uploaded image files

Add support for embedding image files as knowledge sources.

Target image formats at minimum:
	•	.png
	•	.jpg
	•	.jpeg
	•	.webp

For image files:
	•	keep OCR text extraction
	•	also generate visual embeddings
	•	store the original or normalized image asset in a managed asset location
	•	store metadata linking asset ↔ source file ↔ vector entries

2. PDF visual support

Improve PDF ingestion so PDFs can contribute not only text/OCR chunks, but also visual page assets.

For PDFs:
	•	keep current text extraction
	•	keep OCR fallback
	•	render pages to images
	•	create visual embeddings for page images
	•	link visual page assets to the original PDF and page number
	•	keep text and visual retrieval paths both available

Do not implement advanced figure segmentation beyond a basic/simple pass if something easy already fits the architecture.

3. EPUB visual support where straightforward

Keep EPUB text-first, but improve the architecture so embedded images/assets inside EPUBs can be represented when this is straightforward and stable.

Minimum requirement:
	•	keep EPUB text extraction as primary
	•	if EPUB images are easy to extract cleanly, store them as assets and prepare them for future visual retrieval
	•	do not overcomplicate EPUB image extraction in this step

4. CSV ingestion

Add .csv ingestion support in this step.

For CSV:
	•	parse structured rows and columns
	•	convert into clean structured text for embedding
	•	preserve useful metadata such as column names and row grouping
	•	do not add a visual CSV rendering path yet unless it fits very cleanly

5. Asset storage and linking

Introduce a clean asset storage layer for extracted or uploaded visual assets.

This must support:
	•	stable asset ids
	•	source file linkage
	•	file/page/chunk linkage
	•	metadata in Postgres
	•	safe cleanup on source deletion
	•	frontend retrieval later for source preview display

The system should not just compute image embeddings and discard the images. Assets must be stored and linked so retrieved results can later be shown visually in the UI.

6. Retrieval metadata upgrade

Extend retrieval metadata so a retrieved item can represent more than a text chunk.

Support explicit entity/source types such as:
	•	text chunk
	•	OCR text chunk
	•	page image
	•	image asset
	•	table-like text chunk
	•	CSV structured chunk

This will make prompt building and frontend source rendering much cleaner.

7. Frontend source preview support

Extend the frontend source display so it can render visual source previews when retrieval results include linked image/page assets.

Minimum requirement:
	•	if a retrieved source has a linked visual asset, show a small preview or thumbnail in the Sources section/panel
	•	keep existing text/source metadata display working
	•	do not redesign the whole UI in this step unless necessary
	•	keep the implementation stable and consistent with the current UI

8. Attachment compatibility

Review the attachment system.

For image attachments:
	•	OCR text extraction should continue to work
	•	visual embedding path should be added if it fits cleanly
	•	attachments must remain ephemeral
	•	attached images must not be permanently added to Qdrant/library unless the current design explicitly already persists them

9. Hybrid retrieval design

Do not implement image retrieval as “visual only.”

The system should support a hybrid model where:
	•	OCR/text extraction still produces text chunks
	•	visual embeddings produce image/page vectors
	•	both can coexist for the same source document

Design the retrieval logic so the system can work with mixed candidate types.

10. Query-time behavior

Keep this step stable and pragmatic.

If a fully merged multimodal query path is too disruptive, implement the cleanest stable version that:
	•	supports retrieval over image/page vectors
	•	preserves the existing text retrieval path
	•	keeps the architecture ready for future weighting/reranking improvements

Do not force automatic multimodal reranking in this step unless it fits very cleanly.

Architecture requirements

1. Preserve OCR/text paths

Keep and improve the current OCR/text extraction paths. Visual embeddings are additive, not replacement.

2. Use a clean abstraction

Create or improve reusable abstractions for:
	•	multimodal embedding service
	•	asset extraction/storage
	•	PDF page rendering
	•	image metadata
	•	multimodal retrieval result representation

3. Avoid duplication

Do not duplicate image handling separately in:
	•	library ingestion
	•	attachment ingestion
	•	PDF processing
	•	source rendering

Create shared utilities/services where appropriate.

Implementation requirements

1. Update embedding integration for multimodal use

Review and update the current embedding service so Qwen/Qwen3-VL-Embedding-2B is used correctly for multimodal embeddings.

Tasks:
	•	update model loading
	•	update processor handling
	•	update text embedding path if the new processor/model requires a different integration pattern
	•	add image embedding path
	•	keep the rest of the architecture stable

The official model card describes the model as specifically designed for multimodal retrieval and cross-modal understanding, accepting text, images, screenshots, videos, and mixtures of these modalities. That means the project should not keep treating it as if it were a plain text-only embedder.  ￼

2. Add image file ingestion

For uploaded image files in the library:
	•	validate file type
	•	normalize/load image safely
	•	run OCR text extraction if available
	•	generate visual embedding
	•	store asset
	•	store metadata
	•	index appropriately
	•	keep tags, ownership, and enable/disable logic working

3. Add PDF page-image extraction

For PDFs:
	•	render pages to images
	•	store rendered page assets
	•	create visual embeddings for the pages
	•	link page assets to PDF metadata and page numbers
	•	keep current text/OCR chunking/indexing behavior working

4. Add CSV ingestion

Add .csv support with:
	•	robust parsing
	•	row/column-aware normalization
	•	structured text conversion
	•	chunking suitable for tables/rows
	•	metadata for source display

5. Extend asset cleanup lifecycle

When a source file is deleted:
	•	delete linked assets
	•	delete linked metadata
	•	delete linked vectors
	•	keep cleanup safe and consistent

6. Retrieval and metadata updates

Extend retrieval logic and response metadata so results can include:
	•	source type
	•	asset id / asset URL or API path
	•	page number
	•	preview-eligible flag
	•	text snippet when available
	•	existing score/tags/source fields

7. Frontend Sources panel

When a source contains a linked visual asset:
	•	show the preview
	•	keep metadata visible
	•	do not break existing source rendering
	•	handle missing/invalid assets gracefully

8. Prompt-building rule

Because the current answer path is still text-first, do not assume the final answer model can interpret raw retrieved images directly.

For now:
	•	retrieved visual results should primarily improve retrieval and source display
	•	OCR text / extracted text / captions / surrounding text should still be what gets injected into the text prompt where applicable
	•	do not add “vision answer generation” in this step

9. File types covered in this step

At minimum cover:
	•	image files: .png, .jpg, .jpeg, .webp
	•	PDFs with page render assets
	•	CSV structured text support

Keep current support for:
	•	.txt
	•	.md
	•	.html
	•	.htm
	•	.pdf
	•	.epub

10. Keep future video in mind without implementing it

Structure the new asset and multimodal abstractions so video can be added later without a major rewrite, but do not implement video embeddings now.

Data model requirements

Add/extend schema as needed for:
	•	assets table or equivalent
	•	asset-to-file linkage
	•	asset type
	•	preview metadata
	•	page number
	•	retrieval result type
	•	cleanup relationships

Keep migrations clean and production-safe.

Config requirements

Add or update config as needed, for example:
	•	image embedding enabled/disabled
	•	allowed image extensions
	•	PDF page render DPI / scale
	•	asset storage path
	•	preview max dimensions if needed
	•	CSV parsing limits if needed

Do not add unnecessary config, but document anything introduced.

Runtime and dependency requirements

Update dependencies and runtime only as needed based on official guidance and the actual implementation.

Check and update where relevant:
	•	backend Python dependencies
	•	image libraries
	•	PDF rendering dependencies
	•	OCR/runtime dependencies if reused
	•	Dockerfiles
	•	compose files
	•	prod Dockerfiles
	•	prod compose
	•	docs

Validation requirements

This step is not complete when image embeddings merely exist in code.

It is complete only after the result has been checked, tested, and debugged where necessary.

Validate at minimum:
	1.	Qwen/Qwen3-VL-Embedding-2B still loads correctly for the updated integration
	2.	text embeddings still work after the multimodal integration changes
	3.	image file ingestion works
	4.	OCR + image embedding hybrid path works for image files
	5.	PDF page rendering works
	6.	PDF visual page embeddings are created
	7.	PDF text/OCR behavior is not broken
	8.	CSV ingestion works
	9.	retrieval can return image/page-backed results
	10.	source metadata includes visual asset linkage when applicable
	11.	frontend can display visual source previews
	12.	file deletion cleans up linked assets correctly
	13.	attachment behavior is not broken
	14.	auth-protected routes remain protected
	15.	no regression from previous steps

If issues are found:
	1.	identify root cause
	2.	debug and fix
	3.	rerun validation
	4.	update docs and changelog

Testing requirements

Update and/or add tests where practical for:
	•	multimodal embedding wrapper loading
	•	image ingestion
	•	PDF page rendering
	•	asset storage and cleanup
	•	CSV parsing and structured chunking
	•	retrieval metadata with visual sources
	•	frontend source preview rendering
	•	migration coverage for new asset metadata
	•	auth/permissions around visual asset serving if relevant

Documentation requirements

Update at minimum:
	•	README.md
	•	docs/setup.md
	•	docs/development.md
	•	docs/production.md
	•	docs/testing.md
	•	docs/architecture.md
	•	docs/library.md
	•	docs/attachments.md
	•	docs/api.md
	•	changelog.md

Also document:
	•	hybrid retrieval design
	•	supported image formats
	•	PDF visual asset behavior
	•	CSV ingestion behavior
	•	asset storage and cleanup rules
	•	how source previews work
	•	known limitations

Deliverable expectations

When finished:
	•	the system supports multimodal image/document retrieval using hf.co/Qwen/Qwen3-VL-Embedding-2B
	•	image uploads work as knowledge sources
	•	PDFs gain page-image visual support
	•	CSV ingestion works
	•	visual assets are stored and linked cleanly
	•	retrieved visual sources can be previewed in the UI
	•	OCR/text extraction remains intact
	•	the code is clean and maintainable
	•	tests/docs/changelog are updated
	•	the result has been verified and debugged if needed